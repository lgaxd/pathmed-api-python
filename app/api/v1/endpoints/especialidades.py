from fastapi import APIRouter, Depends
from app.db.database import get_db_connection
from app.schemas.especialidade import EspecialidadeRead
from app.crud import crud_especialidade
from typing import List
import oracledb
from app.schemas.msg import Msg

router = APIRouter()

@router.get("/", response_model=List[EspecialidadeRead])
def read_especialidades(conn: oracledb.Connection = Depends(get_db_connection)):
    """
    Lista todas as especialidades médicas.
    """
    return crud_especialidade.get_all(conn)

# O endpoint /disponibilidade pode ser complexo e exigir lógica de negócio
# (cruzar agendas), então o deixaremos como TODO ou uma simples listagem por enquanto.
@router.get("/disponibilidade", response_model=Msg)
def check_disponibilidade():
    """
    Verifica disponibilidade por especialidade. (NÃO IMPLEMENTADO)
    """
    return {"detail": "Endpoint de disponibilidade ainda não implementado."}