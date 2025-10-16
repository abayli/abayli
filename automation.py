#!/usr/bin/env python3
"""Crypto arbitrage opportunity finder.

This script fetches current prices for a configurable list of crypto pairs
from both Binance and CoinGecko public APIs. The output highlights potential
arbitrage opportunities when the price difference exceeds a user-defined
threshold.

Usage:
    python automation.py --symbols BTCUSDT ETHUSDT --threshold 0.5

The script is designed to be run periodically (e.g. cron) and log potential
trades to stdout or an optional CSV file.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from dataclasses import dataclass
from typing import Dict, Iterable, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"


@dataclass
class PriceQuote:
    """Container for normalized price information."""

    symbol: str
    exchange: str
    price: float
    timestamp: dt.datetime


class PriceFetcherError(RuntimeError):
    """Raised when a fetcher cannot retrieve price data."""


def _get_json(url: str, params: Dict[str, str]) -> Dict[str, object]:
    query = urlencode(params)
    full_url = f"{url}?{query}" if params else url
    try:
        with urlopen(full_url, timeout=10) as response:  # nosec B310 (read-only call)
            payload = response.read().decode("utf-8")
    except (HTTPError, URLError) as exc:
        raise PriceFetcherError(f"Request failed for {full_url}: {exc}") from exc
    return json.loads(payload)


def fetch_binance_prices(symbols: Iterable[str]) -> Dict[str, PriceQuote]:
    """Fetch spot prices for the provided Binance symbols."""
    quotes: Dict[str, PriceQuote] = {}
    for symbol in symbols:
        data = _get_json(BINANCE_URL, {"symbol": symbol})
        price = float(data["price"])
        quotes[symbol] = PriceQuote(
            symbol=symbol,
            exchange="binance",
            price=price,
            timestamp=dt.datetime.utcnow(),
        )
    return quotes


def fetch_coingecko_prices(symbols: Iterable[str]) -> Dict[str, PriceQuote]:
    """Fetch prices for the provided symbols via CoinGecko's simple price API.

    CoinGecko identifies assets by lowercase coin ids. The script converts
    Binance-style pairs (e.g. BTCUSDT) to a base currency id and uses USDT as
    the vs_currency when available. Only USDT pairs are supported to keep the
    example simple.
    """
    ids: List[str] = []
    symbol_map: Dict[str, str] = {}
    for symbol in symbols:
        if not symbol.endswith("USDT"):
            raise PriceFetcherError(
                "CoinGecko fetcher currently only supports USDT quote pairs."
            )
        coin_id = symbol[:-4].lower()
        ids.append(coin_id)
        symbol_map[coin_id] = symbol

    data = _get_json(COINGECKO_URL, {"ids": ",".join(ids), "vs_currencies": "usdt"})

    quotes: Dict[str, PriceQuote] = {}
    now = dt.datetime.utcnow()
    for coin_id, payload in data.items():
        price = float(payload["usdt"])
        symbol = symbol_map[coin_id]
        quotes[symbol] = PriceQuote(
            symbol=symbol,
            exchange="coingecko",
            price=price,
            timestamp=now,
        )
    return quotes


def analyze_arbitrage(
    binance_quotes: Dict[str, PriceQuote],
    coingecko_quotes: Dict[str, PriceQuote],
    threshold: float,
) -> List[Dict[str, object]]:
    """Identify arbitrage candidates above the provided percentage threshold."""
    opportunities: List[Dict[str, object]] = []
    for symbol, binance_quote in binance_quotes.items():
        if symbol not in coingecko_quotes:
            continue
        coingecko_quote = coingecko_quotes[symbol]

        # percent difference relative to CoinGecko reference price
        diff = binance_quote.price - coingecko_quote.price
        percent_diff = (diff / coingecko_quote.price) * 100

        if abs(percent_diff) >= threshold:
            opportunities.append(
                {
                    "symbol": symbol,
                    "binance_price": binance_quote.price,
                    "coingecko_price": coingecko_quote.price,
                    "percent_diff": percent_diff,
                    "timestamp": binance_quote.timestamp.isoformat(),
                }
            )
    return sorted(opportunities, key=lambda item: abs(item["percent_diff"]), reverse=True)


def write_csv(opportunities: Iterable[Dict[str, object]], output_path: str) -> None:
    """Persist opportunities to a CSV file for record keeping."""
    fieldnames = [
        "timestamp",
        "symbol",
        "binance_price",
        "coingecko_price",
        "percent_diff",
    ]
    with open(output_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        for row in opportunities:
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan Binance vs CoinGecko prices for arbitrage opportunities."
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["BTCUSDT", "ETHUSDT"],
        help="Binance trading pairs to evaluate (default: BTCUSDT ETHUSDT)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Minimum percent difference to report (default: 0.5)",
    )
    parser.add_argument(
        "--csv",
        type=str,
        help="Optional CSV output path to append arbitrage opportunities.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    binance_quotes = fetch_binance_prices(args.symbols)
    coingecko_quotes = fetch_coingecko_prices(args.symbols)
    opportunities = analyze_arbitrage(binance_quotes, coingecko_quotes, args.threshold)

    if not opportunities:
        print(
            f"No opportunities above {args.threshold:.2f}% for symbols: {', '.join(args.symbols)}"
        )
        return

    print("Potential arbitrage opportunities detected:")
    for opp in opportunities:
        print(
            f"[{opp['timestamp']}] {opp['symbol']}: Binance {opp['binance_price']:.4f} | "
            f"CoinGecko {opp['coingecko_price']:.4f} | diff {opp['percent_diff']:.2f}%"
        )

    if args.csv:
        write_csv(opportunities, args.csv)
        print(f"Logged {len(opportunities)} opportunities to {args.csv}")


if __name__ == "__main__":
    main()
