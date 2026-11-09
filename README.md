# Organizador de tarefas no Trello com Gemini

Desafio **Criando um Agente para Automatizar um Fluxo de Trabalho em Python** da DIO. Usa Google ADK, Gemini e py-trello para planejar o dia e organizar um quadro.

Referência do desafio: [agent04 da DIO](https://github.com/digitalinnovationone/agent-carbon-footprint/tree/main/agents/agent04).

| Ferramenta | Ação |
| --- | --- |
| `data_de_hoje` | Consulta a data no fuso de São Paulo. |
| `criar_tarefa` | Cria o card na lista A fazer com nome, descrição e vencimento. |
| `listar_tarefas` | Lê cards abertos, com opção de filtrar por status. |
| `mover_tarefa` | Move pelo ID conferido no quadro configurado. |

## Configurar

1. Crie um quadro de teste com as listas **A fazer**, **Em andamento** e **Concluído**.
2. Configure a chave e um token do Trello com acesso ao quadro. Copie o ID ou identificador do quadro para `TRELLO_BOARD_ID`.
3. Configure uma chave do Google AI Studio. Preencha o arquivo local `.env` a partir do [.env.exemplo](.env.exemplo). O arquivo com os segredos é ignorado pelo Git.
4. Use Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.exemplo .env
adk web
```

Depois de copiar o arquivo, preencha as chaves antes de iniciar o ADK. No Windows PowerShell, use `.venv\Scripts\Activate.ps1` e `Copy-Item .env.exemplo .env`.

## Melhorias e testes

As ferramentas aceitam acentos e sinônimos de status, convertem o vencimento do meio-dia em São Paulo para UTC e identificam cards pelo ID. O agente solicita confirmação antes de escrever e mantém a mensagem de erro livre de tokens.

```bash
python -m unittest discover -s tests -v
```

Os cinco testes locais usam um quadro simulado e cobrem criação, filtro, movimentação, validação e tratamento de erro. A integração também foi validada com Gemini 3.1 Flash-Lite, Google ADK e um quadro real do Trello. Veja o [registro da validação](evidencias/validacao.md).

Para reproduzir o fluxo, peça um card fictício no ADK, confirme a criação, liste o quadro, mova o card para Concluído e confira as duas interfaces. Use um quadro de laboratório para a demonstração.

- [Configuração do ADK](https://adk.dev/get-started/python/)
- [Configuração da API do Trello](https://support.atlassian.com/trello/docs/getting-started-with-trello-rest-api/)
