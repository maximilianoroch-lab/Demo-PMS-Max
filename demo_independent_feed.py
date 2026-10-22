"""Lectura de la cartera ficticia DEMO en su propia pestaña.

Importes y precios son SIMULADOS; este circuito nunca lee las posiciones de PMS
Bersoch ni usa multiplicadores de patrimonio.
"""
from io import StringIO
import pandas as pd
import requests

DEMO_ID="1xzmw5US1z9CGj0eYdGYS2_FfpSzklGyOYODCJ6vvlcY"
SOURCE_TAB="DEMO_CARTERA_FICTICIA"
ACCOUNT_TAB="DEMO_CUENTAS_FICTICIAS"

def _read_csv(tab):
    url=f"https://docs.google.com/spreadsheets/d/{DEMO_ID}/gviz/tq"
    response=requests.get(url,params={"tqx":"out:csv","sheet":tab},timeout=15)
    response.raise_for_status()
    return pd.read_csv(StringIO(response.text))

def independent_demo_positions():
    df=_read_csv(SOURCE_TAB)
    required={"Cuenta DEMO","Ticker","Cantidad","Precio DEMO (simulado)","Valor DEMO USD","Base de precio","Moneda"}
    if not required.issubset(df.columns):
        raise ValueError("Columnas obligatorias de inventario ficticio ausentes")
    df=df[list(required)].copy()
    for col in ["Cantidad","Precio DEMO (simulado)","Valor DEMO USD"]:
        df[col]=pd.to_numeric(df[col],errors="raise")
    if df.empty or (df[["Cantidad","Precio DEMO (simulado)","Valor DEMO USD"]]<=0).any().any():
        raise ValueError("Inventario ficticio vacío o con valores inválidos")
    if not (df["Moneda"]=="USD").all():
        raise ValueError("Las referencias simuladas deben estar expresadas en USD")
    nominal=df["Base de precio"].str.contains("100 VN",case=False,na=False)
    calc=df["Cantidad"]*df["Precio DEMO (simulado)"]/(1+nominal.astype(float)*99)
    if not ((calc-df["Valor DEMO USD"]).abs()<0.01).all():
        raise ValueError("Error de conciliación en valuación ficticia")
    accounts=_read_csv(ACCOUNT_TAB)
    if not {"Cuenta DEMO","Custodio ficticio"}.issubset(accounts.columns):
        raise ValueError("Falta catálogo de cuentas ficticias")
    if not set(df["Cuenta DEMO"]).issubset(set(accounts["Cuenta DEMO"])):
        raise ValueError("Inventario incluye cuentas fuera del catálogo ficticio")
    return df

def independent_demo_summary():
    df=independent_demo_positions()
    return {"total_usd":float(df["Valor DEMO USD"].sum()),
            "position_count":int(len(df)),
            "account_count":int(df["Cuenta DEMO"].nunique()),
            "valuation_kind":"PRECIOS_SIMULADOS_NO_MERCADO"}
