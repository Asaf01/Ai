
from datetime import timedelta
from typing import Dict, Any

import databento as db
import pandas as pd
import pytz


TODAY = "2025-07-05"


class PriceMovementScanner:
    """Scanner for detecting large price movements in all US equities."""

    # Constants
    PX_SCALE: float = 1e-9
    PX_NULL: int = 2**63 - 1
    PCT_MOVE_THRESHOLD: float = 0.03

    def __init__(self, pct_threshold: float = None, today: str = TODAY) -> None:
        """Initialize scanner with configurable threshold and date."""
        self.pct_threshold = pct_threshold or self.PCT_MOVE_THRESHOLD
        self.today = today
        self.today_midnight_ns = int(pd.Timestamp(today).timestamp() * 1e9)
        self.symbol_directory: Dict[int, str] = {}
        self.last_day_lookup: Dict[str, float] = self.get_last_day_lookup()
        self.is_signal_lit: Dict[str, bool] = {symbol: False for symbol in self.last_day_lookup}

    def get_last_day_lookup(self) -> Dict[str, float]:
        """Get yesterday's closing prices for all symbols."""
        client = db.Historical()

        now = pd.Timestamp(self.today).date()
        yesterday = (pd.Timestamp(self.today) - timedelta(days=1)).date()

        # Get yesterday's closing prices
        data = client.timeseries.get_range(
            dataset="EQUS.SUMMARY",
            schema="ohlcv-1d",
            symbols="ALL_SYMBOLS",
            start=yesterday,
            end=now,
        )

        # Request symbology: ALL_SYMBOLS requests
        #  ID to raw ticker symbol
        symbology_json = data.request_symbology(client)
        data.insert_symbology_json(symbology_json, clear_existing=True)

        df = data.to_df()
        # TODO:  Databento corporate actions API

        return dict(zip(df["symbol"], df["close"]))

    def scan(self, event: Any) -> None:
        """
        Scan for large price movements in market data events.
        """
        if isinstance(event, db.SymbolMappingMsg):
            self.symbol_directory[event.hd.instrument_id] = event.stype_out_symbol
            return

        if not isinstance(event, db.MBP1Msg):
            return
            
        # Skip if event is from replay before today using `.subscribe(..., start=...)` parameter
        #if event.hd.ts_event < self.today_midnight_ns:
        #    return

        symbol = self.symbol_directory[event.instrument_id]
        bid = event.levels[0].bid_px
        ask = event.levels[0].ask_px

        if bid == self.PX_NULL or ask == self.PX_NULL:
            # Handle when one side of book is empty
            return

        mid = (event.levels[0].bid_px + event.levels[0].ask_px) * self.PX_SCALE * 0.5
        last = self.last_day_lookup[symbol]
        abs_r = abs(mid - last) / last

        if abs_r > self.pct_threshold and not self.is_signal_lit[symbol]:
            ts = pd.Timestamp(event.hd.ts_event, unit='ns').tz_localize('UTC').tz_convert('US/Eastern')
            print(
                f"[{ts.isoformat()}] {symbol} moved by {abs_r * 100:.2f}% "
                f"(current: {mid:.4f}, previous: {last:.4f})"
            )
            self.is_signal_lit[symbol] = True

def main() -> None:
    scanner = PriceMovementScanner()
    live = db.Live()

    live.subscribe(
        dataset="EQUS.MINI",
        schema="mbp-1",
        stype_in="raw_symbol",
        symbols="ALL_SYMBOLS",
        start=0,
    )

    live.add_callback(scanner.scan)
    live.start()
    live.block_for_close()


if __name__ == "__main__":
    main()
