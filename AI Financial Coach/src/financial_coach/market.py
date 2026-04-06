from __future__ import annotations

from typing import Dict

import yfinance as yf


def fetch_market_context() -> Dict[str, object]:
    """
    Pull a small set of benchmark series to anchor explanations.
    Uses defensive defaults so the demo still works offline or when the API fails.
    """
    context = {
        "treasury_10y": None,
        "sp500_price": None,
        "notes": "Fallback values used because market data was unavailable.",
    }
    try:
        treasury = yf.Ticker("^TNX").history(period="5d")
        sp500 = yf.Ticker("^GSPC").history(period="5d")
        if not treasury.empty:
            context["treasury_10y"] = round(float(treasury["Close"].iloc[-1]), 2)
        if not sp500.empty:
            context["sp500_price"] = round(float(sp500["Close"].iloc[-1]), 2)
        context["notes"] = "Live market context retrieved via yfinance."
    except Exception:
        context["treasury_10y"] = 4.1
        context["sp500_price"] = 5100.0
    return context
