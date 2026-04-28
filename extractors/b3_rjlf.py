"""
[STUB] Extrator B3 RJLF — a ser implementado quando credencial chegar.
Registros de Letras Financeiras na B3 (sistema RJLF).
"""
import logging
import pandas as pd
from config.filters import FiltrosConsulta
from extractors.base import BaseExtractor

logger = logging.getLogger(__name__)


class B3RjlfExtractor(BaseExtractor):
    """
    Stub do extrator B3 RJLF.
    Aguardando credenciais de acesso ao sistema de registro B3.
    """

    @property
    def source_name(self) -> str:
        return "B3 RJLF"

    def extract(self, filtros: FiltrosConsulta) -> pd.DataFrame:
        """
        STUB — retorna DataFrame vazio até implementação completa.
        Requer credencial B3_RJLF_TOKEN no arquivo .env.
        """
        logger.warning(
            "B3 RJLF: extrator ainda não implementado (aguardando credencial). "
            "Configure B3_RJLF_TOKEN no .env para habilitar esta fonte."
        )
        return self._criar_df_vazio()
