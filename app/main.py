from contextlib import asynccontextmanager 
from fastapi import FastAPI
from app.api.v1.api import api_router 
# ⭐️ IMPORTAÇÃO CORRETA AGORA ⭐️
from app.db.database import close_db_pool_on_shutdown 

# 1. Defina o Context Manager de Lifespan (Ciclo de Vida)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lógica de Inicialização (Startup) - O yield é a chave
    print("Application startup: starting process.")
    
    yield 

    # Lógica de Desligamento (Shutdown)
    close_db_pool_on_shutdown()
    print("Application shutdown: database pool closed.")


# 2. Crie a instância do FastAPI usando o lifespan
app = FastAPI(
    title="PathMed API",
    description="API RESTful para gerenciamento de consultas médicas.",
    version="1.0.0",
    lifespan=lifespan 
)

# 3. Inclua o roteador principal (para resolver o problema 'No operations defined in spec!')
app.include_router(api_router, prefix="/api/v1")