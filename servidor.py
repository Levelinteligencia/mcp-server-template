"""
MCP Server — Ponto de Entrada
LevelInteligencIA

Este servidor expõe ferramentas para agentes de IA via Model Context Protocol (MCP).
Cada ferramenta encapsula a lógica de integração com sistemas externos,
garantindo que o agente receba dados validados e normalizados.
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from ferramentas.ferramenta_exemplo import buscar_dados_exemplo
from loguru import logger

# Inicializa o servidor MCP
app = Server("mcp-server-template")


@app.list_tools()
async def listar_ferramentas() -> list[types.Tool]:
    """
    Registra as ferramentas disponíveis para o agente.
    O agente usa essas informações para decidir quando e como usar cada ferramenta.
    """
    return [
        types.Tool(
            name="buscar_dados_exemplo",
            description="Busca dados do sistema externo e retorna normalizado para o agente.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id_entidade": {
                        "type": "string",
                        "description": "ID da entidade a ser consultada"
                    },
                    "periodo": {
                        "type": "string",
                        "description": "Período de consulta (ex: 30d, 7d)",
                        "default": "30d"
                    }
                },
                "required": ["id_entidade"]
            }
        )
    ]


@app.call_tool()
async def executar_ferramenta(nome: str, argumentos: dict) -> list[types.TextContent]:
    """
    Executa a ferramenta solicitada pelo agente.
    Toda validação e normalização acontece aqui — o agente nunca recebe dados brutos.
    """
    logger.info(f"Ferramenta chamada: {nome} | argumentos: {argumentos}")

    try:
        if nome == "buscar_dados_exemplo":
            resultado = await buscar_dados_exemplo(
                id_entidade=argumentos["id_entidade"],
                periodo=argumentos.get("periodo", "30d")
            )
            return [types.TextContent(type="text", text=str(resultado))]
        else:
            raise ValueError(f"Ferramenta desconhecida: {nome}")

    except Exception as e:
        logger.error(f"Erro ao executar {nome}: {e}")
        return [types.TextContent(
            type="text",
            text=f"ERRO: {str(e)}. Tente novamente ou use dados alternativos."
        )]


async def principal():
    logger.info("MCP Server iniciando...")
    async with stdio_server() as (fluxo_leitura, fluxo_escrita):
        await app.run(
            fluxo_leitura,
            fluxo_escrita,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(principal())
