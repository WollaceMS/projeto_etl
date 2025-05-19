# API para consultar dados da tabela 'data' do banco Fonte.
# Permite filtrar por intervalo de tempo e escolher quais variáveis retornar.

from fastapi import FastAPI, Query, HTTPException
from sqlalchemy import create_engine, Table, MetaData, select, and_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uvicorn

# =============================
# Configurações de banco
# =============================
USER = "postgres"
ENCODED_PASSWORD = "Pizza0305%40"
HOST = "localhost"
PORT = "5432"
DB = "Fonte"
URL = f"postgresql+psycopg2://{USER}:{ENCODED_PASSWORD}@{HOST}:{PORT}/{DB}"

# Conecta com SQLAlchemy
engine = create_engine(URL)
metadata = MetaData()
metadata.reflect(bind=engine)  # Reflete a estrutura do banco
tabela_data = metadata.tables.get('data')

if tabela_data is None:
    raise RuntimeError("Tabela 'data' não encontrada no banco 'Fonte'.")

# =============================
# Inicializa a API FastAPI
# =============================
app = FastAPI(title="API - Banco Fonte", description="Consulta dados da tabela 'data' com filtros dinâmicos.")

# Rota raiz para confirmar que a API está ativa
@app.get("/")
def home():
    return {
        "mensagem": "API do Banco Fonte está no ar.",
        "documentação": "Acesse /docs para ver e testar as rotas disponíveis."
    }

# =============================
# Modelo de resposta opcional
# =============================
class DataRecord(BaseModel):
    timestamp: datetime
    wind_speed: Optional[float]
    power: Optional[float]
    ambient_temperature: Optional[float]

# =============================
# Rota principal: consulta com filtro
# =============================
@app.get("/dados", response_model=List[dict])
def consultar_dados(
    start: datetime = Query(..., description="Data/hora inicial (ex: 2025-05-10T00:00:00)"),
    end: datetime = Query(..., description="Data/hora final (ex: 2025-05-15T23:59:59)"),
    campos: List[str] = Query(default=["timestamp", "wind_speed", "power", "ambient_temperature"],
                              description="Campos a serem retornados")
):
    # Verifica se os campos são válidos
    colunas_validas = tabela_data.columns.keys()
    campos_invalidos = [c for c in campos if c not in colunas_validas]

    if campos_invalidos:
        raise HTTPException(status_code=400, detail=f"Campos inválidos: {campos_invalidos}")

    # Monta a query
    query = select(*[tabela_data.c[c] for c in campos]).where(
        and_(
            tabela_data.c.timestamp >= start,
            tabela_data.c.timestamp <= end
        )
    )

    # Executa a consulta
    with engine.connect() as conn:
        resultados = conn.execute(query).fetchall()

    # Transforma os resultados em dicionário
    return [dict(r._mapping) for r in resultados]

# =============================
# Execução local (opcional)
# =============================
if __name__ == "__main__":
    uvicorn.run("api_FONTE:app", host="127.0.0.1", port=8000, reload=True)
