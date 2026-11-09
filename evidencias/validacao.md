# Validação do agente com Gemini e Trello

Teste com **Gemini 3.1 Flash-Lite**, **Google ADK** e um quadro real do Trello com cards fictícios. O teste executou o agente por meio do `InMemoryRunner` do ADK. O quadro de laboratório tem as listas A fazer, Em andamento e Concluído.

| Etapa | Ferramenta chamada pelo agente | Resultado observado |
| --- | --- | --- |
| Apresentar o plano para criar um card com vencimento hoje | `data_de_hoje` | O agente consultou a data e respondeu antes de escrever no quadro. |
| Confirmar a criação | `criar_tarefa` | O card **Validação Gemini DIO** apareceu em A fazer no Trello. |
| Localizar o card para propor a movimentação | `listar_tarefas` | O agente consultou os cards e respondeu antes da confirmação de movimentação. |
| Confirmar a movimentação | `mover_tarefa` | O agente respondeu após chamar a ferramenta. A presença do card em Concluído foi verificada com uma consulta independente ao Trello. |

Os cinco testes automatizados da camada de ferramentas também passaram. O registro contém apenas informações do card fictício e das ferramentas acionadas.
