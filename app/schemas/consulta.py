from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ConsultaBase(BaseModel):
    id_paciente: int
    id_profissional: int
    data_hora_consulta: datetime

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaRead(ConsultaBase):
    id_consulta: int
    id_status: int

    model_config = ConfigDict(from_attributes=True)

class ConsultaStatusUpdate(BaseModel):
    id_status: int