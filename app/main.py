from contextlib import asynccontextmanager 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router 
from app.db.database import create_db_pool, close_db_pool_on_shutdown 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application startup: starting process...")
    create_db_pool()
    yield 
    close_db_pool_on_shutdown()
    print("🛑 Application shutdown: database pool closed.")

app = FastAPI(
    title="PathMed API",
    description="API RESTful para gerenciamento de consultas médicas.",
    version="1.0.0",
    lifespan=lifespan 
)

# ✅ CONFIGURAÇÃO CORS MAIS PERMISSIVA (PARA DESENVOLVIMENTO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ PERMITE TODAS AS ORIGENS (apenas para desenvolvimento)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "PathMed API está rodando! 🩺"}