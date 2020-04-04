from datetime import datetime
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

        self.tick_storage_limit = 5000

        self.order_volume = 1
        self.theo_price = 0

        self.start_second = 0
        self.current_time = 0
        self.time_diff = 0
        self.action_count = 0

    def on_error_message(self, client_order_id: int, error_message: bytes) -> None:
        """Called when the exchange detects an error."""
        self.logger.warning("error with order %d: %s", client_order_id, error_message.decode())
        self.on_order_status_message(client_order_id, 0, 0, 0)

    def on_order_book_update_message(self, instrument: int, sequence_number: int, ask_prices: List[int],
                                     ask_volumes: List[int], bid_prices: List[int], bid_volumes: List[int]) -> None:
        """Called periodically to report the status of an order book."""

        if instrument == Instrument.FUTURE:

            # Dont place orders if near action limit.
            if self.action_count <= 14:
                if self.action_count == 0:
                    self.start_second = time.time()

                    # Use the current best bid and ask as new bid and ask quotes, skewing by inventory qty.
                    new_bid_price = bid_prices[0] - self.position * 100 if bid_prices[0] != 0 else 0
                    new_ask_price = ask_prices[0] - self.position * 100 if ask_prices[0] != 0 else 0

                    # If the new quoted price differs from the existing quoted price, cancel the old order.
                    if self.bid_id != 0 and new_bid_price not in (self.bid_price, 0):
                        self.send_cancel_order(self.bid_id)
                        self.bid_id = 0
                        self.action_count += 1
                    if self.ask_id != 0 and new_ask_price not in (self.ask_price, 0):
                        self.send_cancel_order(self.ask_id)
                        self.ask_id = 0
                        self.action_count += 1

                    # Determine bid volume according to current position.
                    if self.bid_id == 0 and new_bid_price != 0 and self.position < 95:
                        self.bid_id = next(self.order_ids)
                        self.bid_price = new_bid_price
                        self.send_insert_order(self.bid_id, Side.BUY, new_bid_price, self.order_volume, Lifespan.GOOD_FOR_DAY)
                        self.action_count += 1

                    # Determine ask volume according to current position.
                    if self.ask_id == 0 and new_ask_price != 0 and self.position > -95:
                        self.ask_id = next(self.order_ids)
                        self.ask_price = new_ask_price
                        self.send_insert_order(self.ask_id, Side.SELL, new_ask_price, self.order_volume, Lifespan.GOOD_FOR_DAY)
                        self.action_count += 1

            elif self.action_count > 14:
                self.current_time = time.time()
                self.time_diff = self.current_time - self.start_second

                # Wait for 1 second to elapse if required.
                if self.time_diff < 1:
                    time.sleep(1.01 - self.time_diff)
                    # time.sleep(self.ms_til_next_second())

                self.action_count = 0

    def on_order_status_message(self, client_order_id: int, fill_volume: int, remaining_volume: int, fees: int) -> None:
        """Called when the status of one of your orders changes.

        The fill_volume is the number of lots already traded, remaining_volume
        is the number of lots yet to be traded and fees is the total fees for
        this order. Remember that you pay fees for being a market taker, but
        you receive fees for being a market maker, so fees can be negative.

        If an order is cancelled its remaining volume will be zero.
        """
        if remaining_volume == 0:
            if client_order_id == self.bid_id:
                self.bid_id = 0
            elif client_order_id == self.ask_id:
                self.ask_id = 0

    def on_position_change_message(self, future_position: int, etf_position: int) -> None:
        """Called when your position changes.

        Since every trade in the ETF is automatically hedged in the future,
        future_position and etf_position will always be the inverse of each
        other (i.e. future_position == -1 * etf_position).
        """
        self.position = etf_position

    def on_trade_ticks_message(self, instrument: int, trade_ticks: List[Tuple[int, int]]) -> None:
        """Called periodically to report trading activity on the market.

        Each trade tick is a pair containing a price and the number of lots
        traded at that price since the last trade ticks message.
        """

    def ms_til_next_second(self):
        """Return number of milliseconds (expressed as seconds) until next second."""

        delay = math.trunc((1000000 - datetime.utcnow().microsecond) / 1000)

        return delay / 1000