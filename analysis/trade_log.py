"""Loads and validates a trade log exported by the MQL5 EA."""

import polars as pl

EXPECTED_COLUMNS = [
    "close_time",
    "symbol",
    "direction",
    "exit_price",
    "lots",
    "profit",
    "balance_after",
]


def load_trade_log(path: str) -> pl.DataFrame:
    frame = pl.read_csv(path)
    missing_columns = set(EXPECTED_COLUMNS) - set(frame.columns)
    if missing_columns:
        raise ValueError(f"Trade log is missing expected columns: {sorted(missing_columns)}")

    return frame.with_columns(pl.col("close_time").str.to_datetime("%Y.%m.%d %H:%M:%S"))
