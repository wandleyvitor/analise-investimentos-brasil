# Primeira etapa: entender a base de R$ 1.000

Abra src/analise.py e procure CONFIG e calcular_metricas.

1. Identifique os três ativos, as duas datas e o capital inicial.
2. Leia a linha evolucao = capital × precos / primeiro_preco (o código usa config e iloc[0]).
3. No papel ou no Excel, use preços 100, 120 e 90: os valores devem ser 1.000, 1.200 e 900.
4. Explique com suas palavras por que o retorno final é −10%, mas a queda do pico de 1.200 para 900 é −25%.

Frase para treinar: “Coloquei cada série na mesma base inicial para comparar a evolução proporcional, sem confundir preço unitário com desempenho.”

Este exemplo é artificial e não usa dados dos ativos. Não avance para conclusões de mercado antes de executar e validar a coleta.
