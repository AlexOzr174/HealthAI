"""Общая настройка выхода из PyQt6 (macOS: меньше SIGSEGV при teardown CPython/SIP/нативных либ).

Вызывайте pyqt6_disable_sip_destroy_on_exit() до создания QApplication.

Если в отладчике виден залипание в dyld / AppleSystemPolicy::checkLibraryLoad при импорте PyQt6,
это проверка ОС при dlopen .so (часто дольше на томах /Volumes/* и при атрибуте карантина на wheel).
Перенос проекта на локальный диск или снятие quarantine с site-packages обычно ускоряет старт.
"""
from __future__ import annotations

import gc
import logging
import os
import sys
from typing import Any


def pyqt6_disable_sip_destroy_on_exit() -> None:
    """SIP не вызывает C++-деструкторы всех обёрток в случайном порядке при завершении интерпретатора."""
    try:
        import PyQt6.sip as sip

        if hasattr(sip, "setdestroyonexit"):
            sip.setdestroyonexit(False)
    except Exception:
        pass


def flush_log_handlers() -> None:
    """Сброс буферов до os._exit (atexit не вызывается)."""
    for h in list(logging.root.handlers):
        try:
            h.flush()
        except Exception:
            pass


def qt_safe_teardown() -> None:
    """Вызывать из aboutToQuit — без обращения к виджетам."""
    try:
        import matplotlib.pyplot as plt

        plt.close("all")
    except Exception:
        pass
    try:
        gc.collect()
    except Exception:
        pass


def exit_after_qt_exec(rc: Any) -> None:
    flush_log_handlers()
    code = int(rc) if isinstance(rc, int) else 0
    if os.environ.get("HEALTHAI_NORMAL_PYTHON_EXIT") == "1":
        sys.exit(code)
    os._exit(code)
