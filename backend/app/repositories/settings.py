from datetime import UTC, datetime

from ..database import db_cursor
from ..schemas.settings import AppSetting


class SettingsRepository:
    def list(self) -> list[AppSetting]:
        with db_cursor() as connection:
            rows = connection.execute("SELECT key, value, updated_at FROM app_settings ORDER BY key ASC").fetchall()
        return [AppSetting.model_validate(dict(row)) for row in rows]

    def upsert(self, key: str, value: str) -> AppSetting:
        now = datetime.now(UTC).isoformat()
        with db_cursor() as connection:
            connection.execute(
                """
                INSERT INTO app_settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                (key, value, now),
            )
        return AppSetting(key=key, value=value, updated_at=datetime.fromisoformat(now))
