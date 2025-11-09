from fastapi import APIRouter, Depends
from app.db.database import get_db_connection
from app.schemas.especialidade import EspecialidadeRead
from app.crud import crud_especialidade
from typing import List
import oracledb
# A importação de 'Msg' foi removida, pois não é mais necessária neste arquivo.

router = APIRouter()

@router.get("", response_model=List[EspecialidadeRead], summary="Lista todas as especialidades médicas")
def read_especialidades(conn: oracledb.Connection = Depends(get_db_connection)):
    """
    Lista todas as especialidades médicas.
    """
    return crud_especialidade.get_all(conn)

# NOTA IMPORTANTE:
# O endpoint /disponibilidade foi removido deste arquivo.
# O roteamento para /especialidades/disponibilidade agora é tratado
# exclusivamente pelo arquivo 'disponibilidade.py', garantindo que o seu
# novo fluxo de lógica seja executado.