from pathlib import Path
import sys

from loguru import logger

Path("logs").mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    colorize=True,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level}</level> | "
           "{message}",
)

logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="30 days",
    enqueue=True,
    level="DEBUG",
)

__all__ = ["logger"]