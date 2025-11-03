# bot/services/links.py
from __future__ import annotations

from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode, quote
from ..config import settings

NANO = Decimal("1000000000")  # 1 TON = 1e9 нанотонов


def _to_decimal(x: int | float | str | Decimal) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def _trim_dec(amount: Decimal) -> str:
    """Убираем лишние нули справа для красоты/совместимости (например 0.322550000 -> 0.32255)."""
    s = format(amount.normalize(), "f")
    return s if s != "-0" else "0"


def ton_to_nanoton(amount_ton: int | float | str | Decimal) -> int:
    """
    Конвертация TON → нанотоны (целое), с отсечением до 9 знаков.
    """
    d = _to_decimal(amount_ton).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
    return int((d * NANO).to_integral_value(rounding=ROUND_DOWN))


def build_tg_wallet_link(amount_ton: int | float | str | Decimal, comment: str = "") -> str:
    """
    Ссылка для ВНУТРЕННЕГО Telegram Wallet (Ton Space в Telegram).
    Вариант через tg://resolve — на iOS работает стабильнее, чем https://t.me/wallet?attach=...

    Пример:
    tg://resolve?domain=wallet&attach=send&asset=TON&address=<addr>&amount=0.32255&comment=...
    """
    dec = _to_decimal(amount_ton).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
    params = {
        "attach": "send",
        "asset": "TON",
        "address": settings.TON_WALLET_ADDRESS,
        "amount": _trim_dec(dec),  # для Telegram Wallet допускается десятичный TON
    }
    if comment:
        params["comment"] = comment

    return f"tg://resolve?domain=wallet&{urlencode(params)}"


def build_ton_transfer_link(amount_ton: int | float | str | Decimal, comment: str = "") -> str:
    """
    Универсальная ссылка ton://transfer/... для любых TON-кошельков.
    Сумма строго в НАНОтонах (целое число). Комментарий кладём и в text, и в comment.
    """
    q = {
        "amount": str(ton_to_nanoton(amount_ton)),
    }
    if comment:
        q["text"] = comment
        q["comment"] = comment

    # Некоторые кошельки на iOS лучше воспринимают адрес без спецсимволов — экранируем явно.
    addr = quote(settings.TON_WALLET_ADDRESS, safe="")
    return f"ton://transfer/{addr}?{urlencode(q)}"
