from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

import structlog

from app.config import get_settings

_configured = False


def configure_logging() -> None:
    global _configured
    if _configured:
        return
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]
    renderer = (
        structlog.processors.JSONRenderer()
        if settings.is_prod
        else structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.format_exc_info,
            renderer,
        ],
    )

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if settings.log_dir:
        try:
            Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
            handlers.append(
                logging.handlers.RotatingFileHandler(
                    Path(settings.log_dir) / "app.log",
                    maxBytes=10 * 1024 * 1024,
                    backupCount=10,
                    encoding="utf-8",
                )
            )
        except OSError:
            pass  # read-only filesystem (serverless): stdout only
    for h in handlers:
        h.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = handlers
    root.setLevel(level)
    for name in ("uvicorn", "uvicorn.error"):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True
    access = logging.getLogger("uvicorn.access")
    access.handlers = []
    access.propagate = False
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    structlog.configure(
        processors=[
            *shared,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    _configured = True


def get_logger(name: str = "app"):
    return structlog.get_logger(name)
