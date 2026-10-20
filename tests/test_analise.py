"""Exemplos artificiais identificados; nunca usados como dados de mercado."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from analise import calcular_metricas, extrair_fechamento, baixar_precos

class Formulas(unittest.TestCase):
    def test_exemplo_conhecido(self):
        datas = pd.to_datetime(["2020-01-01","2020-07-01","2021-01-01"])
        p = pd.DataFrame({"A":[100.,120.,90.],"B":[100.,110.,121.]},index=datas)
        r = p.pct_change(fill_method=None).dropna()
        m,e,d,c = calcular_metricas(p,r,dict(capital=1000,pregoes_ano=252))
        self.assertAlmostEqual(e.iloc[-1]["A"],900)
        self.assertAlmostEqual(m.loc["A","retorno_acumulado"],-.1)
        self.assertAlmostEqual(m.loc["A","max_drawdown"],-.25)
        self.assertAlmostEqual(m.loc["A","cagr"],.9**(365.2425/366)-1)
        self.assertAlmostEqual(m.loc["A","volatilidade_anual"],np.std([.2,-.25],ddof=1)*np.sqrt(252))
        self.assertAlmostEqual(c.loc["A","A"],1)
        self.assertAlmostEqual(m.loc["B","retorno_acumulado"],.21)

    def test_colunas(self):
        for colunas in [["Close"],pd.MultiIndex.from_tuples([("Close","A")]),pd.MultiIndex.from_tuples([("A","Close")])]:
            self.assertEqual(extrair_fechamento(pd.DataFrame([[10]],columns=colunas),"A").iloc[0],10)
        with self.assertRaises(ValueError):
            extrair_fechamento(pd.DataFrame(),"A")

    @patch("analise.yf.download")
    def test_lacuna_nao_fabrica_retorno_diario(self,download):
        datas = pd.bdate_range("2020-01-01",periods=7)
        a=pd.DataFrame({"Close":[10.,11.,np.nan,12.,13.,14.,15.]},index=datas)
        b=pd.DataFrame({"Close":[20.,21.,22.,23.,24.,25.,26.]},index=datas)
        download.side_effect=[a,b]
        p,r,params,q=baixar_precos(dict(ativos=["A","B"],inicio="2020-01-01",fim="2020-01-31"))
        self.assertEqual(len(p),6)
        self.assertEqual(len(r),4)
        self.assertNotIn(datas[3],r.index)
        self.assertEqual(q["datas_descartadas_alinhamento"],1)
        self.assertEqual(params["end"],"2020-02-01")

    @patch("analise.yf.download")
    def test_recusa_duplicatas_e_precos_invalidos(self,download):
        for indice,valores in [(["2020-01-01"]*3,[1.,2.,3.]),
            (["2020-01-01","2020-01-02","2020-01-03"],[1.,0.,3.])]:
            download.return_value=pd.DataFrame({"Close":valores},index=pd.to_datetime(indice))
            with self.assertRaises(ValueError):
                baixar_precos(dict(ativos=["A"],inicio="2020-01-01",fim="2020-01-31"))

if __name__ == "__main__":
    unittest.main()
