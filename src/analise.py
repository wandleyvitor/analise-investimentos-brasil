"""Estudo educacional: preços ajustados, sem recomendação de investimento."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.metadata
import json
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yfinance as yf

# Altere ativos, datas e capital somente aqui. A data final abaixo é inclusiva.
CONFIG = dict(ativos=["PETR4.SA", "VALE3.SA", "BOVA11.SA"],
              inicio="2020-01-01", fim="2025-12-31", capital=1000.0,
              pregoes_ano=252)
RAIZ = Path(__file__).resolve().parents[1]


def extrair_fechamento(dados, ativo):
    """Aceita colunas simples ou MultiIndex em qualquer ordem de níveis."""
    if dados is None or dados.empty:
        raise ValueError(f"Download vazio para {ativo}.")
    if isinstance(dados.columns, pd.MultiIndex):
        candidatas = [c for c in dados.columns if "Close" in c and ativo in c]
        if len(candidatas) != 1:
            raise ValueError(f"Colunas inesperadas para {ativo}: {dados.columns}")
        serie = dados[candidatas[0]]
    else:
        if "Close" not in dados.columns:
            raise ValueError(f"Close ausente para {ativo}.")
        serie = dados["Close"]
    return pd.to_numeric(serie, errors="raise").rename(ativo)


def baixar_precos(config):
    fim_exclusivo = (pd.Timestamp(config["fim"]) + pd.Timedelta(days=1)).date().isoformat()
    parametros = dict(start=config["inicio"], end=fim_exclusivo, interval="1d",
        auto_adjust=True, back_adjust=False, repair=False, actions=True,
        keepna=True, progress=False, threads=False, ignore_tz=True,
        group_by="column", multi_level_index=True, rounding=False, timeout=30)
    series, auditoria = [], []
    for ativo in config["ativos"]:
        dados = yf.download(ativo, **parametros)
        serie = extrair_fechamento(dados, ativo)
        serie.index = pd.to_datetime(serie.index, errors="raise")
        if serie.index.tz is not None:
            serie.index = serie.index.tz_localize(None)
        serie.index = serie.index.normalize()
        if serie.index.hasnans or serie.index.has_duplicates:
            raise ValueError(f"Datas inválidas ou duplicadas em {ativo}; investigar a fonte.")
        if ((serie.index < config["inicio"]) | (serie.index > config["fim"])).any():
            raise ValueError(f"Datas fora do período em {ativo}.")
        if np.isinf(serie.to_numpy()).any() or (serie.dropna() <= 0).any():
            raise ValueError(f"Preços não positivos ou infinitos em {ativo}.")
        if serie.notna().sum() < 3:
            raise ValueError(f"Dados insuficientes em {ativo}.")
        auditoria.append(dict(ativo=ativo, linhas_recebidas=len(serie),
            ausentes_na_fonte=int(serie.isna().sum()), duplicatas=0,
            primeiro_preco_valido=str(serie.dropna().index.min().date()),
            ultimo_preco_valido=str(serie.dropna().index.max().date())))
        series.append(serie.sort_index())
    uniao = pd.concat(series, axis=1).sort_index()
    comuns = uniao.dropna(how="any")  # Não preenche preços ausentes.
    if len(comuns) < 3:
        raise ValueError("Menos de três datas comuns válidas.")
    for linha in auditoria:
        linha["ausentes_na_uniao"] = int(uniao[linha["ativo"]].isna().sum())
        linha["validas_descartadas_alinhamento"] = int(uniao[linha["ativo"]].notna().sum()-len(comuns))
    # Retornos são calculados ANTES da exclusão de datas. Assim uma lacuna
    # não vira um retorno de vários pregões rotulado como diário.
    retornos = uniao.pct_change(fill_method=None).dropna(how="any")
    if len(retornos) < 2:
        raise ValueError("Retornos diários comuns insuficientes.")
    qualidade = dict(datas_uniao=len(uniao), datas_comuns=len(comuns),
        datas_descartadas_alinhamento=len(uniao)-len(comuns),
        retornos_diarios_comuns=len(retornos),
        linhas_sem_retorno_comum=len(uniao)-len(retornos), por_ativo=auditoria)
    return comuns, retornos, parametros, qualidade


def calcular_metricas(precos, retornos, config):
    anos = (precos.index[-1]-precos.index[0]).days / 365.2425
    if anos <= 0:
        raise ValueError("Período observado deve ser positivo.")
    fator = precos.iloc[-1] / precos.iloc[0]
    evolucao = config["capital"] * precos / precos.iloc[0]
    drawdown = precos / precos.cummax() - 1
    metricas = pd.DataFrame(dict(valor_final_brl=evolucao.iloc[-1],
        retorno_acumulado=fator-1, cagr=fator**(1/anos)-1,
        volatilidade_anual=retornos.std(ddof=1)*np.sqrt(config["pregoes_ano"]),
        max_drawdown=drawdown.min()))
    metricas.index.name = "ativo"
    metricas["inicio_observado"] = precos.index[0].date().isoformat()
    metricas["fim_observado"] = precos.index[-1].date().isoformat()
    metricas["anos_observados"] = anos
    metricas["n_precos"] = len(precos)
    metricas["n_retornos_diarios"] = len(retornos)
    return metricas, evolucao, drawdown, retornos.corr(method="pearson")


def salvar_csv(tabela, caminho):
    tabela.to_csv(caminho, index=False, encoding="utf-8-sig", float_format="%.10f")


def formato_longo(tabela, valor):
    return tabela.rename_axis("data").reset_index().melt(
        id_vars="data", var_name="ativo", value_name=valor)


def salvar_graficos(evolucao, drawdown, correlacao, destino):
    periodo = f"{evolucao.index[0]:%d/%m/%Y} a {evolucao.index[-1]:%d/%m/%Y}"
    rodape = "Fonte: Yahoo Finance via yfinance | preços ajustados | estudo educacional"
    for tabela, titulo, unidade, nome, escala in [
        (evolucao, "Evolução hipotética de R$ 1.000 por ativo", "Valor nominal (R$)", "evolucao", 1),
        (drawdown, "Queda em relação ao pico observado", "Drawdown (%)", "drawdown", 100)]:
        fig, ax = plt.subplots(figsize=(11,6))
        (tabela*escala).plot(ax=ax, linewidth=1.5)
        ax.set(title=titulo+"\n"+periodo, xlabel="Data", ylabel=unidade)
        ax.grid(alpha=.25)
        fig.text(.08,.02,rodape,fontsize=9)
        fig.tight_layout(rect=(0,.05,1,1))
        fig.savefig(destino/f"{nome}.png",dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(7,6))
    imagem = ax.imshow(correlacao,vmin=-1,vmax=1,cmap="RdBu_r")
    ax.set_xticks(range(len(correlacao)),correlacao.columns)
    ax.set_yticks(range(len(correlacao)),correlacao.index)
    for i in range(len(correlacao)):
        for j in range(len(correlacao)):
            ax.text(j,i,f"{correlacao.iloc[i,j]:.2f}",ha="center",va="center")
    ax.set_title("Correlação de Pearson dos retornos diários\n"+periodo)
    fig.colorbar(imagem,ax=ax,label="Coeficiente (sem unidade)")
    fig.text(.04,.02,rodape,fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1))
    fig.savefig(destino/"correlacao.png",dpi=160)
    plt.close(fig)


def main():
    # Cada tentativa tem pasta própria: uma falha não deixa resultados antigos
    # parecendo novos, e nenhuma execução sobrescreve a anterior.
    agora = datetime.now(timezone.utc)
    destino = RAIZ/"outputs"/agora.strftime("%Y%m%dT%H%M%S%fZ")
    destino.mkdir(parents=True)
    registro = dict(status="iniciada", coleta_utc=agora.isoformat(),
        fonte="Yahoo Finance via yfinance", config=CONFIG,
        python=sys.version, versoes={p:importlib.metadata.version(p)
            for p in ["yfinance","pandas","numpy","matplotlib"]})
    try:
        yf.set_tz_cache_location(str(RAIZ/"data"/"cache"))
        precos, retornos, parametros, qualidade = baixar_precos(CONFIG)
        registro.update(parametros_download=parametros, qualidade=qualidade)
        metricas, evolucao, drawdown, corr = calcular_metricas(precos,retornos,CONFIG)
        tabelas, graficos = destino/"tabelas", destino/"graficos"
        tabelas.mkdir(); graficos.mkdir()
        salvar_csv(metricas.reset_index(),tabelas/"metricas.csv")
        for tabela,nome,coluna in [(precos,"precos","preco_ajustado_brl"),
            (retornos,"retornos","retorno_diario"),(evolucao,"evolucao","valor_brl"),
            (drawdown,"drawdown","drawdown")]:
            salvar_csv(formato_longo(tabela,coluna),tabelas/f"{nome}.csv")
        salvar_csv(corr.rename_axis("ativo").reset_index().melt(
            id_vars="ativo",var_name="outro_ativo",value_name="correlacao"),tabelas/"correlacao.csv")
        salvar_graficos(evolucao,drawdown,corr,graficos)
        registro["status"] = "concluida"
        print(metricas.to_string())
        print(f"Resultados: {destino}")
    except Exception as erro:
        registro.update(status="falhou",erro=f"{type(erro).__name__}: {erro}")
        raise
    finally:
        (destino/"execucao.json").write_text(json.dumps(registro,indent=2,ensure_ascii=False),encoding="utf-8")


if __name__ == "__main__":
    main()
