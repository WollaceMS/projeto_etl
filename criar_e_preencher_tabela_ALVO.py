# Script responsável por criar a tabela 'signal' no banco de dados 'Alvo'
# e inserir alguns dados simulados para fins de teste.

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from datetime import datetime
import random

# =============================
# Configurações de conexão
# =============================
USER = "postgres"
ENCODED_PASSWORD = "Pizza0305%40"  # Senha com "@" codificada como %40
HOST = "localhost"
PORT = "5432"
DB = "Alvo"

# URL de conexão com o banco PostgreSQL já existente
URL = f"postgresql+psycopg2://{USER}:{ENCODED_PASSWORD}@{HOST}:{PORT}/{DB}"

# Cria o engine de conexão
engine = create_engine(URL)

# Base para definição dos modelos ORM
Base = declarative_base()

# =============================
# Definição da Tabela 'signal'
# =============================
class Signal(Base):
    __tablename__ = 'signal'

    id = Column(Integer, primary_key=True, autoincrement=True)     # Identificador único
    name = Column(String, nullable=False)                          # Nome do sinal (ex: temperatura)
    data = Column(String)                                          # Informação complementar (ex: sensor, origem)
    timestamp = Column(DateTime, nullable=False)                   # Data/hora da leitura
    signal_id = Column(Integer, nullable=False)                    # ID que agrupa ou identifica o tipo de sinal
    value = Column(Float, nullable=False)                          # Valor numérico da leitura

# Cria a tabela no banco caso ela ainda não exista
Base.metadata.create_all(engine)

# =============================
# Inserção de dados de exemplo
# =============================
with Session(engine) as session:
    sinais = []

    # Gera 10 registros fictícios com dados aleatórios
    for _ in range(10):
        sinal = Signal(
            name=random.choice(['Temperatura', 'Pressao', 'Vibracao']),
            data="sensor_x",  # Valor simbólico fixo para exemplo
            timestamp=datetime.now(),
            signal_id=random.randint(1, 5),
            value=round(random.uniform(0, 100), 2)
        )
        sinais.append(sinal)

    # Salva os registros no banco
    session.bulk_save_objects(sinais)
    session.commit()

print("Tabela 'signal' criada no banco 'Alvo' e preenchida com dados de exemplo.")
