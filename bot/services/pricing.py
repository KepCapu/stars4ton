from decimal import Decimal, ROUND_HALF_UP
from ..config import settings

TON_DEC = Decimal("0.000000000")  # 9 знаков как у TON

async def quote(quantity: int) -> tuple[Decimal, Decimal, Decimal]:
    """
    Возвращает кортеж:
    (цена_за_звезду, сумма_без_наценки, итоговая_с_наценкой).
    В интерфейсе показываем ТОЛЬКО итоговую сумму — без фразы про наценку.
    """
    # mock / fallback
    price_per_star = Decimal(str(settings.PRICE_MOCK_TON_PER_STAR))

    base = (price_per_star * Decimal(quantity)).quantize(TON_DEC, rounding=ROUND_HALF_UP)
    total = (base * Decimal("1.05")).quantize(TON_DEC, rounding=ROUND_HALF_UP)  # внутренняя наценка 5%
    return price_per_star, base, total
