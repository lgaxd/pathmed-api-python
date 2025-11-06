import oracledb
from app.schemas.user import UserAuth
from typing import Optional

def get_user_from_db(conn: oracledb.Connection, username: str) -> Optional[dict]:
    """
    Tenta encontrar um usuário (paciente ou colaborador) pelo username.
    Retorna um dicionário com os dados do usuário se encontrado.
    """
    try:
        # Tenta na tabela de login de pacientes
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT SENHA_LOGIN, ID_PACIENTE, 'paciente' as TIPO_USUARIO
                FROM TB_PATHMED_LOGIN_PACIENTE
                WHERE USUARIO_LOGIN = :username AND ATIVO = 'S'
            """, username=username)
            user_data = cursor.fetchone()

            if user_data:
                return {
                    "db_password": user_data[0], # !! MUDANÇA AQUI !!
                    "user_id": user_data[1],
                    "role": user_data[2],
                    "username": username
                }

        # Se não achou, tenta na tabela de login de colaboradores
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT SENHA_LOGIN, ID_COLABORADOR, 'colaborador' as TIPO_USUARIO
                FROM TB_PATHMED_LOGIN_COLABORADOR
                WHERE USUARIO_LOGIN = :username AND ATIVO = 'S'
            """, username=username)
            user_data = cursor.fetchone()

            if user_data:
                return {
                    "db_password": user_data[0], # !! MUDANÇA AQUI !!
                    "user_id": user_data[1],
                    "role": user_data[2],
                    "username": username
                }
                
        return None

    except oracledb.DatabaseError as e:
        print(f"Erro ao buscar usuário: {e}")
        return None