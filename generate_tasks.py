from faker import Faker
from database import Session, engine, SQLModel
from models.task import ALLOWED_STATES, Task

if __name__ == "__main__":
    fk = Faker()
    SQLModel.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:

        for task in range(100):
            will_not_have_description = fk.boolean(20)
            fk_titulo = fk.sentence(nb_words=3)
            if will_not_have_description:
                fk_descricao = None
            else:
                fk_descricao = fk.text(max_nb_chars=100)
            estado = ALLOWED_STATES[fk.random_int(min=0, max=2)]

            new_task = Task(
                titulo=fk_titulo,
                descricao=fk_descricao,
                estado=estado
            )

            session.add(new_task)
            session.commit()
    print("Random Tasks Generated!")
