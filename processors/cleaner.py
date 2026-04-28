"""
Limpeza e normalização dos dados brutos de Letras Financeiras.
O cleaner NÃO filtra por rating — isso é responsabilidade do filter_engine.
"""
import logging
import pandas as pd
import numpy as np
from config.filters import normalizar_rating

logger = logging.getLogger(__name__)


def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica limpeza e normalização ao DataFrame consolidado.

    Operações:
    - Remove duplicatas
    - Padroniza tipos de dados
    - Normaliza nomes de emissores
    - Normaliza notas de rating (para a escala padrão)
    - Padroniza tipos de LF
    - Padroniza indexadores
    - Garante datas como datetime
    - Remove linhas sem emissor ou sem data de emissão
    """
    if df.empty:
        logger.warning("Cleaner: DataFrame vazio recebido.")
        return df

    total_inicial = len(df)
    logger.info(f"Cleaner: iniciando limpeza de {total_inicial} registros...")

    # 1. Remover linhas sem emissor ou sem data de emissão
    df = df.dropna(subset=["emissor", "data_emissao"])
    df = df[df["emissor"].astype(str).str.strip() != ""]
    removidos_vazios = total_inicial - len(df)
    if removidos_vazios > 0:
        logger.debug(f"Cleaner: {removidos_vazios} linhas removidas (emissor/data vazios).")

    # 2. Normalizar tipos de dados
    df = df.copy()
    df["emissor"] = df["emissor"].astype(str).str.strip()
    df["cnpj"] = df["cnpj"].astype(str).str.strip().replace("nan", "")
    df["rating_agencia"] = df["rating_agencia"].astype(str).str.strip().replace("nan", "")
    df["rating_nota"] = df["rating_nota"].astype(str).str.strip().replace("nan", "")
    df["serie"] = df["serie"].astype(str).str.strip().replace("nan", "")
    df["modalidade"] = df["modalidade"].astype(str).str.strip().replace("nan", "")
    df["fonte"] = df["fonte"].astype(str).str.strip().replace("nan", "")

    # 3. Garantir datas como datetime
    df["data_emissao"] = pd.to_datetime(df["data_emissao"], errors="coerce")
    df["data_vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce")

    # 4. Normalizar notas de rating para escala padrão (sem filtrar — apenas normaliza)
    df["rating_nota_normalizado"] = df["rating_nota"].apply(
        lambda r: normalizar_rating(r) if pd.notna(r) and r != "" else None
    )

    # 5. Normalizar tipos de LF
    df["tipo_lf"] = df["tipo_lf"].apply(_normalizar_tipo_lf)

    # 6. Normalizar indexadores
    df["indexador"] = df["indexador"].apply(_normalizar_indexador)

    # 7. Garantir valores numéricos
    df["valor_emissao"] = pd.to_numeric(df["valor_emissao"], errors="coerce")
    df["spread_percentual"] = pd.to_numeric(df["spread_percentual"], errors="coerce")
    df["prazo_dias"] = pd.to_numeric(df["prazo_dias"], errors="coerce")

    # 8. Remover duplicatas (mesma emissão de múltiplas fontes — manter a primeira)
    antes_dedup = len(df)
    df = df.drop_duplicates(
        subset=["emissor", "tipo_lf", "data_emissao", "valor_emissao"],
        keep="first",
    )
    removidos_dup = antes_dedup - len(df)
    if removidos_dup > 0:
        logger.debug(f"Cleaner: {removidos_dup} duplicatas removidas.")

    df = df.reset_index(drop=True)
    logger.info(f"Cleaner: {total_inicial} → {len(df)} registros após limpeza.")
    return df


def _normalizar_tipo_lf(tipo: str) -> str:
    """Padroniza o tipo de LF para as categorias internas."""
    if pd.isna(tipo) or not isinstance(tipo, str):
        return "senior"
    t = tipo.lower().strip()
    if "at1" in t or "perpét" in t or "nivel 1" in t or "nível 1" in t:
        return "subordinada_at1"
    if "t2" in t or "nivel 2" in t or "nível 2" in t or ("subordinad" in t and "at1" not in t):
        return "subordinada_t2"
    return "senior"


def _normalizar_indexador(indexador: str) -> str:
    """Padroniza o nome do indexador."""
    if pd.isna(indexador) or not isinstance(indexador, str):
        return "CDI"
    idx = indexador.upper().strip()
    if "IPCA" in idx or "IGP" in idx:
        return "IPCA"
    if "PRÉ" in idx or "PRE" in idx or "FIXA" in idx or "FIXED" in idx:
        return "PRE"
    return "CDI"
