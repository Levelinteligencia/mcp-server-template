"""
MCP Server — Entry Point
LevelInteligencIA

Este servidor expoe ferramentas para agentes de IA via Model Context Protocol.
Cada ferramenta encapsula a logica de integracao com sistemas externos,
garantindo que o agente receba dados validados e normalizados.
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from tools.example_tool import get_example_data
from loguru import logger

app = Server("mcp-server-template")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """
    Registra as ferramentas disponíveis para o agente.
    O agente usa essas informacoes para decidir quando e como usar cada ferramenta.
    """
    return [
        types.Tool(
            name="get_example_data",
            description="Busca dados do sistema externo e retorna normalizado para o agente.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID da entidade a ser consultada"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Periodo de consulta (ex: 30d, 7d)",
                        "default": "30d"
                    }
                },
                "required": ["entity_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    Executa a ferramenta solicitada pelo agente.
    Toda validacao e normalizacao acontece aqui — o agente nunca recebe dados brutos.
    """
    logger.info(f"Ferramenta chamada: {name} | args: {arguments}")

    try:
        if name == "get_example_data":
            result = await get_example_data(
                entity_id=arguments["entity_id"],
                date_range=arguments.get("date_range", "30d")
            )
            return [types.TextContent(type="text", text=str(result))]
        else:
            raise ValueError(f"Ferramenta desconhecida: {name}")

    except Exception as e:
        logger.error(f"Erro ao executar {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"ERRO: {str(e)}. Tente novamente ou use dados alternativos."
        )]


async def main():
    logger.info("MCP Server iniciando...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
