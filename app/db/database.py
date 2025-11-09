import oracledb 
from app.core.config import settings
from typing import Optional, Any
from collections.abc import Generator 

# Variável global do pool de conexões
db_pool: Optional["oracledb.Pool"] = None 

def create_db_pool():
    """Cria o pool de conexões com o Oracle Database."""
    global db_pool
    try:
        if db_pool is None:
            db_pool = oracledb.create_pool(
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                dsn=settings.DB_DSN,
                min=1,
                max=10,
                increment=1
            )
            print("✅ Pool de conexões Oracle criado com sucesso.")
        return db_pool
    except oracledb.DatabaseError as e: 
        print(f"❌ Erro ao criar pool de conexões: {e}")
        raise e

def close_db_pool_on_shutdown():
    """Fecha o pool de conexões quando o aplicativo é encerrado."""
    global db_pool
    if db_pool:
        db_pool.close()
        print("✅ Pool de conexões fechado.")
        db_pool = None

def get_db_connection() -> Generator["oracledb.Connection", Any, None]:
    """Dependência do FastAPI para obter uma conexão do pool."""
    global db_pool
    
    # Cria o pool se não existir
    if db_pool is None:
        create_db_pool() 

    conn: Optional["oracledb.Connection"] = None 
    try:
        conn = db_pool.acquire()
        yield conn 
    except Exception as e:
        print(f"❌ Erro ao adquirir conexão: {e}")
        raise
    finally:
        if conn:
            db_pool.release(conn)