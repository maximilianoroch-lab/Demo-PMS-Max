"""Controles de independencia de DEMO PMS Max.

Un ID de Sheets distinto no prueba independencia: la base puede ser una copia.
"""
from demo_independent_portfolio import DEMO_PORTFOLIO

REAL_SHEET_ID="18qu9LXo55qQZq4oEAq42u_DKaI7e9lZL_PkfUZiu0T0"
DEMO_SHEET_ID="1xzmw5US1z9CGj0eYdGYS2_FfpSzklGyOYODCJ6vvlcY"


def check_synthetic_inventory(portfolio=DEMO_PORTFOLIO):
    accounts=portfolio.get("accounts",[])
    positions=portfolio.get("positions",[])
    ids=[a["id"] for a in accounts]
    if not ids or len(ids)!=len(set(ids)):
        raise ValueError("Cuentas DEMO vacías o duplicadas")
    if not positions:
        raise ValueError("La cartera ficticia debe contener posiciones")
    if any(p["account"] not in ids or float(p["quantity"])<=0 for p in positions):
        raise ValueError("Posiciones ficticias inconsistentes")
    return True


def check_source_independence(sheet_id,data_mode,certified=False):
    if sheet_id==REAL_SHEET_ID:
        raise ValueError("DEMO no puede apuntar a la base real")
    if sheet_id!=DEMO_SHEET_ID:
        raise ValueError("Origen DEMO no reconocido; verificar explícitamente")
    if data_mode!="independent" or not certified:
        return False
    return check_synthetic_inventory()


def assert_ready_for_public_demo(sheet_id,data_mode,certified=False):
    if not check_source_independence(sheet_id,data_mode,certified):
        raise ValueError("DEMO sigue pendiente de migración y auditoría de datos históricos")
    return True
