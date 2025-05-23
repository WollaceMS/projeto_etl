# Projeto de ETL com FastAPI, PostgreSQL, Pandas e Docker

Este projeto é a implementação de um pipeline de ETL utilizando uma estrutura composta por dois bancos de dados PostgreSQL, uma API construída em FastAPI e um script de ETL desenvolvido em Python. A proposta é simular um processo real de extração, transformação e carga de dados.

## Objetivo

- Criar dados simulados (com frequência de 1 em 1 minuto por 10 dias)
- Expor esses dados por meio de uma API REST
- Consumir os dados através de um script de ETL
- Transformar os dados em agregações de 10 minutos
- Armazenar os dados transformados em outro banco PostgreSQL
- Utilizar Docker e Docker Compose para facilitar a execução do projeto

## Estrutura do projeto

```
.
├── api_FONTE.py                       # Código da API FastAPI
├── banco.py                           # Conexão com o banco via SQLAlchemy
├── criar_e_preencher_tabela_FONTE.py  # Geração dos dados simulados
├── criar_e_preencher_tabela_ALVO.py   # Criação da estrutura da tabela de destino
├── etl_fonte_para_alvo.py             # Script de ETL
├── requirements.txt                   # Lista de dependências
├── Dockerfile                         # Dockerfile para a API
├── docker-compose.yml                 # Sobe os containers dos bancos e API
└── README.md                          # Este arquivo
```

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/seunome/projeto-etl-case
cd projeto-etl-case
```

### 2. Subir os containers

```bash
docker-compose up --build
```

Esse comando sobe:
- Um banco de dados PostgreSQL com os dados brutos (Fonte)
- Um segundo banco PostgreSQL para os dados transformados (Alvo)
- Uma API FastAPI para expor os dados do banco Fonte

### 3. Popular os bancos

Em outro terminal, execute:

```bash
python criar_e_preencher_tabela_FONTE.py
python criar_e_preencher_tabela_ALVO.py
```

### 4. Acessar a API

A API estará disponível em: `http://localhost:8000/docs`  
Por lá é possível testar a rota `/dados`, que aceita parâmetros para filtro de datas e escolha das variáveis que serão retornadas.

### 5. Rodar o ETL

O script `etl_fonte_para_alvo.py` aceita uma data como argumento (formato: `dd/mm/aaaa`). Exemplo:

```bash
python etl_fonte_para_alvo.py 20/05/2025
```

Esse script consulta a API, realiza as agregações de 10 minutos (média, mínimo, máximo e desvio padrão) e grava os dados no banco de destino.

## Sobre os dados

O banco de origem simula medições de:
- Velocidade do vento (wind_speed)
- Potência gerada (power)
- Temperatura ambiente (ambient_temperature)

com um registro por minuto durante 10 dias consecutivos.

O banco de destino armazena os dados agregados em uma tabela chamada `signal`.

## Tecnologias utilizadas

- Python 3.10
- FastAPI
- SQLAlchemy
- Pandas
- HTTPX
- PostgreSQL
- Docker / Docker Compose

## Observações finais

O projeto foi desenvolvido com foco didático e para avaliação técnica, mas se aproxima bastante de cenários reais de integração de dados e APIs.

Caso tenha qualquer dúvida ou sugestão, fico à disposição.