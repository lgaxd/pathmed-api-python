# app/crud/crud_disponibilidade.py

import oracledb
from app.schemas.disponibilidade import ProfissionalResumido, HorarioDisponivel
from datetime import date, time, datetime, timedelta
from typing import List

class CRUDDisponibilidade:
    
    def _gerar_horarios_do_dia(self, data: date) -> List[HorarioDisponivel]:
        """Gera lista de slots de 30 minutos das 8:00 às 18:00."""
        horarios: List[HorarioDisponivel] = []
        hora_inicio = time(8, 0)
        hora_fim = time(18, 0)

        data_hora_atual = datetime.combine(data, hora_inicio)
        data_hora_fim = datetime.combine(data, hora_fim)
        
        while data_hora_atual < data_hora_fim:
            horarios.append(HorarioDisponivel(data_hora=data_hora_atual)) 
            data_hora_atual += timedelta(minutes=30) 

        return horarios

    def find_nome_especialidade_by_id(self, conn: "oracledb.Connection", id_especialidade: int) -> str:
        """Busca nome da especialidade por ID."""
        sql = "SELECT DESCRICAO_ESPECIALIDADE FROM TB_PATHMED_ESPECIALIDADE WHERE ID_ESPECIALIDADE = :id_especialidade"
        
        cursor = conn.cursor()
        cursor.execute(sql, [id_especialidade])
        
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return str(row[0])
        return f"Especialidade {id_especialidade}"

    def find_profissionais_disponiveis_no_horario(
        self, 
        conn: "oracledb.Connection", 
        data_hora: datetime, 
        id_especialidade: int
    ) -> List[ProfissionalResumido]:
        """Busca profissionais disponíveis em um horário específico, excluindo consultas agendadas/confirmadas."""
        profissionais: List[ProfissionalResumido] = []
        
        sql = """
            SELECT 
                ps.ID_PROFISSIONAL, 
                ps.NOME_PROFISSIONAL_SAUDE, 
                e.DESCRICAO_ESPECIALIDADE
            FROM 
                TB_PATHMED_PROFISSIONAL_SAUDE ps
            JOIN 
                TB_PATHMED_ESPECIALIDADE e ON ps.ID_ESPECIALIDADE = e.ID_ESPECIALIDADE
            WHERE 
                ps.ID_ESPECIALIDADE = :id_especialidade
                AND NOT EXISTS (
                    SELECT 1 
                    FROM TB_PATHMED_TELECONSULTA tc
                    WHERE tc.ID_PROFISSIONAL = ps.ID_PROFISSIONAL
                    AND tc.DATA_HORA_CONSULTA = :data_hora
                    AND tc.ID_STATUS IN (1, 2) -- Agendada (1) ou Confirmada (2)
                )
            ORDER BY ps.NOME_PROFISSIONAL_SAUDE
        """
        
        cursor = conn.cursor()
        try:
            cursor.execute(sql, id_especialidade=id_especialidade, data_hora=data_hora)
            
            for row in cursor:
                profissional = ProfissionalResumido(
                    id_profissional=row[0],
                    nome_profissional_saude=row[1],
                    descricao_especialidade=row[2]
                )
                profissionais.append(profissional)
                
        except oracledb.DatabaseError as e:
            # Lançar exceção para ser tratada no endpoint
            raise RuntimeError(f"Erro no banco ao buscar profissionais disponíveis: {e}")
        finally:
            cursor.close()

        return profissionais

# Cria uma instância singleton para ser usada no endpoint
crud_disponibilidade = CRUDDisponibilidade()