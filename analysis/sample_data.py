"""Generates a sample trade log matching the EA's CSV export schema exactly.

Used for the shipped example file and for tests — nothing here comes from a
real MetaTrader run, since this environment cannot compile or execute MQL5.
"""

import random
from datetime import datetime, timedelta

import polars as pl


def generate_sample_trade_log(
    trade_count: int = 60,
    starting_balance: float = 10000.0,
    win_probability: float = 0.52,
    seed: int = 42,
) -> pl.DataFrame:
    rng = random.Random(seed)
    balance = starting_balance
    close_time = datetime(2026, 1, 1)
    rows = []

    for _ in range(trade_count):
        won = rng.random() < win_probability
        # Rounded once, here, so the logged profit and the running balance it
        # produces always agree exactly — a real export should never let the
        # two drift apart over many trades of unrounded floating-point sums.
        profit = round(rng.uniform(5, 40) if won else -rng.uniform(5, 35), 2)
        balance = round(balance + profit, 2)
        close_time += timedelta(hours=rng.randint(4, 30))

        rows.append(
            {
                "close_time": close_time.strftime("%Y.%m.%d %H:%M:%S"),
                "symbol": "EURUSD",
                "direction": rng.choice(["buy", "sell"]),
                "exit_price": round(rng.uniform(1.05, 1.15), 5),
                "lots": 0.1,
                "profit": profit,
                "balance_after": balance,
            }
        )

    return pl.DataFrame(rows)
