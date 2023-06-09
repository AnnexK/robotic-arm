from typing import Any
import logging
from logging.config import dictConfig


def logging_config(
    debug: bool = False,
) -> dict[str, Any]:
    loglevel = logging.DEBUG if debug else logging.INFO
    return {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)-6s - %(name): %(message)",
                "datefmt": "%d.%m.%Y %H:%M:%s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": loglevel,
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "handlers": ["console"],
        },
    }


def init_logging(config: dict[str, Any]):
    dictConfig(config)
