from pydantic import BaseModel, ConfigDict

class EspecialidadeRead(BaseModel):
    id_especialidade: int
    descricao_especialidade: str

    model_config = ConfigDict(from_attributes=True)