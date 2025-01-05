
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Path
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from database import create_db_and_tables, SessionDep
from models.task import ALLOWED_STATE_FILTER, Task, TaskCreate, TaskSerializer, TaskUpdate
from sqlmodel import select
from models.user import User, UserCreate, TokenJWT, UserSerializer
from utils import check_hashed_pwd, encode_user, generate_hashed_pwd, get_paginated_tasks, get_task_or_404, get_current_user
from contextlib import asynccontextmanager
from apidocs import responses
from cachetools import TTLCache


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Adjust Redis URL if needed

    create_db_and_tables()
    yield

cache = TTLCache(maxsize=120, ttl=15)
app = FastAPI(lifespan=lifespan, title="API de Gerenciamento de Tarefas")


@app.post("/api/auth/token", response_model=TokenJWT, responses=responses.login_user)
def login_user(session: SessionDep, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
        Este endpoint é aberto e autentica um usuário, permitindo acesso aos endpoints protegidos.

        - **username**: nome de usuário, obrigátorio e deve ser String.
        - **password**: senha do usuário, obrigátorio e deve ser String.

        Os demais campos não são necessários, pode ignorar.
    """

    user_db = session.exec(select(User).where(
        User.username == form.username)).first()
    if not user_db:
        raise HTTPException(status_code=400, detail="Credenciais invalidos.")

    if not check_hashed_pwd(form.password, user_db.password):
        raise HTTPException(status_code=400, detail="Credenciais invalidos.")

    token = encode_user(
        {"username": user_db.username, "password": form.password})
    return TokenJWT(access_token=token, token_type="bearer")


@app.post("/api/user/create", responses=responses.create_user)
def create_users(session: SessionDep, user: UserCreate):
    """
        Este endpoint é aberto e cria um novo usuário, que é necessário para poder acessar os demais endpoints que são protegidos por autenticação, com exclusão do "Login User" que também é aberto.

        - **username**: nome de usuário, obrigatório e deve ser String.
        - **password**: senha do usuário, obrigatório e deve ser String.
    """
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


@app.get("/api/tasks/{id}", responses=responses.read_task)
def read_tasks(session: SessionDep, id: int = Path(..., title="ID", description="Este valor é usado identificar uma tarefa"), current_user: UserSerializer = Depends(get_current_user)):
    """
        Endpoint onde é possivel buscar uma tarefa especifica pelo seu identificador "id".
    """

    return get_task_or_404(session=session, task=Task, id=id)


@app.get("/api/tasks/list/{pagina}", responses=responses.list_tasks)
def list_tasks(session: SessionDep, pagina: int = Path(..., title="Pagina", description="Este valor é usado para paginar as tarefas"), estado: str | None = Query(None, description=f"Usado para filtrar tarefas pelo seu estado, onde há somente 3 possiveis valores: {ALLOWED_STATE_FILTER}, caso este filtro seja enviado com valor incorreto, será gerado uma excessão."), current_user: UserSerializer = Depends(get_current_user)):
    """
        Endpoist para listar tarefas, cada pagina acessa 10 tarefas de cada vez (podendo mudar dependendo da configuração), caso não haja tarefas para uma pagina especifica, será retornado uma lista vazia ou com as tarefas restantes.
    """
    cache_key = pagina if not estado else f"{pagina}-{estado}"
    if cache_key in cache:
        return cache[cache_key]
    if estado:
        if not estado in ALLOWED_STATE_FILTER:
            raise HTTPException(status_code=400, detail=f"Possiveis filtros de estado: {
                                ALLOWED_STATE_FILTER}")
        query = select(Task).where(Task.estado == estado)
    else:
        query = select(Task)
    paginated_query = get_paginated_tasks(page=pagina, select_query=query)
    tasks = session.exec(paginated_query).all()

    cache[cache_key] = tasks
    return tasks


@app.patch("/api/tasks/{id}", response_model=TaskSerializer, responses=responses.update_tasks)
def update_tasks(task: TaskUpdate, session: SessionDep, id: int = Path(..., title="ID", description="Este valor é usado identificar uma tarefa"), current_user: UserSerializer = Depends(get_current_user)):
    """
        Este endpoint é usado para atualizar campos de uma tarefa.

        - **titulo**: titulo, opcional e deve ser String.
        - **descricao**: descricao, opcional e pode ser String ou Nulo.
        - **estado**: estado, opcional e deve ser String, sendo somente um dos tres valores: ("pendente", "concluída", "em andamento") que são valores diferentes da parte de filtragem, caso contrário, será levantada uma excessão.
    """

    if task.estado and not task.is_state_valid(raise_error=True):
        pass

    task_data = get_task_or_404(session=session, task=Task, id=id)
    task_serializer = task.model_dump(exclude_unset=True)
    task_data.sqlmodel_update(task_serializer)

    session.add(task_data)
    session.commit()
    session.refresh(task_data)
    return task_data


@app.post("/api/tasks", response_model=TaskSerializer, responses=responses.create_tasks)
def create_tasks(session: SessionDep, task_create: TaskCreate, current_user: UserSerializer = Depends(get_current_user)):
    """
        Este endpoint é usado para criar uma nova tarefa.

        - **titulo**: titulo, obrigatório e deve ser String.
        - **descricao**: descricao, opcional e pode ser String ou Nulo.
        - **estado**: estado, obrigatório e deve ser String, sendo somente um dos tres valores: ("pendente", "concluída", "em andamento") que são valores diferentes da parte de filtragem, caso contrário, será levantada uma excessão.
    """

    try:
        new_task = Task.model_validate(task_create)
    except ValidationError:
        raise HTTPException(
            status_code=400, detail=task_create.validation_error_message)

    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task


@app.delete("/api/tasks/{id}", responses=responses.delete_tasks)
def delete_tasks(session: SessionDep, id: int = Path(..., title="ID", description="Este valor é usado para identificar uma tarefa"), current_user: UserSerializer = Depends(get_current_user)):
    """
        Este endpoint é usado para excluir uma tarefa especifica.
    """

    task = get_task_or_404(session=session, task=Task, id=id)

    session.delete(task)
    session.commit()
    return {"ok": True}
