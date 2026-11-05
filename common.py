"""Utilidades compartidas por la preparación, publicación y pruebas."""
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HORIZONS = ("1W", "1M", "3M")
FEATURES = ("return_5", "return_20", "return_60", "volatility_20")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, value):
    """La sustitución solo ocurre después de escribir un JSON completo."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


def settings(path=ROOT / "config.toml"):
    import tomllib

    config = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    student = config["student"].strip()
    tickers = [item.strip().upper() for item in config["tickers"]]
    if not student or len(student) > 120:
        raise ValueError("Configura tu nombre en config.toml.")
    if len(tickers) < 3 or len(set(tickers)) != len(tickers):
        raise ValueError("Configura al menos tres acciones distintas.")
    if any(not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", ticker) for ticker in tickers):
        raise ValueError("Un ticker no cumple el formato del contrato.")
    return student, tickers


def validate_payload(payload):
    if not isinstance(payload.get("student"), str) or not payload["student"].strip():
        raise ValueError("Falta el nombre del alumno.")
    generated = datetime.fromisoformat(payload["generated_at"].replace("Z", "+00:00"))
    if generated.tzinfo is None:
        raise ValueError("generated_at debe incluir zona horaria.")
    predictions = payload["predictions"]
    if len(predictions) != 9:
        raise ValueError("Se requieren nueve selecciones.")
    if any(type(item.get("rank")) is not int or item.get("horizon") not in HORIZONS for item in predictions):
        raise ValueError("Puesto u horizonte inválido.")
    for horizon in HORIZONS:
        picks = [item for item in predictions if item["horizon"] == horizon]
        if sorted(item["rank"] for item in picks) != [1, 2, 3] or len({item["ticker"] for item in picks}) != 3:
            raise ValueError("Puestos o tickers repetidos en un horizonte.")
    for item in predictions:
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", item["ticker"]):
            raise ValueError("Ticker inválido.")
    return payload


def finite(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Se ha encontrado un número no finito.")
    return value
