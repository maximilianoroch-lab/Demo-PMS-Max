
PORTFOLIO = {
    "id": "demo_pms_max",
    "display_name": "DEMO PMS Max",
    "sheet_id": "1xzmw5US1z9CGj0eYdGYS2_FfpSzklGyOYODCJ6vvlcY",
    "base_currency": "USD",
    "app_name": "DEMO PMS Max · Cockpit",
    "privacy_scope": "demo_instance",
    "rules": {
        "primary_wealth_excludes_crypto": True,
        "crypto_separate": True,
        "fut_analytics_class": "Crypto",
        "gld_class": "Oro",
        "gld_type": "ETF",
        "global_direct": ["MELI", "VIST", "GLOB"],
        "argentina_direct": ["YPF", "YPFD", "GGAL"],
        "manual_required": ["FUT", "CASH", "GALILEO", "SCHROD"],
        "forbidden_performance_metrics": ["TWR", "XIRR", "Modified Dietz"],
        "weekend_last_valid_ok": True,
    }
}
