from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl

class Settings(BaseSettings):
    BOT_TOKEN: str
    TON_WALLET_ADDRESS: str
    TON_API_PROVIDER: str = "toncenter"  # toncenter | tonapi
    TON_API_KEY: str | None = None
    TON_API_BASE_URL: AnyUrl | None = None

    PAYMENT_POLL_INTERVAL_SEC: int = 5
    PAYMENT_TIMEOUT_SEC: int = 900
    ORDER_TTL_SEC: int = 600
    AMOUNT_DECIMALS: int = 9

    FRAGMENT_PRICE_MODE: str = "auto"   # auto|http|playwright|mock
    FRAGMENT_PRICE_HTTP_URL: str | None = None
    FRAGMENT_PRICE_HTTP_AUTH_HEADER: str | None = None
    USE_PRICE_MOCK: bool = False
    PRICE_MOCK_TON_PER_STAR: str = "0.006451"

    FRAGMENT_AUTH_COOKIES_PATH: str | None = "fragment_cookies.json"
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_SLOWMO_MS: int = 0

    DATABASE_URL: str = "sqlite+aiosqlite:///./stars.db"

    ADMIN_PASSWORD: str | None = None
    ADMIN_USER_ID: int | None = None

    DEFAULT_LANG: str = "ru"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
