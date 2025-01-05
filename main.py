
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from database import create_db_and_tables, SessionDep
from models.task import ALLOWED_STATE_FILTER, Task, TaskCreate, TaskSerializer, TaskUpdate
from sqlmodel import select
from models.user import User, UserCreate, TokenJWT, UserSerializer
from utils import check_hashed_pwd, encode_user, generate_hashed_pwd, get_paginated_tasks, get_task_or_404, get_current_user
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/api/auth/token", response_model=TokenJWT)
def login_user(session: SessionDep, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_db = session.exec(select(User).where(
        User.username == form.username)).first()
    if not user_db:
        raise HTTPException(status_code=400, detail="Credenciais invalidos.")

    if not check_hashed_pwd(form.password, user_db.password):
        raise HTTPException(status_code=400, detail="Credenciais invalidos.")

    token = encode_user(
        {"username": user_db.username, "password": form.password})
    return TokenJWT(access_token=token, token_type="bearer")


@app.post("/api/user/create")
def create_users(session: SessionDep, user: UserCreate):
    validated_data = user.validate_data()
    is_user_already_created = session.exec(select(User).where(
        User.username == user.username)).first()

    if is_user_already_created:
        raise HTTPException(status_code=400, detail="Usuário já existe.")

    hashed_password = generate_hashed_pwd(validated_data.password)

    new_user = User(username=validated_data.username, password=hashed_password)
    session.add(new_user)
    session.commit()
    return {"ok": True}


@app.get("/api/tasks/{id}")
def read_tasks(session: SessionDep, id: int, current_user: UserSerializer = Depends(get_current_user)):
    return get_task_or_404(session=session, task=Task, id=id)


@app.get("/api/tasks/list/{page}")
def list_tasks(session: SessionDep, page: int = 1, estado: str | None = None, current_user: UserSerializer = Depends(get_current_user)):
    if estado:
        if not estado in ALLOWED_STATE_FILTER:
            raise HTTPException(status_code=400, detail=f"Possiveis filtros de estado: {
                                ALLOWED_STATE_FILTER}")
        query = select(Task).where(Task.estado == estado)
    else:
        query = select(Task)
    paginated_query = get_paginated_tasks(page=page, select_query=query)
    tasks = session.exec(paginated_query).all()
    return tasks


@app.patch("/api/tasks/{id}", response_model=TaskSerializer)
def update_tasks(id: int, task: TaskUpdate, session: SessionDep, current_user: UserSerializer = Depends(get_current_user)):
    if task.estado and not task.is_state_valid(raise_error=True):
        pass

    task_data = get_task_or_404(session=session, task=Task, id=id)
    task_serializer = task.model_dump(exclude_unset=True)
    task_data.sqlmodel_update(task_serializer)

    session.add(task_data)
    session.commit()
    session.refresh(task_data)
    return task_data


@app.post("/api/tasks", response_model=TaskSerializer)
def create_tasks(session: SessionDep, task_create: TaskCreate, current_user: UserSerializer = Depends(get_current_user)):
    try:
        new_task = Task.model_validate(task_create)
    except ValidationError:
        raise HTTPException(
            status_code=400, detail=task_create.validation_error_message)

    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task


@app.delete("/api/tasks/{id}")
def delete_tasks(session: SessionDep, id: int, current_user: UserSerializer = Depends(get_current_user)):
    task = get_task_or_404(session=session, task=Task, id=id)

    session.delete(task)
    session.commit()
    return {"ok": True}
