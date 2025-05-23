from banco import motor  # Importa o motor de conexão criado no arquivo banco.py
from sqlalchemy import text  # Permite executar comandos SQL em formato textual
from sqlalchemy.exc import SQLAlchemyError  # Captura erros específicos do SQLAlchemy

try:
    print("Tentando conectar ao banco de dados...")

    # Abre uma conexão com o banco usando o motor
    with motor.connect() as conexao:
        print("Conexão estabelecida com sucesso!")

        # Executa uma consulta SQL simples para verificar a versão do PostgreSQL
        resultado = conexao.execute(text("SELECT version();"))

        # Recupera o primeiro resultado da consulta
        versao = resultado.fetchone()

        if versao:
            # Mostra a versão retornada pelo banco
            print("Versão do PostgreSQL:", versao[0])
        else:
            # Caso não retorne nada (raro, mas possível)
            print("Consulta executada, mas nenhum resultado foi retornado.")

except SQLAlchemyError as erro:
    # Captura erros relacionados à conexão ou consulta SQL
    print("Erro ao conectar ou executar consulta no banco de dados:")
    print(erro)

except Exception as erro:
    # Captura qualquer outro erro inesperado
    print("Erro inesperado:")
    print(erro)
