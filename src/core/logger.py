import sys
from loguru import logger
from src.core.config import settings

def setup_logger():
    """Configures the Loguru logger for the application."""
    logger.remove()  # Remove default handler
    
    # Console Handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True
    )
    
    # File Handler (Rotated daily, kept for 7 days)
    logger.add(
        "logs/bot.log",
        rotation="00:00",
        retention="7 days",
        level="INFO",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )

    logger.info(f"Logger initialized. App: {settings.APP_NAME} v{settings.VERSION}")
    if settings.DRY_RUN:
        logger.warning("⚠️ DRY_RUN MODE ENABLED: No tweets will be posted!")

setup_logger()
