from pydantic import BaseModel, ConfigDict, EmailStr

class ProfissionalRead(BaseModel):
    id_profissional: int
    id_especialidade: int
    nome_profissional_saude: str
    email_corporativo_profissional: EmailStr

    model_config = ConfigDict(from_attributes=True)