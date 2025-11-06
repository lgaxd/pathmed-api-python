import oracledb
from app.schemas.consulta import ConsultaCreate
from typing import List, Dict, Any, Optional
from app.crud.crud_paciente import db_row_to_dict

def create(conn: oracledb.Connection, consulta: ConsultaCreate) -> Optional[int]:
    """Agenda uma nova consulta."""
    try:
        new_consulta_id = conn.var(int)
        
        # O ID_STATUS inicial pode ser '1' (Agendada), por exemplo.
        # Você pode ajustar isso ou receber do schema.
        id_status_inicial = 1 
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TB_PATHMED_TELECONSULTA (
                    ID_PACIENTE, ID_PROFISSIONAL, ID_STATUS, DATA_HORA_CONSULTA
                ) VALUES (
                    :id_pac, :id_prof, :id_status, :dt_hora
                ) RETURNING ID_CONSULTA INTO :id
            """, {
                "id_pac": consulta.id_paciente,
                "id_prof": consulta.id_profissional,
                "id_status": id_status_inicial,
                "dt_hora": consulta.data_hora_consulta,
                "id": new_consulta_id
            })
            
            conn.commit()
            return new_consulta_id.getvalue()[0]
            
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar consulta: {e}")
        return None

def get_all(conn: oracledb.Connection) -> List[dict]:
    """Busca todas as consultas."""
    consultas = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ID_CONSULTA, ID_PACIENTE, ID_PROFISSIONAL, ID_STATUS, DATA_HORA_CONSULTA
                FROM TB_PATHMED_TELECONSULTA
            """)
            for row in cursor:
                consultas.append(db_row_to_dict(cursor, row))
        return consultas
    except Exception as e:
        print(f"Erro ao buscar consultas: {e}")
        return []

def update_status(conn: oracledb.Connection, consulta_id: int, new_status_id: int) -> bool:
    """Atualiza o status de uma consulta."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE TB_PATHMED_TELECONSULTA
                SET ID_STATUS = :status
                WHERE ID_CONSULTA = :id
            """, status=new_status_id, id=consulta_id)
            
            conn.commit()
            return cursor.rowcount > 0 # Retorna True se alguma linha foi afetada
            
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar status da consulta: {e}")
        return False