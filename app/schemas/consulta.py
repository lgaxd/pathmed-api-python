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

# ✅ VERSÃO SIMPLIFICADA: Usando campos opcionais e configuração flexível
class ConsultaDetalhada(BaseModel):
    id_consulta: int
    id_paciente: int
    id_profissional: int
    id_status: int
    data_hora_consulta: datetime
    nome_paciente: str
    nome_profissional_saude: str  # ✅ USA O NOME EXATO DO BANCO
    descricao_especialidade: str
    descricao_status: str

    model_config = ConfigDict(from_attributes=True)