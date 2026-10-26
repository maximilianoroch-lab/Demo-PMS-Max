"""Persisted DEMO V5 daily observations. Prices are indicative, NOT market returns."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

ROOT=Path(__file__).resolve().parent
HISTORY=ROOT/"data"/"demo_daily_snapshots.csv"
ASSETS=ROOT/"data"/"demo_daily_assets.csv"

def snapshot_frames(model, day=None):
    day=str(day or datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date())
    positions=model["positions"]
    total=float(model["summary"]["total"])
    overview=pd.DataFrame([{"Fecha":day,"Patrimonio USD":round(total,6),
        "Instrumentos":int(model["summary"]["positions_count"]),
        "Estado":"INDICATIVO V5"}])
    assets=positions.groupby("Ticker",as_index=False)["Valor USD_num"].sum()
    assets=assets.rename(columns={"Valor USD_num":"Valor USD"})
    assets.insert(0,"Fecha",day)
    if abs(float(assets["Valor USD"].sum())-total)>max(0.02,total*0.000001):
        raise ValueError("Snapshot DEMO no concilia con el detalle de activos")
    if not pd.notna(total) or total<=0:
        raise ValueError("Snapshot DEMO con patrimonio inválido")
    return overview,assets

def upsert_csv(frame,path,keys):
    old=pd.read_csv(path) if path.exists() else pd.DataFrame(columns=frame.columns)
    merged=pd.concat([old,frame],ignore_index=True)
    merged=merged.drop_duplicates(subset=keys,keep="last").sort_values(keys)
    path.parent.mkdir(parents=True,exist_ok=True)
    merged.to_csv(path,index=False,float_format="%.8f")
    return merged

def load_history():
    if not HISTORY.exists():return pd.DataFrame(columns=["Fecha","Patrimonio USD"])
    frame=pd.read_csv(HISTORY)
    frame["Fecha"]=pd.to_datetime(frame["Fecha"],errors="coerce")
    frame["Patrimonio USD"]=pd.to_numeric(frame["Patrimonio USD"],errors="coerce")
    return frame.dropna(subset=["Fecha","Patrimonio USD"]).sort_values("Fecha").drop_duplicates("Fecha",keep="last")

def load_asset_history():
    if not ASSETS.exists():return pd.DataFrame(columns=["Fecha","Ticker","Valor USD"])
    frame=pd.read_csv(ASSETS)
    frame["Fecha"]=pd.to_datetime(frame["Fecha"],errors="coerce")
    frame["Valor USD"]=pd.to_numeric(frame["Valor USD"],errors="coerce")
    return frame.dropna(subset=["Fecha","Ticker","Valor USD"]).sort_values("Fecha").drop_duplicates(["Fecha","Ticker"],keep="last")

def top15_daily(positions,history):
    current=positions.groupby("Ticker",as_index=False)["Valor USD_num"].sum().nlargest(15,"Valor USD_num")
    if history.empty:return current.assign(**{"Cambio USD":float("nan"),"Cambio %":float("nan")})
    dates=sorted(history["Fecha"].unique())
    if len(dates)<2:return current.assign(**{"Cambio USD":float("nan"),"Cambio %":float("nan")})
    latest=history.loc[history["Fecha"]==dates[-1],["Ticker","Valor USD"]].set_index("Ticker")["Valor USD"]
    previous=history.loc[history["Fecha"]==dates[-2],["Ticker","Valor USD"]].set_index("Ticker")["Valor USD"]
    # Comparar sólo fechas consecutivas de observación; no inventar cierres faltantes.
    # La variación es entre dos cierres observados, no necesariamente días contiguos.
    common=latest.index.intersection(previous.index)
    valid=previous.loc[common].gt(0) & latest.loc[common].ge(0)
    comparable=common[valid]
    usd_change=latest.loc[comparable]-previous.loc[comparable]
    pct_change=(latest.loc[comparable]/previous.loc[comparable]-1)*100
    current["Cambio USD"]=current["Ticker"].map(usd_change)
    current["Cambio %"]=current["Ticker"].map(pct_change)
    return current

if __name__=="__main__":
    from demo_independent_model import build_independent_model
    model=build_independent_model()
    day,assets=snapshot_frames(model)
    upsert_csv(day,HISTORY,["Fecha"])
    upsert_csv(assets,ASSETS,["Fecha","Ticker"])
    print("DEMO snapshot",day.iloc[0]["Fecha"],day.iloc[0]["Patrimonio USD"],len(assets))
