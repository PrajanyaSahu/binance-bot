import os
import time
import argparse
from decimal import Decimal
from threading import Thread
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


def place_oco(client, symbol, side, qty, tp_price: Decimal, sl_price: Decimal, dry_run=True):
    logger.info(f"Placing OCO emulation: {symbol} {side} qty={qty} TP={tp_price} SL={sl_price}")
    if dry_run or client is None:
        logger.info("Dry-run mode: not placing real OCO orders")
        return {"status": "DRY_RUN"}

    # Define order directions
    tp_side = side
    sl_side = "SELL" if side == "BUY" else "BUY"

    try:
        # Place take-profit (limit) order
        tp_order = client.futures_create_order(
            symbol=symbol,
            side=tp_side,
            type="LIMIT",
            timeInForce="GTC",
            quantity=float(qty),
            price=str(tp_price),
        )
        # Place stop-market order
        sl_order = client.futures_create_order(
            symbol=symbol,
            side=sl_side,
            type="STOP_MARKET",
            stopPrice=str(sl_price),
            closePosition=False,
            quantity=float(qty),
        )
        logger.info(f"TP order: {tp_order}")
        logger.info(f"SL order: {sl_order}")

        # Background watcher thread: cancels the other when one fills
        def watcher():
            while True:
                try:
                    tp_status = client.futures_get_order(symbol=symbol, orderId=tp_order.get("orderId"))
                    sl_status = client.futures_get_order(symbol=symbol, orderId=sl_order.get("orderId"))
                    logger.debug(f"TP status: {tp_status.get('status')}, SL status: {sl_status.get('status')}")
                    if tp_status.get("status") == "FILLED":
                        client.futures_cancel_order(symbol=symbol, orderId=sl_order.get("orderId"))
                        logger.info("TP filled — cancelled SL")
                        break
                    if sl_status.get("status") == "FILLED":
                        client.futures_cancel_order(symbol=symbol, orderId=tp_order.get("orderId"))
                        logger.info("SL filled — cancelled TP")
                        break
                except Exception:
                    logger.exception("Error while watching OCO orders")
                time.sleep(2)

        Thread(target=watcher, daemon=True).start()
        return {"tp": tp_order, "sl": sl_order}
    except Exception:
        logger.exception("Failed to place OCO orders")
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", required=True)
    p.add_argument("--side", required=True)
    p.add_argument("--qty", required=True)
    p.add_argument("--tp", required=True, help="take profit price")
    p.add_argument("--sl", required=True, help="stop loss trigger price")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        qty = validate_quantity(args.qty)
        tp = validate_price(args.tp)
        sl = validate_price(args.sl)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise SystemExit(1)

    client = create_client()
    res = place_oco(client, symbol, side, qty, tp, sl, dry_run=args.dry_run)
    logger.info(f"Placed OCO result: {res}")
