from __future__ import annotations

from decimal import Decimal, ROUND_DOWN
from urllib.parse import quote

from ..config import settings


def _amount_str(amount: Decimal | float | str) -> str:
    """Строка суммы в TON с точностью до 9 знаков, без хвостовых нулей."""
    d = Decimal(str(amount)).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s if s else "0"


def build_tg_wallet_send_link(amount_ton: Decimal | float | str, memo: str = "") -> str:
    """
    Открывает мини-приложение Telegram Wallet c экраном отправки TON.
    В большинстве клиентов подставляет адрес/сумму/комментарий.
    """
    addr = settings.TON_WALLET_ADDRESS
    a = _amount_str(amount_ton)
    comment = quote(memo) if memo else ""
    # Вариант через startattach=send (на iOS/Android работает стабильнее, чем startapp)
    url = (
        "tg://resolve?domain=wallet"
        f"&startattach=send&asset=TON&address={addr}&amount={a}"
    )
    if comment:
        url += f"&comment={comment}"
    return url


def build_ton_link(amount_ton: Decimal | float | str, memo: str = "") -> str:
    """
    Нативная схема TON. Открывает встроенный TON-кошелёк Telegram
    с формой перевода и заполненными полями.
    """
    addr = settings.TON_WALLET_ADDRESS
    a = _amount_str(amount_ton)
    q = [f"amount={a}"]
    if memo:
        q.append(f"text={quote(memo)}")
    return f"ton://transfer/{addr}?{'&'.join(q)}"
