
from enum import Enum
from typing import Union
from datetime import datetime
from utils import BaseModelSerializer, get_utc_now
from database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy import Integer, String, Column, DateTime, Enum as EnumSQL


# Cada tarefa deve ter os seguintes campos:
# id (inteiro, autoincrementado)
# titulo (string, obrigatório)
# descricao (string, opcional)
# estado (string, obrigatório, valores possíveis: "pendente", "em andamento", "concluída")
# data_criacao (datetime, gerado automaticamente)
# data_atualizacao (datetime, atualizado automaticamente)


class PossiveisEstados(str, Enum):
    PENDENTE = "Pendente"
    CONCLUIDO = "Concluído"
    EM_ANDAMENTO = "Em andamento"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    titulo = Column(String, nullable=False)
    descricao: Mapped[str | None] = Column(String, nullable=True)
    estado: Mapped[str] = Column(EnumSQL(PossiveisEstados), nullable=False)
    data_criacao = Column(DateTime, default=get_utc_now, nullable=False)
    data_atualizacao = Column(
        DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)


class TaskSerializer(BaseModelSerializer):
    id: int
    titulo: str
    descricao: Union[str, None] = None
    estado: str
    data_criacao: datetime
    data_atualizacao: datetime
