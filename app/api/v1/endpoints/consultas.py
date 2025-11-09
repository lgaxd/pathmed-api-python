from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db_connection
from app.schemas.consulta import ConsultaRead, ConsultaCreate, ConsultaStatusUpdate, ConsultaDetalhada
from app.schemas.msg import Msg
from app.crud import crud_consulta
from typing import List
import oracledb

router = APIRouter()

@router.get("/", response_model=List[ConsultaRead])
def read_consultas(conn: oracledb.Connection = Depends(get_db_connection)):
    """
    Lista todas as consultas.
    """
    consultas_db = crud_consulta.get_all(conn)
    return consultas_db

@router.get("/paciente/{paciente_id}", response_model=List[ConsultaDetalhada])
def read_consultas_por_paciente(
    paciente_id: int,
    conn: oracledb.Connection = Depends(get_db_connection)
):
    """
    Lista todas as consultas de um paciente específico.
    """
    consultas_db = crud_consulta.get_by_paciente_id(conn, paciente_id)
    
    if not consultas_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhuma consulta encontrada para o paciente ID {paciente_id}"
        )
    
    return consultas_db

@router.post("/", response_model=ConsultaRead, status_code=201)
def create_consulta(
    consulta_in: ConsultaCreate,
    conn: oracledb.Connection = Depends(get_db_connection)
):
    """
    Agenda uma nova consulta.
    """
    consulta_id = crud_consulta.create(conn, consulta_in)
    if not consulta_id:
        raise HTTPException(status_code=500, detail="Erro ao agendar consulta")
    
    return ConsultaRead(
        id_consulta=consulta_id,
        id_status=1, # Status inicial
        **consulta_in.model_dump()
    )

@router.put("/status", response_model=Msg)
def update_consulta_status(
    consulta_id: int,
    status_update: ConsultaStatusUpdate,
    conn: oracledb.Connection = Depends(get_db_connection)
):
    """
    Atualiza o status de uma consulta.
    """
    success = crud_consulta.update_status(conn, consulta_id, status_update.id_status)
    if not success:
        raise HTTPException(status_code=404, detail="Consulta não encontrada ou falha ao atualizar")
    return {"detail": "Status da consulta atualizado com sucesso"}