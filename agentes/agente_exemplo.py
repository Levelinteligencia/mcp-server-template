"""
Exemplo de Agente consumindo o MCP Server — LevelInteligencIA

Ilustra como um agente usa as ferramentas expostas pelo MCP Server
para raciocinar e executar ações de forma autônoma.
"""

import asyncio
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def executar_agente(id_entidade: str, tarefa: str):
    """
    Executa o agente com acesso ao MCP Server.

    O agente recebe uma tarefa em linguagem natural e usa as ferramentas
    disponíveis no servidor para completá-la de forma autônoma.

    Parâmetros:
        id_entidade: entidade sobre a qual o agente deve raciocinar
        tarefa: descrição da tarefa em linguagem natural
    """
    parametros_servidor = StdioServerParameters(
        command="python",
        args=["servidor.py"]
    )

    async with stdio_client(parametros_servidor) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()

            # Lista as ferramentas disponíveis no servidor
            resposta_ferramentas = await sessao.list_tools()
            ferramentas = [
                {
                    "name": ferramenta.name,
                    "description": ferramenta.description,
                    "input_schema": ferramenta.inputSchema
                }
                for ferramenta in resposta_ferramentas.tools
            ]

            cliente = anthropic.Anthropic()
            mensagens = [
                {"role": "user", "content": f"id_entidade: {id_entidade}\n\nTarefa: {tarefa}"}
            ]

            # Loop de raciocínio do agente
            while True:
                resposta = cliente.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    tools=ferramentas,
                    messages=mensagens,
                    system="""Você é um agente autônomo com acesso a ferramentas de consulta.
                    Use as ferramentas disponíveis para completar a tarefa solicitada.
                    Seja preciso e objetivo nos resultados."""
                )

                # Agente terminou de raciocinar
                if resposta.stop_reason == "end_turn":
                    resultado = next(
                        (b.text for b in resposta.content if hasattr(b, "text")), ""
                    )
                    print(f"Resultado: {resultado}")
                    break

                # Agente quer usar uma ferramenta
                if resposta.stop_reason == "tool_use":
                    uso_ferramenta = next(
                        (b for b in resposta.content if b.type == "tool_use"), None
                    )
                    if not uso_ferramenta:
                        break

                    print(f"Agente usando ferramenta: {uso_ferramenta.name}")

                    resultado_ferramenta = await sessao.call_tool(
                        uso_ferramenta.name,
                        uso_ferramenta.input
                    )

                    mensagens.extend([
                        {"role": "assistant", "content": resposta.content},
                        {
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": uso_ferramenta.id,
                                "content": resultado_ferramenta.content[0].text
                            }]
                        }
                    ])


if __name__ == "__main__":
    asyncio.run(executar_agente(
        id_entidade="12345",
        tarefa="Analise os dados desta entidade e identifique pontos de atenção."
    ))
