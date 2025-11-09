from fastapi import APIRouter, Depends, HTTPException, Query
from app.db.database import get_db_connection
from app.schemas.disponibilidade import DisponibilidadeDia
from app.crud.crud_disponibilidade import crud_disponibilidade
import oracledb
from datetime import date
from typing import Optional, Dict, Any

router = APIRouter()

def _validar_parametros(data: date, id_especialidade: int):
    if data is None:
        raise ValueError("Data não pode ser nula")
    if data < date.today():
        raise ValueError("Data não pode ser no passado")
    if id_especialidade is None or id_especialidade <= 0:
        raise ValueError("ID da especialidade é obrigatório e deve ser maior que zero")

def _gerar_relatorio(disponibilidade: DisponibilidadeDia) -> str:
    if disponibilidade is None or not disponibilidade.horarios:
        return "Nenhuma disponibilidade encontrada"

    total_horarios = len(disponibilidade.horarios)
    horarios_disponiveis = disponibilidade.total_horarios_disponiveis
    
    if total_horarios == 0:
        return "Nenhuma disponibilidade encontrada"
        
    percentual = (horarios_disponiveis * 100.0) / total_horarios

    return (
        f"📅 {disponibilidade.data} | {disponibilidade.nome_especialidade}\n"
        f"📊 {horarios_disponiveis}/{total_horarios} horários disponíveis ({percentual:.1f}%)"
    )

@router.get(
    "/disponibilidade", 
    response_model=Dict[str, Any],
    summary="Verifica disponibilidade por especialidade e data",
)
def get_disponibilidade(  # ✅ REMOVIDO 'async' - função síncrona
    conn: oracledb.Connection = Depends(get_db_connection),
    especialidade: int = Query(..., alias="especialidade", description="ID da especialidade médica"),
    data: Optional[date] = Query(None, description="Data para buscar disponibilidade (YYYY-MM-DD)")
):
    data = data if data is not None else date.today()
        
    try:
        _validar_parametros(data, especialidade)
        
        nome_especialidade = crud_disponibilidade.find_nome_especialidade_by_id(conn, especialidade)
        disponibilidade_dia = DisponibilidadeDia(
            data=data, 
            id_especialidade=especialidade, 
            nome_especialidade=nome_especialidade
        )

        # Gera horários usando o método da classe CRUD
        horarios = crud_disponibilidade._gerar_horarios_do_dia(data)

        # Busca disponibilidade para cada horário
        for horario in horarios:
            profissionais = crud_disponibilidade.find_profissionais_disponiveis_no_horario(
                conn, 
                horario.data_hora, 
                especialidade
            )
            horario.profissionais_disponiveis.extend(profissionais)

        disponibilidade_dia.horarios = horarios
        
        # Verifica se há pelo menos um horário com disponibilidade
        if not any(h.has_disponibilidade for h in horarios):
             raise HTTPException(
                status_code=404, 
                detail="Nenhuma disponibilidade encontrada para os parâmetros informados"
            )

        relatorio = _gerar_relatorio(disponibilidade_dia)

        response_data = {
            "disponibilidade": disponibilidade_dia,
            "relatorio": relatorio
        }
        
        return response_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Erro no acesso ao banco de dados: {e}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro inesperado no endpoint de disponibilidade: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")