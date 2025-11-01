import sys
import asyncio
from .config import settings
from .storage import init_db

def _mask(s: str | None, keep: int = 6) -> str:
    if not s:
        return "(empty)"
    return (s[:keep] + "...") if len(s) > keep else "(set)"

async def _run():
    print("✅ Конфиг загружен. Проверка окружения:")
    print(" - Python:", sys.version.split()[0])
    print(" - BOT_TOKEN:", _mask(settings.BOT_TOKEN))
    print(" - TON_WALLET_ADDRESS:", _mask(settings.TON_WALLET_ADDRESS, keep=8))
    print(" - TON_API_PROVIDER:", settings.TON_API_PROVIDER)
    print(" - DB:", settings.DATABASE_URL)
    print(" - FRAGMENT_PRICE_MODE:", settings.FRAGMENT_PRICE_MODE)

    print("⏳ Инициализирую БД…")
    await init_db()
    print("✅ DB init OK (таблицы созданы/актуальны).")

    print("Готово. Дальше добавим модели хэндлеров и запуск aiogram бота.")

def main():
    asyncio.run(_run())

if __name__ == "__main__":
    main()
