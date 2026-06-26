# Decisões Arquiteturais — MCP Server Template

## Contexto

Este projeto nasceu da necessidade de conectar agentes de IA autônomos a sistemas legados de forma resiliente. O desafio central era: como garantir que um agente opere de forma estável quando o sistema externo é instável?

## O padrão MCP Server como camada de integração

### Problema
Agentes de IA que consomem APIs externas diretamente apresentam comportamento imprevisível quando:
- A API retorna dados em formato inesperado
- Campos obrigatórios chegam vazios ou nulos
- O sistema externo está lento ou indisponível
- O esquema da API muda sem aviso

### Solução
Introduzir um MCP Server como camada intermediária que:
1. **Abstrai a complexidade** do sistema externo
2. **Normaliza os dados** antes de entregar ao agente
3. **Trata falhas** de forma controlada e previsível
4. **Desacopla** o agente do sistema externo

## Fluxo de dados

```
Agente
  └── chama ferramenta via MCP
        └── MCP Server recebe a chamada
              └── consulta sistema externo (API REST / BD / ERP)
                    └── normaliza e valida os dados
                          └── retorna ao agente no formato esperado
```

## Princípios de design

### 1. Contrato estável para o agente
O agente sempre recebe dados no mesmo esquema, independente do que o sistema externo retorna. Toda variação é absorvida na camada de normalização.

### 2. Falha controlada
Erros são capturados, registrados com contexto e retornados ao agente como mensagens estruturadas. O agente pode decidir o que fazer com o erro em vez de simplesmente parar.

### 3. Configuração via variáveis de ambiente
Nenhuma credencial no código. Toda configuração sensível via `.env`, com `.env.exemplo` documentando o que é necessário.

### 4. Testabilidade
A função `_resposta_mock` permite rodar o servidor localmente sem conexão com o sistema externo, facilitando desenvolvimento e testes.

## Evolução futura

- [ ] Adicionar cache para reduzir chamadas repetitivas à API
- [ ] Implementar nova tentativa com espera exponencial
- [ ] Adicionar métricas de latência por ferramenta
- [ ] Suporte a múltiplos sistemas externos no mesmo servidor
