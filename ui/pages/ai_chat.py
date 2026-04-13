# ui/pages/ai_chat.py
from __future__ import annotations

import html
import logging
import random

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.components.press_feedback import attach_press_flash

try:
    from utils.chat_text_sanitize import sanitize_assistant_markdown
except ImportError:
    def sanitize_assistant_markdown(t: str) -> str:
        return t

_log = logging.getLogger(__name__)

# Ссылки на QThread, не успевшие завершиться к моменту закрытия окна (без terminate() на macOS).
_ORPHAN_CHAT_THREADS: list = []

_CHAT_PLACEHOLDERS = (
    "Спросите про завтрак, перекус или норму белка…",
    "Например: как разнообразить салат или сколько воды пить…",
    "Расскажите про цель — похудение, набор или просто здоровье…",
    "Спросите про БЖУ, калории или привычки на неделю…",
    "Можно начать с «что перекусить до тренировки?»…",
)


def _fade_in_widget(w: QWidget) -> None:
    eff = QGraphicsOpacityEffect(w)
    w.setGraphicsEffect(eff)
    anim = QPropertyAnimation(eff, b"opacity", w)
    anim.setDuration(260)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)


try:
    from config.settings import COLORS
except ImportError:
    COLORS = {
        "surface": "#FFFFFF",
        "background": "#F0F2F5",
        "primary": "#3498DB",
        "primary_dark": "#2980B9",
        "text_primary": "#2C3E50",
        "text_secondary": "#7F8C8D",
    }


def _build_ai_engine():
    """Ленивый импорт ai_engine (sklearn и др.) — только при открытии страницы чата."""
    try:
        from ai_engine import AIEngine

        return AIEngine()
    except ImportError as e:
        _log.warning("AI Engine недоступен: %s", e)
        return None


def _profile_dict_from_user(user) -> dict:
    return {
        "name": user.name,
        "weight": user.weight,
        "height": user.height,
        "age": user.age,
        "gender": user.gender,
        "goal": user.goal,
        "activity_level": user.activity_level,
        "diet_type": user.diet_type,
        "target_calories": getattr(user, "target_calories", None),
    }


class MessageBubble(QFrame):
    """Сообщение в чате: пользователь — обычный текст; ответ AI — Markdown (Qt)."""

    def __init__(self, sender: str, text: str, is_user: bool = False):
        super().__init__()
        self.setup_ui(sender, text, is_user)

    def setup_ui(self, sender, text, is_user):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        if is_user:
            safe = html.escape(text).replace("\n", "<br/>")
            bubble = QLabel(f"<b>{html.escape(sender)}:</b><br>{safe}")
            bubble.setWordWrap(True)
            bubble.setTextFormat(Qt.TextFormat.RichText)
            bubble.setMaximumWidth(500)
            bubble.setStyleSheet(
                f"""
                background-color: {COLORS['primary']};
                color: white;
                border-radius: 14px;
                padding: 12px 16px;
                font-size: 13px;
            """
            )
            layout.addStretch()
            layout.addWidget(bubble)
            return

        title = QLabel(f"✨ <b>{html.escape(sender)}</b>")
        title.setTextFormat(Qt.TextFormat.RichText)
        col = QVBoxLayout()
        col.setSpacing(4)
        col.addWidget(title)

        border_soft = COLORS["border"] if "border" in COLORS else "#E0E0E0"
        body = QTextEdit()
        body.setReadOnly(True)
        body.setFrameShape(QFrame.Shape.NoFrame)
        body.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body.setMaximumWidth(560)
        body.document().setDocumentMargin(0)
        body.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {border_soft};
                border-left: 4px solid {COLORS['primary']};
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 13px;
            }}
        """
        )
        body.setMarkdown(sanitize_assistant_markdown(text))
        _shrink_textedit_height(body)
        col.addWidget(body)

        wrap = QWidget()
        wrap.setLayout(col)
        layout.addWidget(wrap)
        layout.addStretch()


def _markdown_textedit_content_width(te: QTextEdit) -> float:
    """Ширина для переноса текста в QTextEdit; до первого layout viewport может быть 0."""
    w = te.viewport().width()
    if w <= 0:
        w = te.width()
    if w <= 0:
        w = 520
    return max(200.0, float(w - 16))


def _shrink_textedit_height(te: QTextEdit) -> None:
    """Подогнать высоту только под содержимое (без лишнего пустого места)."""
    doc = te.document()
    doc.setTextWidth(_markdown_textedit_content_width(te))
    h = int(doc.size().height()) + int(te.contentsMargins().top() + te.contentsMargins().bottom()) + 8
    te.setFixedHeight(max(40, min(h, 400)))


class StreamAIResponseFrame(QFrame):
    """Сообщение AI с наращиванием текста (стриминг); рендер Markdown через QTextEdit.setMarkdown."""

    def __init__(self, parent=None, start_with_thinking: bool = True):
        super().__init__(parent)
        self._md_buffer = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        title = QLabel("✨ <b>Нутрициолог</b>")
        title.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(title)

        self._thinking = QLabel()
        self._thinking.setStyleSheet(
            f"color: {COLORS.get('text_secondary', '#7F8C8D')}; font-size: 12px; font-style: italic; padding: 2px 0 6px 0;"
        )
        self._dot_phase = 0
        self._thinking_timer = QTimer(self)
        self._thinking_timer.timeout.connect(self._tick_thinking)
        layout.addWidget(self._thinking)

        border_soft = COLORS["border"] if "border" in COLORS else "#E0E0E0"
        self._body = QTextEdit()
        self._body.setReadOnly(True)
        self._body.setFrameShape(QFrame.Shape.NoFrame)
        self._body.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._body.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._body.setMinimumHeight(80)
        self._body.setMaximumWidth(560)
        self._body.document().setDocumentMargin(0)
        self._body.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {border_soft};
                border-left: 4px solid {COLORS['primary']};
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 13px;
            }}
        """
        )
        row = QHBoxLayout()
        row.addWidget(self._body)
        row.addStretch()
        layout.addLayout(row)

        if start_with_thinking:
            self._thinking.setVisible(True)
            self._body.setVisible(False)
            self._thinking_timer.start(420)
            self._tick_thinking()
        else:
            self._thinking.setVisible(False)
            self._body.setVisible(True)

    def _tick_thinking(self) -> None:
        dots = "." * (self._dot_phase % 4)
        self._dot_phase += 1
        self._thinking.setText(f"Собираю мысли{dots}")

    def _end_thinking(self) -> None:
        self._thinking_timer.stop()
        self._thinking.setVisible(False)
        self._body.setVisible(True)

    def append_chunk(self, text: str) -> None:
        if self._thinking_timer.isActive() or self._thinking.isVisible():
            self._end_thinking()
        self._md_buffer += text
        self._body.setMarkdown(sanitize_assistant_markdown(self._md_buffer))
        self._body.document().setTextWidth(_markdown_textedit_content_width(self._body))
        doc_h = self._body.document().size().height()
        pad = (
            self._body.contentsMargins().top()
            + self._body.contentsMargins().bottom()
            + 8
        )
        h = int(doc_h) + int(pad)
        self._body.setMinimumHeight(min(max(80, h), 520))
        sb = self._body.verticalScrollBar()
        sb.setValue(sb.maximum())

    def set_error(self, msg: str) -> None:
        self._end_thinking()
        self._md_buffer = ""
        self._body.setPlainText(msg)


class ChatStreamWorker(QThread):
    """Запрос к модели в фоне, чтобы не блокировать Qt."""

    chunk = pyqtSignal(str)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, engine, user_id: int, text: str) -> None:
        super().__init__()
        self._engine = engine
        self._user_id = user_id
        self._text = text

    def run(self) -> None:
        try:
            from database.operations import get_user

            u = get_user(self._user_id)
            if not u:
                self.failed.emit("Пользователь не найден в базе.")
                return
            profile = _profile_dict_from_user(u)
            self._engine.initialize_user(u.id, profile)

            got_any = False
            for part in self._engine.chat_stream(u.id, self._text):
                if self.isInterruptionRequested():
                    break
                if part:
                    got_any = True
                    self.chunk.emit(part)
            if not got_any:
                self.chunk.emit("Пустой ответ. Проверьте Ollama или повторите вопрос.")
            self.finished_ok.emit()
        except Exception as e:
            _log.exception("Ошибка фонового чата")
            self.failed.emit(str(e))


class WelcomeStreamWorker(QThread):
    """Приветствие от модели при открытии чата (стриминг, без записи в историю)."""

    chunk = pyqtSignal(str)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, engine, user_id: int) -> None:
        super().__init__()
        self._engine = engine
        self._user_id = user_id

    def run(self) -> None:
        try:
            from database.operations import get_user

            u = get_user(self._user_id)
            if not u:
                self.failed.emit("Пользователь не найден в базе.")
                return
            profile = _profile_dict_from_user(u)
            self._engine.initialize_user(u.id, profile)

            got_any = False
            for part in self._engine.chat_stream_welcome(u.id):
                if self.isInterruptionRequested():
                    break
                if part:
                    got_any = True
                    self.chunk.emit(part)
            if not got_any:
                self.chunk.emit(
                    "Здравствуйте! Я ИИ-нутрициолог HealthAI. Задайте вопрос о питании."
                )
            self.finished_ok.emit()
        except Exception as e:
            _log.exception("Ошибка приветствия чата")
            self.failed.emit(str(e))


class AIChatPage(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        self.ai_engine = _build_ai_engine()
        self._sync_profile_from_db()

        self._worker: ChatStreamWorker | None = None
        self._welcome_worker: WelcomeStreamWorker | None = None
        self._pending_stream_frame: StreamAIResponseFrame | None = None

        self.setup_ui()
        QTimer.singleShot(120, self._start_welcome_stream)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🥗 Чат с нутрициологом")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        hint = QLabel("Здесь можно спросить про рацион, привычки и цели — ответ приходит по мере генерации.")
        hint.setWordWrap(True)
        hint.setStyleSheet(
            f"color: {COLORS.get('text_secondary', '#7F8C8D')}; font-size: 12px; margin-bottom: 4px;"
        )
        layout.addWidget(hint)

        self.mode_label = QLabel("")
        self.mode_label.setStyleSheet("color: #757575; font-size: 12px;")
        self.mode_label.setWordWrap(True)
        layout.addWidget(self.mode_label)
        self._update_mode_label()

        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("border: none; background-color: transparent;")

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_area.setWidget(self.chat_container)
        layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self._roll_input_placeholder()
        self.input_field.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("В путь ✨")
        self.send_btn.setObjectName("primaryBtn")
        self.send_btn.clicked.connect(self.send_message)
        attach_press_flash(self.send_btn)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    def _roll_input_placeholder(self) -> None:
        self.input_field.setPlaceholderText(random.choice(_CHAT_PLACEHOLDERS))

    def _scroll_chat_to_bottom(self) -> None:
        bar = self.chat_area.verticalScrollBar()
        QTimer.singleShot(30, lambda: bar.setValue(bar.maximum()))

    def _sync_profile_from_db(self) -> None:
        """Актуальные поля пользователя из БД → движок и main_window (для чата и Ollama)."""
        try:
            from database.operations import get_user
        except ImportError:
            return

        uid = 1
        if self.main_window and self.main_window.current_user:
            uid = self.main_window.current_user.id
        u = get_user(uid)
        if not u:
            return
        if self.main_window:
            self.main_window.current_user = u
        if not self.ai_engine:
            return
        self.ai_engine.initialize_user(u.id, _profile_dict_from_user(u))

    def _update_mode_label(self):
        if not self.ai_engine:
            self.mode_label.setText("Режим: заглушка (движок не загружен).")
            return
        try:
            from core.config import get_ollama_settings
            from ai_engine.ollama_client import ollama_has_model

            cfg = get_ollama_settings()
            if cfg.get("enabled"):
                base = str(cfg.get("base_url") or "")
                model = str(cfg.get("model") or "")
                if ollama_has_model(base, model, timeout=3.0):
                    self.mode_label.setText(
                        f"Режим: Ollama — нутрициолог-консультант ({model}, {base}). "
                        "Ответ приходит по частям; интерфейс не блокируется."
                    )
                    return
                self.mode_label.setText(
                    f"Ollama включена, но модель «{model}» недоступна на {base}. "
                    "Запустите launch-скрипт или ollama pull. Ответы — по правилам."
                )
                return
            self.mode_label.setText(
                "Ollama отключена в settings.env — ответы чата из правил NutritionistChatbot."
            )
        except Exception as e:
            self.mode_label.setText(
                f"Не удалось проверить Ollama ({str(e)[:120]}). Используются правила чата."
            )

    def refresh(self):
        """После сохранения профиля или смены пользователя — подтянуть БД, не пересоздавая движок."""
        if self.ai_engine is None:
            self.ai_engine = _build_ai_engine()
        self._sync_profile_from_db()
        self._update_mode_label()

    def shutdown_background_threads(self, timeout_ms: int = 15000) -> None:
        """
        Дождаться завершения фоновых QThread до уничтожения страницы/выхода из приложения.
        Не вызываем QThread.terminate() — на macOS с PyQt это часто даёт segmentation fault.
        Незавершившийся поток удерживаем в _ORPHAN_CHAT_THREADS до завершения процесса.
        """
        for name in ("_worker", "_welcome_worker"):
            w = getattr(self, name, None)
            if w is None:
                continue
            setattr(self, name, None)
            try:
                w.disconnect(self)
            except TypeError:
                pass
            w.blockSignals(True)
            if w.isRunning():
                w.requestInterruption()
                if not w.wait(timeout_ms):
                    _log.warning(
                        "%s: поток чата не завершился за %s мс — удерживаем ссылку, без terminate()",
                        name,
                        timeout_ms,
                    )
                    _ORPHAN_CHAT_THREADS.append(w)
                    continue
            w.deleteLater()

    def _start_welcome_stream(self) -> None:
        stream_frame = StreamAIResponseFrame(start_with_thinking=True)
        self._pending_stream_frame = stream_frame
        self.chat_layout.addWidget(stream_frame)
        _fade_in_widget(stream_frame)
        self._scroll_chat_to_bottom()

        if not self.ai_engine:
            stream_frame.append_chunk(
                "ИИ-движок недоступен. Установите зависимости проекта — ответы будут из простых правил."
            )
            self._pending_stream_frame = None
            self._refocus_input()
            return

        self._sync_profile_from_db()
        user_id = (
            self.main_window.current_user.id
            if self.main_window and self.main_window.current_user
            else 1
        )

        self._set_chat_busy(True)
        w = WelcomeStreamWorker(self.ai_engine, user_id)
        self._welcome_worker = w
        w.chunk.connect(self._on_welcome_chunk)
        w.finished_ok.connect(self._on_welcome_finished)
        w.failed.connect(self._on_welcome_failed)
        w.finished.connect(w.deleteLater)
        w.start()

    def _on_welcome_chunk(self, s: str) -> None:
        if self._pending_stream_frame:
            self._pending_stream_frame.append_chunk(s)
            self._scroll_chat_to_bottom()

    def _on_welcome_finished(self) -> None:
        self._pending_stream_frame = None
        self._welcome_worker = None
        self._set_chat_busy(False)
        self._scroll_chat_to_bottom()
        self._refocus_input()

    def _on_welcome_failed(self, err: str) -> None:
        if self._pending_stream_frame:
            self._pending_stream_frame.append_chunk(
                f"\n\nНе удалось получить приветствие от модели: {err[:280]}"
            )
        self._pending_stream_frame = None
        self._welcome_worker = None
        self._set_chat_busy(False)
        self._scroll_chat_to_bottom()
        self._refocus_input()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if random.random() < 0.55:
            self._roll_input_placeholder()
        if not self._chat_is_busy():
            self._refocus_input()

    def _chat_is_busy(self) -> bool:
        w = self._worker is not None and self._worker.isRunning()
        ww = self._welcome_worker is not None and self._welcome_worker.isRunning()
        return w or ww

    def _refocus_input(self) -> None:
        if not self.input_field.isEnabled():
            return

        def _do() -> None:
            self.input_field.setFocus(Qt.FocusReason.OtherFocusReason)

        QTimer.singleShot(0, _do)

    def add_message(self, sender: str, text: str, is_user: bool = False):
        bubble = MessageBubble(sender, text, is_user)
        self.chat_layout.addWidget(bubble)
        _fade_in_widget(bubble)
        self._scroll_chat_to_bottom()

    def _set_chat_busy(self, busy: bool) -> None:
        self.send_btn.setEnabled(not busy)
        self.input_field.setEnabled(not busy)

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        if self._worker is not None and self._worker.isRunning():
            return
        if self._welcome_worker is not None and self._welcome_worker.isRunning():
            return

        self.add_message("Вы", text, is_user=True)
        self.input_field.clear()

        if not self.ai_engine:
            ai_response = self.get_mock_response(text)
            self.add_message("Нутрициолог", ai_response, is_user=False)
            self._refocus_input()
            return

        self._sync_profile_from_db()

        user_id = (
            self.main_window.current_user.id
            if self.main_window and self.main_window.current_user
            else 1
        )

        stream_frame = StreamAIResponseFrame(start_with_thinking=True)
        self._pending_stream_frame = stream_frame
        self.chat_layout.addWidget(stream_frame)
        _fade_in_widget(stream_frame)
        self._scroll_chat_to_bottom()

        self._set_chat_busy(True)

        worker = ChatStreamWorker(self.ai_engine, user_id, text)
        self._worker = worker

        worker.chunk.connect(self._on_stream_chunk)
        worker.finished_ok.connect(self._on_stream_finished)
        worker.failed.connect(self._on_stream_failed)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _on_stream_chunk(self, s: str) -> None:
        if self._pending_stream_frame:
            self._pending_stream_frame.append_chunk(s)
            self._scroll_chat_to_bottom()

    def _on_stream_finished(self) -> None:
        self._pending_stream_frame = None
        self._worker = None
        self._set_chat_busy(False)
        self._scroll_chat_to_bottom()
        self._refocus_input()

    def _on_stream_failed(self, err: str) -> None:
        if self._pending_stream_frame:
            self._pending_stream_frame.set_error(f"Ошибка: {err}")
        self._pending_stream_frame = None
        self._worker = None
        self._set_chat_busy(False)
        self._scroll_chat_to_bottom()
        self._refocus_input()

    def get_mock_response(self, user_message: str) -> str:
        msg_lower = user_message.lower()
        if "привет" in msg_lower:
            return "Привет! Добро пожаловать в чат 🌿 С чего начнём — завтрак, перекус или цели по весу?"
        elif "калори" in msg_lower:
            return (
                "Чтобы посчитать норму калорий «под вас», пригодятся вес, рост, возраст и уровень активности — "
                "всё это можно указать в профиле, и картина станет гораздо точнее."
            )
        elif "белок" in msg_lower or "протеин" in msg_lower:
            return (
                "Ориентир по белку: примерно **1,2–2,0 г на кг** веса — выше, если много тренируетесь или набираете массу."
            )
        elif "вода" in msg_lower:
            return "Правило большого пальца: около **30 мл на каждый кг** веса в день — плюс чуть больше в жару и после спорта 💧"
        else:
            return (
                "Хороший вопрос! Сейчас я отвечаю по простым шаблонам; с полным движком смогу опереться на ваш профиль "
                "и ответить развернутее."
            )
