from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date
from typing import Optional

# Propriedades base compartilhadas
class PacienteBase(BaseModel):
    identificador_rghc: str
    cpf_paciente: str
    nome_paciente: str
    data_nascimento: date
    tipo_sanguineo: str
    email_paciente: EmailStr
    telefone_paciente: str

# Schema para criação (recebido via API)
class PacienteCreate(PacienteBase):
    password: str # Adicionamos a senha para o registro

# Schema para atualização (recebido via API)
class PacienteUpdate(BaseModel):
    nome_paciente: Optional[str] = None
    email_paciente: Optional[EmailStr] = None
    telefone_paciente: Optional[str] = None

# Schema para leitura (retornado pela API)
class PacienteRead(PacienteBase):
    id_paciente: int
    
    model_config = ConfigDict(from_attributes=True)