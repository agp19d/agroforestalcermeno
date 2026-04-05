"""Display-formatting utilities used across the UI layer.

All helpers are pure functions with no side-effects.
"""

from __future__ import annotations


def fmt_currency(value: float, decimals: int = 2) -> str:
    """Format *value* as US-dollar currency.

    Args:
        value: The numeric amount.
        decimals: Number of decimal places (default 2).

    Returns:
        A string such as ``"$1,234.56"``.
    """
    return f"${value:,.{decimals}f}"


def fmt_percent(value: float, decimals: int = 1) -> str:
    """Format *value* as a percentage.

    Args:
        value: The numeric amount (already multiplied by 100, e.g. 45.2
            means 45.2 %).
        decimals: Number of decimal places (default 1).

    Returns:
        A string such as ``"45.2%"``.
    """
    return f"{value:,.{decimals}f}%"


def fmt_number(value: float, decimals: int = 0) -> str:
    """Format *value* as a plain number with thousand separators.

    Args:
        value: The numeric amount.
        decimals: Number of decimal places (default 0).

    Returns:
        A string such as ``"6,400"``.
    """
    return f"{value:,.{decimals}f}"
