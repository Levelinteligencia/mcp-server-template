"""
Exemplo de Agente consumindo o MCP Server — LevelInteligencIA

Ilustra como um agente usa as ferramentas expostas pelo MCP Server
para raciocinar e executar acoes de forma autonoma.
"""

import asyncio
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_agent(entity_id: str, task: str):
    """
    Executa o agente com acesso ao MCP Server.

    O agente recebe uma tarefa em linguagem natural e usa as ferramentas
    disponíveis no servidor para completá-la autonomamente.
    """
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Lista as ferramentas disponíveis no servidor
            tools_response = await session.list_tools()
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools_response.tools
            ]

            client = anthropic.Anthropic()
            messages = [
                {"role": "user", "content": f"entity_id: {entity_id}\n\nTarefa: {task}"}
            ]

            # Loop de raciocinio do agente
            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    tools=tools,
                    messages=messages,
                    system="""Voce e um agente autonomo com acesso a ferramentas de consulta.
                    Use as ferramentas disponiveis para completar a tarefa solicitada.
                    Seja preciso e objetivo nos resultados."""
                )

                if response.stop_reason == "end_turn":
                    final = next(
                        (b.text for b in response.content if hasattr(b, "text")), ""
                    )
                    print(f"Resultado: {final}")
                    break

                if response.stop_reason == "tool_use":
                    tool_use = next(
                        (b for b in response.content if b.type == "tool_use"), None
                    )
                    if not tool_use:
                        break

                    print(f"Agente usando ferramenta: {tool_use.name}")

                    tool_result = await session.call_tool(
                        tool_use.name,
                        tool_use.input
                    )

                    messages.extend([
                        {"role": "assistant", "content": response.content},
                        {
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": tool_result.content[0].text
                            }]
                        }
                    ])


if __name__ == "__main__":
    asyncio.run(run_agent(
        entity_id="12345",
        task="Analise os dados desta entidade e identifique pontos de atencao."
    ))
