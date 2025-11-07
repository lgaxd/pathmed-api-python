# app/db/database.py

import oracledb 
from app.core.config import settings
from typing import Optional, Any
from collections.abc import Generator 

# Variável global do pool de conexões.
# O type hinting usa string literal para evitar erros de ImportError.
db_pool: Optional["oracledb.Pool"] = None 

def create_db_pool():
    """Cria o pool de conexões com o Oracle Database."""
    global db_pool
    try:
        if db_pool is None:
            # Tenta criar o pool se ele ainda não existe
            db_pool = oracledb.create_pool(
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                dsn=settings.DB_DSN,
                min=1,
                max=10,
                increment=1,
                # ⭐️ CORREÇÃO: Argumento 'encoding' removido ⭐️
            )
            print("Pool de conexões Oracle criado com sucesso.")
        return db_pool
    except oracledb.DatabaseError as e: 
        print(f"Erro ao criar pool de conexões: {e}")
        raise e

def close_db_pool_on_shutdown():
    """Fecha o pool de conexões quando o aplicativo é encerrado."""
    global db_pool
    if db_pool:
        db_pool.close()
        db_pool = None

# A dependência do FastAPI deve ser um Generator (função com yield).
def get_db_connection() -> Generator["oracledb.Connection", Any, None]:
    """Dependência do FastAPI para obter uma conexão do pool."""
    global db_pool
    
    # Garante que o pool seja criado se for a primeira requisição
    if db_pool is None:
        create_db_pool() 

    conn: Optional["oracledb.Connection"] = None 
    try:
        conn = db_pool.acquire()
        yield conn 
    finally:
        if conn:
            db_pool.release(conn)

# Chama a criação do pool para que ele seja inicializado quando o módulo é importado
create_db_pool()