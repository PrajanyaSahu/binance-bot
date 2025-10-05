"""
Simple CLI script to place Market Orders on Binance USDT-M Futures.
Supports --dry-run mode so you can test without sending real trades.

Example:
    python src/market_orders.py --symbol BTCUSDT --side BUY --qty 0.001 --dry-run
"""
import os
import argparse
from decimal import Decimal
from binance.client import Client
from binance.enums import FUTURE_ORDER_TYPE_MARKET
from logger_config import get_logger
from validation import validate_symbol, validate_side, validate_quantity

logger = get_logger(__name__)

# Load API keys from environment variables
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


def create_client():
    """Initialize Binance Futures client, or None if keys not found (dry-run only)."""
    if not API_KEY or not API_SECRET:
        logger.warning("API key/secret not found in environment; running dry-run only")
        return None
    return Client(API_KEY, API_SECRET)


def place_market_order(client, symbol: str, side: str, qty: Decimal, dry_run: bool = True):
    """Places a market order or simulates if dry-run is enabled."""
    logger.info(f"Placing market order: {symbol} {side} {qty}")
    if dry_run or client is None:
        logger.info("Dry-run mode: not sending order to Binance")
        return {"status": "DRY_RUN", "symbol": symbol, "side": side, "qty": str(qty)}

    try:
        response = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=FUTURE_ORDER_TYPE_MARKET,
            quantity=float(qty)
        )
        logger.info(f"Order response: {response}")
        return response
    except Exception:
        logger.exception("Failed to place market order")
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", required=True)
    p.add_argument("--side", required=True)
    p.add_argument("--qty", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    # Validate inputs
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        qty = validate_quantity(args.qty)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return

    client = create_client()
    res = place_market_order(client, symbol, side, qty, dry_run=args.dry_run)
    logger.info(f"Result: {res}")


if __name__ == "__main__":
    main()
