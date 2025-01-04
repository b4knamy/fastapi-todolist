
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from database import create_db_and_tables, SessionDep
from models.task import ALLOWED_STATE_FILTER, Task, TaskCreate, TaskUpdate
from sqlmodel import select
from utils import get_paginated_tasks, get_task_or_404


def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/tasks/{id}")
def read_tasks(session: SessionDep, id: int):
    return get_task_or_404(session=session, task=Task, id=id)


@app.get("/api/tasks/list/{page}")
def list_tasks(session: SessionDep, page: int = 1, estado: str | None = None):
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


@app.patch("/api/tasks/{id}", response_model=TaskUpdate)
def update_tasks(id: int, task: TaskUpdate, session: SessionDep):
    if task.estado and not task.is_state_valid(raise_error=True):
        pass

    task_data = get_task_or_404(session=session, task=Task, id=id)
    task_serializer = task.model_dump(exclude_unset=True)
    task_data.sqlmodel_update(task_serializer)

    session.add(task_data)
    session.commit()
    session.refresh(task_data)
    return task_data


@app.post("/api/tasks", response_model=TaskCreate)
def create_tasks(session: SessionDep, task_create: TaskCreate):
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
def delete_tasks(session: SessionDep, id: int):
    task = get_task_or_404(session=session, task=Task, id=id)

    session.delete(task)
    session.commit()
    return {"ok": True}
