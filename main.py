from typing import Union
from fastapi import FastAPI
from database import db_session
from models.task import Task, TaskSerializer
from utils import get_paginated_tasks

# random_task_andamento = {
#     "titulo": "random_title 2",
#     "descricao": "random description 2",
#     "estado": "Em andamento"
# }
# random_task_concluido = {
#     "titulo": "random_title 2",
#     "descricao": "random description 2",
#     "estado": "Concluído"
# }
# random_task_pendente = {
#     "titulo": "random_title 2",
#     "descricao": "random description 2",
#     "estado": "Pendente"
# }


app = FastAPI()


@app.get("/api/tasks/{page}")
def read_tasks(page: int, state: Union[str | None]):
    if not state == "all":
        tasks = db_session.query(Task).where(Task.estado == state)
    else:
        tasks = db_session.query(Task)
    paginated_tasks = get_paginated_tasks(tasks, page)
    return paginated_tasks
