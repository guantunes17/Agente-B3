"""Testes do módulo de relatórios do Agente B3."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from config.filters import FiltrosConsulta
from report.templates import (
    gerar_titulo_relatorio,
    gerar_cabecalho_header,
    gerar_nota_metodologica,
    gerar_sumario_executivo,
    gerar_analise_emissor,
    gerar_contexto_macro,
    gerar_consideracoes_finais,
)
from report.tables import (
    preparar_tabela_emissoes,
    preparar_tabela_resumo_emissor,
    preparar_tabela_por_tipo,
)


@pytest.fixture
def filtros():
    return FiltrosConsulta(rating_minimo="A-", rating_maximo="A-", periodo_meses=12)


@pytest.fixture
def df_amostra():
    return pd.DataFrame({
        "emissor": ["Banco ABC Brasil S.A.", "Banco Pine S.A."],
        "cnpj": ["28.195.667/0001-06", "62.144.175/0001-20"],
        "rating_agencia": ["Fitch", "Moody's"],
        "rating_nota": ["A-(bra)", "A-.br"],
        "rating_nota_normalizado": ["A-", "A-"],
        "tipo_lf": ["senior", "subordinada_t2"],
        "data_emissao": pd.to_datetime(["2024-01-15", "2024-01-25"]),
        "data_vencimento": pd.to_datetime(["2026-01-25", "2029-01-25"]),
        "valor_emissao": [600_200_000.0, 180_000_000.0],
        "indexador": ["CDI", "CDI"],
        "spread_percentual": [0.90, 1.85],
        "prazo_dias": [740, 1827],
        "serie": ["1ª", "75ª"],
        "modalidade": ["LF Sênior", "LF Sub T2"],
        "fonte": ["ANBIMA", "ANBIMA"],
        "prazo_label": ["2 anos", "5 anos"],
        "label_tipo_lf": ["Sênior (Quirografária)", "Subordinada Nível 2 (T2)"],
        "retorno_estimado_aa": [11.40, 12.35],
        "classificacao_spread": ["Na média", "Na média"],
        "dias_ate_vencimento": [365, 1825],
        "status_vencimento": ["Vigente", "Vigente"],
    })


class TestTemplates:
    def test_titulo_contem_rating(self, filtros):
        titulo = gerar_titulo_relatorio(filtros)
        assert "A-" in titulo
        assert "LETRAS FINANCEIRAS" in titulo

    def test_cabecalho_contem_rating(self, filtros):
        header = gerar_cabecalho_header(filtros)
        assert "A-" in header
        assert "ANÁLISE" in header

    def test_nota_metodologica_contem_filtros(self, filtros, df_amostra):
        nota = gerar_nota_metodologica(filtros, ["ANBIMA Data"], 2, 10)
        assert "A-" in nota
        assert "ANBIMA" in nota
        assert "10" in nota or "2" in nota

    def test_sumario_executivo_com_dados(self, filtros, df_amostra):
        sumario = gerar_sumario_executivo(df_amostra, filtros, 10)
        assert "SUMÁRIO" in sumario
        assert "A-" in sumario

    def test_sumario_executivo_sem_dados(self, filtros):
        df_vazio = pd.DataFrame()
        sumario = gerar_sumario_executivo(df_vazio, filtros, 0)
        assert "SUMÁRIO" in sumario
        assert "não identificou" in sumario.lower() or "nenhum" in sumario.lower() or "não" in sumario

    def test_analise_emissor(self):
        emissor_dict = {
            "nome": "Banco ABC Brasil S.A.",
            "rating": "A-",
            "emissoes": [
                {
                    "tipo_lf": "senior",
                    "valor_emissao": 600_200_000.0,
                    "data_emissao": pd.Timestamp("2024-01-15"),
                    "indexador": "CDI",
                    "spread_percentual": 0.90,
                    "prazo_label": "2 anos",
                }
            ],
        }
        texto = gerar_analise_emissor(emissor_dict)
        assert "Banco ABC" in texto
        assert "A-" in texto
        assert "600" in texto

    def test_contexto_macro(self):
        texto = gerar_contexto_macro()
        assert "Letras Financeiras" in texto
        assert "Basileia" in texto

    def test_consideracoes_finais_com_dados(self, filtros, df_amostra):
        texto = gerar_consideracoes_finais(df_amostra, filtros)
        assert "CONSIDERAÇÕES" in texto
        assert "A-" in texto

    def test_consideracoes_finais_sem_dados(self, filtros):
        df_vazio = pd.DataFrame()
        texto = gerar_consideracoes_finais(df_vazio, filtros)
        assert "CONSIDERAÇÕES" in texto


class TestTables:
    def test_tabela_emissoes(self, df_amostra):
        linhas = preparar_tabela_emissoes(df_amostra)
        assert len(linhas) == 2
        assert "Emissor" in linhas[0]
        assert "Banco ABC Brasil S.A." in linhas[0]["Emissor"]

    def test_tabela_resumo_emissor(self, df_amostra):
        linhas = preparar_tabela_resumo_emissor(df_amostra)
        assert len(linhas) == 2
        emissores = [l["Emissor"] for l in linhas]
        assert "Banco ABC Brasil S.A." in emissores

    def test_tabela_por_tipo(self, df_amostra):
        linhas = preparar_tabela_por_tipo(df_amostra)
        assert len(linhas) >= 1
        tipos = [l["Tipo de LF"] for l in linhas]
        assert any("Sênior" in t for t in tipos)

    def test_tabela_emissoes_vazia(self):
        df_vazio = pd.DataFrame(columns=[
            "emissor", "rating_nota_normalizado", "rating_nota", "tipo_lf",
            "data_emissao", "data_vencimento", "valor_emissao", "indexador",
            "spread_percentual", "prazo_label", "status_vencimento",
        ])
        linhas = preparar_tabela_emissoes(df_vazio)
        assert linhas == []
