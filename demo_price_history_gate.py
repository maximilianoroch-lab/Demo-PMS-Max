"""Strict DEMO V5 unit-price history validation. Does NOT download or fabricate prices.

This source is independent from the legacy copied Google Sheet history.
No market change or return is claimed without dated market-price evidence.
"""
from pathlib import Path
import math
import pandas as pd

REQUIRED = {
    "Fecha", "Ticker", "Precio", "Moneda", "Fuente", "Referencia", "Fecha_fuente",
    "Origen_cartera"
}
BANNED_ORIGINS = {"BERSOCH", "PMS_BERSOCH", "LEGACY_COPY", "DEMO_SCALED", "UNKNOWN"}
ALLOWED_CURRENCIES = {"ARS", "USD"}

def validate_price_history(frame, allowed_tickers=None):
    """Return a validated copy. Never imply DEMO simulated prices are market closes."""
    if frame is None or frame.empty:
        raise ValueError("DEMO V5 sin historial de precios verificables")
    missing = REQUIRED.difference(frame.columns)
    if missing:
        raise ValueError("Faltan columnas de procedencia: " + ", ".join(sorted(missing)))
    result = frame.copy()
    provenance_columns = ("Ticker", "Moneda", "Fuente", "Referencia", "Origen_cartera")
    # astype(str) turns pd.NA/None into apparent values like 'nan' or 'None'.
    # Reject them BEFORE and AFTER normalization, never silently certify them.
    if result[list(provenance_columns)].isna().any().any():
        raise ValueError("Cotización DEMO sin ticker o trazabilidad")
    for col in provenance_columns:
        result[col] = result[col].astype(str).str.strip()
    invalid_labels = {"", "nan", "none", "null", "n/a", "undefined"}
    if result[list(provenance_columns)].apply(
        lambda column: column.str.lower().isin(invalid_labels)
    ).any().any():
        raise ValueError("Cotización DEMO sin ticker o trazabilidad")
    if not result["Referencia"].str.startswith("https://").all():
        raise ValueError("Referencia de cotización DEMO debe usar URL HTTPS verificable")
    result["Ticker"] = result["Ticker"].str.upper()
    result["Moneda"] = result["Moneda"].str.upper()
    result["Origen_cartera"] = result["Origen_cartera"].str.upper()
    if (result[["Ticker", "Fuente", "Referencia", "Origen_cartera"]] == "").any().any():
        raise ValueError("Cotización DEMO sin ticker o trazabilidad")
    if result["Origen_cartera"].isin(BANNED_ORIGINS).any():
        raise ValueError("Historia heredada de Bersoch o simulación no certificada")
    if not result["Origen_cartera"].eq("DEMO_V5_MERCADO_INDEPENDIENTE").all():
        raise ValueError("Origen DEMO V5 no reconocido")
    if not result["Moneda"].isin(ALLOWED_CURRENCIES).all():
        raise ValueError("Moneda no admitida")
    for field in ("Fecha", "Fecha_fuente"):
        original = result[field]
        if original.isna().any() or not original.astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
            raise ValueError("Fecha histórica inválida; usar YYYY-MM-DD")
        result[field] = pd.to_datetime(original, format="%Y-%m-%d", errors="coerce")
    if result[["Fecha", "Fecha_fuente"]].isna().any().any():
        raise ValueError("Fecha histórica inválida; usar YYYY-MM-DD")
    if not result["Fecha_fuente"].eq(result["Fecha"]).all():
        raise ValueError("Fecha de la cotización y de su fuente no coinciden")
    if (result["Fecha"] > pd.Timestamp.today().normalize()).any():
        raise ValueError("Fecha histórica futura no es una cotización observada")
    result["Precio"] = pd.to_numeric(result["Precio"], errors="coerce")
    if result["Precio"].isna().any() or not result["Precio"].map(math.isfinite).all() or not result["Precio"].gt(0).all():
        raise ValueError("Precio unitario histórico inválido")
    if result.duplicated(["Fecha", "Ticker", "Moneda"]).any():
        raise ValueError("Cotizaciones históricas duplicadas para ticker/fecha/moneda")
    if allowed_tickers is not None:
        allowed = {str(t).strip().upper() for t in allowed_tickers}
        if not result["Ticker"].isin(allowed).all():
            raise ValueError("Histórico incluye tickers ajenos al inventario DEMO V5")
    return result.sort_values(["Fecha", "Ticker", "Moneda"]).reset_index(drop=True)


def load_verified_price_history(path, allowed_tickers=None):
    path = Path(path)
    if not path.is_file():
        raise ValueError("No existe histórico independiente DEMO V5; variaciones no disponibles")
    return validate_price_history(pd.read_csv(path, dtype=str), allowed_tickers)


def rank_two_verified_dates(frame, date=None):
    """Only compare synchronized unit prices on two actual common dates.

    Require same ticker AND currency on both dates. Does not infer FX,
    skip stale quotes into a common date, or calculate portfolio returns.
    """
    hist = validate_price_history(frame)
    dates = sorted(hist["Fecha"].unique())
    if len(dates) < 2:
        raise ValueError("Se necesitan dos fechas de cotizaciones verificadas")
    chosen = pd.Timestamp(date) if date is not None else dates[-1]
    if chosen not in dates:
        raise ValueError("Fecha de cierre solicitado sin evidencia")
    earlier = [x for x in dates if x < chosen]
    if not earlier:
        raise ValueError("No hay fecha previa verificada")
    prior = earlier[-1]
    current = hist[hist["Fecha"].eq(chosen)].set_index(["Ticker", "Moneda"])
    previous = hist[hist["Fecha"].eq(prior)].set_index(["Ticker", "Moneda"])
    common = current.index.intersection(previous.index)
    if len(common) == 0:
        raise ValueError("No existen instrumentos comparables entre ambas fechas")
    result = pd.DataFrame({
        "Precio": current.loc[common, "Precio"],
        "Precio_previo": previous.loc[common, "Precio"],
    }).reset_index()
    result["Variacion_pct"] = (result["Precio"] / result["Precio_previo"] - 1) * 100
    result["Fecha"] = chosen
    result["Fecha_previa"] = prior
    result["Cobertura_tickers"] = len(common)
    return result.sort_values("Variacion_pct", ascending=False).reset_index(drop=True)
