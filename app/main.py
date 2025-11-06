from fastapi import FastAPI
from app.api.v1.api import api_router
from app.db.database import pool # Importa o pool para fechar no shutdown
from contextlib import asynccontextmanager

app = FastAPI(
    title="PathMed API",
    description="API RESTful para gerenciamento de consultas e pacientes do sistema PathMed.",
    version="1.0.0"
)

# Inclui o roteador da v1
app.include_router(api_router, prefix="/v1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions can go here if needed
    yield
    # Shutdown actions
    print("Encerrando aplicação e fechando pool de conexões...")
    if pool:
        pool.close()
    print("Pool de conexões fechado.")

app = FastAPI(
    title="PathMed API",
    description="API RESTful para gerenciamento de consultas e pacientes do sistema PathMed.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Bem-vindo à PathMed API. Acesse /v1/docs para a documentação."}