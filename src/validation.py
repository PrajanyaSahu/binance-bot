from decimal import Decimal, InvalidOperation
from typing import Tuple

# Optional: can be extended to fetch symbols from Binance exchange info
SUPPORTED_SYMBOLS = None  

def validate_symbol(symbol: str) -> str:
    """
    Ensures symbol looks valid (non-empty, at least 6 chars).
    Example: BTCUSDT, ETHUSDT
    """
    if not isinstance(symbol, str) or len(symbol) < 6:
        raise ValueError(f"Invalid symbol: {symbol}")
    return symbol.upper()

def validate_side(side: str) -> str:
    """
    Validates order side: BUY or SELL.
    """
    s = side.upper()
    if s not in ("BUY", "SELL"):
        raise ValueError("Side must be BUY or SELL")
    return s

def validate_quantity(qty: str) -> Decimal:
    """
    Validates that quantity is a positive decimal number.
    """
    try:
        d = Decimal(qty)
    except InvalidOperation:
        raise ValueError("Quantity must be a decimal number")
    if d <= 0:
        raise ValueError("Quantity must be > 0")
    return d

def validate_price(price: str) -> Decimal:
    """
    Validates that price is a positive decimal number.
    """
    try:
        d = Decimal(price)
    except InvalidOperation:
        raise ValueError("Price must be a decimal number")
    if d <= 0:
        raise ValueError("Price must be > 0")
    return d

def validate_twap_params(total_qty: str, chunks: str, duration_s: str) -> Tuple[Decimal, int, int]:
    """
    Special validation for TWAP strategy.
    Ensures total quantity, number of chunks, and duration (seconds) are valid.
    """
    total = validate_quantity(total_qty)
    try:
        chunks_i = int(chunks)
        duration_i = int(duration_s)
    except Exception:
        raise ValueError("chunks and duration must be integers")
    if chunks_i <= 0:
        raise ValueError("chunks must be > 0")
    if duration_i < 0:
        raise ValueError("duration must be >= 0")
    return total, chunks_i, duration_i
