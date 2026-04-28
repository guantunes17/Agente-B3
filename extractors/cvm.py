"""
Extrator CVM — fatos relevantes e comunicados sobre Letras Financeiras.
Consulta o portal de dados abertos da CVM.
"""
import logging
import pandas as pd
from config.filters import FiltrosConsulta
from extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

CVM_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/"


class CVMExtractor(BaseExtractor):
    """Extrator de fatos relevantes da CVM sobre emissões de LFs."""

    @property
    def source_name(self) -> str:
        return "CVM (Portal Dados Abertos)"

    def extract(self, filtros: FiltrosConsulta) -> pd.DataFrame:
        """
        Tenta extrair fatos relevantes da CVM relacionados a LFs.
        Em caso de falha, retorna DataFrame vazio com aviso.
        """
        data_inicio = filtros.obter_data_inicio()
        data_fim = filtros.obter_data_fim()
        logger.info(f"CVM: buscando comunicados de {data_inicio} a {data_fim}...")

        try:
            df = self._extrair_portal(data_inicio, data_fim)
            if df is not None and len(df) > 0:
                logger.info(f"CVM: {len(df)} registros obtidos.")
                return self._garantir_colunas(df)
        except Exception as exc:
            logger.warning(f"CVM extração falhou: {exc}. Retornando DataFrame vazio.")

        logger.warning("CVM: sem dados disponíveis — fonte complementar ignorada.")
        return self._criar_df_vazio()

    def _extrair_portal(self, data_inicio, data_fim) -> pd.DataFrame | None:
        """Extrai dados do portal de dados abertos da CVM."""
        import requests
        from config.settings import USER_AGENT, REQUEST_TIMEOUT

        headers = {"User-Agent": USER_AGENT}
        ano = data_inicio.year
        url = f"{CVM_URL}fre_cia_aberta_{ano}.zip"

        resposta = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resposta.status_code != 200:
            logger.warning(f"CVM: arquivo {url} não encontrado (status {resposta.status_code}).")
            return None

        import io, zipfile
        with zipfile.ZipFile(io.BytesIO(resposta.content)) as z:
            nomes = z.namelist()
            # Busca arquivo de debêntures/LF dentro do zip
            alvo = next((n for n in nomes if "letra" in n.lower() or "lf" in n.lower()), None)
            if alvo is None:
                return None
            with z.open(alvo) as f:
                df_raw = pd.read_csv(f, sep=";", encoding="latin-1")

        # Normalização básica
        df_raw.columns = [c.lower().strip() for c in df_raw.columns]
        registros = []
        for _, row in df_raw.iterrows():
            registros.append({
                "emissor": row.get("nome_companhia", ""),
                "cnpj": row.get("cnpj_companhia", ""),
                "rating_agencia": "",
                "rating_nota": "",
                "tipo_lf": "senior",
                "data_emissao": row.get("dt_emissao"),
                "data_vencimento": row.get("dt_vencimento"),
                "valor_emissao": row.get("vl_emissao"),
                "indexador": row.get("indexador", ""),
                "spread_percentual": row.get("spread"),
                "prazo_dias": None,
                "serie": row.get("serie", ""),
                "modalidade": row.get("modalidade", ""),
                "fonte": "CVM",
            })

        df = pd.DataFrame(registros)
        df["data_emissao"] = pd.to_datetime(df["data_emissao"], errors="coerce")
        df["data_vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce")
        mask = (df["data_emissao"] >= pd.Timestamp(data_inicio)) & (df["data_emissao"] <= pd.Timestamp(data_fim))
        return df[mask].reset_index(drop=True)
