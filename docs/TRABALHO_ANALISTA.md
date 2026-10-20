# Onde entra o trabalho de analista de dados?

Python é a ferramenta. O trabalho de análise está nas escolhas e na interpretação.

| Etapa | Decisão neste projeto | O que explicar |
|---|---|---|
| Formular a pergunta | Comparar comportamento histórico de três ativos | O estudo não escolhe uma carteira ideal |
| Definir o recorte | Ativos e período comuns | Seleção e período influenciam os resultados |
| Avaliar a fonte | Yahoo Finance via yfinance | Dados podem conter erros e ajustes posteriores |
| Conferir qualidade | Verificar datas, duplicatas, preços e ausências | Uma data foi excluída; nenhum preço foi inventado |
| Preparar comparação | Base de R$ 1.000 por ativo | Preço unitário diferente não significa desempenho melhor |
| Escolher métricas | Crescimento, volatilidade, drawdown e correlação | Retorno final sozinho não descreve o caminho |
| Interpretar | Comparar crescimento com oscilações e quedas | Maior retorno passado não implica melhor escolha futura |
| Comunicar | Gráficos, tabelas, README e limitações | Distinguir fatos observados de hipóteses |
| Validar | Exemplos conhecidos e testes | Um gráfico bonito não prova que o cálculo está certo |

## Exercício para Wandley
Compare as métricas locais de PETR4 e BOVA11. Responda: qual teve maior retorno acumulado? Qual teve maior volatilidade e maior queda? Por que uma conclusão baseada apenas no valor final seria incompleta?

Exemplo artificial: 100 → 120 → 90 representa retorno final de −10%, mas queda de −25% desde o pico. São perguntas diferentes respondidas por métricas diferentes.

## Transparência em entrevistas
Você pode dizer que está desenvolvendo o projeto com assistência de IA e estudando as decisões. Só declare domínio das etapas que consegue explicar. Ainda não há experiência profissional ou impacto comercial demonstrado por este projeto.
