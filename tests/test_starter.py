import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app
from common import ROOT, HORIZONS, validate_payload
from prepare import read_raw
from publish import build, publish


def features(tickers):
    return [{"ticker": ticker, "snapshot_date": "2026-10-22", "observations": 100,
             "return_5": 0.1, "return_20": 0.2, "return_60": 0.3, "volatility_20": 0.02}
            for ticker in tickers]


def test_universe_is_configurable_and_ties_are_reproducible():
    tickers = ["ORCL", "KO", "ADBE", "TM"]
    payload, report = build("Laura García", tickers, features(tickers))
    assert len(report["candidates"]) == 12
    assert validate_payload(payload) == payload
    for horizon in HORIZONS:
        assert [p["ticker"] for p in payload["predictions"] if p["horizon"] == horizon] == ["ADBE", "KO", "ORCL"]


def test_a_missing_company_or_invalid_score_stops_publication():
    with pytest.raises(ValueError, match="Faltan datos"):
        build("Laura", ["ORCL", "KO", "ADBE"], features(["ORCL", "KO"]))
    with pytest.raises(ValueError, match="no finito"):
        build("Laura", ["ORCL", "KO", "ADBE"], features(["ORCL", "KO", "ADBE"]), scorer=lambda row, horizon: float("nan"))


def test_invalid_inputs_keep_last_published_artifact(tmp_path):
    artifact = tmp_path / "artifacts/predictions.json"
    artifact.parent.mkdir()
    artifact.write_text('{"previous": true}')
    config = tmp_path / "config.toml"
    config.write_text('student = "Laura"\ntickers = ["ORCL", "KO", "ADBE"]\n')
    with pytest.raises(ValueError, match="Faltan datos"):
        publish(config, ROOT / "lake/curated/features.csv", tmp_path)
    assert artifact.read_text() == '{"previous": true}'


def test_api_reads_the_same_saved_result_and_reports_missing_artifact(tmp_path, monkeypatch):
    payload, _ = build("Laura García", ["ORCL", "KO", "ADBE"], features(["ORCL", "KO", "ADBE"]))
    artifact = tmp_path / "predictions.json"
    artifact.write_text(json.dumps(payload))
    monkeypatch.setattr(app, "PREDICTIONS_FILE", artifact)
    with TestClient(app.app) as client:
        assert client.get("/api/predictions").json() == payload
        assert client.get("/api/predictions").json()["generated_at"] == payload["generated_at"]
        artifact.unlink()
        assert client.get("/api/predictions").status_code == 503
        assert client.get("/api/health").status_code == 503


def test_raw_checksum_detects_changes(tmp_path):
    raw = tmp_path / "ORCL.json"
    raw.write_bytes(b"original")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"files": [{"file": raw.name, "ticker": "ORCL", "sha256": hashlib.sha256(raw.read_bytes()).hexdigest()}]}))
    raw.write_bytes(b"modified")
    with pytest.raises(ValueError, match="raw ha cambiado"):
        read_raw(manifest)


def test_bundled_snapshot_and_api_are_ready_without_download():
    manifests = sorted((ROOT / "lake/raw/yahoo").glob("*/manifest.json"))
    rows, nulls = read_raw(manifests[-1])
    assert len(rows) > 600
    assert nulls >= 0
    payload = validate_payload(json.loads((ROOT / "artifacts/predictions.json").read_text()))
    assert len(payload["predictions"]) == 9
