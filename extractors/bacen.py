"""
Extrator BACEN — dados agregados do IF.Data (Banco Central do Brasil).
Fonte complementar para validar volumes de captação via LFs.
"""
import logging
import pandas as pd
from config.filters import FiltrosConsulta
from extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

BACEN_IFDATA_URL = "https://www3.bcb.gov.br/ifdata/rest/dadosSeries"


class BacenExtractor(BaseExtractor):
    """Extrator de dados agregados BACEN/IF.Data sobre captação via LFs."""

    @property
    def source_name(self) -> str:
        return "BACEN IF.Data"

    def extract(self, filtros: FiltrosConsulta) -> pd.DataFrame:
        """
        Tenta extrair dados do IF.Data do Banco Central.
        Retorna DataFrame vazio com aviso se indisponível.
        """
        data_inicio = filtros.obter_data_inicio()
        data_fim = filtros.obter_data_fim()
        logger.info(f"BACEN IF.Data: consultando período {data_inicio} a {data_fim}...")

        try:
            df = self._extrair_ifdata(data_inicio, data_fim)
            if df is not None and len(df) > 0:
                logger.info(f"BACEN IF.Data: {len(df)} registros obtidos.")
                return self._garantir_colunas(df)
        except Exception as exc:
            logger.warning(f"BACEN extração falhou: {exc}. Fonte complementar ignorada.")

        logger.warning("BACEN IF.Data: sem dados disponíveis — fonte complementar ignorada.")
        return self._criar_df_vazio()

    def _extrair_ifdata(self, data_inicio, data_fim) -> pd.DataFrame | None:
        """Extrai dados do IF.Data BACEN."""
        import requests
        from config.settings import USER_AGENT, REQUEST_TIMEOUT

        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        params = {
            "dataIni": data_inicio.strftime("%Y%m"),
            "dataFim": data_fim.strftime("%Y%m"),
            "tipo": "LF",
        }

        resposta = requests.get(
            BACEN_IFDATA_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT
        )

        if resposta.status_code != 200:
            logger.warning(f"BACEN IF.Data retornou status {resposta.status_code}.")
            return None

        dados = resposta.json()
        if not dados:
            return None

        registros = []
        for item in dados:
            registros.append({
                "emissor": item.get("nomeInstituicao", ""),
                "cnpj": item.get("cnpj", ""),
                "rating_agencia": "",
                "rating_nota": "",
                "tipo_lf": "senior",
                "data_emissao": item.get("data"),
                "data_vencimento": None,
                "valor_emissao": item.get("valorTotal"),
                "indexador": item.get("indexador", ""),
                "spread_percentual": None,
                "prazo_dias": item.get("prazoDias"),
                "serie": "",
                "modalidade": item.get("modalidade", "LF"),
                "fonte": "BACEN IF.Data",
            })

        df = pd.DataFrame(registros)
        df["data_emissao"] = pd.to_datetime(df["data_emissao"], errors="coerce")
        return df
