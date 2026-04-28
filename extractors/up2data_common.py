"""
Lógica compartilhada entre UP2DATA Cloud e Client.
- Parsers para CSV, JSON, XML e TXT
- Mapeamento flexível de colunas
- Detecção automática de formato
"""
import json
import logging
from io import StringIO
from pathlib import Path

import pandas as pd

from config.up2data_config import COLUMN_MAP, FORMATOS_PREFERENCIA

logger = logging.getLogger(__name__)


def detectar_formato(arquivo: "Path | str") -> str:
    """Detecta o formato de um arquivo pela extensão."""
    ext = Path(arquivo).suffix.lower().lstrip(".")
    if ext in FORMATOS_PREFERENCIA:
        return ext
    return "csv"


def parse_arquivo(conteudo: "str | bytes", formato: str, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Parseia o conteúdo de um arquivo UP2DATA em DataFrame.
    Suporta CSV, JSON, XML e TXT.
    """
    try:
        if isinstance(conteudo, bytes):
            conteudo_str = conteudo.decode(encoding)
        else:
            conteudo_str = conteudo

        if formato in ("csv", "txt"):
            for sep in [";", ",", "\t", "|"]:
                try:
                    df = pd.read_csv(StringIO(conteudo_str), sep=sep)
                    if len(df.columns) > 1:
                        return df
                except Exception:
                    continue
            if formato == "txt":
                try:
                    return pd.read_fwf(StringIO(conteudo_str))
                except Exception:
                    pass
            return pd.read_csv(StringIO(conteudo_str))

        elif formato == "json":
            dados = json.loads(conteudo_str)
            if isinstance(dados, list):
                return pd.DataFrame(dados)
            elif isinstance(dados, dict):
                for chave in ["data", "records", "items", "registros", "dados"]:
                    if chave in dados and isinstance(dados[chave], list):
                        return pd.DataFrame(dados[chave])
                return pd.DataFrame([dados])
            return pd.DataFrame()

        elif formato == "xml":
            return pd.read_xml(StringIO(conteudo_str))

        else:
            logger.warning(f"Formato '{formato}' não suportado. Tentando como CSV.")
            return pd.read_csv(StringIO(conteudo_str))

    except Exception as e:
        logger.error(f"Erro ao parsear arquivo ({formato}): {e}")
        return pd.DataFrame()


def mapear_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mapeia colunas do UP2DATA para o esquema padronizado do agente usando COLUMN_MAP.
    Colunas não mapeadas são descartadas; colunas do esquema ausentes ficam como NA.
    """
    colunas_df = set(df.columns)
    mapeamento_final: dict[str, str] = {}

    for coluna_agente, possiveis_nomes in COLUMN_MAP.items():
        for nome_up2data in possiveis_nomes:
            if nome_up2data in colunas_df:
                mapeamento_final[nome_up2data] = coluna_agente
                break

    if not mapeamento_final:
        logger.warning(
            "Nenhuma coluna do UP2DATA foi mapeada. "
            "Verifique o mapeamento em config/up2data_config.py."
        )
        return pd.DataFrame()

    df_mapeado = df.rename(columns=mapeamento_final)
    colunas_encontradas = list(mapeamento_final.values())
    df_mapeado = df_mapeado[colunas_encontradas].copy()

    colunas_faltantes = [c for c in COLUMN_MAP if c not in colunas_encontradas]
    for col in colunas_faltantes:
        df_mapeado[col] = pd.NA

    logger.info(
        f"Colunas mapeadas: {len(colunas_encontradas)}/{len(COLUMN_MAP)} "
        f"({', '.join(colunas_encontradas)})"
    )
    if colunas_faltantes:
        logger.warning(f"Colunas ausentes no UP2DATA (NA): {', '.join(colunas_faltantes)}")

    return df_mapeado


def parse_e_mapear(
    conteudo: "str | bytes", formato: str, encoding: str = "utf-8"
) -> pd.DataFrame:
    """Conveniência: parseia e mapeia colunas em uma chamada."""
    df = parse_arquivo(conteudo, formato, encoding)
    if df.empty:
        return df
    return mapear_colunas(df)


def parse_arquivo_local(caminho: Path) -> pd.DataFrame:
    """Lê e parseia um arquivo local (para uso pelo UP2DATA Client)."""
    if not caminho.exists():
        logger.error(f"Arquivo não encontrado: {caminho}")
        return pd.DataFrame()

    formato = detectar_formato(caminho)
    conteudo = caminho.read_bytes()
    return parse_e_mapear(conteudo, formato)
