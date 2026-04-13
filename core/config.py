"""Конфигурация приложения — загрузка настроек из .env / settings.env."""
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


# Каталог моделей: models/vision (фото), models/ollama — веса Ollama (не в git).
# Текст для чата — через Ollama, отдельный NLP-снимок не используется.
MODELS_DIR = _project_root() / "models"
OLLAMA_MODELS_DIR = MODELS_DIR / "ollama"


def load_env_file(env_path: Path) -> Dict[str, str]:
    """Загружает переменные окружения из файла KEY=VALUE."""
    env_vars: Dict[str, str] = {}
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    env_vars[key.strip()] = value.strip()
    for k, v in os.environ.items():
        if k.startswith(('EDAMAM_', 'USDA_', 'SPOONACULAR_', 'NUTRITIONIX_', 'HEALTHAI_')):
            env_vars[k] = v
    return env_vars


def _get_env_path() -> Path:
    return _project_root() / 'settings.env'


def get_api_keys(env_vars: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Ключи для NutritionAPI (см. core/services/nutrition_api.py)."""
    if env_vars is None:
        env_vars = load_env_file(_get_env_path())

    edamam_key = env_vars.get('EDAMAM_APP_KEY', '')
    return {
        'edamam_app_id': env_vars.get('EDAMAM_APP_ID', ''),
        'edamam_app_key': edamam_key,
        'edamam_key': edamam_key,
        'usda_key': env_vars.get('USDA_API_KEY', ''),
        'spoonacular_key': env_vars.get('SPOONACULAR_API_KEY', ''),
        'nutritionix_app_id': env_vars.get('NUTRITIONIX_APP_ID', ''),
        'nutritionix_key': env_vars.get('NUTRITIONIX_APP_KEY', ''),
        'usda': env_vars.get('USDA_API_KEY', ''),
        'spoonacular': env_vars.get('SPOONACULAR_API_KEY', ''),
    }


def _resolve_food_fallback() -> Optional[str]:
    """PyTorch ResNet50 или Keras .h5 в models/vision."""
    vdir = MODELS_DIR / "vision"
    pth = vdir / "resnet50.pth"
    if pth.is_file() and pth.stat().st_size > 1000:
        return str(pth)
    for name in ("food_model.h5", "food_classifier.h5"):
        h5 = vdir / name
        if h5.is_file() and h5.stat().st_size > 10000:
            return str(h5)
    return None


def get_food_model_path(env_vars: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Путь к весам распознавания еды: HEALTHAI_FOOD_MODEL_PATH или models/vision."""
    if env_vars is None:
        env_vars = load_env_file(_get_env_path())
    food = env_vars.get("HEALTHAI_FOOD_MODEL_PATH", "").strip() or None
    if food:
        fp = Path(food)
        if not fp.exists():
            food = None
    if not food:
        food = _resolve_food_fallback()
    return food


def get_model_paths(env_vars: Optional[Dict[str, str]] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Совместимость: (None, путь_к_vision).
    Текст — только Ollama; первый элемент всегда None.
    """
    return None, get_food_model_path(env_vars)


def describe_model_paths() -> str:
    f = get_food_model_path()
    o = get_ollama_settings()
    lines = [
        f"Модели: {MODELS_DIR}",
        f"  Чат: Ollama ({'вкл' if o.get('enabled') else 'выкл'}) → {o.get('base_url')} / {o.get('model')}",
        f"  Vision (фото): {f or 'не найден (положите resnet50.pth в models/vision)'}",
        f"  Каталог весов Ollama: {OLLAMA_MODELS_DIR} (не в git)",
    ]
    return "\n".join(lines)


def apply_default_ollama_env() -> None:
    """
    Подставляет OLLAMA_MODELS и OLLAMA_HOST для совпадения со скриптами launch/setup
    (веса в проекте, отдельный порт 11435). Не трогает HEALTHAI_* — их задаёт settings.env или логика ниже.
    """
    os.environ.setdefault("OLLAMA_MODELS", str(OLLAMA_MODELS_DIR))
    os.environ.setdefault("OLLAMA_HOST", "127.0.0.1:11435")


def get_ollama_settings(env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Локальная генерация через Ollama. Без ручной настройки: по умолчанию включено,
    хост http://127.0.0.1:11435 и модель qwen2.5:3b (как в setup.sh / launch.sh).
    Отключить явно: HEALTHAI_OLLAMA_ENABLED=0 в settings.env.
    """
    if env_vars is None:
        env_vars = load_env_file(_get_env_path())

    raw_en = (env_vars.get("HEALTHAI_OLLAMA_ENABLED") or "").strip().lower()
    if raw_en in ("0", "false", "no", "off"):
        enabled = False
    else:
        # пусто или не задано — вкл, чтобы пользователю не нужен был settings.env
        enabled = True

    base_url = (env_vars.get("HEALTHAI_OLLAMA_HOST") or "").strip().rstrip("/")
    if not base_url:
        base_url = "http://127.0.0.1:11435"

    model = (env_vars.get("HEALTHAI_OLLAMA_MODEL") or "").strip() or "qwen2.5:3b"

    try:
        timeout_s = float((env_vars.get("HEALTHAI_OLLAMA_TIMEOUT") or "120").strip() or "120")
    except ValueError:
        timeout_s = 120.0

    raw_temp = (env_vars.get("HEALTHAI_OLLAMA_CHAT_TEMPERATURE") or "").strip()
    if raw_temp:
        try:
            chat_temperature = float(raw_temp)
        except ValueError:
            chat_temperature = 0.52
    else:
        # чуть ниже «дефолта» модели — меньше скачков языка и лишнего LaTeX у Qwen
        chat_temperature = 0.52
    chat_temperature = max(0.1, min(1.2, chat_temperature))

    return {
        "enabled": enabled,
        "base_url": base_url,
        "model": model,
        "timeout": max(60.0, timeout_s),
        "models_dir": str(OLLAMA_MODELS_DIR),
        "chat_temperature": chat_temperature,
    }


_settings: Optional[Dict[str, str]] = None


def load_settings() -> Dict[str, str]:
    return load_env_file(_get_env_path())


def get_settings() -> Dict[str, str]:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings
