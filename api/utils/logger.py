import logging

from Cloud_Stock.settings import BASE_DIR

logger = logging.getLogger("api_logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d.%m.%y %H:%M:%S")

log_file_path = BASE_DIR / f"logs/api_logs.log"
file_handler = logging.handlers.RotatingFileHandler(
    log_file_path,
    mode="a",
    encoding="UTF-8",
    maxBytes=1024 * 1024 * 1024,
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)