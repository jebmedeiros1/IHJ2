from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import logging


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar engine do SQLAlchemy para PostgreSQL
try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DEBUG,
    )
    logger.info(f"Conectado ao PostgreSQL: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
except Exception as e:
    logger.error(f"Erro ao conectar com PostgreSQL: {e}")
    raise

from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_search_path(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('SET search_path TO dbo')
    cursor.close()

#with engine.connect() as conn:
#    conn.execute(text("SET search_path TO dbo, public"))

# Criar SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos SQLAlchemy
Base = declarative_base()

def get_database():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"Conexão PostgreSQL bem-sucedida. Versão: {version}")
            return True
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {e}")
        return False

def execute_query(query: str, params: dict = None):
    """Executa uma query SQL e retorna os resultados"""
    try:
        with engine.connect() as connection:
            if params:
                result = connection.execute(text(query), params)
            else:
                result = connection.execute(text(query))
            
            # Se for uma query SELECT, retorna os resultados
            if query.strip().upper().startswith('SELECT'):
                return result.fetchall()
            else:
                connection.commit()
                return result.rowcount
    except Exception as e:
        logger.error(f"Erro ao executar query: {e}")
        raise

def get_equipamentos():
    """Busca todos os equipamentos"""
    query = """
    SELECT equipamento, localizacao, denominacao_localizacao, material, classe
    FROM equipamentos
    ORDER BY equipamento
    """
    return execute_query(query)

def get_classes():
    """Busca todas as classes de equipamentos"""
    query = """
    SELECT DISTINCT classe
    FROM equipamentos
    WHERE classe IS NOT NULL
    ORDER BY classe
    """
    result = execute_query(query)
    return [row[0] for row in result] if result else []

def get_caracteristicas_by_classes(classes: list):
    """Busca características por classes de equipamentos"""
    if not classes:
        return []
    
    classes_str = "', '".join(classes)
    query = f"""
    SELECT DISTINCT c.nome_caracteristica
    FROM caracteristicas c
    JOIN equipamentos e ON c.equipamento_id = e.id
    WHERE e.classe IN ('{classes_str}')
    ORDER BY c.nome_caracteristica
    """
    result = execute_query(query)
    return [row[0] for row in result] if result else []

def search_equipamentos_by_filters(classes: list = None, filtros: dict = None):
    """Busca equipamentos por filtros"""
    base_query = """
    SELECT DISTINCT e.equipamento, e.localizacao, e.denominacao_localizacao, e.material, e.classe
    FROM equipamentos e
    """
    
    conditions = []
    
    if classes:
        classes_str = "', '".join(classes)
        conditions.append(f"e.classe IN ('{classes_str}')")
    
    if filtros:
        for caracteristica, valores in filtros.items():
            if valores:
                valores_str = "', '".join(valores)
                base_query += f"""
                JOIN caracteristicas c_{caracteristica.replace(' ', '_')} ON e.id = c_{caracteristica.replace(' ', '_')}.equipamento_id
                """
                conditions.append(f"""
                (c_{caracteristica.replace(' ', '_')}.nome_caracteristica = '{caracteristica}' 
                 AND c_{caracteristica.replace(' ', '_')}.valor_caracteristica IN ('{valores_str}'))
                """)
    
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " ORDER BY e.equipamento"
    
    return execute_query(base_query)

def get_equipamento_details(equipamento: str):
    """Busca detalhes de um equipamento específico"""
    query = """
    SELECT e.equipamento, e.localizacao, e.denominacao_localizacao, e.material, e.classe,
           c.nome_caracteristica, c.valor_caracteristica
    FROM equipamentos e
    LEFT JOIN caracteristicas c ON e.id = c.equipamento_id
    WHERE e.equipamento = :equipamento
    ORDER BY c.nome_caracteristica
    """
    return execute_query(query, {"equipamento": equipamento})
    
def execute_insert(df, table_name: str):
    """Insere um DataFrame no banco (modo append)"""
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
        return True
    except Exception as e:
        logger.error(f"Erro ao inserir dados na tabela {table_name}: {e}")
        return False

if __name__ == "__main__":
    # Teste de conexão
    if test_connection():
        print("✅ Conexão PostgreSQL funcionando!")
        
        # Teste básico de queries
        classes = get_classes()
        print(f"Classes encontradas: {classes}")
        
        equipamentos = get_equipamentos()
        print(f"Total de equipamentos: {len(equipamentos) if equipamentos else 0}")
    else:
        print("❌ Falha na conexão PostgreSQL!")

