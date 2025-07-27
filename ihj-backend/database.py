from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from config import settings

# Criando a engine SQLAlchemy
engine = create_engine(settings.DATABASE_URL)#, fast_executemany=True)
#with engine.connect() as conn:
#    conn.execute(text("SET search_path TO dbo, public"))

# Criando a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_query(query: str) -> pd.DataFrame:
    """Executa uma query SQL e retorna um DataFrame pandas"""
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)

def execute_insert(df: pd.DataFrame, table_name: str) -> str:
    """Insere dados de um DataFrame em uma tabela"""
    if df.empty:
        return "Nenhum dado disponível para inserir."
    
    try:
        with engine.begin() as connection:
            # Limpa a tabela temporária se for dbo.tb_temp
            if table_name == "dbo.tb_temp":
                connection.execute(text("DELETE FROM dbo.tb_temp"))
            
            # Insere os dados
            df.to_sql(table_name, con=engine, if_exists="append", index=False, method="multi")
        return "OK"
    except Exception as e:
        return f"Erro ao executar a inserção: {e}"

