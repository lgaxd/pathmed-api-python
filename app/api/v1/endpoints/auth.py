from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_db_connection
from app.schemas.token import Token
from app.schemas.paciente import PacienteCreate
from app.schemas.msg import Msg
from app.security.core import create_access_token, verify_password_simple 
from app.crud import crud_user, crud_paciente
from typing import Any
import oracledb

router = APIRouter()

@router.post("/login", response_model=Token)
def login_for_access_token(
    conn: oracledb.Connection = Depends(get_db_connection),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Autenticação de usuário (paciente ou colaborador).
    """
    user = crud_user.get_user_from_db(conn, form_data.username)
    
    # !! MUDANÇA AQUI !!
    # Usa a verificação simples de string e a chave 'db_password'
    if not user or not verify_password_simple(form_data.password, user["db_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "id": user["user_id"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/pacientes/register", response_model=Msg, status_code=201)
def register_paciente(
    paciente_in: PacienteCreate,
    conn: oracledb.Connection = Depends(get_db_connection)
):
    """
    Registro de um novo paciente.
    """
    try:
        paciente_id = crud_paciente.create(conn, paciente_in)
        if paciente_id:
            return {"detail": f"Paciente {paciente_id} criado com sucesso."}
        
    except oracledb.IntegrityError as e:
        error_code, _ = e.args[0].full_code.split(':')
        if "TB_PACIENTE_CPF_PAC_UC" in str(e) or "TB_CTT_PACIENTE_EMAIL_PA_UC" in str(e):
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF ou E-mail já cadastrado."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de integridade: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar paciente: {e}"
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Não foi possível criar o paciente."
    )