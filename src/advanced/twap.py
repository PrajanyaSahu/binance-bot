
import argparse
import time
import os
from decimal import Decimal, ROUND_DOWN, getcontext
from binance.client import Client
from logger_config import get_logger
from validation import validate_symbol, validate_side, validate_twap_params

# Increase decimal precision for slicing calculations
getcontext().prec = 12

logger = get_logger(__name__)
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


def create_client():
    if not API_KEY or not API_SECRET:
        logger.warning("API key/secret not found in environment; running dry-run only")
        return None
    return Client(API_KEY, API_SECRET)


def run_twap(client, symbol: str, side: str, total_qty: Decimal, chunks: int, duration_s: int, dry_run=True):
    """
    Executes TWAP by sending `chunks` market orders spaced evenly across `duration_s`.
    Returns a list of results (responses or dry-run records).
    """
    logger.info(f"Starting TWAP: {symbol} {side} total={total_qty} chunks={chunks} duration={duration_s}s")
    # Calculate per-chunk quantity with safe rounding down to avoid over-ordering
    qty_per = (total_qty / Decimal(chunks)).quantize(Decimal("1e-8"), rounding=ROUND_DOWN)
    remainder = total_qty - (qty_per * Decimal(chunks))
    interval = duration_s / max(1, chunks)

    logger.info(f"Each chunk: {qty_per} (remainder carried until last chunk) every {interval:.2f}s")

    results = []
    for i in range(chunks):
        # Add remainder to the last chunk
        execute_qty = qty_per + (remainder if i == (chunks - 1) else Decimal("0"))
        logger.info(f"TWAP chunk {i+1}/{chunks} qty={execute_qty}")

        if dry_run or client is None:
            logger.info("Dry-run: skipping actual market order")
            results.append({"chunk": i + 1, "status": "DRY_RUN", "qty": str(execute_qty)})
        else:
            try:
                res = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type="MARKET",
                    quantity=float(execute_qty),
                )
                logger.info(f"Chunk response: {res}")
                results.append(res)
            except Exception:
                logger.exception("Failed chunk order")
                results.append({"chunk": i + 1, "status": "ERROR"})

        # Sleep between chunks unless it's the last one
        if i < (chunks - 1):
            time.sleep(interval)

    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", required=True)
    p.add_argument("--side", required=True)
    p.add_argument("--total", required=True, help="total quantity")
    p.add_argument("--chunks", required=True, help="number of slices")
    p.add_argument("--duration", required=True, help="total duration in seconds")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        total, chunks, duration = validate_twap_params(args.total, args.chunks, args.duration)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise SystemExit(1)

    client = create_client()
    res = run_twap(client, symbol, side, total, chunks, duration, dry_run=args.dry_run)
    logger.info(f"TWAP result: {res}")
