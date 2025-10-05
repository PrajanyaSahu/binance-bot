import logging
import sys
from logging.handlers import RotatingFileHandler

# Default log filename (can be overridden if you want)
LOG_FILE = "bot.log"

def get_logger(name: str = "binance_bot") -> logging.Logger:
    """
    Returns a configured logger. Uses a RotatingFileHandler (5MB per file,
    3 backups) and a console StreamHandler. Levels:
      - File: DEBUG (detailed logs, stack traces)
      - Console: INFO (user-facing)
    """
    logger = logging.getLogger(name)
    # If logger already configured (e.g., imported multiple times), reuse it.
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Rotating file handler for persistent structured logs
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Stream handler for console output (info-level)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(sh)

    return logger
