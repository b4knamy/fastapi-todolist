
from time import sleep
from fastapi.testclient import TestClient
import pytest
from database import engine
from sqlmodel import SQLModel
from main import app
import os
from pathlib import Path
import dotenv
from models.task import ALLOWED_STATE_FILTER, ALLOWED_STATES, Task, TaskSerializer
os.environ.setdefault("USE_DATABASE_TEST", "1")
dotenv.load_dotenv()

fake_test_tasks = [
    {
        "titulo": "Titulo 1",
        "descricao": "Descrição 1",
        "estado": "pendente",
    },
    {
        "titulo": "Titulo 2",
        "descricao": "Descrição 2",
        "estado": "concluída",
    },
    {
        "titulo": "Titulo 3",
        "descricao": "Descrição 3",
        "estado": "pendente",
    },
    {
        "titulo": "Titulo 4",
        "descricao": "Descrição 4",
        "estado": "em andamento",
    },
    {
        "titulo": "Titulo 5",
        "descricao": "Descrição 5",
        "estado": "concluída",
    },
    {
        "titulo": "Titulo 6",
        "descricao": "Descrição 6",
        "estado": "pendente",
    },
    {
        "titulo": "Titulo 7",
        "descricao": "Descrição 7",
        "estado": "concluída",
    },
    {
        "titulo": "Titulo 8",
        "descricao": "Descrição 8",
        "estado": "pendente",
    },
    {
        "titulo": "Titulo 9",
        "descricao": "Descrição 9",
        "estado": "em andamento",
    },
    {
        "titulo": "Titulo 10",
        "descricao": "Descrição 10",
        "estado": "concluída",
    }
]

fake_user = {
    "username": "fake_username",
    "password": "fake_password",
    "client_id": None,
    "client_secret": None,
    "grant_type": "password"
}


@pytest.fixture(scope="session", autouse=True)
def create_and_delete_test_db():
    SQLModel.metadata.create_all(engine)
    yield
    os.remove(Path(__file__).resolve().parent / "sqlite3_test.db")


client = TestClient(app)


def test_crud_endpoints_are_protected():
    get_read_response = client.get("/api/tasks/1")
    get_list_response = client.get("/api/tasks/list/1")
    post_response = client.post("/api/tasks", json=fake_test_tasks[0])
    patch_response = client.patch(
        "/api/tasks/1", json={"titulo": "titulo comum"})
    delete_response = client.delete("/api/tasks/1")

    assert get_read_response.status_code == 401
    assert get_list_response.status_code == 401
    assert post_response.status_code == 401
    assert patch_response.status_code == 401
    assert delete_response.status_code == 401


def test_create_user_success():
    fake_user = {
        "username": "fake_username",
        "password": "fake_password"
    }

    response = client.post("/api/user/create", json=fake_user)
    assert response.json() == {"ok": True}
    assert response.status_code == 200


def test_create_user_missing_password():
    fake_user = {
        "username": "fake_username",
    }

    response = client.post("/api/user/create", json=fake_user)

    assert "detail" in response.json()
    assert response.status_code == 422


def test_create_user_password_integer():
    fake_user = {
        "username": "fake_username",
        "password": 23
    }

    response = client.post("/api/user/create", json=fake_user)

    assert "detail" in response.json()
    assert response.status_code == 422


def test_user_already_exist():
    fake_user = {
        "username": "fake_username",
        "password": "fake_password"
    }

    response = client.post("/api/user/create", json=fake_user)
    assert response.json() == {"detail": "Usuário já existe."}
    assert response.status_code == 400


def test_login_user_invalid_password():
    fk_user = fake_user.copy()
    fk_user["password"] = "fake_password_"
    response = client.post("/api/auth/token", data=fk_user)

    assert response.json()["detail"] == "Credenciais invalidos."
    assert response.status_code == 400


def test_login_user_invalid_username():
    fk_user = fake_user.copy()
    fk_user["username"] = "fake_username_"
    response = client.post("/api/auth/token", data=fk_user)

    assert response.json()["detail"] == "Credenciais invalidos."
    assert response.status_code == 400


def test_login_user_success():
    response = client.post("/api/auth/token", data=fake_user)
    json_response = response.json()
    assert "access_token" in json_response
    assert "token_type" in json_response
    assert response.status_code == 200


def test_read_specific_task_which_do_not_exist():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    task_response = client.get("/api/tasks/1", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 404
    assert task_response.json()["detail"] == "Tarefa não encontrada."


def test_list_tasks_when_do_not_exists_even_one():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    task_response = client.get("/api/tasks/list/1", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 200
    assert task_response.json() == []


def test_create_task_with_missing_title():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    fake_task = fake_test_tasks[0].copy()
    del fake_task["titulo"]

    task_response = client.post("/api/tasks", json=fake_task, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert "detail" in task_response.json()
    assert task_response.status_code == 422


def test_create_task_with_missing_description():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    fake_task = fake_test_tasks[0].copy()
    del fake_task["descricao"]

    task_response = client.post("/api/tasks", json=fake_task, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    task = task_response.json()

    assert task_response.status_code == 200

    assert task["data_criacao"]
    assert task["data_atualizacao"]
    assert task["id"]
    assert task["titulo"]
    assert task["descricao"] == None
    assert task["estado"]


def test_create_task_with_missing_state():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    fake_task = fake_test_tasks[0].copy()
    del fake_task["estado"]

    task_response = client.post("/api/tasks", json=fake_task, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 422
    assert "detail" in task_response.json()


def test_create_task_with_wrong_state():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    fake_task = fake_test_tasks[0].copy()
    fake_task["estado"] = "pendentee"

    task_response = client.post("/api/tasks", json=fake_task, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 400
    assert task_response.json()["detail"] == {
        "titulo": "Campo obrigatório",
        "descricao": "Campo opcional",
        "estado": f'Somente 3 valores possiveis: {ALLOWED_STATES}'
    }


def test_create_task_success():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    fake_task = fake_test_tasks[0].copy()

    task_response = client.post("/api/tasks", json=fake_task, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    task = task_response.json()
    assert task_response.status_code == 200
    assert task["data_criacao"]
    assert task["data_atualizacao"]
    assert task["id"]
    assert task["titulo"]
    assert task["descricao"]
    assert task["estado"]


def test_read_first_task_which_description_is_null():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    task_response = client.get("/api/tasks/1", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    fake_task: Task = fake_test_tasks[0].copy()
    task: Task = task_response.json()

    assert task_response.status_code == 200

    assert task["descricao"] == None
    assert task["titulo"] == fake_task["titulo"]
    assert task["estado"] == fake_task["estado"]


def test_read_second_task():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    task_response = client.get("/api/tasks/2", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    fake_task: Task = fake_test_tasks[0].copy()
    task: Task = task_response.json()

    assert task_response.status_code == 200

    assert task["descricao"] == fake_task["descricao"]
    assert task["titulo"] == fake_task["titulo"]
    assert task["estado"] == fake_task["estado"]


def test_update_first_task_description_which_is_null_to_a_value():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()
    fake_task = fake_test_tasks[0].copy()

    task_response = client.patch("/api/tasks/1", json={"descricao": fake_task["descricao"]}, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    task: Task = task_response.json()

    assert task_response.status_code == 200

    assert task["descricao"] == fake_task["descricao"]
    assert task["titulo"] == fake_task["titulo"]
    assert task["estado"] == fake_task["estado"]


def test_update_all_value_from_the_first_task():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()
    fake_task_first_example = fake_test_tasks[0].copy()
    fake_task = fake_test_tasks[1].copy()

    task_response = client.patch("/api/tasks/2", json=fake_task, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    task: Task = task_response.json()
    assert task_response.status_code == 200
    assert task != fake_task_first_example
    assert task["data_criacao"]
    assert task["data_atualizacao"]
    assert task["id"]
    assert task["titulo"]
    assert task["descricao"]
    assert task["estado"]


def test_update_and_check_updated_at():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    task_response = client.get("/api/tasks/1", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    task_json: Task = task_response.json()

    updated_response = client.patch("/api/tasks/1", json={
        "titulo": "random title s"
    }, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    updated_json: Task = updated_response.json()

    assert updated_json["data_atualizacao"] > task_json["data_criacao"]


def test_error_when_setting_wrong_state_in_possible_values():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()
    fake_task = fake_test_tasks[0].copy()
    fake_task["estado"] = "andamentoo"

    task_response = client.patch("/api/tasks/2", json=fake_task, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    task_response.json()
    assert task_response.status_code == 400
    assert task_response.json()["detail"] == {
        "estado": f'Somente 3 valores possiveis: {ALLOWED_STATES}'}


def test_update_non_existent_task():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()
    fake_task = fake_test_tasks[0].copy()
    fake_task["estado"] = "em andamento"
    fake_task["titulo"] = "random titleee"

    task_response = client.patch("/api/tasks/3", json=fake_task, headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    task_response.json()
    assert task_response.status_code == 404
    assert task_response.json()["detail"] == "Tarefa não encontrada."


def test_list_tasks():
    response = client.post("/api/auth/token", data=fake_user)

    response_json = response.json()

    task_response = client.get("/api/tasks/list/1", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 200
    assert len(task_response.json()) == 2


def test_create_many_tasks():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    tasks = [{
        "titulo": "Titulo 2",
        "descricao": "Descrição 2",
        "estado": "concluída",
    },
        {
        "titulo": "Titulo 3",
        "descricao": "Descrição 3",
        "estado": "pendente",
    },
        {
        "titulo": "Titulo 4",
        "descricao": "Descrição 4",
        "estado": "em andamento",
    },]
    count = 0
    for _ in range(50):
        if count == 3:
            count = 0
        fake_task = tasks[count]
        fake_task["titulo"] = f"Titulo {_}"
        fake_task["descricao"] = f"Descrição {_}"
        count += 1
        client.post("/api/tasks", json=fake_task, headers={
            "Authorization": f"Bearer {response_json["access_token"]}"
        })

    task_response = client.get("/api/tasks/list/1", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 200
    assert len(task_response.json()) == 5


def test_paginated_tasks():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()
    for _ in range(1, 12):
        task_response = client.get(f"/api/tasks/list/{_}", headers={
            "Authorization": f"Bearer {response_json["access_token"]}"
        })
        tasks: list[TaskSerializer] = task_response.json()

        assert task_response.status_code == 200
        if _ == 11:

            assert len(tasks) == 2
        else:
            for i in range(0, 5):
                assert tasks[i]


def test_empty_list_in_particular_paginated_page():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    task_response = client.get(f"/api/tasks/list/12", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 200
    assert task_response.json() == []


def test_list_filter_pending_state():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    for i in range(1, 4):
        task_response = client.get(f"/api/tasks/list/{i}?estado=pendente", headers={
            "Authorization": f"Bearer {response_json["access_token"]}"
        })
        tasks = task_response.json()
        assert task_response.status_code == 200
        for task in tasks:
            assert task["estado"] == "pendente"


def test_list_filter_concluded_state():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    for i in range(1, 4):
        task_response = client.get(f"/api/tasks/list/{i}?estado=concluida", headers={
            "Authorization": f"Bearer {response_json["access_token"]}"
        })
        tasks = task_response.json()
        assert task_response.status_code == 200
        for task in tasks:
            assert task["estado"] == "concluída"


def test_list_filter_progress_state():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    for i in range(1, 4):
        task_response = client.get(f"/api/tasks/list/{i}?estado=andamento", headers={
            "Authorization": f"Bearer {response_json["access_token"]}"
        })
        tasks = task_response.json()
        assert task_response.status_code == 200
        for task in tasks:
            assert task["estado"] == "em andamento"


def test_list_filter_not_in_allowed_states_filter():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    task_response = client.get("/api/tasks/list/1?estado=pendentee", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    assert task_response.status_code == 400
    assert task_response.json()["detail"] == f"Possiveis filtros de estado: {
        ALLOWED_STATE_FILTER}"


def test_list_filter_wrong_state_key_being_ignored():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    task_response = client.get("/api/tasks/list/1?estadowd=pendentee", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })
    assert task_response.status_code == 200
    assert len(task_response.json()) == 5


def test_delete_task_which_do_not_exist():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    task_response = client.delete("/api/tasks/55", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 404
    assert task_response.json()["detail"] == "Tarefa não encontrada."


def test_delete_task_which_do_not_exist():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    task_response = client.delete("/api/tasks/55", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 404
    assert task_response.json()["detail"] == "Tarefa não encontrada."


def test_delete_task_and_check_is_was_deleted():
    response = client.post("/api/auth/token", data=fake_user)
    response_json = response.json()

    delete_response = client.delete("/api/tasks/1", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert delete_response.status_code == 200
    assert delete_response.json() == {"ok": True}

    task_response = client.get("/api/tasks/1", headers={
        "Authorization": f"Bearer {response_json["access_token"]}"
    })

    assert task_response.status_code == 404
    assert task_response.json()["detail"] == "Tarefa não encontrada."
