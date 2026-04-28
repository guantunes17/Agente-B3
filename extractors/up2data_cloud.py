"""
Extrator UP2DATA Cloud.
Acessa dados via Azure Blob Storage usando chaves SAS geradas pela API da B3.
"""
import logging
from datetime import date

import pandas as pd

from config.filters import FiltrosConsulta
from config.up2data_config import CANAIS_LF
from extractors.base import BaseExtractor
from extractors.up2data_auth import UP2DataAuth
from extractors.up2data_common import parse_e_mapear

logger = logging.getLogger(__name__)


class UP2DataCloudExtractor(BaseExtractor):
    """Extrai dados de Letras Financeiras do UP2DATA Cloud (Azure Blob Storage)."""

    @property
    def source_name(self) -> str:
        return "UP2DATA Cloud"

    def extract(self, filtros: FiltrosConsulta) -> pd.DataFrame:
        """
        Extrai dados do UP2DATA Cloud.

        Fluxo:
        1. Verificar se credenciais UP2DATA Cloud estão configuradas
        2. Autenticar e obter chaves SAS
        3. Para cada canal relevante (CANAIS_LF):
           a. Listar blobs disponíveis no período (máx. 30 dias no Cloud)
           b. Baixar arquivos no formato preferido (CSV > JSON > XML > TXT)
           c. Parsear e mapear colunas
        4. Consolidar DataFrames de todos os canais
        """
        if not UP2DataAuth.disponivel():
            logger.info("UP2DATA Cloud não configurado — pulando.")
            return pd.DataFrame()

        try:
            from gui.credentials import obter_credencial
            auth = UP2DataAuth(
                client_id=obter_credencial("up2data_client_id") or "",
                client_secret=obter_credencial("up2data_client_secret") or "",
                cert_path=obter_credencial("up2data_cert_path") or "",
                cert_password=obter_credencial("up2data_cert_password"),
            )

            chaves_sas = auth.obter_chaves_sas()
            dfs = []

            for canal_id, canal_info in CANAIS_LF.items():
                logger.info(f"Consultando canal: {canal_info['descricao']}...")
                sas_url = chaves_sas.get(canal_info["canal"])
                if not sas_url:
                    logger.warning(
                        f"Canal '{canal_info['canal']}' não disponível nas chaves SAS contratadas."
                    )
                    continue

                df_canal = self._extrair_canal(
                    sas_url=sas_url,
                    subcanal=canal_info.get("subcanal", ""),
                    data_inicio=filtros.obter_data_inicio(),
                    data_fim=filtros.obter_data_fim(),
                )

                if not df_canal.empty:
                    df_canal["fonte"] = f"UP2DATA Cloud / {canal_info['descricao']}"
                    dfs.append(df_canal)

            if dfs:
                resultado = pd.concat(dfs, ignore_index=True)
                logger.info(
                    f"UP2DATA Cloud: {len(resultado)} registros de {len(dfs)} canal(is)."
                )
                return resultado

            logger.warning("UP2DATA Cloud: nenhum dado encontrado nos canais consultados.")
            return pd.DataFrame()

        except NotImplementedError as e:
            logger.warning(f"UP2DATA Cloud: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Erro ao acessar UP2DATA Cloud: {e}")
            return pd.DataFrame()

    def _extrair_canal(
        self,
        sas_url: str,
        subcanal: str,
        data_inicio: date,
        data_fim: date,
    ) -> pd.DataFrame:
        """
        Extrai dados de um canal específico do Azure Blob Storage.

        Implementar quando credenciais estiverem disponíveis:
        - List Blobs: GET {sas_url}&restype=container&comp=list&prefix={subcanal}
        - Filtrar blobs por data (nome do arquivo geralmente contém YYYYMMDD)
        - Download: GET {blob_url}?{sas_token}
        - Parsear com parse_e_mapear()
        """
        logger.debug(f"Extração do canal '{subcanal}' aguarda credenciais reais.")
        return pd.DataFrame()
