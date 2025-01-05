API de Gerenciamento de Tarefas com FastAPI



- Configuração
  * Rode os seguintes comandos no terminal *

  comando: git clone https://github.com/b4knamy/fastapi-todolist.git app
  * Este comando irá clonar este repositório para sua maquina e jogando os arquivos na pasta app *


  comando: cd app
  * Navegue para a pasta app *


  comando: docker-compose up --build
  * Rode o comando para gerar uma imagem do docker *



- Comandos uteis da aplicação
  * Rode os seguintes comandos no terminal *

  comando: docker exec -it app sh
  * Este comando irá entrar dentro do container app, onde poderá rodar commandos da aplicação *


  * Comandos disponiveis *


  comando: python run_tests.py
  * Este comando configura um banco de dados de teste e depois roda o pytest, também aceita parametros do pytest normalmente. *

  comando: python generate_tasks.py
  * Este comando irá gerar dados aleatorios e introduzir dentro do banco de dados SQLite da aplicação, caso não tenha, irá ser gerado um. *
  * É adicionado 100 dados aleatorios * 


  
- Documentação da API com Swagger ficará disponivel após rodar a aplicação em: http://0.0.0.0:8000/docs

  
