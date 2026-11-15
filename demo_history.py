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

def has_new_observation(assets, previous, tolerance=0.000001):
    """No registrar otro día si se repite idéntica valuación por ticker."""
    if previous is None or previous.empty:
        return True
    required={"Ticker","Valor USD"}
    if not required.issubset(assets.columns) or not required.issubset(previous.columns):
        raise ValueError("Comparación DEMO sin ticker o valuación")
    old=previous.copy()
    if "Fecha" in old:
        old["Fecha"]=pd.to_datetime(old["Fecha"],errors="coerce")
        old=old.loc[old["Fecha"]==old["Fecha"].max()]
    a=assets.groupby("Ticker")["Valor USD"].sum().sort_index().astype(float)
    b=old.groupby("Ticker")["Valor USD"].sum().sort_index().astype(float)
    if not a.index.equals(b.index):
        return True
    return bool((a-b).abs().gt(tolerance).any())

def upsert_csv(frame,path,keys):
    old=pd.read_csv(path) if path.exists() else pd.DataFrame(columns=frame.columns)
    merged=pd.concat([old,frame],ignore_index=True)
    merged=merged.drop_duplicates(subset=keys,keep="last").sort_values(keys)
    path.parent.mkdir(parents=True,exist_ok=True)
    merged.to_csv(path,index=False,float_format="%.8f")
    return merged

def material_changes(frame, value_columns, date_column="Fecha", tolerance=0.000001):
    """Conservar la primera observación y cambios posteriores; no inventar mercado.
    La serie de archivo permanece intacta: solo se depura la visualización.
    """
    if frame is None or frame.empty:
        return frame
    frame=frame.sort_values(date_column).copy()
    values=frame[list(value_columns)].apply(pd.to_numeric,errors="coerce")
    valid=values.notna().all(axis=1)
    changed=(values.diff().abs()>tolerance).any(axis=1)
    keep=valid & (changed | frame.index.to_series().eq(frame.index[0]))
    return frame.loc[keep].copy()

def load_history():
    if not HISTORY.exists():return pd.DataFrame(columns=["Fecha","Patrimonio USD"])
    frame=pd.read_csv(HISTORY)
    frame["Fecha"]=pd.to_datetime(frame["Fecha"],errors="coerce")
    frame["Patrimonio USD"]=pd.to_numeric(frame["Patrimonio USD"],errors="coerce")
    frame=frame.dropna(subset=["Fecha","Patrimonio USD"]).sort_values("Fecha").drop_duplicates("Fecha",keep="last")
    return material_changes(frame,["Patrimonio USD","Instrumentos"] if "Instrumentos" in frame else ["Patrimonio USD"])

def load_asset_history():
    if not ASSETS.exists():return pd.DataFrame(columns=["Fecha","Ticker","Valor USD"])
    frame=pd.read_csv(ASSETS)
    frame["Fecha"]=pd.to_datetime(frame["Fecha"],errors="coerce")
    frame["Valor USD"]=pd.to_numeric(frame["Valor USD"],errors="coerce")
    frame=frame.dropna(subset=["Fecha","Ticker","Valor USD"]).sort_values("Fecha").drop_duplicates(["Fecha","Ticker"],keep="last")
    if frame.empty:return frame
    # Comparar vectores completos de valuación y cobertura de activos por fecha.
    # Un día archivado sin ningún cambio NO es otro cierre de mercado.
    matrix=frame.pivot(index="Fecha",columns="Ticker",values="Valor USD").sort_index()
    changed=matrix.ne(matrix.shift()).any(axis=1)
    changed.iloc[0]=True
    dates=matrix.index[changed]
    return frame.loc[frame["Fecha"].isin(dates)].copy()

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
    historical_assets=pd.read_csv(ASSETS) if ASSETS.exists() else pd.DataFrame()
    if not has_new_observation(assets,historical_assets):
        print("DEMO V5 sin cambio de valuación/posiciones: no se registra un nuevo cierre simulado.")
    else:
        upsert_csv(day,HISTORY,["Fecha"])
        upsert_csv(assets,ASSETS,["Fecha","Ticker"])
        print("DEMO snapshot indicativo (cambio efectivo)",day.iloc[0]["Fecha"],day.iloc[0]["Patrimonio USD"],len(assets))
