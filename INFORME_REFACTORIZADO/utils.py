import sys
from config import LOG_DIVIDER


def imprimir_titulo(texto):
    print(f"\n{LOG_DIVIDER}\n{texto.center(len(LOG_DIVIDER))}\n{LOG_DIVIDER}")


def imprimir_info(texto):
    print(f"[INFO] {texto}")


def imprimir_warning(texto):
    print(f"[WARNING] {texto}")


def imprimir_ok(texto):
    print(f"[OK] {texto}")


def imprimir_error(texto):
    print(f"[ERROR] {texto}")


def safe_text(value):
    return "" if value is None else str(value)
