import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Settings:
    # Configurações do banco de dados PostgreSQL
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "ihj_database")
    DB_USER = os.getenv("DB_USER", "ihj_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "ihj_password")
    
    # String de conexão PostgreSQL
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Configurações de autenticação
    SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-muito-forte-aqui-mude-em-producao")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Configurações do servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()

