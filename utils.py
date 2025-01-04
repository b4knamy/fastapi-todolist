
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone
from settings import PAGINATION_PER_PAGE
from fastapi import HTTPException
from database import SessionDep
from sqlmodel.sql._expression_select_cls import SelectOfScalar


class BaseModelSerializer(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def get_utc_now():
    return datetime.now(timezone.utc)


def get_paginated_tasks(page: int, select_query: SelectOfScalar):
    if not isinstance(page, int) or page < 1:
        page = 1

    initial = page * PAGINATION_PER_PAGE - PAGINATION_PER_PAGE
    return select_query.offset(initial).limit(PAGINATION_PER_PAGE)


def get_task_or_404(session: SessionDep, task, id: int):
    task_data = session.get(task, id)
    if not task_data:
        raise HTTPException(
            status_code=404, detail="Tarefa não encontrada.")
    return task_data
