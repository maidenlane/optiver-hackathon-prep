from datetime import datetime
from bisect import bisect
import itertools
import asyncio
import math
import time

from typing import List, Tuple

from ready_trader_one import BaseAutoTrader, Instrument, Lifespan, Side


class AutoTrader(BaseAutoTrader):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        """Initialise a new instance of the AutoTrader class."""

        super(AutoTrader, self).__init__(loop)
        self.order_ids = itertools.count(1)
        self.ask_id = self.ask_price = self.bid_id = self.bid_price = self.position = self.size = 0

        self.bid_volume = self.ask_volume = self.new_bid_price = self.new_ask_price = 0

        self.last_bid_id = self.last_ask_id = 0

        self.abs_position = 0
        self.theo_price = 0

        self.start_second = 0
        self.current_time = 0
        self.time_diff = 0
        self.action_count = 0

        self._abs = abs
        self._int = int
        self._print = print
        self._next = next

    def on_error_message(self, client_order_id: int, error_message: bytes) -> None:
        """Called when the exchange detects an error."""

        self.logger.warning("error with order %d: %s", client_order_id, error_message.decode())
        self._print("error with order", client_order_id, error_message.decode(), "Position:", self.position, "Bid vol:", self.bid_volume, "Ask_vol:", self.ask_volume)
        self.on_order_status_message(client_order_id, 0, 0, 0)

    def on_order_book_update_message(self, instrument: int, sequence_number: int, ask_prices: List[int],
                                     ask_volumes: List[int], bid_prices: List[int], bid_volumes: List[int]) -> None:
        """Called periodically to report the status of an order book."""

        if instrument == Instrument.FUTURE:

            # Count action
            if self.action_count == 0:
                self.start_second = time.time()

            # Theoretical price = weighted average orderbook levels 1, 2 and 3.
            if 0 not in bid_prices and self.action_count <= 16:
                self.theo_price = self._int((((
                    (bid_prices[0] * bid_volumes[0] + bid_prices[1] * bid_volumes[1] + bid_prices[2] * bid_volumes[2]) / (bid_volumes[0] + bid_volumes[1] + bid_volumes[2]) +
                    (ask_prices[0] * ask_volumes[0] + ask_prices[1] * ask_volumes[1] + ask_prices[2] * ask_volumes[2]) / (ask_volumes[0] + ask_volumes[1] + ask_volumes[2])) / 2)) / 100) * 100

                # Use theo price += $1 for bid/ask.
                self.new_bid_price = self.theo_price - 100 if bid_prices[0] != 0 else 0
                self.new_ask_price = self.theo_price + 100 if ask_prices[0] != 0 else 0

                # Cancel existing quotes if they differ from new quotes.
                if self.bid_id != 0 and self.new_bid_price not in (self.bid_price, 0):
                    self.send_cancel_order(self.bid_id)
                    # print("Order", self.bid_id, "cancelled.")
                    self.bid_id = 0
                    self.action_count += 1
                if self.ask_id != 0 and self.new_ask_price not in (self.ask_price, 0):
                    self.send_cancel_order(self.ask_id)
                    # print("Order", self.ask_id, "cancelled.")
                    self.ask_id = 0
                    self.action_count += 1

            # Place new orders if within action limit.
            if self.action_count <= 14:

                """
                Position should never exceed +-99 lots. This method accounts
                for when orders are crossed before they have a chance to be
                cancelled.
                """

                # If long.
                if self.position > 0:

                    # Adjust quote volume for small long position.
                    if self.position < 45:
                        self.bid_volume = 45 - self.position
                        self.ask_volume = 50

                    # Adjust quote volume for moderate long position.
                    elif self.position >= 45 and self.position < 65:
                        self.bid_volume = 65 - self.position
                        self.ask_volume = 50

                    # Adjust quote volume for large long position.
                    elif self.position >= 65 and self.position < 82:
                        self.bid_volume = 82 - self.position
                        self.ask_volume = 65

                    # Adjust quote volume for extreme long position.
                    elif self.position >= 82 and self.position < 100:
                        self.bid_volume = 91 - self.position
                        self.ask_volume = 85

                # If short.
                elif self.position < 0:

                    self.abs_position = self._abs(self.position)

                    # Adjust quote volume for small short position.
                    if self.position > -45:
                        self.bid_volume = 10
                        self.ask_volume = 45 - self.abs_position

                    # Adjust quote volume for moderate short position.
                    elif self.position <= -45 and self.position > -65:
                        self.bid_volume = 50
                        self.ask_volume = 65 - self.abs_position

                    # Adjust quote volume for large short position.
                    elif self.position <= -65 and self.position > -82:
                        self.bid_volume = 65
                        self.ask_volume = 82 - self.abs_position

                    # Adjust quote volume for extreme short position.
                    elif self.position <= -82 and self.position > -100:
                        self.bid_volume = 75
                        self.ask_volume = 85 - self.abs_position

                # Adjust quote volume for no position.
                elif self.position == 0:
                    self.bid_volume = 50
                    self.ask_volume = 50

                # Correct negative bids (need to identify why this happens).
                if self.bid_volume < 0:
                    self.bid_volume = 0
                if self.ask_volume < 0:
                    self.ask_volume = 0

                # Place bid quotes only if within hard limits.
                if self.bid_id == 0 and self.new_bid_price != 0 and self.bid_volume != 0:
                    self.bid_id = self._next(self.order_ids)
                    self.bid_price = self.new_bid_price
                    self.send_insert_order(self.bid_id, Side.BUY, self.new_bid_price, self.bid_volume, Lifespan.GOOD_FOR_DAY)
                    # self._print("Order#:", self.bid_id,  "Bid volume:", self.bid_volume, "Position:", self.position)
                    self.action_count += 1

                # Place ask quote only if within hard limits.
                if self.ask_id == 0 and self.new_ask_price != 0 and self.ask_volume != 0:
                    self.ask_id = self._next(self.order_ids)
                    self.ask_price = self.new_ask_price
                    self.send_insert_order(self.ask_id, Side.SELL, self.new_ask_price, self.ask_volume, Lifespan.GOOD_FOR_DAY)
                    # print("Order#:", self.ask_id,  "Ask volume:", self.ask_volume, "Position:", self.position)
                    self.action_count += 1

            # Reset action count if within time constraints.
            elif self.action_count >= 14:
                self.current_time = time.time()
                self.time_diff = self.current_time - self.start_second

                # print("Time diff:", self.time_diff, "Action count:", self.action_count)

                # Sleep for remainder of second if necessary.
                if self.time_diff < 1:
                    time.sleep(1.01 - self.time_diff)

                self.action_count = 0

    def on_order_status_message(self, client_order_id: int, fill_volume: int, remaining_volume: int, fees: int) -> None:
        """Called when the status of one of your orders changes."""

        # Set order ID's for orders just filled.
        if remaining_volume == 0:
            if client_order_id == self.bid_id:
                self.bid_id = 0
            elif client_order_id == self.ask_id:
                self.ask_id = 0

    def on_position_change_message(self, future_position: int, etf_position: int) -> None:
        """Called when your position changes."""
        self.position = etf_position

    def on_trade_ticks_message(self, instrument: int, trade_ticks: List[Tuple[int, int]]) -> None:
        """Called periodically to report trading activity on the market.
        Each trade tick is a pair containing a price and the number of lots
        traded at that price since the last trade ticks message.
        """
