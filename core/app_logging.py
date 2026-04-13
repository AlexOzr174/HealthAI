"""Настройка логирования для продакшена (консоль, уровни по HEALTHAI_DEBUG)."""
from __future__ import annotations

import logging
import os

_configured = False


def setup_logging() -> None:
    """Вызывать один раз при старте приложения (из main.py до тяжёлых импортов UI)."""
    global _configured
    if _configured:
        return

    debug = os.environ.get("HEALTHAI_DEBUG", "").strip().lower() in ("1", "true", "yes", "on")
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    _configured = True
