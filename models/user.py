from fastapi import HTTPException
from pydantic import ValidationError
from sqlmodel import SQLModel, Field
from utils import BaseModelSerializer


class UserValidator:
    validate_error_message = {
        "username": "Campo obrigatório",
        "password": "Campo obrigatório",
    }

    def validate_data(self):
        try:
            validated_user_data = User.model_validate(self)
        except ValidationError:
            raise HTTPException(
                status_code=400, detail=self.validate_error_message)
        return validated_user_data


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    password: str


class UserSerializer(BaseModelSerializer):
    id: int
    username: str


class UserCreate(BaseModelSerializer, UserValidator):
    username: str
    password: str


class TokenJWT(BaseModelSerializer):
    access_token: str | None
    token_type: str | None
