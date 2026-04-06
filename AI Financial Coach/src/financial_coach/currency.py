from __future__ import annotations

from typing import Dict

import pandas as pd


CURRENCY_SYMBOLS: Dict[str, str] = {
    "INR": "INR",
    "USD": "USD",
    "EUR": "EUR",
    "GBP": "GBP",
    "JPY": "JPY",
    "AED": "AED",
}

SYMBOL_TO_CODE: Dict[str, str] = {
    "₹": "INR",
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
}


def detect_currency_code(tables: Dict[str, pd.DataFrame]) -> str:
    for frame in tables.values():
        if frame.empty:
            continue
        for column in ("currency_code", "currency", "currency_symbol"):
            if column not in frame.columns:
                continue
            values = frame[column].dropna().astype(str).str.strip()
            if values.empty:
                continue
            raw = values.iloc[0].upper()
            if raw in CURRENCY_SYMBOLS:
                return raw
            if raw in SYMBOL_TO_CODE:
                return SYMBOL_TO_CODE[raw]
            if raw.lower() in {"rupee", "rupees", "inr"}:
                return "INR"
    return "INR"


def currency_label(currency_code: str) -> str:
    return CURRENCY_SYMBOLS.get(currency_code.upper(), currency_code.upper())


def format_money(amount: float, currency_code: str = "INR", decimals: int = 0) -> str:
    code = currency_label(currency_code)
    return f"{code} {amount:,.{decimals}f}"
