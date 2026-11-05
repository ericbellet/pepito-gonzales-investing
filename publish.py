"""Genera el Top 3 desde los datos incluidos, sin descargar ni arrancar Spark."""
import argparse
import csv
import hashlib
from pathlib import Path

from common import ROOT, HORIZONS, FEATURES, finite, save_json, settings, utc_now, validate_payload
from strategy import score


def build(student, tickers, rows, scorer=score):
    by_ticker = {}
    for row in rows:
        ticker = row["ticker"]
        if ticker in by_ticker:
            raise ValueError(f"Más de una fotografía para {ticker}.")
        by_ticker[ticker] = {**row, **{field: finite(row[field]) for field in FEATURES}}
    missing = set(tickers) - set(by_ticker)
    if missing:
        raise ValueError(f"Faltan datos de {', '.join(sorted(missing))}. Incorpóralos antes de publicar.")
    snapshots = {by_ticker[ticker]["snapshot_date"] for ticker in tickers}
    if len(snapshots) != 1:
        raise ValueError("Las acciones deben compartir fecha de corte.")
    candidates = []
    predictions = []
    for horizon in HORIZONS:
        ranking = sorted(
            [{"ticker": ticker, "horizon": horizon, "score": finite(scorer(by_ticker[ticker], horizon))} for ticker in tickers],
            key=lambda item: (-item["score"], item["ticker"]),
        )
        candidates.extend(ranking)
        predictions.extend({"ticker": item["ticker"], "horizon": horizon, "rank": rank}
                           for rank, item in enumerate(ranking[:3], 1))
    payload = validate_payload({"student": student, "generated_at": utc_now(), "predictions": predictions})
    return payload, {"snapshot_date": next(iter(snapshots)), "universe": tickers, "candidates": candidates}


def publish(config=ROOT / "config.toml", features=ROOT / "lake/curated/features.csv", output=ROOT):
    student, tickers = settings(config)
    with Path(features).open(encoding="utf-8", newline="") as stream:
        payload, report = build(student, tickers, list(csv.DictReader(stream)))
    # Validar todo antes de sustituir la última salida correcta.
    report.update({"generated_at": payload["generated_at"],
                   "strategy_sha256": hashlib.sha256((ROOT / "strategy.py").read_bytes()).hexdigest(),
                   "features_sha256": hashlib.sha256(Path(features).read_bytes()).hexdigest()})
    save_json(Path(output) / "reports/selection.json", report)
    save_json(Path(output) / "artifacts/predictions.json", payload)
    print(f"Publicadas {len(payload['predictions'])} selecciones para {student}; {len(tickers)} acciones candidatas.")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.toml")
    parser.add_argument("--features", type=Path, default=ROOT / "lake/curated/features.csv")
    args = parser.parse_args()
    publish(args.config, args.features)
