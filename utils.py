
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone
from sqlalchemy.orm import Query
from settings import PAGINATION_PER_PAGE


class BaseModelSerializer(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def get_utc_now():
    return datetime.now(timezone.utc)


def get_paginated_tasks(q: Query, page: int):
    initial = page * PAGINATION_PER_PAGE - PAGINATION_PER_PAGE
    return q.offset(initial).limit(PAGINATION_PER_PAGE).all()
