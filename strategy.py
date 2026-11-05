"""Regla común de partida. Cambiarla es opcional y debe documentarse."""


def score(row, horizon):
    # Cada plazo utiliza una ventana distinta de sesiones conocidas.
    signal = {"1W": "return_5", "1M": "return_20", "3M": "return_60"}[horizon]
    return float(row[signal]) - 0.25 * float(row["volatility_20"])
