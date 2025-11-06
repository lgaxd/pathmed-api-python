from fastapi import APIRouter
from app.api.v1.endpoints import auth, pacientes, consultas, especialidades, profissionais

api_router = APIRouter()

# Inclui os roteadores dos endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(pacientes.router, prefix="/pacientes", tags=["Pacientes"])
api_router.include_router(consultas.router, prefix="/consultas", tags=["Consultas"])
api_router.include_router(especialidades.router, prefix="/especialidades", tags=["Especialidades"])
api_router.include_router(profissionais.router, prefix="/profissionais", tags=["Profissionais"])