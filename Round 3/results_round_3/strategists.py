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

        self.bid_volume = self.ask_volume = self.new_bid_price = self.new_ask_price = 0

        self.last_bid_id = self.last_ask_id = 0

        self._abs = abs
        self._int = int
        self._print = print
        self._next = next

        self.abs_position = 0
        self.theo_price = 0

        self.start_second = 0
        self.current_time = 0
        self.time_diff = 0
        self.action_count = 0

        self.risk_factor = 10
        self.bid_vol_map, self.ask_vol_map = self.quote_maps(self.risk_factor)

    def on_error_message(self, client_order_id: int, error_message: bytes) -> None:
        """Called when the exchange detects an error."""

        self.logger.warning("error with order %d: %s", client_order_id, error_message.decode())
        self.on_order_status_message(client_order_id, 0, 0, 0)

    def on_order_book_update_message(self, instrument: int, sequence_number: int, ask_prices: List[int],
                                     ask_volumes: List[int], bid_prices: List[int], bid_volumes: List[int]) -> None:
        """Called periodically to report the status of an order book."""

        if instrument == Instrument.FUTURE:

            if self.action_count == 0:
                self.start_second = time.time()

            if 0 not in bid_prices:
                self.theo_price = self._int(((
                    (((bid_prices[0] * bid_volumes[0])) +
                        ((bid_prices[1] * bid_volumes[1])) +
                        ((bid_prices[2] * bid_volumes[2])) +
                        ((bid_prices[3] * bid_volumes[3])) +
                        ((bid_prices[4] * bid_volumes[4])) +
                        ((ask_prices[0] * ask_volumes[0])) +
                        ((ask_prices[1] * ask_volumes[1])) +
                        ((ask_prices[2] * ask_volumes[2])) +
                        ((ask_prices[3] * ask_volumes[3])) +
                        ((ask_prices[4] * ask_volumes[4]))) /
                    ((bid_volumes[0] +
                        bid_volumes[1] +
                        bid_volumes[2] +
                        bid_volumes[3] +
                        bid_volumes[4] +
                        ask_volumes[0] +
                        ask_volumes[1] +
                        ask_volumes[2] +
                        ask_volumes[3] +
                        ask_volumes[4])))) / 100) * 100

                self.new_bid_price = self.theo_price - 100 if bid_prices[0] != 0 else 0
                self.new_ask_price = self.theo_price + 100 if ask_prices[0] != 0 else 0

            if self.action_count <= 18:

                # Cancel existing quotes if they differ from new quotes.
                if self.bid_id != 0 and self.new_bid_price not in (self.bid_price, 0):
                    self.send_cancel_order(self.bid_id)
                    self.bid_id = 0
                    self.action_count += 1
                if self.ask_id != 0 and self.new_ask_price not in (self.ask_price, 0):
                    self.send_cancel_order(self.ask_id)
                    self.ask_id = 0
                    self.action_count += 1

            if self.action_count <= 14:

                self.bid_volume = self.bid_vol_map[self.position]
                self.ask_volume = self.ask_vol_map[self.position]

                if self.bid_id == 0 and self.new_bid_price != 0 and self.bid_volume != 0:
                    self.bid_id = self._next(self.order_ids)
                    self.bid_price = self.new_bid_price
                    self.send_insert_order(self.bid_id, Side.BUY, self.new_bid_price, self.bid_volume, Lifespan.GOOD_FOR_DAY)
                    self.action_count += 1

                if self.ask_id == 0 and self.new_ask_price != 0 and self.ask_volume != 0:
                    self.ask_id = self._next(self.order_ids)
                    self.ask_price = self.new_ask_price
                    self.send_insert_order(self.ask_id, Side.SELL, self.new_ask_price, self.ask_volume, Lifespan.GOOD_FOR_DAY)
                    self.action_count += 1

            elif self.action_count > 14:
                self.current_time = time.time()
                self.time_diff = self.current_time - self.start_second

                if self.time_diff < 1:
                    time.sleep(1.01 - self.time_diff)

                self.action_count = 0

    def on_order_status_message(self, client_order_id: int, fill_volume: int, remaining_volume: int, fees: int) -> None:
        """Called when the status of one of your orders changes."""

        if remaining_volume == 0:
            if client_order_id == self.bid_id:
                self.bid_id = 0
            elif client_order_id == self.ask_id:
                self.ask_id = 0

    def on_position_change_message(self, future_position: int, etf_position: int) -> None:
        """Called when your position changes."""
        self.position = etf_position

        # Set quote volumes.
        self.bid_volume = self.bid_vol_map[self.position]
        self.ask_volume = self.ask_vol_map[self.position]

    def on_trade_ticks_message(self, instrument: int, trade_ticks: List[Tuple[int, int]]) -> None:
        """Called periodically to report trading activity on the market.
        Each trade tick is a pair containing a price and the number of lots
        traded at that price since the last trade ticks message.
        """

    def quote_maps(self, risk_factor) -> dict:
        """Return bid and ask quote maps."""

        ask_vol_map = {}
        bid_vol_map = {}

        for position in range(-100, 101):

            bid_vol = self._int(math.floor(((100 - position - risk_factor) / 2)) - self._int(risk_factor / 2))
            bid_vol = 0 if bid_vol < 0 else bid_vol

            if position < 0:
                ask_vol = self._int(math.floor(((100 - self._abs(position) - risk_factor) / 2)) - self._int(risk_factor / 2))
            else:
                ask_vol = self._int(math.floor(((100 + abs(position) - risk_factor) / 2)) - self._int(risk_factor / 2))
            ask_vol = 0 if ask_vol < 0 else ask_vol

            bid_vol_map[position] = bid_vol
            ask_vol_map[position] = ask_vol

        return bid_vol_map, ask_vol_map
