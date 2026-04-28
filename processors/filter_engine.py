"""
Motor de filtros dinâmicos do Agente B3.
Aplica FiltrosConsulta ao DataFrame consolidado de LFs.
"""
import logging
import pandas as pd
from config.filters import FiltrosConsulta, normalizar_rating, rating_no_intervalo
from config.settings import INDEXADORES

logger = logging.getLogger(__name__)


def aplicar_filtros(df: pd.DataFrame, filtros: FiltrosConsulta) -> pd.DataFrame:
    """
    Aplica todos os filtros dinâmicos ao DataFrame.

    Ordem dos filtros:
    1. Período (data de emissão)
    2. Rating (faixa normalizada)
    3. Tipo de LF
    4. Valor de emissão (faixa)
    5. Spread (faixa)
    6. Indexador
    7. Emissores específicos

    Retorna DataFrame filtrado com log individual de cada etapa.
    """
    if df.empty:
        logger.warning("Filter engine: DataFrame vazio — nenhum filtro aplicado.")
        return df

    total_inicial = len(df)
    logger.info(f"Aplicando filtros a {total_inicial} registros...")

    # ── 1. Filtro de período ──────────────────────────────────────────────────
    data_inicio = pd.Timestamp(filtros.obter_data_inicio())
    data_fim = pd.Timestamp(filtros.obter_data_fim())

    antes = len(df)
    mask_periodo = (
        df["data_emissao"].notna()
        & (df["data_emissao"] >= data_inicio)
        & (df["data_emissao"] <= data_fim)
    )
    df = df[mask_periodo].copy()
    removidos = antes - len(df)
    logger.info(
        f"Filtro período ({filtros.descricao_periodo()}): "
        f"{removidos} registros removidos, {len(df)} restantes."
    )

    if df.empty:
        logger.warning("Nenhum registro restou após filtro de período.")
        return df

    # ── 2. Filtro de rating ───────────────────────────────────────────────────
    antes = len(df)

    # Garantir coluna normalizada (pode já existir do cleaner)
    if "rating_nota_normalizado" not in df.columns:
        df["rating_nota_normalizado"] = df["rating_nota"].apply(
            lambda r: normalizar_rating(str(r)) if pd.notna(r) and str(r).strip() != "" else None
        )

    sem_rating = df["rating_nota_normalizado"].isna()
    if sem_rating.sum() > 0:
        logger.warning(
            f"Filtro rating: {sem_rating.sum()} registros com rating não normalizável — mantidos."
        )

    mask_rating = sem_rating | df["rating_nota_normalizado"].apply(
        lambda r: rating_no_intervalo(r, filtros.rating_minimo, filtros.rating_maximo)
        if r is not None
        else True
    )
    df = df[mask_rating].copy()
    removidos = antes - len(df)
    logger.info(
        f"Filtro rating ({filtros.descricao_rating()}): "
        f"{removidos} removidos, {len(df)} restantes."
    )

    if df.empty:
        logger.warning("Nenhum registro restou após filtro de rating.")
        return df

    # ── 3. Filtro de tipo de LF ───────────────────────────────────────────────
    antes = len(df)
    tipos_selecionados = filtros.obter_tipos_lf()
    df = df[df["tipo_lf"].isin(tipos_selecionados)].copy()
    removidos = antes - len(df)
    logger.info(
        f"Filtro tipo LF ({', '.join(tipos_selecionados)}): "
        f"{removidos} removidos, {len(df)} restantes."
    )

    if df.empty:
        logger.warning("Nenhum registro restou após filtro de tipo de LF.")
        return df

    # ── 4. Filtro de valor ────────────────────────────────────────────────────
    if filtros.valor_minimo is not None or filtros.valor_maximo is not None:
        antes = len(df)
        mask_valor = pd.Series(True, index=df.index)

        if filtros.valor_minimo is not None:
            # Manter NaN (não temos info para filtrar)
            mask_valor &= df["valor_emissao"].isna() | (df["valor_emissao"] >= filtros.valor_minimo)

        if filtros.valor_maximo is not None:
            mask_valor &= df["valor_emissao"].isna() | (df["valor_emissao"] <= filtros.valor_maximo)

        df = df[mask_valor].copy()
        removidos = antes - len(df)
        logger.info(
            f"Filtro valor (R$ {filtros.valor_minimo or 'sem mínimo'} "
            f"a R$ {filtros.valor_maximo or 'sem máximo'}): "
            f"{removidos} removidos, {len(df)} restantes."
        )

        if df.empty:
            logger.warning("Nenhum registro restou após filtro de valor.")
            return df

    # ── 5. Filtro de spread ───────────────────────────────────────────────────
    if filtros.spread_minimo is not None or filtros.spread_maximo is not None:
        antes = len(df)
        mask_spread = pd.Series(True, index=df.index)

        if filtros.spread_minimo is not None:
            mask_spread &= df["spread_percentual"].isna() | (df["spread_percentual"] >= filtros.spread_minimo)

        if filtros.spread_maximo is not None:
            mask_spread &= df["spread_percentual"].isna() | (df["spread_percentual"] <= filtros.spread_maximo)

        df = df[mask_spread].copy()
        removidos = antes - len(df)
        logger.info(
            f"Filtro spread ({filtros.spread_minimo or 'sem mínimo'}% "
            f"a {filtros.spread_maximo or 'sem máximo'}% a.a.): "
            f"{removidos} removidos, {len(df)} restantes."
        )

        if df.empty:
            logger.warning("Nenhum registro restou após filtro de spread.")
            return df

    # ── 6. Filtro de indexador ────────────────────────────────────────────────
    if filtros.indexador != "todos":
        antes = len(df)
        termos = [t.upper() for t in INDEXADORES.get(filtros.indexador, [])]

        def _match_indexador(idx_valor: str) -> bool:
            if pd.isna(idx_valor):
                return True  # Manter NaN
            idx_upper = str(idx_valor).upper().strip()
            return any(termo in idx_upper for termo in termos)

        df = df[df["indexador"].apply(_match_indexador)].copy()
        removidos = antes - len(df)
        logger.info(
            f"Filtro indexador ({filtros.indexador}): "
            f"{removidos} removidos, {len(df)} restantes."
        )

        if df.empty:
            logger.warning("Nenhum registro restou após filtro de indexador.")
            return df

    # ── 7. Filtro de emissores específicos ────────────────────────────────────
    if filtros.emissores and len(filtros.emissores) > 0:
        antes = len(df)
        filtros_upper = [e.strip().upper() for e in filtros.emissores if e.strip()]

        def _match_emissor(nome: str) -> bool:
            nome_upper = str(nome).upper()
            return any(f in nome_upper for f in filtros_upper)

        df = df[df["emissor"].apply(_match_emissor)].copy()
        removidos = antes - len(df)
        logger.info(
            f"Filtro emissores ({', '.join(filtros.emissores)}): "
            f"{removidos} removidos, {len(df)} restantes."
        )

    total_final = len(df)
    logger.info(
        f"Filtros concluídos: {total_inicial} → {total_final} registros "
        f"({total_inicial - total_final} removidos no total)."
    )
    return df.reset_index(drop=True)
