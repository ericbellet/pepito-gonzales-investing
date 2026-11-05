"""Prepara el snapshot incluido con Python. RA1 reproduce el ETL con PySpark."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import pstdev

from common import ROOT, finite, save_json, utc_now


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def read_raw(manifest):
    doc = json.loads(Path(manifest).read_text(encoding="utf-8"))
    rows = []
    nulls = 0
    for entry in doc["files"]:
        path = Path(manifest).parent / entry["file"]
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != entry["sha256"]:
            raise ValueError(f"El raw ha cambiado: {path}")
        result = json.loads(body)["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        dates = result["timestamp"]
        if len(dates) != len(closes):
            raise ValueError("Las fechas no corresponden a los cierres.")
        for timestamp, close in zip(dates, closes):
            if close is None:
                nulls += 1
                continue
            close = finite(close)
            if close <= 0:
                raise ValueError("Precio no positivo.")
            rows.append({"ticker": entry["ticker"], "date": datetime.fromtimestamp(timestamp, timezone.utc).date().isoformat(), "close": close})
    if not rows:
        raise ValueError("No hay precios válidos.")
    return rows, nulls


def prepare(manifest, output=ROOT):
    rows, nulls = read_raw(manifest)
    grouped = defaultdict(list)
    keys = set()
    for row in rows:
        key = (row["ticker"], row["date"])
        if key in keys:
            raise ValueError("Clave de precio duplicada.")
        keys.add(key)
        grouped[row["ticker"]].append(row)
    features = []
    for ticker, history in sorted(grouped.items()):
        history.sort(key=lambda row: row["date"])
        if len(history) < 61:
            raise ValueError(f"{ticker} requiere al menos 61 sesiones válidas.")
        prices = [row["close"] for row in history]
        returns = [prices[i] / prices[i-1] - 1 for i in range(len(prices)-20, len(prices))]
        features.append({"ticker": ticker, "snapshot_date": history[-1]["date"], "observations": len(prices),
                         **{f"return_{n}": prices[-1] / prices[-n-1] - 1 for n in (5, 20, 60)},
                         "volatility_20": pstdev(returns)})
    write_csv(Path(output) / "lake/clean/prices.csv", sorted(rows, key=lambda row: (row["ticker"], row["date"])))
    write_csv(Path(output) / "lake/curated/features.csv", features)
    save_json(Path(output) / "reports/quality.json", {"engine": "python-reference", "generated_at": utc_now(),
              "read": len(rows) + nulls, "rejected_null_close": nulls, "clean": len(rows), "companies": len(grouped),
              "source_manifest": str(Path(manifest).relative_to(ROOT)) if Path(manifest).is_relative_to(ROOT) else str(manifest),
              "snapshot_date": max(row["snapshot_date"] for row in features)})
    print(f"Preparados {len(rows)} precios y {len(features)} empresas.")
    return features


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    manifests = sorted((ROOT / "lake/raw/yahoo").glob("*/manifest.json"))
    manifest = args.manifest or (manifests[-1] if manifests else None)
    if manifest is None:
        parser.error("Falta un manifiesto raw.")
    prepare(manifest)
