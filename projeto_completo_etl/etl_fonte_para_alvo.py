# Script ETL - Extrai dados da API do banco "Fonte",
# transforma com agregações 10-minutais,
# e carrega no banco "Alvo" na tabela 'signal'.

import httpx
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import sys

# =============================
# CONFIGURAÇÕES
# =============================

# URL da API que expõe os dados do banco "Fonte"
API_URL = "http://127.0.0.1:8000/dados"

# Dados para conectar ao banco "Alvo"
USER = "postgres"
ENCODED_PASSWORD = "Pizza0305%40"
HOST = "localhost"
PORT = "5432"
DB_ALVO = "Alvo"
URL_ALVO = f"postgresql+psycopg2://{USER}:{ENCODED_PASSWORD}@{HOST}:{PORT}/{DB_ALVO}"

# =============================
# INPUT: data informada pelo usuário
# =============================

# Verifica se a data foi passada como argumento. Se não, solicita ao usuário.
if len(sys.argv) > 1:
    data_str = sys.argv[1]
else:
    data_str = input("Informe a data no formato DD/MM/AAAA: ")

# Valida e converte a string para objeto datetime
try:
    data = datetime.strptime(data_str, "%d/%m/%Y")
except ValueError:
    print("Data inválida. Use o formato DD/MM/AAAA.")
    sys.exit(1)

# Define o intervalo do dia completo (00:00 até 23:59)
start = data.replace(hour=0, minute=0, second=0)
end = data.replace(hour=23, minute=59, second=59)

# =============================
# EXTRAÇÃO: consulta API do banco "Fonte"
# =============================

params = {
    "start": start.isoformat(),
    "end": end.isoformat(),
    "campos": ["timestamp", "wind_speed", "power"]
}

print("Consultando API...")
try:
    response = httpx.get(API_URL, params=params)
    response.raise_for_status()
except Exception as e:
    print("Erro ao consultar API:", e)
    sys.exit(1)

dados = response.json()

# =============================
# TRANSFORMAÇÃO: agrega a cada 10 minutos
# =============================

df = pd.DataFrame(dados)

if df.empty:
    print("Nenhum dado encontrado para essa data.")
    sys.exit(0)

# Converte o campo timestamp para datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Define o timestamp como índice para resample
df.set_index('timestamp', inplace=True)

# Faz a agregação 10-minutal com as estatísticas pedidas
df_agg = df.resample("10min").agg({
    "wind_speed": ["mean", "min", "max", "std"],
    "power": ["mean", "min", "max", "std"]
})

# Renomeia as colunas
df_agg.columns = ['_'.join(col).strip() for col in df_agg.columns.values]
df_agg.reset_index(inplace=True)

# Cria coluna auxiliar para 'name' e 'signal_id'
df_agg['name'] = "ETL_wind_power"
df_agg['data'] = "fonte_api"
df_agg['signal_id'] = 999  # Arbitrário

# =============================
# TRANSFORMA: converte para modelo da tabela 'signal'
# =============================

linhas_signal = []

for _, row in df_agg.iterrows():
    for col in ['wind_speed_mean', 'wind_speed_min', 'wind_speed_max', 'wind_speed_std',
                'power_mean', 'power_min', 'power_max', 'power_std']:
        linhas_signal.append({
            "name": col,
            "data": "fonte_api",
            "timestamp": row['timestamp'],
            "signal_id": 999,
            "value": row[col] if pd.notnull(row[col]) else None
        })

df_final = pd.DataFrame(linhas_signal)

# =============================
# CARGA: envia os dados para o banco "Alvo"
# =============================

print(f"Inserindo {len(df_final)} registros no banco Alvo...")
engine = create_engine(URL_ALVO)

# Insere na tabela 'signal'
df_final.to_sql("signal", engine, index=False, if_exists="append")

print("ETL concluído com sucesso.")
