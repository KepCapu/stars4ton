from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[KeyboardButton(text="Купить звёзды ⭐")]],
        input_field_placeholder="Напишите количество или нажмите кнопку"
    )

def confirm_kb() -> InlineKeyboardMarkup:
    # Показываем после ввода количества (без deeplink — он появится на шаге оплаты)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", callback_data="pay")],
        [
            InlineKeyboardButton(text="Изменить количество", callback_data="edit"),
            InlineKeyboardButton(text="Отмена", callback_data="cancel")
        ]
    ])

def pay_kb(deeplink_url: str) -> InlineKeyboardMarkup:
    # Клавиатура с прямой оплатой в Telegram Wallet
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить в Telegram Wallet", url=deeplink_url)],
        [InlineKeyboardButton(text="Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ])
