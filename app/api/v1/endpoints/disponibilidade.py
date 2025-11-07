# app/api/v1/endpoints/disponibilidade.py

from fastapi import APIRouter, Depends, HTTPException, Query
from app.db.database import get_db_connection
from app.schemas.disponibilidade import DisponibilidadeDia
from app.crud.crud_disponibilidade import crud_disponibilidade # Importa a instância do CRUD
import oracledb
from datetime import date
from typing import Optional, Dict, Any

router = APIRouter()

# --- Lógica de Validação e Relatório (Service/Controller) ---

def _validar_parametros(data: date, id_especialidade: int):
    """Valida se a data não é no passado e se o ID é válido."""
    if data is None:
        raise ValueError("Data não pode ser nula")

    if data < date.today():
        raise ValueError("Data não pode ser no passado")

    if id_especialidade is None or id_especialidade <= 0:
        raise ValueError("ID da especialidade é obrigatório e deve ser maior que zero")

def _gerar_relatorio(disponibilidade: DisponibilidadeDia) -> str:
    """Gera relatório resumido da disponibilidade do dia."""
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

# --- Endpoint Principal ---

@router.get(
    "/disponibilidade", 
    response_model=Dict[str, Any],
    summary="Verifica disponibilidade por especialidade e data",
)
async def get_disponibilidade(
    conn: "oracledb.Connection" = Depends(get_db_connection),
    especialidade: int = Query(..., alias="especialidade", description="ID da especialidade médica. Obrigatório."),
    data: Optional[date] = Query(None, description="Data para buscar a disponibilidade (YYYY-MM-DD). Padrão: hoje.")
):
    """
    Retorna a lista de horários disponíveis (30 em 30 minutos, das 8h às 18h) 
    para uma especialidade específica em uma determinada data.
    """
    
    data = data if data is not None else date.today()
        
    try:
        # 1. Validação
        _validar_parametros(data, especialidade)
        
        # 2. Inicialização e busca de nome
        nome_especialidade = crud_disponibilidade.find_nome_especialidade_by_id(conn, especialidade)
        disponibilidade_dia = DisponibilidadeDia(
            data=data, 
            id_especialidade=especialidade, 
            nome_especialidade=nome_especialidade
        )

        horarios = crud_disponibilidade._gerar_horarios_do_dia(data)

        # 3. Busca por slot usando a lógica do CRUD
        for horario in horarios:
            profissionais = crud_disponibilidade.find_profissionais_disponiveis_no_horario(
                conn, 
                horario.data_hora, 
                especialidade
            )
            horario.profissionais_disponiveis.extend(profissionais)

        disponibilidade_dia.horarios = horarios
        
        # 4. Checagem final (se nenhum horário tiver disponibilidade)
        if not any(h.has_disponibilidade for h in horarios):
             raise HTTPException(
                status_code=404, 
                detail="Nenhuma disponibilidade encontrada para os parâmetros informados"
            )

        # 5. Gerar o relatório e montar a resposta
        relatorio = _gerar_relatorio(disponibilidade_dia)

        response_data = {
            "disponibilidade": disponibilidade_dia,
            "relatorio": relatorio
        }
        
        return response_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Captura erros lançados pela camada CRUD/DB (ex: RuntimeError)
        raise HTTPException(status_code=500, detail=f"Erro no acesso ao banco de dados: {e}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro inesperado no endpoint de disponibilidade: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor ao buscar disponibilidade.")