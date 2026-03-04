import os


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./todosapp.db")
        self.db_sslmode = os.getenv("DB_SSLMODE", "require")
        self.secret_key = os.getenv(
            "SECRET_KEY",
            "197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3",
        )
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_minutes = int(os.getenv("ACCESS_TOKEN_MINUTES", "20"))

        self.cookie_name = os.getenv("AUTH_COOKIE_NAME", "access_token")
        self.cookie_secure = _to_bool(os.getenv("COOKIE_SECURE"), default=False)
        self.cookie_samesite = os.getenv("COOKIE_SAMESITE", "lax")


settings = Settings()