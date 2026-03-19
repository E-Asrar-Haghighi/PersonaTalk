from datetime import datetime

from pydantic import BaseModel


class AppSetting(BaseModel):
    key: str
    value: str
    updated_at: datetime
