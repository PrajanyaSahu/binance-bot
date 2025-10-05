"""
Stop-Limit watcher: watches market price and places a LIMIT order when a STOP trigger is hit.

Usage example (dry-run):
  python src/advanced/stop_limit.py --symbol BTCUSDT --side BUY --qty 0.001 --stop 65000 --limit 64900 --dry-run

Notes:
- This uses polling (`futures_symbol_ticker`) for simplicity. For production replace with WebSocket
  user data / market streams to get lower latency and fewer missed triggers.
- For SELL side, the stop condition flips (we place limit when price <= stop).
"""
import argparse
import time
import os
from decimal import Decimal
from binance.client import Client
from logger_config import get_logger
from validation import validate_symbol, validate_side, validate_quantity, validate_price

logger = get_logger(__name__)
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


def create_client():
    if not API_KEY or not API_SECRET:
        logger.warning("API key/secret not found in environment; running dry-run only")
        return None
    return Client(API_KEY, API_SECRET)


def stop_limit_watch_and_place(client, symbol, side, qty, stop_price: Decimal, limit_price: Decimal, dry_run=True, poll_interval=2):
    """
    Polls the ticker price and when the stop condition is met, places a limit order.
    Returns the order response or a dry-run dictionary.
    """
    logger.info(f"Starting stop-limit watcher: {symbol} stop={stop_price} limit={limit_price} side={side}")
    if dry_run or client is None:
        logger.info("Dry-run mode: will not place real orders. Simulating trigger check.")
        # Simulate a few polling cycles in dry-run for log clarity
        for i in range(2):
            logger.debug(f"Dry-run poll {i+1}: price=SIMULATED")
            time.sleep(poll_interval)
        return {"status": "DRY_RUN", "symbol": symbol, "side": side, "qty": str(qty), "stop": str(stop_price), "limit": str(limit_price)}

    while True:
        try:
            ticker = client.futures_symbol_ticker(symbol=symbol)
            price = Decimal(ticker.get("price"))
            logger.debug(f"Current price for {symbol}: {price}")
            # For BUY: trigger when price >= stop_price
            # For SELL: trigger when price <= stop_price
            if (side == "BUY" and price >= stop_price) or (side == "SELL" and price <= stop_price):
                logger.info(f"Stop price hit (price={price}) — placing limit order {side} {qty} @ {limit_price}")
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type="LIMIT",
                    timeInForce="GTC",
                    quantity=float(qty),
                    price=str(limit_price),
                )
                logger.info(f"Placed limit order: {order}")
                return order
        except Exception:
            logger.exception("Error in stop-limit watcher")
        time.sleep(poll_interval)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", required=True)
    p.add_argument("--side", required=True)
    p.add_argument("--qty", required=True)
    p.add_argument("--stop", required=True, help="trigger price")
    p.add_argument("--limit", required=True, help="limit order price to place once triggered")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--poll-interval", type=int, default=2, help="polling interval seconds")
    args = p.parse_args()

    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        qty = validate_quantity(args.qty)
        stop = validate_price(args.stop)
        limit = validate_price(args.limit)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise SystemExit(1)

    client = create_client()
    res = stop_limit_watch_and_place(client, symbol, side, qty, stop, limit, dry_run=args.dry_run, poll_interval=args.poll_interval)
    logger.info(f"Result: {res}")
