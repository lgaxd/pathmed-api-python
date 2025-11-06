import oracledb
from typing import List, Dict, Any
from app.crud.crud_paciente import db_row_to_dict

def get_all(conn: oracledb.Connection) -> List[dict]:
    """Busca todos os profissionais de saúde."""
    profissionais = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ID_PROFISSIONAL, ID_ESPECIALIDADE, NOME_PROFISSIONAL_SAUDE,
                       EMAIL_CORPORATIVO_PROFISSIONAL
                FROM TB_PATHMED_PROFISSIONAL_SAUDE
            """)
            for row in cursor:
                profissionais.append(db_row_to_dict(cursor, row))
        return profissionais
    except Exception as e:
        print(f"Erro ao buscar profissionais: {e}")
        return []