"""Utilidades de formato para la capa de interfaz de usuario.

Todas las funciones son puras, sin efectos secundarios.
La moneda utilizada es el Balboa panameño (B/.).
"""

from __future__ import annotations


def fmt_currency(value: float, decimals: int = 2) -> str:
    """Formatea *value* como moneda en Balboas panameños.

    Args:
        value: El monto numérico.
        decimals: Cantidad de decimales (por defecto 2).

    Returns:
        Una cadena como ``"B/.1,234.56"``.
    """
    return f"B/.{value:,.{decimals}f}"


def fmt_percent(value: float, decimals: int = 1) -> str:
    """Formatea *value* como porcentaje.

    Args:
        value: El monto numérico (ya multiplicado por 100, ej. 45.2
            significa 45.2 %).
        decimals: Cantidad de decimales (por defecto 1).

    Returns:
        Una cadena como ``"45.2%"``.
    """
    return f"{value:,.{decimals}f}%"


def fmt_number(value: float, decimals: int = 0) -> str:
    """Formatea *value* como número con separadores de miles.

    Args:
        value: El monto numérico.
        decimals: Cantidad de decimales (por defecto 0).

    Returns:
        Una cadena como ``"6,400"``.
    """
    return f"{value:,.{decimals}f}"
