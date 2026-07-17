import logging
import sys


def setup_logging(debug: bool = True) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # These libraries are extremely chatty at DEBUG level (every HTTP call,
    # every SSL handshake) and drown out the app's own logs without adding
    # much value day-to-day. Keep them at INFO/WARNING regardless of the
    # app's debug setting.
    for noisy_logger in ("httpx", "httpcore", "urllib3", "sentence_transformers"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
