"""
Ferramenta de exemplo — LevelInteligencIA

Este módulo ilustra o padrão de integração com sistemas externos.
Adapte para sua API, banco de dados ou qualquer fonte de dados.
"""

import httpx
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

URL_BASE = os.getenv("URL_API_EXTERNA", "")
TOKEN_API = os.getenv("TOKEN_API_EXTERNA", "")


async def buscar_dados_exemplo(id_entidade: str, periodo: str = "30d") -> dict:
    """
    Busca dados do sistema externo e normaliza antes de retornar ao agente.

    Princípio central: o agente sempre recebe dados no mesmo formato,
    independente do que o sistema externo retornar.

    Parâmetros:
        id_entidade: identificador da entidade no sistema externo
        periodo: período de consulta

    Retorna:
        dicionário com dados normalizados e validados
    """
    logger.info(f"Buscando dados: id_entidade={id_entidade} | periodo={periodo}")

    if not URL_BASE or not TOKEN_API:
        logger.warning("API não configurada. Retornando dados de exemplo.")
        return _resposta_mock(id_entidade)

    try:
        async with httpx.AsyncClient(timeout=10.0) as cliente:
            resposta = await cliente.get(
                f"{URL_BASE}/entidades/{id_entidade}",
                headers={"Authorization": f"Bearer {TOKEN_API}"},
                params={"periodo": periodo}
            )
            resposta.raise_for_status()
            dados_brutos = resposta.json()
            return _normalizar(dados_brutos)

    except httpx.TimeoutException:
        logger.error(f"Tempo esgotado: id_entidade={id_entidade}")
        raise Exception("Sistema externo não respondeu no tempo esperado.")

    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP {e.response.status_code}: id_entidade={id_entidade}")
        raise Exception(f"Sistema externo retornou erro: {e.response.status_code}")

    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise


def _normalizar(dados_brutos: dict) -> dict:
    """
    Normaliza o payload bruto da API para o contrato esperado pelo agente.
    Toda lógica de transformação de dados fica aqui, nunca no agente.
    """
    return {
        "id": dados_brutos.get("id") or dados_brutos.get("id_entidade"),
        "nome": dados_brutos.get("name") or dados_brutos.get("nome") or "N/D",
        "status": dados_brutos.get("status", "desconhecido"),
        "metricas": dados_brutos.get("metrics") or dados_brutos.get("metricas") or {},
        "atualizado_em": dados_brutos.get("updated_at") or dados_brutos.get("atualizado_em"),
    }


def _resposta_mock(id_entidade: str) -> dict:
    """Dados de exemplo para desenvolvimento sem API configurada."""
    return {
        "id": id_entidade,
        "nome": "Exemplo",
        "status": "ativo",
        "metricas": {"valor": 42, "tendencia": "crescimento"},
        "atualizado_em": "2025-01-01T00:00:00Z",
    }
