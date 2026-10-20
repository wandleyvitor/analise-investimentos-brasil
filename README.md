# Análise de Investimentos Brasileiros com Python

Projeto educacional de portfólio de **Wandley Vitor**, em desenvolvimento com assistência de IA.

## Pergunta
Como se comportaram os preços ajustados de PETR4, VALE3 e BOVA11 entre 01/01/2020 e 31/12/2025, em termos de crescimento, oscilações, quedas e correlação?

PETR4.SA e VALE3.SA são ações. BOVA11.SA é um ETF de ações brasileiras: pode conter as próprias empresas analisadas, portanto há possível sobreposição. São exemplos de estudo, sem indicação de compra. Esta seleção pequena não representa uma análise completa do mercado brasileiro nem uma carteira ideal.

## Estado real — 20/10/2026

Fluxo completo executado com dados reais; quatro testes passaram. Foram gerados três PNG e seis CSV em outputs/20261020T113818299454Z. O gráfico de evolução foi inspecionado visualmente. A primeira tentativa falhou por conexão; a segunda terminou após autorização de rede.

Período observado: 02/01/2020 a 30/12/2025. Foram recebidas 1.494 datas na união; 1.493 preços comuns e 1.491 retornos diários comuns foram usados. Uma data foi excluída por ausência no BOVA11, sem preenchimento. Sem duplicatas detectadas.

Os resultados numéricos completos, preços e gráficos permanecem locais enquanto a revisão das condições de redistribuição da fonte estiver pendente. Este repositório publica código, metodologia e evidências de execução, sem redistribuir as séries históricas.

Versões utilizadas: Python 3.14.2, yfinance 1.7.0, pandas 3.0.6, numpy 2.5.4 e matplotlib 3.11.2. As dependências exatas estão em requirements-lock.txt.

## Estrutura

    requirements.txt           intervalos de versões aceitos
    src/analise.py             configuração e funções do fluxo
    tests/test_analise.py      exemplos pequenos e casos de erro
    data/README.md            regras para dados locais
    outputs/<execução>/
      execucao.json           fonte, coleta UTC, parâmetros, versões e auditoria
      tabelas/                CSV para análise local e Power BI
      graficos/               PNG
    docs/ESTUDO.md             primeira etapa de aprendizagem
    docs/TRABALHO_ANALISTA.md  decisões de análise presentes no projeto

Cada execução recebe uma pasta própria para preservar o histórico. Os resultados anteriores não são apresentados como novos em caso de falha.

## Instalar e executar no Windows / PowerShell
Abra o PowerShell na pasta deste README. Requer Python instalado, acesso ao PyPI para instalação e ao Yahoo Finance para coleta.

~~~powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe src\analise.py
~~~

Não é necessário ativar o ambiente nem mudar a política de execução do PowerShell. Não há instalação global, senha ou serviço pago.
Depois de uma execução bem-sucedida, registre o ambiente exato:

~~~powershell
.\.venv\Scripts\python.exe -m pip freeze | Set-Content -Encoding utf8 requirements-lock.txt
~~~

Para reproduzir esse ambiente depois, instale com -r requirements-lock.txt. O ambiente registrado foi utilizado na execução e nos testes de 20/10/2026.

## Fonte, período e ajustes
Fonte: Yahoo Finance, acessada com yfinance. A documentação foi consultada em 19/10/2026. Em download, start é inclusivo e end é exclusivo. Portanto o código pede start=2020-01-01 e end=2026-01-01. Os limites são civis; o primeiro e o último preço serão os pregões disponíveis, não necessariamente essas datas.

O código usa explicitamente auto_adjust=True, back_adjust=False, repair=False e actions=True. O Close recebido é ajustado pelo yfinance com base nos ajustes fornecidos pelo Yahoo. Dividendos e desdobramentos podem afetar esses ajustes; os eventos são solicitados, mas não são somados aos retornos. Somá-los de novo poderia contar o efeito duas vezes. Outros eventos corporativos dependem da cobertura e do tratamento da fonte. A série ajustada é uma aproximação fornecida pelo provedor, sujeita a revisões e erros, não uma reconstrução auditada de todos os fluxos de caixa de um investidor.

Os resultados serão descritos como **retornos baseados em preços ajustados da fonte**, sem promessa de correspondência exata com o retorno líquido realizável. O investimento hipotético usa frações teóricas de cotas/ações, sem aportes ou regras de lote.

## Qualidade e alinhamento
O download é individual por ativo para identificar falhas. O extrator aceita colunas simples e MultiIndex nos dois sentidos. Download vazio, menos de três preços, datas inválidas ou duplicadas, preços não positivos ou infinitos interrompem o fluxo. Valores ausentes são contabilizados, nunca preenchidos.

As séries são alinhadas por datas comuns válidas. O registro informa a união das datas, datas comuns, descartes totais e, por ativo, ausências e preços válidos excluídos. Não há calendário oficial de pregões nesta versão: um dia ausente em todas as séries pode passar despercebido. Verifique cobertura e lacunas antes de interpretar resultados.

Os retornos diários são calculados na união das datas, antes de remover lacunas, com pct_change(fill_method=None). Só depois são retidos retornos válidos para todos os ativos. Assim, uma falha intermediária não vira automaticamente retorno de vários pregões chamado de diário. O total de retornos pode ser menor que o total de preços comuns menos um. Se todas as fontes omitirem o mesmo pregão, essa proteção não detectará a lacuna.

Crescimento e drawdown usam preços nas datas comuns. Uma data excluída pode conter um pico ou uma queda; a estimativa de drawdown pode assim ser afetada. Estatísticas usam o mesmo recorte para comparação e não significam risco futuro.

## Métricas em linguagem simples
Considere P0 como primeiro preço comum válido, Pt como preço na data e Pf como último preço.

| Medida | Cálculo e interpretação |
|---|---|
| Evolução de R$ 1.000 | 1000 × Pt/P0: comparação numa mesma base inicial |
| Retorno acumulado | Pf/P0 − 1: mudança entre o início e o fim |
| CAGR | (Pf/P0)^(1/anos) − 1: taxa composta equivalente por ano; anos = dias corridos efetivamente observados / 365,2425 |
| Retorno diário | Pt/Panterior − 1, sem preencher preços ausentes |
| Volatilidade anualizada | Desvio padrão amostral dos retornos diários (ddof=1) × raiz de 252; é uma convenção, não uma previsão |
| Maximum drawdown | Mínimo de Pt/máximo(P0...Pt) − 1; número negativo, queda a partir do pico observado |
| Correlação | Pearson entre retornos diários comuns; varia de −1 a 1, sem implicar causalidade |

Exemplos artificiais, apenas para conferir fórmulas: preços 100 → 120 → 90 produzem valor final de R$ 900, retorno de −10% e drawdown máximo de −25%. O CAGR considera os dias reais entre as datas. Esses exemplos não são resultados da B3. Há testes para as fórmulas, colunas, lacunas, preços inválidos e duplicatas; os quatro testes passaram em 20/10/2026.

## CSV e Power BI
Arquivos UTF-8 com BOM, vírgula como separador e ponto decimal. No Power BI use Obter dados > Texto/CSV, tipo Data para data e número decimal com localidade compatível (por exemplo, inglês dos EUA) para medidas numéricas. Taxas são frações: 0,10 equivale a 10%; formate-as como porcentagem.

- metricas.csv: uma linha por ativo com retorno, CAGR, volatilidade, drawdown e período efetivo.
- precos.csv, retornos.csv, evolucao.csv e drawdown.csv: formato longo, uma linha por data e ativo.
- correlacao.csv: uma linha por par de ativos, coeficiente sem unidade.

## Limitações e uso dos dados
Resultados nominais em reais, sem descontar inflação, impostos ou custos. Não há renda fixa, FIIs, criptoativos, otimização ou Monte Carlo. A escolha atual de ativos pode introduzir viés de seleção e sobrevivência. Desempenho histórico não garante desempenho futuro.

O yfinance não é um produto oficial do Yahoo e declara uso de pesquisa/educação e uso pessoal dos dados da API. A consulta direta aos termos do Yahoo retornou erro HTTP 999 neste ambiente; **a revisão integral das condições permanece pendente**. Não se presume que os dados sejam livres para redistribuição. Dados, CSV e imagens gerados ficam locais e são ignorados no Git. Antes de compartilhar dados ou gráficos derivados, confira termos do Yahoo e direitos de terceiros; o projeto não concede licença sobre esses dados.

Referências consultadas:
- https://ranaroussi.github.io/yfinance/ (aviso sobre fonte e uso)
- https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html
- https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pct_change.html
- https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.std.html
- https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.corr.html
- https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html
- https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html (acesso bloqueado)
- https://legal.yahoo.com/us/en/yahoo/terms/product-atos/finance/index.html (acesso bloqueado)

## Autoria e aprendizagem
Wandley Vitor definiu o objetivo do portfólio e está estudando análise de dados, com maior familiaridade com Excel e conhecimentos básicos de Python, SQL e Power BI. A primeira implementação e a documentação foram preparadas com assistência de IA. Revisar, executar, interpretar e conseguir explicar as escolhas faz parte do trabalho ainda em andamento. Este repositório não afirma experiência profissional nem domínio de etapas que Wandley ainda não estudou.

## O trabalho de análise de dados
Consulte [Onde entra o analista](docs/TRABALHO_ANALISTA.md) para relacionar a pergunta, a qualidade dos dados, os cálculos e a interpretação. O código automatiza as contas; a análise exige justificar as escolhas e comunicar limites.

## Próximos passos
1. Estudar e explicar cada etapa do código.
2. Investigar a data ausente e comparar com um calendário de pregões.
3. Estudar a importação das tabelas no Power BI.
4. Revisar as condições da fonte antes de divulgar dados ou gráficos derivados.

Projeto educacional em desenvolvimento. Nenhuma publicação em redes sociais foi realizada.
