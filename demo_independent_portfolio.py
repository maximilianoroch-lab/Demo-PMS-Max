"""Inventario independiente y ficticio para reemplazar la base DEMO heredada.

No deriva cantidades, cuentas ni pesos de PMS Bersoch. Todos los importes son
ilustrativos. Este archivo es una especificación de migración, NO un feed activo.
"""
DEMO_PORTFOLIO={
    "portfolio_id":"demo_pms_max",
    "currency":"USD",
    "as_of":"2026-10-22",
    "accounts":[
        {"id":"DEMO-BROKER-01","custodian":"Broker Atlas (ficticio)"},
        {"id":"DEMO-BROKER-02","custodian":"Broker Delta (ficticio)"},
        {"id":"DEMO-BANK-01","custodian":"Banco Horizonte (ficticio)"},
    ],
    "positions":[
        {"account":"DEMO-BROKER-01","ticker":"AAPL","quantity":80},
        {"account":"DEMO-BROKER-01","ticker":"MSFT","quantity":55},
        {"account":"DEMO-BROKER-01","ticker":"SPY","quantity":70},
        {"account":"DEMO-BROKER-01","ticker":"GLD","quantity":45},
        {"account":"DEMO-BROKER-02","ticker":"GGAL","quantity":650},
        {"account":"DEMO-BROKER-02","ticker":"YPF","quantity":160},
        {"account":"DEMO-BROKER-02","ticker":"MELI","quantity":18},
        {"account":"DEMO-BROKER-02","ticker":"GD35","quantity":5000},
        {"account":"DEMO-BANK-01","ticker":"CASH","quantity":12000},
    ],
}
