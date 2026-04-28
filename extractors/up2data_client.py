"""
Extrator UP2DATA Client.
Lê arquivos de Letras Financeiras do diretório local onde o UP2DATA Client
deposita os dados automaticamente.
"""
import logging
import re
from datetime import date
from pathlib import Path

import pandas as pd

from config.filters import FiltrosConsulta
from config.up2data_config import CANAIS_LF, DEFAULT_CLIENT_PATH, FORMATOS_PREFERENCIA
from extractors.base import BaseExtractor
from extractors.up2data_common import parse_arquivo_local

logger = logging.getLogger(__name__)


class UP2DataClientExtractor(BaseExtractor):
    """Extrai dados de Letras Financeiras dos arquivos locais do UP2DATA Client."""

    def __init__(self, diretorio_base: "Path | str | None" = None):
        if diretorio_base:
            self.diretorio = Path(diretorio_base)
        else:
            try:
                from gui.credentials import obter_credencial
                path = obter_credencial("up2data_client_path")
                self.diretorio = Path(path) if path else DEFAULT_CLIENT_PATH
            except ImportError:
                self.diretorio = DEFAULT_CLIENT_PATH

    @property
    def source_name(self) -> str:
        return "UP2DATA Client"

    def extract(self, filtros: FiltrosConsulta) -> pd.DataFrame:
        """
        Extrai dados dos arquivos locais do UP2DATA Client.

        Fluxo:
        1. Verificar se o diretório existe
        2. Para cada canal relevante (CANAIS_LF):
           a. Localizar a pasta correspondente (tenta múltiplas estruturas)
           b. Listar arquivos que correspondem ao período
           c. Parsear cada arquivo com detecção automática de formato
        3. Consolidar todos os DataFrames
        """
        if not self.diretorio.exists():
            logger.info(
                f"Diretório UP2DATA Client não encontrado ({self.diretorio}) — pulando."
            )
            return pd.DataFrame()

        logger.info(f"UP2DATA Client: buscando arquivos em {self.diretorio}...")
        dfs = []
        data_inicio = filtros.obter_data_inicio()
        data_fim = filtros.obter_data_fim()

        for canal_id, canal_info in CANAIS_LF.items():
            pastas_possiveis = [
                self.diretorio / canal_info["canal"] / canal_info.get("subcanal", ""),
                self.diretorio / canal_info["canal"],
                self.diretorio / canal_info.get("subcanal", canal_info["canal"]),
            ]

            pasta_encontrada = next(
                (p for p in pastas_possiveis if p.exists() and p.is_dir()), None
            )

            if not pasta_encontrada:
                logger.debug(
                    f"Pasta do canal '{canal_info['descricao']}' não encontrada em {self.diretorio}"
                )
                continue

            arquivos = self._listar_arquivos_periodo(pasta_encontrada, data_inicio, data_fim)
            logger.info(f"Canal '{canal_info['descricao']}': {len(arquivos)} arquivo(s).")

            for arquivo in arquivos:
                df = parse_arquivo_local(arquivo)
                if not df.empty:
                    df["fonte"] = f"UP2DATA Client / {canal_info['descricao']}"
                    dfs.append(df)

        if dfs:
            resultado = pd.concat(dfs, ignore_index=True)
            logger.info(f"UP2DATA Client: {len(resultado)} registros extraídos.")
            return resultado

        logger.warning("UP2DATA Client: nenhum dado encontrado nos diretórios.")
        return pd.DataFrame()

    def _listar_arquivos_periodo(
        self, pasta: Path, data_inicio: date, data_fim: date
    ) -> list[Path]:
        """
        Lista arquivos na pasta que correspondem ao período solicitado.
        Tenta extrair a data do nome do arquivo (padrões: YYYYMMDD, YYYY-MM-DD).
        Se não conseguir extrair a data, inclui o arquivo (abordagem conservadora).
        """
        arquivos: list[Path] = []
        padrao_data = re.compile(r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})")

        for arquivo in pasta.iterdir():
            if not arquivo.is_file():
                continue
            if arquivo.suffix.lower().lstrip(".") not in FORMATOS_PREFERENCIA:
                continue

            match = padrao_data.search(arquivo.stem)
            if match:
                try:
                    data_arquivo = date(
                        int(match.group(1)), int(match.group(2)), int(match.group(3))
                    )
                    if data_inicio <= data_arquivo <= data_fim:
                        arquivos.append(arquivo)
                except ValueError:
                    arquivos.append(arquivo)
            else:
                # Sem data no nome — incluir (melhor ter dados demais que de menos)
                arquivos.append(arquivo)

        arquivos.sort(key=lambda f: f.stem, reverse=True)
        return arquivos
