"""Testes dos extratores do Agente B3."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from config.filters import FiltrosConsulta
from extractors.anbima import AnbimaExtractor
from extractors.cvm import CVMExtractor
from extractors.bacen import BacenExtractor
from extractors.b3_rjlf import B3RjlfExtractor
from extractors.base import COLUNAS_PADRAO


@pytest.fixture
def filtros_padrao():
    return FiltrosConsulta(
        rating_minimo="BBB-",
        rating_maximo="AAA",
        periodo_meses=24,
    )


class TestAnbimaExtractor:
    def test_retorna_dataframe(self, filtros_padrao):
        ext = AnbimaExtractor()
        df = ext.extract(filtros_padrao)
        assert isinstance(df, pd.DataFrame)

    def test_tem_colunas_padrao(self, filtros_padrao):
        ext = AnbimaExtractor()
        df = ext.extract(filtros_padrao)
        for col in COLUNAS_PADRAO:
            assert col in df.columns, f"Coluna ausente: {col}"

    def test_source_name(self):
        ext = AnbimaExtractor()
        assert "ANBIMA" in ext.source_name

    def test_mock_retorna_emissores_conhecidos(self, filtros_padrao):
        ext = AnbimaExtractor()
        df = ext.extract(filtros_padrao)
        emissores = set(df["emissor"].tolist())
        # Com período de 24 meses, deve incluir os emissores mock
        assert len(emissores) > 0

    def test_periodo_curto_pode_retornar_vazio(self):
        # Período muito no futuro — nenhum dado mock deve estar dentro
        filtros_futuro = FiltrosConsulta(
            data_inicio="2030-01-01",
            data_fim="2030-06-01",
        )
        ext = AnbimaExtractor()
        df = ext.extract(filtros_futuro)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


class TestCVMExtractor:
    def test_retorna_dataframe(self, filtros_padrao):
        ext = CVMExtractor()
        df = ext.extract(filtros_padrao)
        assert isinstance(df, pd.DataFrame)

    def test_source_name(self):
        ext = CVMExtractor()
        assert "CVM" in ext.source_name

    def test_tem_colunas_padrao(self, filtros_padrao):
        ext = CVMExtractor()
        df = ext.extract(filtros_padrao)
        for col in COLUNAS_PADRAO:
            assert col in df.columns, f"Coluna ausente: {col}"


class TestBacenExtractor:
    def test_retorna_dataframe(self, filtros_padrao):
        ext = BacenExtractor()
        df = ext.extract(filtros_padrao)
        assert isinstance(df, pd.DataFrame)

    def test_source_name(self):
        ext = BacenExtractor()
        assert "BACEN" in ext.source_name


class TestB3RjlfExtractor:
    def test_retorna_dataframe_vazio(self, filtros_padrao):
        ext = B3RjlfExtractor()
        df = ext.extract(filtros_padrao)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_source_name(self):
        ext = B3RjlfExtractor()
        assert "B3" in ext.source_name
