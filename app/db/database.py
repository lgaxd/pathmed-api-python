import oracledb
from app.core.config import settings
from fastapi import HTTPException
import sys

# Tenta inicializar o pool de conexões com o Oracle
try:
    pool = oracledb.create_pool(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        dsn=settings.DB_DSN,
        min=4,
        max=10,
        increment=1
    )
    print("Pool de conexões Oracle criado com sucesso.")
except Exception as e:
    print(f"Erro ao criar pool de conexões Oracle: {e}")
    sys.exit(1)

def get_db_connection():
    """
    Dependência do FastAPI para obter uma conexão do pool.
    Isso garante que a conexão seja fechada após o uso.
    """
    conn = None
    try:
        conn = pool.acquire()
        yield conn
    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=503, detail=f"Erro de banco de dados: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")
    finally:
        if conn:
            pool.release(conn)