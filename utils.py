from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone


class BaseModelSerializer(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def get_utc_now():
    return datetime.now(timezone.utc)
