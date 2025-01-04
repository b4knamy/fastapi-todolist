
from enum import Enum
from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Field, SQLModel
from utils import BaseModelSerializer, get_utc_now


# Cada tarefa deve ter os seguintes campos:
# id (inteiro, autoincrementado)
# titulo (string, obrigatório)
# descricao (string, opcional)
# estado (string, obrigatório, valores possíveis: "pendente", "em andamento", "concluída")
# data_criacao (datetime, gerado automaticamente)
# data_atualizacao (datetime, atualizado automaticamente)

ALLOWED_STATES = ("Pendente", "Concluído", "Em andamento")
ALLOWED_STATE_FILTER = ("pendente", "andamento", "concluido")


class TaskStateValidation:

    validation_error_message = {
        "titulo": "Campo obrigatório",
        "descricao": "Campo opcional",
        "estado": f'Somente 3 valores: {ALLOWED_STATES}'
    }

    def is_state_valid(self, raise_error=False):
        if not self.estado:
            raise NotImplemented("Estado não está implementado.")

        is_valid = self.estado in ALLOWED_STATES

        if raise_error and not is_valid:
            raise HTTPException(
                status_code=400, detail={"estado": f'Somente 3 valores: {ALLOWED_STATES}'})
        return is_valid


class PossiveisEstados(str, Enum):
    pendente = "Pendente"
    concluido = "Concluído"
    andamento = "Em andamento"


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str
    descricao: str | None = None
    estado: PossiveisEstados
    data_criacao: datetime = Field(default_factory=get_utc_now)
    data_atualizacao: datetime = Field(default_factory=get_utc_now)


class TaskSerializer(BaseModelSerializer):
    id: int
    titulo: str
    descricao: str | None
    estado: str
    data_criacao: datetime
    data_atualizacao: datetime


class TaskUpdate(BaseModelSerializer, TaskStateValidation):
    titulo: str | None = None
    descricao: str | None = None
    estado: str | None = None


class TaskCreate(BaseModelSerializer, TaskStateValidation):
    titulo: str
    descricao: str | None = None
    estado: str
