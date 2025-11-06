import oracledb
from typing import List, Dict, Any
from app.crud.crud_paciente import db_row_to_dict # Reutilizando a função helper

def get_all(conn: oracledb.Connection) -> List[dict]:
    """Busca todas as especialidades."""
    especialidades = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ID_ESPECIALIDADE, DESCRICAO_ESPECIALIDADE FROM TB_PATHMED_ESPECIALIDADE")
            for row in cursor:
                especialidades.append(db_row_to_dict(cursor, row))
        return especialidades
    except Exception as e:
        print(f"Erro ao buscar especialidades: {e}")
        return []