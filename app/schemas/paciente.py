from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import date
from typing import Optional

class PacienteBase(BaseModel):
    identificador_rghc: str
    cpf_paciente: str
    nome_paciente: str
    data_nascimento: date
    tipo_sanguineo: str
    email_paciente: EmailStr
    telefone_paciente: str

class PacienteCreate(PacienteBase):
    password: str

class PacienteUpdate(BaseModel):
    nome_paciente: Optional[str] = None
    email_paciente: Optional[EmailStr] = None
    telefone_paciente: Optional[str] = None

class PacienteRead(BaseModel):
    id_paciente: int
    identificador_rghc: str
    cpf_paciente: str
    nome_paciente: str
    data_nascimento: date
    tipo_sanguineo: str
    email_paciente: Optional[str] = None
    telefone_paciente: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)