from sqlalchemy import create_engine  # Importa a função para criar o motor de conexão com o banco
from sqlalchemy.orm import sessionmaker  # Importa a fábrica de sessões para operações com ORM

# Credenciais e informações de conexão com o banco
USUARIO = "postgres"  # Nome de usuário do banco
SENHA = "Pizza0305%40"  # Senha do usuário (o caractere "@" foi codificado como "%40")
SERVIDOR = "localhost"  # Endereço do servidor (localhost = máquina local)
PORTA = "5432"  # Porta padrão do PostgreSQL
BANCO = "Fonte"  # Nome do banco de dados a ser acessado

# Monta a URL de conexão no formato aceito pelo SQLAlchemy
URL_CONEXAO = f"postgresql+psycopg2://{USUARIO}:{SENHA}@{SERVIDOR}:{PORTA}/{BANCO}"

# Cria o motor de conexão (engine), que é a interface com o banco
motor = create_engine(URL_CONEXAO)

# Cria uma fábrica de sessões para manipular objetos
Sessao = sessionmaker(bind=motor)