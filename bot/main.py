import sys
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties

from .config import settings
from .storage import init_db
from .handlers.start import start_router


def _mask(s: str | None, keep: int = 6) -> str:
    if not s:
        return "(empty)"
    return (s[:keep] + "...") if len(s) > keep else "(set)"


async def _run() -> None:
    # Диагностика окружения
    print("✅ Конфиг загружен. Проверка окружения:")
    print(" - Python:", sys.version.split()[0])
    print(" - BOT_TOKEN:", _mask(settings.BOT_TOKEN))
    print(" - DB:", settings.DATABASE_URL)
    print(" - FRAGMENT_PRICE_MODE:", settings.FRAGMENT_PRICE_MODE)

    # Инициализация БД
    print("⏳ Инициализирую БД…")
    await init_db()
    print("✅ DB init OK (таблицы созданы/актуальны).")

    # Инициализация бота и диспетчера
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(start_router)

    # Команда /start и сброс вебхука
    await bot.set_my_commands([BotCommand(command="start", description="Начать")])
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск long polling
    print("🚀 Запускаю бота… Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
