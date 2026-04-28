"""Classe base abstrata para todos os extratores do Agente B3."""
from abc import ABC, abstractmethod
import pandas as pd
from config.filters import FiltrosConsulta

# Colunas padronizadas que todo extrator deve retornar
COLUNAS_PADRAO = [
    "emissor",
    "cnpj",
    "rating_agencia",
    "rating_nota",
    "tipo_lf",
    "data_emissao",
    "data_vencimento",
    "valor_emissao",
    "indexador",
    "spread_percentual",
    "prazo_dias",
    "serie",
    "modalidade",
    "fonte",
]


class BaseExtractor(ABC):
    """Classe base para extratores de dados de Letras Financeiras."""

    @abstractmethod
    def extract(self, filtros: FiltrosConsulta) -> pd.DataFrame:
        """
        Extrai dados da fonte.

        O extrator usa filtros.obter_data_inicio() e filtros.obter_data_fim()
        para delimitar o período. Os demais filtros (rating, tipo, valor, spread,
        indexador, emissores) são aplicados pelo filter_engine após consolidação.

        Retorna DataFrame com as colunas de COLUNAS_PADRAO.
        Usa NaN onde o dado não está disponível.
        """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Nome da fonte de dados (para logging e relatório)."""

    def _criar_df_vazio(self) -> pd.DataFrame:
        """Retorna DataFrame vazio com o schema padronizado."""
        return pd.DataFrame(columns=COLUNAS_PADRAO)

    def _garantir_colunas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Garante que o DataFrame tem todas as colunas padronizadas (adiciona NaN onde falta)."""
        for col in COLUNAS_PADRAO:
            if col not in df.columns:
                df[col] = float("nan")
        return df[COLUNAS_PADRAO]
