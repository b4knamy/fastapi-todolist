
from pydantic import BaseModel, ConfigDict
from typing import Annotated
from datetime import datetime, timezone
from settings import JWT_EXPIRATION_TIME, PAGINATION_PER_PAGE, JWT_SECRET_KEY, JWT_HASH_ALGORITHM
from fastapi import Depends, HTTPException
from database import SessionDep, oauth_scheme
from sqlmodel.sql._expression_select_cls import SelectOfScalar
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError


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


def encode_user(payload: dict[str]):
    to_encode = payload.copy()
    to_encode["exp"] = get_utc_now() + JWT_EXPIRATION_TIME
    print(to_encode)
    print("\n\n")
    return encode(to_encode, key=JWT_SECRET_KEY,
                  algorithm=JWT_HASH_ALGORITHM)


def decode_user(token: str):

    try:
        return decode(token, key=JWT_SECRET_KEY,
                      algorithms=(JWT_HASH_ALGORITHM))
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")
    except Exception:
        raise HTTPException(status_code=400, detail="Algo deu errado!")


def get_current_user(token: Annotated[str, Depends(oauth_scheme)]):
    return decode_user(token)
