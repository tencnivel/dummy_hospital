import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure concise process-level logging for application entry points."""
    logging.basicConfig(level=level.upper())
