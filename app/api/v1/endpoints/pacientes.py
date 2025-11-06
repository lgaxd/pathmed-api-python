from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db_connection
from app.schemas.paciente import PacienteRead, PacienteCreate, PacienteUpdate
from app.schemas.msg import Msg
from app.crud import crud_paciente
from typing import List
import oracledb

router = APIRouter()

@router.get("/", response_model=List[PacienteRead])
def read_pacientes(conn: oracledb.Connection = Depends(get_db_connection)):
    """
    Lista todos os pacientes.
    """
    pacientes_db = crud_paciente.get_all(conn)
    return pacientes_db

@router.get("/{paciente_id}", response_model=PacienteRead)
def read_paciente(
    paciente_id: int,
    conn: oracledb.Connection = Depends(get_db_connection)
):
    """
    Obtém um paciente por ID.
    """
    paciente_db = crud_paciente.get_by_id(conn, paciente_id)
    if not paciente_db:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente_db

# O endpoint POST /pacientes (criar) foi movido para /auth/pacientes/register
# Se você precisar de um endpoint de criação autenticado (ex: por um admin),
# pode adicioná-lo aqui, mas o do README parecia ser um registro público.

@router.put("/{paciente_id}", response_model=Msg)
def update_paciente_info(
    paciente_id: int,
    paciente_in: PacienteUpdate,
    conn: oracledb.Connection = Depends(get_db_connection)
):
    """
    Atualiza informações do paciente (nome, email, telefone).
    """
    # (Adicionar lógica de autorização aqui - ex: só o próprio paciente ou admin)
    
    success = crud_paciente.update(conn, paciente_id, paciente_in)
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao atualizar paciente")
    return {"detail": "Paciente atualizado com sucesso"}