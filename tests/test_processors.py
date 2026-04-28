"""Testes dos processadores do Agente B3."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
import numpy as np
from datetime import date
from config.filters import FiltrosConsulta
from processors.cleaner import limpar_dados, _normalizar_tipo_lf, _normalizar_indexador
from processors.enricher import enriquecer


@pytest.fixture
def df_bruto():
    return pd.DataFrame({
        "emissor": ["Banco ABC Brasil S.A.", "Banco Pine S.A.", None, "Banco Daycoval"],
        "cnpj": ["28.195.667/0001-06", "62.144.175/0001-20", "00.000.000/0001-00", "62.232.889/0001-90"],
        "rating_agencia": ["Fitch", "Moody's", "Fitch", "Moody's"],
        "rating_nota": ["A-(bra)", "A-.br", "A(bra)", "A.br"],
        "tipo_lf": ["senior", "subordinada_t2", "LF Senior", "senior"],
        "data_emissao": ["2024-01-15", "2024-01-25", "2024-03-10", "2024-09-03"],
        "data_vencimento": ["2026-01-25", "2029-01-25", None, "2026-09-03"],
        "valor_emissao": ["600200000", "180000000", "500000000", "750000000"],
        "indexador": ["CDI", "DI", "% do CDI", "CDI+"],
        "spread_percentual": ["0.90", "1.85", "3.00", "0.85"],
        "prazo_dias": ["740", "1827", None, "731"],
        "serie": ["1ª", "75ª", "1ª", "5ª"],
        "modalidade": ["LF Sênior", "LF Sub T2", "LF AT1", "LF Sênior"],
        "fonte": ["ANBIMA", "ANBIMA", "ANBIMA", "ANBIMA"],
    })


class TestCleaner:
    def test_remove_linhas_sem_emissor(self, df_bruto):
        df = limpar_dados(df_bruto)
        assert df["emissor"].notna().all()
        assert (df["emissor"] != "").all()

    def test_normaliza_datas(self, df_bruto):
        df = limpar_dados(df_bruto)
        assert pd.api.types.is_datetime64_any_dtype(df["data_emissao"])

    def test_normaliza_valores_numericos(self, df_bruto):
        df = limpar_dados(df_bruto)
        assert pd.api.types.is_numeric_dtype(df["valor_emissao"])
        assert pd.api.types.is_numeric_dtype(df["spread_percentual"])

    def test_adiciona_rating_normalizado(self, df_bruto):
        df = limpar_dados(df_bruto)
        assert "rating_nota_normalizado" in df.columns
        # A-(bra) → A-
        row_abc = df[df["emissor"] == "Banco ABC Brasil S.A."].iloc[0]
        assert row_abc["rating_nota_normalizado"] == "A-"

    def test_normalizar_tipo_lf_senior(self):
        assert _normalizar_tipo_lf("senior") == "senior"
        assert _normalizar_tipo_lf("LF Senior") == "senior"
        assert _normalizar_tipo_lf("SÊNIOR") == "senior"

    def test_normalizar_tipo_lf_t2(self):
        assert _normalizar_tipo_lf("subordinada_t2") == "subordinada_t2"
        assert _normalizar_tipo_lf("Subordinada Nível 2") == "subordinada_t2"
        assert _normalizar_tipo_lf("T2") == "subordinada_t2"

    def test_normalizar_tipo_lf_at1(self):
        assert _normalizar_tipo_lf("subordinada_at1") == "subordinada_at1"
        assert _normalizar_tipo_lf("AT1") == "subordinada_at1"
        assert _normalizar_tipo_lf("Perpétua") == "subordinada_at1"

    def test_normalizar_indexador_cdi(self):
        assert _normalizar_indexador("CDI") == "CDI"
        assert _normalizar_indexador("DI") == "CDI"
        assert _normalizar_indexador("% do CDI") == "CDI"

    def test_normalizar_indexador_ipca(self):
        assert _normalizar_indexador("IPCA") == "IPCA"
        assert _normalizar_indexador("IPCA+") == "IPCA"

    def test_remove_duplicatas(self):
        df_dup = pd.DataFrame({
            "emissor": ["Banco X", "Banco X"],
            "cnpj": ["", ""],
            "rating_agencia": ["Fitch", "Fitch"],
            "rating_nota": ["A-", "A-"],
            "tipo_lf": ["senior", "senior"],
            "data_emissao": ["2024-01-01", "2024-01-01"],
            "data_vencimento": [None, None],
            "valor_emissao": [100e6, 100e6],
            "indexador": ["CDI", "CDI"],
            "spread_percentual": [1.0, 1.0],
            "prazo_dias": [None, None],
            "serie": ["1ª", "1ª"],
            "modalidade": ["LF", "LF"],
            "fonte": ["ANBIMA", "CVM"],
        })
        df = limpar_dados(df_dup)
        assert len(df) == 1


class TestEnricher:
    @pytest.fixture
    def df_filtrado(self):
        return pd.DataFrame({
            "emissor": ["Banco ABC", "Banco Pine", "Banco Votorantim"],
            "cnpj": ["", "", ""],
            "rating_agencia": ["Fitch", "Moody's", "Fitch"],
            "rating_nota": ["A-(bra)", "A-.br", "AA-(bra)"],
            "rating_nota_normalizado": ["A-", "A-", "AA-"],
            "tipo_lf": ["senior", "subordinada_t2", "senior"],
            "data_emissao": pd.to_datetime(["2024-01-15", "2024-01-25", "2024-08-12"]),
            "data_vencimento": pd.to_datetime(["2026-01-25", "2029-01-25", "2027-08-12"]),
            "valor_emissao": [600e6, 180e6, 1200e6],
            "indexador": ["CDI", "CDI", "IPCA"],
            "spread_percentual": [0.90, 1.85, 5.50],
            "prazo_dias": [740, 1827, 1096],
            "serie": ["1ª", "75ª", "8ª"],
            "modalidade": ["LF Sênior", "LF Sub T2", "LF Sênior IPCA"],
            "fonte": ["ANBIMA", "ANBIMA", "ANBIMA"],
        })

    def test_adiciona_prazo_label(self, df_filtrado):
        f = FiltrosConsulta()
        df = enriquecer(df_filtrado, f)
        assert "prazo_label" in df.columns
        assert df["prazo_label"].notna().all()

    def test_adiciona_retorno_estimado(self, df_filtrado):
        f = FiltrosConsulta()
        df = enriquecer(df_filtrado, f)
        assert "retorno_estimado_aa" in df.columns

    def test_adiciona_classificacao_spread(self, df_filtrado):
        f = FiltrosConsulta()
        df = enriquecer(df_filtrado, f)
        assert "classificacao_spread" in df.columns
        valores_validos = {"Abaixo do mercado", "Na média", "Acima do mercado"}
        for v in df["classificacao_spread"]:
            assert v in valores_validos

    def test_adiciona_label_tipo_lf(self, df_filtrado):
        f = FiltrosConsulta()
        df = enriquecer(df_filtrado, f)
        assert "label_tipo_lf" in df.columns
        assert "Sênior" in df["label_tipo_lf"].iloc[0]

    def test_retorno_cdi_soma_spread(self, df_filtrado):
        f = FiltrosConsulta()
        cdi_ref = 10.50
        df = enriquecer(df_filtrado, f, cdi_referencia=cdi_ref)
        # Banco ABC: CDI + 0.90% → retorno = 10.50 + 0.90 = 11.40
        row_abc = df[df["emissor"] == "Banco ABC"].iloc[0]
        assert abs(row_abc["retorno_estimado_aa"] - 11.40) < 0.01

    def test_status_vencimento_vigente(self, df_filtrado):
        f = FiltrosConsulta()
        df = enriquecer(df_filtrado, f)
        assert "status_vencimento" in df.columns
        for _, row in df.iterrows():
            assert row["status_vencimento"] in ("Vigente", "Vencida", "Perpétua")
