"""
Нормализация текста ответа чата для отображения в Qt Markdown:
LaTeX в QTextEdit не рендерится — переводим в обычную запись; убираем случайные CJK-вставки.
"""
from __future__ import annotations

import re

# Китайский, японский, корейский (частые «просачивания» у мультиязычных LLM)
_CJK_RE = re.compile(
    "["
    "\u3040-\u30ff"  # hiragana, katakana
    "\u3400-\u9fff"  # CJK unified
    "\uf900-\ufaff"  # compatibility
    "\uac00-\ud7af"  # hangul syllables
    "\uff66-\uff9f"  # halfwidth katakana
    "]"
)


def _replace_cases(m: re.Match[str]) -> str:
    inner = (m.group(1) or "").strip()
    inner = inner.replace("\\times", "×").replace("\\cdot", "·")
    inner = re.sub(r"\\leq", "≤", inner)
    inner = re.sub(r"\\geq", "≥", inner)
    inner = re.sub(r"\\neq", "≠", inner)
    chunks = [c.strip() for c in re.split(r"\\\\", inner) if c.strip()]
    lines: list[str] = []
    for c in chunks:
        if "&" in c:
            left, right = c.split("&", 1)
            cond = right.strip().lstrip(":").strip()
            val = left.strip()
            if cond and val:
                lines.append(f"- если {cond}: **{val}**")
            elif cond:
                lines.append(f"- {cond}")
            else:
                lines.append(f"- {val}")
        else:
            lines.append(f"- {c}")
    return "\n" + "\n".join(lines) if lines else ""


def _replace_frac_all(s: str) -> str:
    while True:
        m = re.search(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", s)
        if not m:
            break
        s = s[: m.start()] + f"({m.group(1)})/({m.group(2)})" + s[m.end() :]
    return s


def _replace_sqrt(s: str) -> str:
    return re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", s)


def _subscripts_readable(s: str) -> str:
    def _sub(m: re.Match[str]) -> str:
        inner = m.group(1).strip()
        low = inner.lower()
        if low in ("cm", "см"):
            return " (см)"
        if low in ("kg", "кг"):
            return " (кг)"
        if low == "kcal" or low == "ккал":
            return " (ккал)"
        return f"_{inner}"

    return re.sub(r"_\{([^{}]+)\}", _sub, s)


_digit_sup = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _superscripts_simple(s: str) -> str:
    s = re.sub(r"\^\{2\}", "²", s)
    s = re.sub(r"\^\{3\}", "³", s)
    s = re.sub(r"\^(\d)", lambda m: m.group(1).translate(_digit_sup), s)
    return s


def _strip_text_commands(s: str) -> str:
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\\text\{([^{}]*)\}", r"\1", s)
    return s


def _latex_symbols(s: str) -> str:
    pairs = [
        (r"\\times", "×"),
        (r"\\cdot", "·"),
        (r"\\div", "÷"),
        (r"\\pm", "±"),
        (r"\\mp", "∓"),
        (r"\\leq", "≤"),
        (r"\\geq", "≥"),
        (r"\\neq", "≠"),
        (r"\\approx", "≈"),
        (r"\\sim", "~"),
        (r"\\infty", "∞"),
        (r"\\rightarrow", "→"),
        (r"\\leftarrow", "←"),
        (r"\\Rightarrow", "⇒"),
        (r"\\to", "→"),
        (r"\\%", "%"),
        (r"\\,", " "),
        (r"\\;", " "),
        (r"\\quad", "  "),
        (r"\\ ", " "),
    ]
    for pat, rep in pairs:
        s = re.sub(pat, rep, s)
    return s


def _remove_empty_bold(s: str) -> str:
    s = re.sub(r"\*\*\s*\*\*", "", s)
    s = re.sub(r"__\s*__", "", s)
    return s


def sanitize_assistant_markdown(text: str) -> str:
    if not text:
        return text
    s = text

    s = re.sub(
        r"\\begin\{cases\}(.*?)\\end\{cases\}",
        _replace_cases,
        s,
        flags=re.DOTALL,
    )

    s = _replace_frac_all(s)
    s = _replace_sqrt(s)
    s = _subscripts_readable(s)
    s = _superscripts_simple(s)
    s = _strip_text_commands(s)
    s = _latex_symbols(s)

    # остатки «математических» окружений — грубо выкинуть оболочку
    s = re.sub(r"\\begin\{[a-zA-Z*]+\}", "", s)
    s = re.sub(r"\\end\{[a-zA-Z*]+\}", "", s)

    s = _CJK_RE.sub("", s)
    s = _remove_empty_bold(s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s
