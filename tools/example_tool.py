"""
Exemplo de ferramenta MCP — LevelInteligencIA

Ilustra o padrao de integracao com sistemas externos.
Adapte para sua API, banco de dados ou qualquer fonte de dados.
"""

import httpx
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("EXTERNAL_API_URL", "")
API_TOKEN = os.getenv("EXTERNAL_API_TOKEN", "")


async def get_example_data(entity_id: str, date_range: str = "30d") -> dict:
    """
    Busca dados do sistema externo e normaliza antes de retornar ao agente.

    Principio central: o agente sempre recebe dados no mesmo formato,
    independente do que o sistema externo retornar.

    Args:
        entity_id: identificador da entidade no sistema externo
        date_range: periodo de consulta

    Returns:
        dict com dados normalizados e validados
    """
    logger.info(f"Buscando dados: entity_id={entity_id} | range={date_range}")

    if not BASE_URL or not API_TOKEN:
        logger.warning("API nao configurada. Retornando dados de exemplo.")
        return _mock_response(entity_id)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/entities/{entity_id}",
                headers={"Authorization": f"Bearer {API_TOKEN}"},
                params={"range": date_range}
            )
            response.raise_for_status()
            raw_data = response.json()
            return _normalize(raw_data)

    except httpx.TimeoutException:
        logger.error(f"Timeout: entity_id={entity_id}")
        raise Exception("Sistema externo nao respondeu no tempo esperado.")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code}: entity_id={entity_id}")
        raise Exception(f"Sistema externo retornou erro: {e.response.status_code}")

    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise


def _normalize(raw_data: dict) -> dict:
    """
    Normaliza o payload bruto da API para o contrato esperado pelo agente.
    Toda logica de transformacao de dados fica aqui, nunca no agente.
    """
    return {
        "id": raw_data.get("id") or raw_data.get("entity_id"),
        "name": raw_data.get("name") or raw_data.get("nome") or "N/A",
        "status": raw_data.get("status", "unknown"),
        "metrics": raw_data.get("metrics") or raw_data.get("metricas") or {},
        "last_updated": raw_data.get("updated_at") or raw_data.get("atualizado_em"),
    }


def _mock_response(entity_id: str) -> dict:
    """Dados de exemplo para desenvolvimento sem API configurada."""
    return {
        "id": entity_id,
        "name": "Exemplo",
        "status": "active",
        "metrics": {"value": 42, "trend": "up"},
        "last_updated": "2025-01-01T00:00:00Z",
    }
