from models.task import ALLOWED_STATE_FILTER, ALLOWED_STATES


create_user = {
    200: {"description": "Usuário criado com sucesso!",
          "content": {
              "application/json": {
                  "example": {
                      "ok": True
                  }
              }
          }
          },
    400: {"description": "Usuário já existe!",
          "content": {
              "application/json": {
                  "example": {
                      "detail": "Usuário já existe."
                  }
              }
          }
          },
}


login_user = {
    200: {"description": "Usuário autenticado com sucesso!",
          "content": {
              "application/json": {
                  "example": {
                      "access_token": "226347324deiwf...",
                      "token_type": "bearer"
                  }
              }
          }
          },
    400: {"description": "Dados invalidos!",
          "content": {
              "application/json": {
                  "example": {
                      "detail": "Credenciais invalidos."
                  }
              }
          }
          },
}

read_task = {
    200: {"description": "Tarefa acessada com sucesso!",
          "content": {
              "application/json": {
                  "example": {
                      "id": 1,
                      "titulo": "Ir ao mercado",
                      "descricao": "comprar ovos, pães e café",
                      "estado": "pendente",
                      "data_criacao": "data aleatoría",
                      "data_atualizacao": "data aleatória"
                  }
              }
          }
          },
    404: {"description": "Tarefa não encontrada!",
          "content": {
              "application/json": {
                  "example": {
                      "detail": "Tarefa não encontrada."
                  }
              }
          }
          },
    401: {"description": "Acesso negado.",
          "content": {
              "application/json": {
                  "example": {
                      "nao_autenticado": {"detail": "Not authenticated"},
                      "token_invalido":  {
                          "detail": "Token invalido"
                      },
                      "token_expirado":  {
                          "detail": "Token expirado"
                      },
                      "acesso_negado": {
                          "detail": "Acesso negado."
                      }
                  },
              }
          }
          },
}

list_tasks = {
    200: {"description": "Listas de tarefas acessada com sucesso!",
          "content": {
              "application/json": {
                  "example": [
                      {
                          "id": 1,
                          "titulo": "Ir ao mercado",
                          "descricao": "comprar ovos, pães e café",
                          "estado": "pendente",
                          "data_criacao": "data aleatoría",
                          "data_atualizacao": "data aleatória"
                      },
                      {
                          "id": 2,
                          "titulo": "Arrumar a casa",
                          "descricao": "limpar o banheiro, cozinha...",
                          "estado": "pendente",
                          "data_criacao": "data aleatoría",
                          "data_atualizacao": "data aleatória"
                      },
                      {
                          "id": 3,
                          "titulo": "Fazer comida",
                          "descricao": "macarrão, carne...",
                          "estado": "pendente",
                          "data_criacao": "data aleatoría",
                          "data_atualizacao": "data aleatória"
                      },
                  ]
              }
          }
          },
    400: {"description": "Valor de estado incorreto.",
          "content": {
              "application/json": {
                  "example": {
                      "detail": f"Possiveis filtros de estado: {
                          ALLOWED_STATE_FILTER}"
                  }
              }
          }
          },
    401: {"description": "Acesso negado.",
          "content": {
              "application/json": {
                  "example": {
                      "nao_autenticado": {"detail": "Not authenticated"},
                      "token_invalido":  {
                          "detail": "Token invalido"
                      },
                      "token_expirado":  {
                          "detail": "Token expirado"
                      },
                      "acesso_negado": {
                          "detail": "Acesso negado."
                      }
                  },
              }
          }
          },
}


update_tasks = {
    200: {"description": "Tarefa atualizada com sucesso!",
          "content": {
              "application/json": {
                  "example": {
                      "id": 1,
                      "titulo": "Ir ao mercado",
                      "descricao": "comprar ovos, pães e acuçar",
                      "estado": "pendente",
                      "data_criacao": "data aleatoría",
                      "data_atualizacao": "data aleatória"
                  }
              }
          }
          },
    400: {"description": "Valor de estado incorreto.",
          "content": {
              "application/json": {
                  "example": {
                      "detail": {"estado": f'Somente 3 valores possiveis: {ALLOWED_STATES}'},
                  },
              },
          },
          },
    404: {"description": "Tarefa não existe.",
          "content": {
              "application/json": {
                  "example": {
                      "detail": "Tarefa não encontrada.",
                  },
              },
          },
          }, 401: {"description": "Acesso negado.",
                   "content": {
                       "application/json": {
                           "example": {
                               "nao_autenticado": {"detail": "Not authenticated"},
                               "token_invalido":  {
                                   "detail": "Token invalido"
                               },
                               "token_expirado":  {
                                   "detail": "Token expirado"
                               },
                               "acesso_negado": {
                                   "detail": "Acesso negado."
                               }
                           },
                       }
                   }
                   },
}


create_tasks = {
    200: {"description": "Tarefa criada com sucesso!",
          "content": {
              "application/json": {
                  "example": {
                      "id": 1,
                      "titulo": "Ir ao mercado",
                      "descricao": "comprar ovos, pães e acuçar",
                      "estado": "pendente",
                      "data_criacao": "data aleatoría",
                      "data_atualizacao": "data aleatória"
                  }
              }
          }
          },
    400: {"description": "Valores incorretos ou faltando.",
          "content": {
              "application/json": {
                  "example": {
                      "detail": {
                          "titulo": "Campo obrigatório",
                          "descricao": "Campo opcional",
                          "estado": f'Somente 3 valores possiveis: {ALLOWED_STATES}'
                      },
                  },
              },
          },
          }, 401: {"description": "Acesso negado.",
                   "content": {
                       "application/json": {
                           "example": {
                               "nao_autenticado": {"detail": "Not authenticated"},
                               "token_invalido":  {
                                   "detail": "Token invalido"
                               },
                               "token_expirado":  {
                                   "detail": "Token expirado"
                               },
                               "acesso_negado": {
                                   "detail": "Acesso negado."
                               }
                           },
                       }
                   }
                   },
}


delete_tasks = {
    200: {"description": "Tarefa excluída com sucesso!",
          "content": {
              "application/json": {
                  "example": {
                      "ok": True
                  }
              }
          }
          },
    404: {"description": "Tarefa não existe.",
          "content": {
              "application/json": {
                  "example": {
                      "detail": "Tarefa não encontrada."
                  },
              },
          },
          }, 401: {"description": "Acesso negado.",
                   "content": {
                       "application/json": {
                           "example": {
                               "nao_autenticado": {"detail": "Not authenticated"},
                               "token_invalido":  {
                                   "detail": "Token invalido"
                               },
                               "token_expirado":  {
                                   "detail": "Token expirado"
                               },
                               "acesso_negado": {
                                   "detail": "Acesso negado."
                               }
                           },
                       }
                   }
                   },
}


{
    "token_invalido":  {
        "detail": "Token invalido"
    },
    "token_expirado":  {
        "detail": "Token expirado"
    },
    "acesso_negado": {
        "detail": "Acesso negado."
    }
}
