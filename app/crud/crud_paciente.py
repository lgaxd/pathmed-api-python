import oracledb
from app.schemas.paciente import PacienteCreate, PacienteUpdate
# Não importamos mais o get_password_hash
from typing import List, Optional, Dict, Any

def db_row_to_dict(cursor: oracledb.Cursor, row: tuple) -> Dict[str, Any]:
    """Converte uma linha do cursor (tuple) em um dicionário (chave=coluna)."""
    return {col[0].lower(): val for col, val in zip(cursor.description, row)}

def create(conn: oracledb.Connection, paciente: PacienteCreate) -> Optional[int]:
    """
    Cria um novo paciente e seu login (com senha em texto puro).
    Usa transação e RETURNING para obter os IDs gerados pelos triggers.
    """
    try:
        # Variáveis para armazenar os IDs gerados
        new_paciente_id = conn.var(int)
        
        # Inicia a transação
        conn.begin()

        # 1. Inserir na TB_PATHMED_PACIENTE
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TB_PATHMED_PACIENTE (
                    IDENTIFICADOR_RGHC, CPF_PACIENTE, NOME_PACIENTE, 
                    DATA_NASCIMENTO, TIPO_SANGUINEO
                ) VALUES (
                    :rghc, :cpf, :nome, :dt_nasc, :sangue
                ) RETURNING ID_PACIENTE INTO :id
            """, {
                "rghc": paciente.identificador_rghc,
                "cpf": paciente.cpf_paciente,
                "nome": paciente.nome_paciente,
                "dt_nasc": paciente.data_nascimento,
                "sangue": paciente.tipo_sanguineo,
                "id": new_paciente_id
            })
            
            paciente_id = new_paciente_id.getvalue()[0]

        # 2. Inserir na TB_PATHMED_CONTATO_PACIENTE
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TB_PATHMED_CONTATO_PACIENTE (
                    ID_PACIENTE, EMAIL_PACIENTE, TELEFONE_PACIENTE
                ) VALUES (
                    :id_pac, :email, :tel
                )
            """, {
                "id_pac": paciente_id,
                "email": paciente.email_paciente,
                "tel": paciente.telefone_paciente
            })

        # 3. Inserir na TB_PATHMED_LOGIN_PACIENTE (com senha em texto puro)
        
        plain_password = paciente.password
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TB_PATHMED_LOGIN_PACIENTE (
                    ID_PACIENTE, USUARIO_LOGIN, SENHA_LOGIN
                ) VALUES (
                    :id_pac, :user, :pass
                )
            """, {
                "id_pac": paciente_id,
                "user": paciente.email_paciente, # Usando email como login
                "pass": plain_password  # Salva a senha original
            })
            
        # Commita a transação
        conn.commit()
        return paciente_id

    except oracledb.IntegrityError as e:
        conn.rollback()
        print(f"Erro de integridade: {e}")
        # Retorna um código de erro ou lança uma exceção específica
        raise e
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar paciente: {e}")
        return None

#
# As funções get_by_id, get_all, e update não precisam de alteração
# (Elas podem ser copiadas da resposta anterior)
#
def get_by_id(conn: oracledb.Connection, paciente_id: int) -> Optional[dict]:
    """Busca um paciente pelo ID, juntando com a tabela de contatos."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.ID_PACIENTE, p.IDENTIFICADOR_RGHC, p.CPF_PACIENTE,
                    p.NOME_PACIENTE, p.DATA_NASCIMENTO, p.TIPO_SANGUINEO,
                    c.EMAIL_PACIENTE, c.TELEFONE_PACIENTE
                FROM TB_PATHMED_PACIENTE p
                JOIN TB_PATHMED_CONTATO_PACIENTE c ON p.ID_PACIENTE = c.ID_PACIENTE
                WHERE p.ID_PACIENTE = :id
            """, id=paciente_id)
            
            row = cursor.fetchone()
            if row:
                return db_row_to_dict(cursor, row)
        return None
    except Exception as e:
        print(f"Erro ao buscar paciente por ID: {e}")
        return None

def get_all(conn: oracledb.Connection) -> List[dict]:
    """Busca todos os pacientes."""
    pacientes = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.ID_PACIENTE, p.IDENTIFICADOR_RGHC, p.CPF_PACIENTE,
                    p.NOME_PACIENTE, p.DATA_NASCIMENTO, p.TIPO_SANGUINEO,
                    c.EMAIL_PACIENTE, c.TELEFONE_PACIENTE
                FROM TB_PATHMED_PACIENTE p
                LEFT JOIN TB_PATHMED_CONTATO_PACIENTE c ON p.ID_PACIENTE = c.ID_PACIENTE
            """)
            
            for row in cursor:
                pacientes.append(db_row_to_dict(cursor, row))
        return pacientes
    except Exception as e:
        print(f"Erro ao buscar todos os pacientes: {e}")
        return []

def update(conn: oracledb.Connection, paciente_id: int, paciente: PacienteUpdate) -> bool:
    """Atualiza dados do paciente (nome, email, telefone)."""
    try:
        conn.begin()
        
        # Atualiza TB_PATHMED_PACIENTE
        if paciente.nome_paciente:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE TB_PATHMED_PACIENTE
                    SET NOME_PACIENTE = :nome
                    WHERE ID_PACIENTE = :id
                """, nome=paciente.nome_paciente, id=paciente_id)

        # Atualiza TB_PATHMED_CONTATO_PACIENTE
        if paciente.email_paciente or paciente.telefone_paciente:
            fields_to_update = []
            params = {"id": paciente_id}
            if paciente.email_paciente:
                fields_to_update.append("EMAIL_PACIENTE = :email")
                params["email"] = paciente.email_paciente
            if paciente.telefone_paciente:
                fields_to_update.append("TELEFONE_PACIENTE = :tel")
                params["tel"] = paciente.telefone_paciente
            
            sql_update = f"UPDATE TB_PATHMED_CONTATO_PACIENTE SET {', '.join(fields_to_update)} WHERE ID_PACIENTE = :id"
            
            with conn.cursor() as cursor:
                cursor.execute(sql_update, params)

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar paciente: {e}")
        return False