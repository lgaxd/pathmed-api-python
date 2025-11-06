from fastapi import APIRouter, Depends
from app.db.database import get_db_connection
from app.schemas.profissional import ProfissionalRead
from app.crud import crud_profissional
from typing import List
import oracledb

router = APIRouter()

@router.get("/", response_model=List[ProfissionalRead])
def read_profissionais(conn: oracledb.Connection = Depends(get_db_connection)):
    """
    Lista todos os profissionais de saúde.
    """
    return crud_profissional.get_all(conn)