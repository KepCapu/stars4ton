# bot/handlers/start.py
from __future__ import annotations

from decimal import Decimal, ROUND_DOWN, InvalidOperation
from urllib.parse import quote_plus

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from ..config import settings

start_router = Router()

MIN_STARS = 50
MAX_STARS = 1_000_000
FEE_MULT = Decimal("1.05")
NANO = Decimal("1000000000")  # 1 TON = 1e9 nano


# ---------- helpers ----------
def _D(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))

def _format_ton(tons: Decimal) -> str:
    """Красиво форматируем TON без экспоненты, до 9 знаков"""
    t = _D(tons).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
    s = f"{t.normalize()}"
    return "0" if "E" in s else s

def _to_nano(tons: Decimal) -> int:
    return int((_D(tons) * NANO).quantize(Decimal("1"), rounding=ROUND_DOWN))

def compute_total(qty: int) -> tuple[Decimal, Decimal]:
    """(цена_за_звезду, сумма_с_наценкой)"""
    per_star = _D(settings.PRICE_MOCK_TON_PER_STAR)
    subtotal = per_star * _D(qty)
    total = (subtotal * FEE_MULT).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
    return per_star, total


# ---------- links ----------
def build_ton_uri(address: str, tons: Decimal, comment: str) -> str:
    """Внешние TON-кошельки (Tonkeeper / MyTonWallet): подставляют все поля надёжно."""
    nano = _to_nano(tons)
    return f"ton://transfer/{address}?amount={nano}&text={quote_plus(comment)}"

def build_wallet_open_uri() -> str:
    """Открыть чат/мини-приложение Telegram Wallet (без попытки автоперевода)."""
    # Обе ссылки рабочие; оставим https-вариант, он открывает @wallet даже из бота.
    return "https://t.me/wallet?attach=wallet"


# ---------- keyboards ----------
def payment_keyboard(qty: int, total_ton: Decimal, address: str, memo: str) -> InlineKeyboardMarkup:
    tg_link  = build_wallet_open_uri()
    ton_link = build_ton_uri(address, total_ton, memo)

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Открыть Telegram Wallet", url=tg_link)],
        [InlineKeyboardButton(text="🪙 Оплатить TON-кошельком",  url=ton_link)],
        [
            InlineKeyboardButton(text="✅ Проверить оплату",     callback_data=f"check:{qty}"),
            InlineKeyboardButton(text="✏️ Изменить количество",  callback_data="change_qty"),
        ],
    ])


# ---------- handlers ----------
@start_router.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
        "Привет! Я помогу купить ⭐ Stars.\n\n"
        f"Напишите нужное количество звёзд (от {MIN_STARS} до {MAX_STARS})."
    )

@start_router.message(F.text.regexp(r"^\d+$"))
async def take_qty(msg: Message):
    qty = int(msg.text)
    if not (MIN_STARS <= qty <= MAX_STARS):
        await msg.answer(f"Введите число от {MIN_STARS} до {MAX_STARS}.")
        return

    try:
        _, total = compute_total(qty)
    except (InvalidOperation, ValueError):
        await msg.answer("Не удалось посчитать цену. Попробуйте другое число.")
        return

    addr = settings.TON_WALLET_ADDRESS
    memo = f"Stars x{qty}"

    text = (
        "Выберите способ для оплаты — форма перевода откроется с заполненными полями.\n\n"
        f"• Количество: <b>{qty}</b> ⭐\n"
        f"• К оплате: <b>{_format_ton(total)}</b> TON\n"
        "• <b>Кошелёк получателя</b> <i>(нажмите для копирования)</i>:\n"
        f"<u><code>{addr}</code></u>"
    )
    await msg.answer(text, reply_markup=payment_keyboard(qty, total, addr, memo))

@start_router.callback_query(F.data == "change_qty")
async def change_qty(cb: CallbackQuery):
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(
        f"Ок, введите новое количество звёзд (от {MIN_STARS} до {MAX_STARS})."
    )
    await cb.answer()

@start_router.callback_query(F.data.startswith("check:"))
async def check_payment(cb: CallbackQuery):
    # Пока mock; реальную проверку подключим через toncenter/tonapi позже.
    await cb.answer("Пока включён mock-режим проверки платежа.", show_alert=True)
