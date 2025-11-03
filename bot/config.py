from typing import Literal, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Централизованные настройки проекта.
    Читает значения из .env (ключи регистронезависимые) и игнорирует лишние.
    """

    # ----- Телеграм -----
    BOT_TOKEN: str = Field(..., description="Токен бота от BotFather")

    # ----- TON -----
    TON_WALLET_ADDRESS: str = Field(..., description="Адрес кошелька для получения TON")
    TON_API_PROVIDER: Literal["toncenter", "tonapi", "none"] = "toncenter"
    TON_API_KEY: Optional[str] = None
    # Опционально: если нужен кастомный base url к API
    TON_API_BASE_URL: Optional[str] = None

    # ----- Источник цены Fragment -----
    # mock  — использовать PRICE_MOCK_TON_PER_STAR
    # auto  — (зарезервировано под авто-получение)
    # http  — забирать цену из FRAGMENT_PRICE_HTTP_URL
    FRAGMENT_PRICE_MODE: Literal["mock", "auto", "http"] = "mock"
    # Сделаем строкой и допускаем пустое значение — чтобы не падало,
    # когда режим не "http". При режиме http проверим ниже.
    FRAGMENT_PRICE_HTTP_URL: Optional[str] = None
    FRAGMENT_PRICE_HTTP_AUTH_HEADER: Optional[str] = None
    PRICE_MOCK_TON_PER_STAR: float = 0.006451

    # ----- Параметры заказа/оплаты -----
    DEFAULT_LANG: Literal["ru", "en"] = "ru"
    ORDER_TTL_SEC: int = 600
    PAYMENT_POLL_INTERVAL_SEC: int = 5
    PAYMENT_TIMEOUT_SEC: int = 900

    # Как открывать оплату: встроенный @wallet, системный TON-кошелёк или авто
    WALLET_LINK_MODE: Literal["telegram", "ton", "auto"] = "telegram"

    # ----- База данных -----
    DATABASE_URL: str = "sqlite+aiosqlite:///./stars.db"

    # ----- Playwright / Fragment auth (на будущее) -----
    FRAGMENT_AUTH_COOKIES_PATH: str = "fragment_cookies.json"
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_SLOWMO_MS: int = 0

    # ----- Админ (опционально) -----
    ADMIN_USER_ID: Optional[int] = None
    ADMIN_PASSWORD: Optional[str] = None

    # ----- Конфиг чтения .env -----
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # допускаем USE_PAYMENT_MOCK == use_payment_mock и т.п.
        extra="ignore",        # игнорируем незнакомые ключи в .env
    )

    # ----- Валидации -----
    @model_validator(mode="after")
    def _check_fragment_http_url(self):
        """
        Если выбран режим http, URL должен быть указан (но валидировать формат не жестко).
        """
        if self.FRAGMENT_PRICE_MODE == "http" and not self.FRAGMENT_PRICE_HTTP_URL:
            raise ValueError(
                "FRAGMENT_PRICE_HTTP_URL must be set when FRAGMENT_PRICE_MODE=http"
            )
        return self


# Единый экземпляр настроек
settings = Settings()

