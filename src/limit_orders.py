
import os
import argparse
from decimal import Decimal
from binance.client import Client
from binance.enums import FUTURE_ORDER_TYPE_LIMIT
from logger_config import get_logger
from validation import validate_symbol, validate_side, validate_quantity, validate_price

logger = get_logger(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


def create_client():
    """Return a Binance client or None if API keys are missing (implies dry-run only)."""
    if not API_KEY or not API_SECRET:
        logger.warning("API key/secret not found in environment; running dry-run only")
        return None
    return Client(API_KEY, API_SECRET)


def place_limit_order(client, symbol: str, side: str, qty: Decimal, price: Decimal, time_in_force: str = "GTC", dry_run: bool = True):
    """
    Place a limit order. If dry_run or client is None, simulate the action.
    """
    logger.info(f"Placing limit order: {symbol} {side} {qty} @ {price} TIF={time_in_force}")
    if dry_run or client is None:
        logger.info("Dry-run mode: not sending limit order to Binance")
        return {"status": "DRY_RUN", "symbol": symbol, "side": side, "qty": str(qty), "price": str(price)}

    try:
        response = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=FUTURE_ORDER_TYPE_LIMIT,
            timeInForce=time_in_force,
            quantity=float(qty),
            price=str(price),
        )
        logger.info(f"Order response: {response}")
        return response
    except Exception:
        logger.exception("Failed to place limit order")
        raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", required=True)
    p.add_argument("--side", required=True)
    p.add_argument("--qty", required=True)
    p.add_argument("--price", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    # Validate inputs
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        qty = validate_quantity(args.qty)
        price = validate_price(args.price)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return

    client = create_client()
    res = place_limit_order(client, symbol, side, qty, price, dry_run=args.dry_run)
    logger.info(f"Result: {res}")


if __name__ == "__main__":
    main()
