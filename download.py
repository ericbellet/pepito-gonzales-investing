"""Actualización opcional de precios. El arranque normal usa el snapshot incluido."""
import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from common import ROOT, save_json, settings, utc_now


def download(start, end, output=ROOT / "lake/raw/yahoo"):
    _, tickers = settings()
    run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = output / run
    destination.mkdir(parents=True, exist_ok=False)
    manifests = []
    for ticker in tickers:
        parameters = {"interval": "1d", "period1": int(datetime.combine(start, time(), timezone.utc).timestamp()),
                      "period2": int(datetime.combine(end + timedelta(days=1), time(), timezone.utc).timestamp())}
        url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(ticker, safe="") + "?" + urllib.parse.urlencode(parameters)
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 LaSalleCourse"})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
        parsed = json.loads(body)
        if parsed["chart"].get("error") or not parsed["chart"].get("result"):
            raise ValueError(f"Respuesta sin precios para {ticker}.")
        path = destination / f"{ticker}.json"
        path.write_bytes(body)  # Respuesta literal, antes de transformar.
        manifests.append({"ticker": ticker, "file": path.name, "url": url, "provider": "Yahoo Finance chart",
                          "downloaded_at": utc_now(), "sha256": hashlib.sha256(body).hexdigest(),
                          "requested_start": start.isoformat(), "requested_end": end.isoformat()})
    manifest = destination / "manifest.json"
    save_json(manifest, {"source": "Yahoo Finance chart", "files": manifests,
                         "note": "Snapshot de cierres diarios; acceso web no oficial, sujeto a disponibilidad del proveedor."})
    print(f"Raw conservado en {destination}")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    args = parser.parse_args()
    if args.start >= args.end:
        parser.error("start debe ser anterior a end")
    download(args.start, args.end)
