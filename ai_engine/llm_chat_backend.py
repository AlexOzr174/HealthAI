"""
Текст для чата и подписей к фото: Ollama + шаблоны без локальных языковых моделей.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Generator, List, Optional, Tuple

from core.config import get_ollama_settings
from core.ollama_prompts import (
    SYSTEM_CHAT_NUTRITIONIST,
    SYSTEM_FOOD_LABELS_TRANSLATE_RU,
    SYSTEM_PHOTO_ANALYSIS,
    build_food_labels_translate_user_prompt,
    build_photo_analysis_user_prompt,
)
from ai_engine.ollama_client import ollama_chat, ollama_chat_stream, ollama_has_model


def _ollama_chat_options(cfg: Dict[str, Any]) -> Dict[str, float]:
    return {"temperature": float(cfg.get("chat_temperature") or 0.52)}


def _parse_ollama_json_string_array(raw: str, expect_len: int) -> Optional[List[str]]:
    t = (raw or "").strip()
    if "```" in t:
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE | re.MULTILINE)
        t = re.sub(r"\s*```\s*$", "", t)
    m = re.search(r"\[[\s\S]*\]", t)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list) or len(data) != expect_len:
        return None
    out: List[str] = []
    for x in data:
        if not isinstance(x, str) or not x.strip():
            return None
        out.append(x.strip())
    return out


def _ollama_messages_with_history(
    history: Optional[List[Dict[str, str]]],
    user_message: str,
    profile_context: str,
) -> List[Dict[str, str]]:
    """system + прошлые реплики (без текущего user) + текущее сообщение (с контекстом профиля)."""
    out: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_CHAT_NUTRITIONIST},
    ]
    for m in history or []:
        role = (m.get("role") or "").strip()
        content = (m.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            out.append({"role": role, "content": content})
    user_text = user_message.strip()
    if profile_context and "не заполнены" not in profile_context:
        user_text += f"\n\nКонтекст профиля: {profile_context[:500]}"
    out.append({"role": "user", "content": user_text})
    return out


class LLMChatBackend:
    """Через Ollama при доступности; иначе шаблоны (фото) или None (чат → правила в AIEngine)."""

    def __init__(self) -> None:
        self._error: Optional[str] = None

    def last_error(self) -> Optional[str]:
        return self._error

    def try_ollama_chat(
        self,
        user_message: str,
        profile_context: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[str]:
        cfg = get_ollama_settings()
        if not cfg.get("enabled"):
            return None
        base_url = str(cfg.get("base_url") or "")
        model = str(cfg.get("model") or "")
        timeout = float(cfg.get("timeout") or 120.0)
        if not ollama_has_model(base_url, model, timeout=5.0):
            return None
        messages = _ollama_messages_with_history(
            history, user_message, profile_context
        )
        gen = ollama_chat(
            base_url,
            model,
            messages,
            timeout=timeout,
            options=_ollama_chat_options(cfg),
        )
        return gen if gen else None

    def iter_ollama_chat(
        self,
        user_message: str,
        profile_context: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[Generator[str, None, None]]:
        """Итератор по кускам ответа Ollama или None, если Ollama недоступна."""
        cfg = get_ollama_settings()
        if not cfg.get("enabled"):
            return None
        base_url = str(cfg.get("base_url") or "")
        model = str(cfg.get("model") or "")
        timeout = float(cfg.get("timeout") or 120.0)
        if not ollama_has_model(base_url, model, timeout=5.0):
            return None
        messages = _ollama_messages_with_history(
            history, user_message, profile_context
        )
        return ollama_chat_stream(
            base_url,
            model,
            messages,
            timeout=timeout,
            options=_ollama_chat_options(cfg),
        )

    def generate(self, user_message: str, profile_context: str) -> Optional[str]:
        return self.try_ollama_chat(user_message, profile_context)

    def translate_food_labels_to_ru(
        self, entries: List[Tuple[str, str]]
    ) -> Optional[List[str]]:
        """
        Русские названия для карточек: (англ. метка классификатора, internal food_class).
        None — Ollama выключена/недоступна или ответ не JSON нужной длины.
        """
        if not entries:
            return None
        cfg = get_ollama_settings()
        if not cfg.get("enabled"):
            return None
        base_url = str(cfg.get("base_url") or "")
        model = str(cfg.get("model") or "")
        timeout = float(cfg.get("timeout") or 120.0)
        if not ollama_has_model(base_url, model, timeout=5.0):
            return None
        gen = ollama_chat(
            base_url,
            model,
            [
                {"role": "system", "content": SYSTEM_FOOD_LABELS_TRANSLATE_RU},
                {
                    "role": "user",
                    "content": build_food_labels_translate_user_prompt(entries),
                },
            ],
            timeout=min(60.0, timeout),
            options={"temperature": 0.22},
        )
        if not gen:
            return None
        return _parse_ollama_json_string_array(gen, len(entries))

    def narrate_photo_analysis(
        self,
        results: dict,
        profile_context: str = "",
    ) -> str:
        products = results.get("products") or []
        if results.get("source") == "error" and products:
            return (
                "Не удалось применить модель распознавания к этому снимку.\n\n"
                f"{products[0].get('name', 'Ошибка')}"
            )

        names = [p.get("name", "") for p in products if p.get("confidence", 0) >= 0]
        foods_str = ", ".join(names) if names else "не определено однозначно"
        total = int(results.get("total_calories", 0))
        tm = results.get("total_macros") or {}
        p, f, c = float(tm.get("protein", 0)), float(tm.get("fat", 0)), float(tm.get("carbs", 0))

        cfg = get_ollama_settings()
        if cfg.get("enabled"):
            base_url = str(cfg.get("base_url") or "")
            model = str(cfg.get("model") or "")
            timeout = float(cfg.get("timeout") or 120.0)
            if ollama_has_model(base_url, model, timeout=5.0):
                user_prompt = build_photo_analysis_user_prompt(results, profile_context)
                gen = ollama_chat(
                    base_url,
                    model,
                    [
                        {"role": "system", "content": SYSTEM_PHOTO_ANALYSIS},
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=timeout,
                    options={"temperature": min(0.48, float(cfg.get("chat_temperature") or 0.52))},
                )
                if gen:
                    footer = (
                        "\n\n—\nОценки калорий и классов по фото приблизительные; "
                        "при заболеваниях и строгих диетах ориентируйтесь на врача или диетолога."
                    )
                    return (gen.strip() + footer).strip()

        # Fallback без Ollama: кратко на русском по внутренним именам
        intro = (
            f"Классификатор указал (внутренние метки, могут быть на английском): {foods_str}.\n"
            f"Ориентировочно: ~{total} ккал; белки ≈ {p:.1f} г, жиры ≈ {f:.1f} г, углеводы ≈ {c:.1f} г.\n"
        )
        intro += _goal_hint_ru(profile_context, total) + "\n"
        body = _photo_template_advice(total, p, f, c)
        if profile_context and "не заполнены" not in profile_context:
            body += f"\n\nУчтите данные профиля: {profile_context[:280]}"
        body += (
            "\n\nДля перевода подписей и развёрнутого объяснения на русском запустите Ollama "
            "(см. launch-скрипт проекта)."
        )
        return (intro + "\n" + body).strip()


def _goal_hint_ru(profile_context: str, total_kcal: int) -> str:
    low = (profile_context or "").lower()
    if "lose" in low or "похуд" in low:
        if total_kcal > 700:
            return "При цели снижения веса такая порция может занимать заметную долю дневной нормы — спланируйте остальные приёмы легче."
        return "Следите за суммарным дефицитом калорий за день и достаточным белком."
    if "gain" in low or "набор" in low:
        return "При наборе массы важно добрать белок и калории в остальных приёмах, если эта порция лёгкая."
    return "Сопоставьте порцию с вашей суточной нормой калорий и целями."


def _photo_template_advice(total: int, p: float, f: float, c: float) -> str:
    parts = []
    if total >= 800:
        parts.append(
            "Порция по калориям довольно плотная: имеет смысл сбалансировать остальной день более лёгкими приёмами и добавить овощи."
        )
    elif total > 0:
        parts.append(
            "Калорийность умеренная; следите, чтобы за день набрать достаточно белка и клетчатки из овощей."
        )
    if p >= 25:
        parts.append("Заметная доля белка поддерживает сытость и мышцы — хорошее сочетание для многих целей.")
    if f >= 30:
        parts.append("Жиров много — учитывайте общий дневной баланс, особенно при контроле энергии.")
    if c >= 60:
        parts.append("Углеводов много; при чувствительности к скачкам сахара можно добавить белок или клетчатку к следующему приёму.")
    if not parts:
        parts.append(
            "Постарайтесь сбалансировать день: достаточно белка, овощей и воды между приёмами пищи."
        )
    parts.append(
        "Оценка по фото приблизительная; при заболеваниях и целевых диетах лучше согласовать рацион со специалистом."
    )
    return "\n\n".join(parts)
