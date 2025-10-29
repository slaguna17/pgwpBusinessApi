import logging
import sys

logger = logging.getLogger("store_agent")
handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
