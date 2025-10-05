"""
Grid Trading Strategy (simplified).

Creates a grid of buy and sell limit orders between a low and high price.
This example just demonstrates order placement, not dynamic rebalancing.

Usage (dry-run):
  python src/advanced/grid_strategy.py --symbol BTCUSDT --low 60000 --high 70000 --steps 10 --qty 0.0005 --dry-run

Notes:
- In practice, you'd want smarter logic (like cancel/replace, balance allocation).
- Here we only place BUY orders at grid prices (for simplicity).
"""
import argparse
import os
from decimal import Decimal
from binance.client import Client
from logger_config import get_logger
from validation import validate_symbol, validate_quantity, validate_price

logger = get_logger(__name__)
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


def create_client():
    if not API_KEY or not API_SECRET:
        logger.warning("API key/secret not found in environment; running dry-run only")
        return None
    return Client(API_KEY, API_SECRET)


def create_grid(client, symbol: str, low: Decimal, high: Decimal, steps: int, qty_per_order: Decimal, dry_run=True):
    """
    Splits the price range [low, high] into `steps` intervals
    and places one BUY limit order at each grid price.
    """
    logger.info(f"Creating grid: {symbol} from {low} to {high} with {steps} steps, qty={qty_per_order}")
    if low >= high:
        raise ValueError("low must be < high")

    step_size = (high - low) / Decimal(steps)
    orders = []

    for i in range(steps + 1):
        price = (low + step_size * i).quantize(Decimal("1.00"))  # adjust precision as needed
        if dry_run or client is None:
            logger.info(f"Dry-run grid order {i}: BUY {qty_per_order} @ {price}")
            orders.append({"price": str(price), "qty": str(qty_per_order), "status": "DRY_RUN"})
        else:
            try:
                res = client.futures_create_order(
                    symbol=symbol,
                    side="BUY",
                    type="LIMIT",
                    timeInForce="GTC",
                    quantity=float(qty_per_order),
                    price=str(price),
                )
                orders.append(res)
            except Exception:
                logger.exception(f"Failed to place grid order at {price}")

    return orders


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", required=True)
    p.add_argument("--low", required=True, help="lower bound of grid")
    p.add_argument("--high", required=True, help="upper bound of grid")
    p.add_argument("--steps", required=True, help="number of grid steps")
    p.add_argument("--qty", required=True, help="quantity per order")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    try:
        symbol = validate_symbol(args.symbol)
        low = validate_price(args.low)
        high = validate_price(args.high)
        steps = int(args.steps)
        qty = validate_quantity(args.qty)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise SystemExit(1)

    client = create_client()
    res = create_grid(client, symbol, low, high, steps, qty, dry_run=args.dry_run)
    logger.info(f"Grid result: {res}")
