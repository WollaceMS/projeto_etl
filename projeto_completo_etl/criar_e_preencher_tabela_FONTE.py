# Importa o psycopg2 para manipular diretamente bancos PostgreSQL
import psycopg2

# Permite executar comandos como CREATE DATABASE fora de uma transação
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Importações do SQLAlchemy para trabalhar com tabelas e engine de conexão
from sqlalchemy import create_engine, Table, Column, MetaData, Float, DateTime

# Importa a versão do insert compatível com PostgreSQL, que permite "ON CONFLICT DO NOTHING"
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Módulos padrão para manipulação de data e hora
from datetime import datetime, timedelta

# Pandas para gerar a lista de timestamps por minuto; random para gerar os valores simulados
import pandas as pd
import random

# ======================
# CONFIGURAÇÕES INICIAIS
# ======================

# Informações básicas de conexão com o banco PostgreSQL
USER = "postgres"           # Nome do usuário do banco
PASSWORD = "Pizza0305@"       # Senha original do usuário (sem codificação)
ENCODED_PW = "Pizza0305%40"   # Senha codificada (o @ vira %40 para ser usada na URL de conexão)
HOST = "localhost"          # Servidor onde o banco está hospedado (localhost = máquina local)
PORT = "5432"               # Porta padrão do PostgreSQL
DB = "Fonte"                # Nome do banco de dados a ser usado/criado

# Monta a URL de conexão para o SQLAlchemy (ORM)
URL = f"postgresql+psycopg2://{USER}:{ENCODED_PW}@{HOST}:{PORT}/{DB}"

# ======================================================
# ETAPA 1 - VERIFICAR SE O BANCO EXISTE OU CRIÁ-LO
# ======================================================

try:
    # Conecta ao banco padrão "postgres", que já existe e permite gerenciar os outros
    conn = psycopg2.connect(
        dbname="postgres",
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    
    # Permite executar comandos como CREATE DATABASE fora de uma transação
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Verifica se já existe um banco com o nome desejado
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB,))
    if not cur.fetchone():
        # Se não existe, cria o banco de dados
        cur.execute(f"CREATE DATABASE {DB}")
        print(f"Banco '{DB}' criado com sucesso.")
    else:
        print(f"O banco '{DB}' já existe.")
    
    # Fecha a conexão de controle
    cur.close()
    conn.close()

except Exception as e:
    # Exibe mensagem de erro e interrompe o script caso algo falhe nessa etapa
    print("Erro ao verificar ou criar o banco de dados:", e)
    exit(1)

# ======================================================
# ETAPA 2 - DEFINIR A TABELA E CONECTAR COM SQLALCHEMY
# ======================================================

# Cria o motor de conexão usando SQLAlchemy para se comunicar com o banco "Fonte"
motor = create_engine(URL)

# Inicializa o objeto que armazena a estrutura das tabelas
meta = MetaData()

# Define a tabela "data" com os campos solicitados
tabela = Table('data', meta,
    Column('timestamp', DateTime, primary_key=True),      # Data/hora como chave primária
    Column('wind_speed', Float),                          # Velocidade do vento (m/s)
    Column('power', Float),                               # Potência gerada (kW)
    Column('ambient_temperature', Float)                  # Temperatura ambiente (°C)
)

# Cria a tabela no banco, se ainda não existir
meta.create_all(motor)

# ======================================================
# ETAPA 3 - GERAR OS DADOS SIMULADOS PARA A TABELA
# ======================================================

# Define o período de geração dos dados: do momento atual até 10 dias depois
inicio = datetime.now().replace(second=0, microsecond=0)
fim = inicio + timedelta(days=10)

# Gera uma lista de registros com frequência de 1 em 1 minuto
dados = []
for t in pd.date_range(inicio, fim, freq='1min'):
    dados.append({
        'timestamp': t,
        'wind_speed': round(random.uniform(3, 25), 2),           # Gera um valor de vento entre 3 e 25 m/s
        'power': round(random.uniform(0, 5000), 2),              # Gera um valor de potência entre 0 e 5000 kW
        'ambient_temperature': round(random.uniform(-5, 40), 1)  # Gera temperatura entre -5 e 40 °C
    })

# ======================================================
# ETAPA 4 - INSERIR OS DADOS NA TABELA DO BANCO
# ======================================================

# Abre uma conexão com o banco via SQLAlchemy
with motor.connect() as conn:
    # Monta um comando de inserção que ignora valores duplicados de timestamp
    stmt = pg_insert(tabela).values(dados).on_conflict_do_nothing(index_elements=['timestamp'])

    # Executa a inserção
    conn.execute(stmt)

    # Confirma a operação no banco
    conn.commit()

# ======================================================
# ETAPA 5 - RESUMO FINAL
# ======================================================

# Exibe no terminal um resumo da operação
print(f"Total de registros gerados: {len(dados)}")
print(f"Período dos dados: {inicio} até {fim}")
