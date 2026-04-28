"""Testes do motor de filtros dinâmicos do Agente B3."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from datetime import date
from config.filters import (
    FiltrosConsulta,
    normalizar_rating,
    rating_no_intervalo,
    ESCALA_RATINGS,
)
from processors.filter_engine import aplicar_filtros


class TestNormalizarRating:
    def test_rating_padrao(self):
        assert normalizar_rating("A-") == "A-"

    def test_rating_fitch(self):
        assert normalizar_rating("A-(bra)") == "A-"

    def test_rating_sp(self):
        assert normalizar_rating("brA-") == "A-"

    def test_rating_moodys(self):
        assert normalizar_rating("A-.br") == "A-"

    def test_rating_moodys_a(self):
        assert normalizar_rating("A.br") == "A"

    def test_rating_fitch_aa(self):
        assert normalizar_rating("AA(bra)") == "AA"

    def test_rating_fitch_bbb_mais(self):
        assert normalizar_rating("BBB+(bra)") == "BBB+"

    def test_rating_invalido(self):
        assert normalizar_rating("XYZ") is None

    def test_rating_vazio(self):
        assert normalizar_rating("") is None

    def test_rating_aaa(self):
        assert normalizar_rating("AAA(bra)") == "AAA"

    def test_rating_sp_aa_menos(self):
        assert normalizar_rating("brAA-") == "AA-"


class TestRatingNoIntervalo:
    def test_rating_exato(self):
        assert rating_no_intervalo("A-", "A-", "A-") is True

    def test_rating_dentro_faixa(self):
        assert rating_no_intervalo("A", "A-", "A+") is True

    def test_rating_abaixo_faixa(self):
        assert rating_no_intervalo("BBB+", "A-", "A+") is False

    def test_rating_acima_faixa(self):
        assert rating_no_intervalo("AA", "A-", "A+") is False

    def test_faixa_ampla(self):
        assert rating_no_intervalo("A-", "BBB-", "AAA") is True

    def test_extremo_inferior(self):
        assert rating_no_intervalo("BBB-", "BBB-", "BBB-") is True

    def test_extremo_superior(self):
        assert rating_no_intervalo("AAA", "AAA", "AAA") is True

    def test_rating_invalido_no_intervalo(self):
        assert rating_no_intervalo("XYZ", "A-", "A+") is False

    def test_bbb_mais_fora_de_a_menos(self):
        assert rating_no_intervalo("BBB+", "A-", "A-") is False


class TestFiltrosConsulta:
    def test_validacao_ok(self):
        f = FiltrosConsulta(rating_minimo="A-", rating_maximo="A+")
        assert f.validar() == []

    def test_validacao_rating_invertido(self):
        f = FiltrosConsulta(rating_minimo="A+", rating_maximo="A-")
        erros = f.validar()
        assert len(erros) > 0

    def test_validacao_nenhum_tipo(self):
        f = FiltrosConsulta(
            incluir_senior=False,
            incluir_subordinada_t2=False,
            incluir_subordinada_at1=False,
        )
        erros = f.validar()
        assert len(erros) > 0

    def test_validacao_valor_invertido(self):
        f = FiltrosConsulta(valor_minimo=1_000_000.0, valor_maximo=500_000.0)
        erros = f.validar()
        assert len(erros) > 0

    def test_validacao_spread_invertido(self):
        f = FiltrosConsulta(spread_minimo=2.0, spread_maximo=1.0)
        erros = f.validar()
        assert len(erros) > 0

    def test_validacao_indexador_invalido(self):
        f = FiltrosConsulta(indexador="selic")
        erros = f.validar()
        assert len(erros) > 0

    def test_serializar_deserializar(self):
        f = FiltrosConsulta(rating_minimo="BBB+", rating_maximo="A", periodo_meses=6)
        d = f.to_dict()
        f2 = FiltrosConsulta.from_dict(d)
        assert f2.rating_minimo == "BBB+"
        assert f2.rating_maximo == "A"
        assert f2.periodo_meses == 6

    def test_obter_tipos_lf_todos(self):
        f = FiltrosConsulta()
        tipos = f.obter_tipos_lf()
        assert "senior" in tipos
        assert "subordinada_t2" in tipos
        assert "subordinada_at1" in tipos

    def test_obter_tipos_lf_apenas_senior(self):
        f = FiltrosConsulta(incluir_subordinada_t2=False, incluir_subordinada_at1=False)
        tipos = f.obter_tipos_lf()
        assert tipos == ["senior"]

    def test_descricao_rating_exato(self):
        f = FiltrosConsulta(rating_minimo="A-", rating_maximo="A-")
        assert f.descricao_rating() == "A-"

    def test_descricao_rating_faixa(self):
        f = FiltrosConsulta(rating_minimo="A-", rating_maximo="A+")
        assert "A-" in f.descricao_rating()
        assert "A+" in f.descricao_rating()

    def test_obter_data_inicio_periodo(self):
        f = FiltrosConsulta(periodo_meses=12)
        inicio = f.obter_data_inicio()
        hoje = date.today()
        # Deve ser aproximadamente 12 meses atrás
        delta_dias = (hoje - inicio).days
        assert 360 <= delta_dias <= 370

    def test_obter_data_inicio_customizada(self):
        f = FiltrosConsulta(data_inicio="2024-01-01")
        assert f.obter_data_inicio().isoformat() == "2024-01-01"

    def test_preset_salvar_carregar(self, tmp_path):
        f = FiltrosConsulta(rating_minimo="BBB+", rating_maximo="AA", periodo_meses=24)
        caminho = f.salvar_preset("teste_preset", tmp_path)
        assert caminho.exists()

        f2, nome = FiltrosConsulta.carregar_preset(caminho)
        assert nome == "teste_preset"
        assert f2.rating_minimo == "BBB+"
        assert f2.rating_maximo == "AA"
        assert f2.periodo_meses == 24

    def test_listar_presets_vazio(self, tmp_path):
        presets = FiltrosConsulta.listar_presets(tmp_path)
        assert presets == []

    def test_listar_presets_com_arquivo(self, tmp_path):
        f = FiltrosConsulta(rating_minimo="A-")
        f.salvar_preset("meu_preset", tmp_path)
        presets = FiltrosConsulta.listar_presets(tmp_path)
        assert len(presets) == 1
        assert presets[0]["nome"] == "meu_preset"


class TestAplicarFiltros:
    @pytest.fixture
    def df_mock(self):
        return pd.DataFrame({
            "emissor": ["Banco A", "Banco B", "Banco C", "Banco D"],
            "cnpj": ["", "", "", ""],
            "rating_agencia": ["Fitch", "Moody's", "Fitch", "Fitch"],
            "rating_nota": ["A-(bra)", "A.br", "BBB+(bra)", "AA-(bra)"],
            "rating_nota_normalizado": ["A-", "A", "BBB+", "AA-"],
            "tipo_lf": ["senior", "subordinada_t2", "senior", "subordinada_at1"],
            "data_emissao": pd.to_datetime(["2024-06-01", "2024-08-01", "2024-03-01", "2024-10-01"]),
            "data_vencimento": pd.to_datetime(["2026-06-01", "2029-08-01", "2026-03-01", pd.NaT]),
            "valor_emissao": [500e6, 200e6, 100e6, 1000e6],
            "spread_percentual": [0.90, 1.75, 1.40, 2.80],
            "indexador": ["CDI", "CDI", "IPCA", "CDI"],
            "serie": ["1ª", "2ª", "3ª", "1ª"],
            "modalidade": ["LF Sênior", "LF Sub T2", "LF Sênior", "LF AT1"],
            "fonte": ["ANBIMA", "ANBIMA", "ANBIMA", "ANBIMA"],
            "prazo_dias": [731, 1827, 731, None],
        })

    def test_filtro_rating_exato(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="A-", rating_maximo="A-",
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        assert len(resultado) == 1
        assert resultado.iloc[0]["emissor"] == "Banco A"

    def test_filtro_rating_faixa_a_menos_a_aa_menos(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="A-", rating_maximo="AA-",
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        # A-, A e AA- devem passar; BBB+ não
        assert len(resultado) == 3
        emissores = set(resultado["emissor"])
        assert "Banco A" in emissores
        assert "Banco B" in emissores
        assert "Banco D" in emissores
        assert "Banco C" not in emissores

    def test_filtro_tipo_apenas_senior(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="BBB-", rating_maximo="AAA",
            incluir_senior=True,
            incluir_subordinada_t2=False,
            incluir_subordinada_at1=False,
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        assert all(r == "senior" for r in resultado["tipo_lf"])
        assert len(resultado) == 2

    def test_filtro_tipo_apenas_t2(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="BBB-", rating_maximo="AAA",
            incluir_senior=False,
            incluir_subordinada_t2=True,
            incluir_subordinada_at1=False,
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        assert all(r == "subordinada_t2" for r in resultado["tipo_lf"])

    def test_filtro_valor_minimo(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="BBB-", rating_maximo="AAA",
            valor_minimo=300e6,
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        assert all(v >= 300e6 for v in resultado["valor_emissao"])

    def test_filtro_valor_maximo(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="BBB-", rating_maximo="AAA",
            valor_maximo=500e6,
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        assert all(v <= 500e6 for v in resultado["valor_emissao"])

    def test_filtro_indexador_ipca(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="BBB-", rating_maximo="AAA",
            indexador="ipca",
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        assert len(resultado) == 1
        assert resultado.iloc[0]["emissor"] == "Banco C"

    def test_filtro_indexador_cdi(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="BBB-", rating_maximo="AAA",
            indexador="cdi",
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        assert len(resultado) == 3
        assert "Banco C" not in resultado["emissor"].values

    def test_filtro_spread_minimo(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="BBB-", rating_maximo="AAA",
            spread_minimo=1.50,
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        spreads_validos = resultado["spread_percentual"].dropna()
        assert all(s >= 1.50 for s in spreads_validos)

    def test_filtro_emissor_especifico(self, df_mock):
        f = FiltrosConsulta(
            rating_minimo="BBB-", rating_maximo="AAA",
            emissores=["Banco A"],
            data_inicio="2024-01-01", data_fim="2024-12-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        assert len(resultado) == 1
        assert resultado.iloc[0]["emissor"] == "Banco A"

    def test_filtro_periodo_exclui_registros(self, df_mock):
        # Só emissões de junho a agosto 2024
        f = FiltrosConsulta(
            rating_minimo="BBB-", rating_maximo="AAA",
            data_inicio="2024-06-01", data_fim="2024-08-31",
        )
        resultado = aplicar_filtros(df_mock, f)
        assert len(resultado) == 2
        emissores = set(resultado["emissor"])
        assert "Banco A" in emissores
        assert "Banco B" in emissores

    def test_df_vazio_retorna_vazio(self):
        df_vazio = pd.DataFrame()
        f = FiltrosConsulta()
        resultado = aplicar_filtros(df_vazio, f)
        assert resultado.empty
