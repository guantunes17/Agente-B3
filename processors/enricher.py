"""
Enriquecimento dos dados filtrados de Letras Financeiras.
Adiciona colunas derivadas: prazo calculado, classificação de spread, retorno estimado, etc.
"""
import logging
import pandas as pd
import numpy as np
from datetime import date
from config.filters import FiltrosConsulta
from config.settings import LF_TYPES, SPREAD_RANGES

logger = logging.getLogger(__name__)

# CDI de referência para cálculo de retorno estimado (% a.a.)
CDI_REFERENCIA_DEFAULT = 10.50


def enriquecer(df: pd.DataFrame, filtros: FiltrosConsulta, cdi_referencia: float | None = None) -> pd.DataFrame:
    """
    Enriquece o DataFrame filtrado com colunas calculadas.

    Colunas adicionadas:
    - prazo_meses_calculado: prazo em meses entre emissão e vencimento
    - prazo_label: texto legível do prazo (ex: "36 meses", "Perpétuo")
    - classificacao_spread: "Abaixo do mercado", "Na média" ou "Acima do mercado"
    - retorno_estimado_aa: retorno total estimado em % a.a. (CDI ref. + spread)
    - label_tipo_lf: nome completo do tipo de LF
    - dias_ate_vencimento: dias restantes até o vencimento a partir de hoje
    - status_vencimento: "Vigente", "Vencida" ou "Perpétua"
    """
    if df.empty:
        return df

    df = df.copy()
    cdi_ref = cdi_referencia if cdi_referencia is not None else CDI_REFERENCIA_DEFAULT
    hoje = pd.Timestamp(date.today())

    # ── Prazo calculado ───────────────────────────────────────────────────────
    df["prazo_meses_calculado"] = df.apply(
        lambda row: _calcular_prazo_meses(row["data_emissao"], row["data_vencimento"]),
        axis=1,
    )

    df["prazo_label"] = df.apply(
        lambda row: _label_prazo(row["data_emissao"], row["data_vencimento"]),
        axis=1,
    )

    # ── Retorno estimado ──────────────────────────────────────────────────────
    df["retorno_estimado_aa"] = df.apply(
        lambda row: _calcular_retorno(row["indexador"], row["spread_percentual"], cdi_ref),
        axis=1,
    )

    # ── Classificação de spread ───────────────────────────────────────────────
    df["classificacao_spread"] = df.apply(
        lambda row: _classificar_spread(row["tipo_lf"], row["spread_percentual"]),
        axis=1,
    )

    # ── Label do tipo de LF ───────────────────────────────────────────────────
    df["label_tipo_lf"] = df["tipo_lf"].apply(
        lambda t: LF_TYPES.get(t, {}).get("label", t)
    )

    # ── Dias até vencimento ───────────────────────────────────────────────────
    df["dias_ate_vencimento"] = df["data_vencimento"].apply(
        lambda dv: (dv - hoje).days if pd.notna(dv) else None
    )

    df["status_vencimento"] = df.apply(
        lambda row: _status_vencimento(row["data_vencimento"], row["tipo_lf"], hoje),
        axis=1,
    )

    logger.info(f"Enricher: {len(df)} registros enriquecidos com colunas derivadas.")
    return df


def _calcular_prazo_meses(data_emissao: pd.Timestamp, data_vencimento: pd.Timestamp) -> float | None:
    """Calcula prazo em meses entre emissão e vencimento."""
    if pd.isna(data_vencimento) or pd.isna(data_emissao):
        return None
    delta = data_vencimento - data_emissao
    return round(delta.days / 30.44, 1)


def _label_prazo(data_emissao: pd.Timestamp, data_vencimento: pd.Timestamp) -> str:
    """Retorna texto descritivo do prazo."""
    if pd.isna(data_vencimento):
        return "Perpétuo"
    if pd.isna(data_emissao):
        return "N/D"
    delta = data_vencimento - data_emissao
    meses = round(delta.days / 30.44)
    if meses < 12:
        return f"{meses} meses"
    anos = meses / 12
    if anos == int(anos):
        return f"{int(anos)} anos"
    return f"{anos:.1f} anos"


def _calcular_retorno(indexador: str, spread: float | None, cdi_ref: float) -> float | None:
    """Estima retorno total anual com base no indexador e spread."""
    if pd.isna(spread) or spread is None:
        return None
    idx = str(indexador).upper()
    if "IPCA" in idx:
        # IPCA + spread: retorno estimado = spread (não somamos IPCA ao CDI)
        return round(spread, 2)
    if "PRE" in idx or "FIXA" in idx or "PRÉ" in idx:
        return round(spread, 2)
    # CDI: retorno = CDI_ref + spread
    return round(cdi_ref + spread, 2)


def _classificar_spread(tipo_lf: str, spread: float | None) -> str:
    """Classifica o spread em relação à faixa típica do tipo de LF."""
    if pd.isna(spread) or spread is None:
        return "N/D"
    faixa = SPREAD_RANGES.get(tipo_lf, {"min": 0, "max": 999})
    media = (faixa["min"] + faixa["max"]) / 2
    tolerancia = (faixa["max"] - faixa["min"]) * 0.2
    if spread < media - tolerancia:
        return "Abaixo do mercado"
    if spread > media + tolerancia:
        return "Acima do mercado"
    return "Na média"


def _status_vencimento(data_vencimento: pd.Timestamp, tipo_lf: str, hoje: pd.Timestamp) -> str:
    """Retorna status de vencimento da emissão."""
    if tipo_lf == "subordinada_at1" or pd.isna(data_vencimento):
        return "Perpétua"
    if data_vencimento < hoje:
        return "Vencida"
    return "Vigente"
