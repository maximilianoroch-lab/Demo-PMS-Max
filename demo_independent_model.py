"""Adaptador de feeds exclusivamente ficticios, independiente del PMS real.

Aún no sustituye todas las páginas del escritorio. Permite probar el origen
ficticio y conciliaciones sin reutilizar snapshots/históricos reales.
"""
import pandas as pd
from demo_independent_feed import independent_demo_positions

ASSET_TYPES={
 "AAPL":("Cedear","Renta variable","Estados Unidos","Tecnología"),
 "MSFT":("Cedear","Renta variable","Estados Unidos","Tecnología"),
 "SPY":("ETF","Renta variable","Global","ETF diversificado"),
 "GLD":("ETF","Oro","Global","Oro"),
 "GGAL":("Acción AR","Renta variable","Argentina","Financiero"),
 "YPF":("Acción AR","Renta variable","Argentina","Energía"),
 "MELI":("Cedear","Renta variable","Latinoamérica","Consumo"),
 "GD35":("Bono","Renta fija","Argentina","Soberano"),
 "CASH":("Cash","Cash","Global","Efectivo"),
}

def build_independent_model(raw=None):
    positions=independent_demo_positions() if raw is None else raw.copy()
    ticker=set(positions["Ticker"].astype(str))
    if not ticker.issubset(ASSET_TYPES):
        raise ValueError("Activo ficticio sin clasificación explícita")
    df=positions.rename(columns={"Cuenta DEMO":"Cuenta","Valor DEMO USD":"Valor USD","Cantidad":"Cantidad"}).copy()
    df["Tipo"]=df["Ticker"].map(lambda t:ASSET_TYPES[t][0])
    df["Clase"]=df["Ticker"].map(lambda t:ASSET_TYPES[t][1])
    df["Región directa"]=df["Ticker"].map(lambda t:ASSET_TYPES[t][2])
    df["Sector"]=df["Ticker"].map(lambda t:ASSET_TYPES[t][3])
    df["Custodio"]=df["Cuenta"].map({"DEMO-BROKER-01":"Broker Atlas","DEMO-BROKER-02":"Broker Delta","DEMO-BANK-01":"Banco Horizonte"})
    df["Valor USD_num"]=pd.to_numeric(df["Valor USD"],errors="raise")
    df["Cantidad_num"]=pd.to_numeric(df["Cantidad"],errors="raise")
    total=float(df["Valor USD_num"].sum())
    if total<=0 or df["Custodio"].isna().any():
        raise ValueError("Inventario ficticio no conciliado")
    df["Peso_num"]=df["Valor USD_num"]/total
    df["Peso"]=df["Peso_num"]*100
    df["Fuente valor"]="SIMULADO_NO_MERCADO"
    df["Estado dato"]="SIMULADO"
    summary={
        "total":total,"non_crypto":total,"crypto":0.0,"crypto_pct":0.0,
        "argentina_pct":float(df.loc[df["Región directa"]=="Argentina","Valor USD_num"].sum()/total),
        "top5_pct":float(df.groupby("Ticker")["Valor USD_num"].sum().nlargest(5).sum()/total),
        "positions_count":int(df["Ticker"].nunique()),"total_change":None,
        "non_crypto_change":None,"crypto_change":None,"argentina_change":None,"top5_change":None,
        "price_update":"PRECIOS SIMULADOS","last_market":"Cartera ficticia","summary_source":"INDEPENDENT_SYNTHETIC",
        "reconciled":True,"home_total":total,"feed_total":total,"reconciliation_diff":0.0
    }
    return {"positions":df,"summary":summary,
            "by_type":df.groupby("Tipo",as_index=False)["Valor USD_num"].sum(),
            "by_region":df.groupby("Región directa",as_index=False)["Valor USD_num"].sum(),
            "by_custodian":df.groupby("Custodio",as_index=False)["Valor USD_num"].sum()}
