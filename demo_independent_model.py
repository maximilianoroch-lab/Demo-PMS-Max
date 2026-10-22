"""Modelo independiente DEMO V5. Usa solo DEMO_INVENTARIO_V5, no feeds heredados."""
from io import StringIO
import pandas as pd
import requests

SHEET_ID="1xzmw5US1z9CGj0eYdGYS2_FfpSzklGyOYODCJ6vvlcY"
CUSTODIANS=["SANTANDER","BBVA","CRITERIA 1234","CRITERIA 5678","ADCAP","IOL","GALICIA","BINANCE"]
ETF=set("SPY ACWI QQQ FXI XLV GLD VEA EEM EWZ".split())
ARG=set("ALUA BBAR BHIP BMA CEPU COME CRES GGAL PAMP SUPV TGSU2 TXAR YPFD".split())
BONDS=set("AO28 AO29 AN29 GD35 GD38 GD41".split())
CRYPTO=set("BTC ETH ADA SOL XRP".split())
US=set("AAPL AMD AMZN AVGO BRKB DISN GLOB GOOGL HD JNJ JPM KO LLY LAC LAR LRCX MCD MELI META MSFT NKE NU NVDA PBR PEP PFE T TSLA V VIST WMT".split())
REGION_AR=ARG|BONDS

def parse_demo_numbers(series):
    """CSV de Google Sheets: soporta coma decimal sin redondear importes."""
    return pd.to_numeric(series.astype(str).str.strip().str.replace(",",".",regex=False),errors="raise")

def build_independent_model(raw=None):
    if raw is None:
        url=f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq"
        r=requests.get(url,params={"sheet":"DEMO_INVENTARIO_V5","tqx":"out:csv"},timeout=20)
        r.raise_for_status()
        raw=pd.read_csv(StringIO(r.text))
    required={"Ticker","Cantidad total","Precio USD indicativo","Valor USD indicativo"}|set(CUSTODIANS)
    if not required.issubset(raw.columns):
        raise ValueError("Faltan columnas del inventario V5")
    raw=raw.copy()
    raw["Ticker"]=raw["Ticker"].astype(str).str.upper().str.strip()
    if len(raw)!=65 or raw["Ticker"].duplicated().any():
        raise ValueError("Inventario V5 incompleto o con tickers duplicados")
    if not set(raw["Ticker"]).issubset(ETF|ARG|BONDS|CRYPTO|US|{"CASH"}):
        raise ValueError("Ticker sin clasificación")
    for col in CUSTODIANS+["Cantidad total","Precio USD indicativo","Valor USD indicativo"]:
        raw[col]=parse_demo_numbers(raw[col])
    if raw[CUSTODIANS].lt(0).any().any() or raw["Precio USD indicativo"].le(0).any():
        raise ValueError("Cantidades o precios DEMO inválidos")
    if not (raw[CUSTODIANS].sum(axis=1)-raw["Cantidad total"]).abs().lt(0.000001).all():
        raise ValueError("Las cuentas no concilian con el total de cada instrumento")
    if not ((raw["Cantidad total"]*raw["Precio USD indicativo"]-raw["Valor USD indicativo"]).abs()<0.02).all():
        raise ValueError("Los valores USD no concilian con los precios indicativos")
    long=raw.melt(id_vars=["Ticker","Precio USD indicativo"],value_vars=CUSTODIANS,var_name="Cuenta",value_name="Cantidad")
    long=long[long["Cantidad"]>0].copy()
    long["Valor USD_num"]=long["Cantidad"]*long["Precio USD indicativo"]
    long["Valor USD"]=long["Valor USD_num"]
    long["Cantidad_num"]=long["Cantidad"]
    def typ(t):
        return "ETF" if t in ETF else "Acción AR" if t in ARG else "Bono" if t in BONDS else "Cripto" if t in CRYPTO else "Cash" if t=="CASH" else "Cedear"
    long["Tipo"]=long["Ticker"].map(typ)
    long["Clase"]=long["Tipo"].map({"ETF":"Renta variable","Acción AR":"Renta variable","Bono":"Renta fija","Cripto":"Crypto","Cash":"Cash","Cedear":"Renta variable"})
    long["Región directa"]=long["Ticker"].map(lambda t:"Argentina" if t in REGION_AR else "Global" if t in ETF or t in CRYPTO or t=="CASH" else "Estados Unidos / Internacional")
    long["Sector"]="Sin desagregar"
    long["Custodio"]=long["Cuenta"]
    total=float(long["Valor USD_num"].sum())
    if total<=0:raise ValueError("Patrimonio ficticio nulo")
    long["Peso_num"]=long["Valor USD_num"]/total
    long["Peso"]=long["Peso_num"]*100
    long["Fuente valor"]="REFERENCIA DEMO NO VALIDADA"
    long["Estado dato"]="SIMULADO"
    non_crypto=float(long.loc[long["Tipo"]!="Cripto","Valor USD_num"].sum())
    crypto=total-non_crypto
    summary={"total":total,"non_crypto":non_crypto,"crypto":crypto,"crypto_pct":crypto/total,
        "argentina_pct":float(long.loc[long["Región directa"]=="Argentina","Valor USD_num"].sum()/total),
        "top5_pct":float(long.groupby("Ticker")["Valor USD_num"].sum().nlargest(5).sum()/total),
        "positions_count":int(long["Ticker"].nunique()),"total_change":None,"non_crypto_change":None,
        "crypto_change":None,"argentina_change":None,"top5_change":None,
        "price_update":"PRECIOS INDICATIVOS","last_market":"Inventario V5 ficticio",
        "summary_source":"INDEPENDENT_V5","reconciled":True,"home_total":total,
        "feed_total":total,"reconciliation_diff":0}
    return {"positions":long,"summary":summary,
        "by_type":long.groupby("Tipo",as_index=False)["Valor USD_num"].sum(),
        "by_region":long.groupby("Región directa",as_index=False)["Valor USD_num"].sum(),
        "by_custodian":long.groupby("Custodio",as_index=False)["Valor USD_num"].sum()}
