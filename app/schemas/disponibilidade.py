# app/schemas/disponibilidade.py

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List

class ProfissionalResumido(BaseModel):
    id_profissional: int = Field(..., alias="id_profissional")
    nome_profissional_saude: str = Field(..., alias="nome_profissional_saude")
    descricao_especialidade: str = Field(..., alias="descricao_especialidade")

    class Config:
        populate_by_name = True
        from_attributes = True

class HorarioDisponivel(BaseModel):
    data_hora: datetime = Field(..., alias="data_hora")
    profissionais_disponiveis: List[ProfissionalResumido] = Field(default_factory=list, alias="profissionais_disponiveis")

    @property
    def has_disponibilidade(self) -> bool:
        return len(self.profissionais_disponiveis) > 0

    class Config:
        populate_by_name = True
        from_attributes = True

class DisponibilidadeDia(BaseModel):
    data: date = Field(..., alias="data")
    id_especialidade: int = Field(..., alias="id_especialidade")
    nome_especialidade: str = Field(..., alias="nome_especialidade")
    horarios: List[HorarioDisponivel] = Field(default_factory=list)

    @property
    def total_horarios_disponiveis(self) -> int:
        return sum(1 for horario in self.horarios if horario.has_disponibilidade)

    class Config:
        populate_by_name = True
        from_attributes = True