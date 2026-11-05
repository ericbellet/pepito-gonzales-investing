"""API que lee el artefacto publicado; no descarga ni vuelve a calcular."""
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from common import ROOT, validate_payload

app = FastAPI(title="LaSalle Investing · API del alumno")
PREDICTIONS_FILE = Path(os.environ.get("PREDICTIONS_FILE", ROOT / "artifacts/predictions.json"))


def read_predictions():
    try:
        return validate_payload(json.loads(PREDICTIONS_FILE.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError, KeyError) as error:
        raise HTTPException(status_code=503, detail="No hay un resultado válido. Revisa la ejecución de publish.py.") from error


@app.get("/api/predictions")
def predictions():
    return read_predictions()


@app.get("/api/health")
def health():
    payload = read_predictions()
    return {"status": "ok", "student": payload["student"], "generated_at": payload["generated_at"]}
