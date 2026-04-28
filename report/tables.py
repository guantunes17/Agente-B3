"""
Geração de tabelas comparativas para o relatório de Letras Financeiras.
"""
import logging
import pandas as pd
from utils.helpers import formatar_brl_milhoes, formatar_data, formatar_spread
from config.settings import LF_TYPES

logger = logging.getLogger(__name__)


def preparar_tabela_emissoes(df: pd.DataFrame) -> list[dict]:
    """
    Prepara lista de dicionários para a tabela principal de emissões.
    Cada dict representa uma linha da tabela no Word.
    """
    linhas = []
    for _, row in df.iterrows():
        tipo_label = LF_TYPES.get(row.get("tipo_lf", ""), {}).get("label", row.get("tipo_lf", ""))
        spread = row.get("spread_percentual")
        idx = str(row.get("indexador", "CDI")).upper()

        if idx in ("CDI", "DI"):
            taxa_str = formatar_spread(spread)
        else:
            taxa_str = (
                f"{idx} + {spread:.2f}% a.a.".replace(".", ",")
                if spread is not None and pd.notna(spread)
                else idx
            )

        linhas.append({
            "Emissor": row.get("emissor", "N/D"),
            "Rating": row.get("rating_nota_normalizado") or row.get("rating_nota", "N/D"),
            "Tipo": tipo_label,
            "Data Emissão": formatar_data(row.get("data_emissao")),
            "Vencimento": formatar_data(row.get("data_vencimento")) if pd.notna(row.get("data_vencimento")) else "Perpétuo",
            "Valor (R$ mi)": formatar_brl_milhoes(row.get("valor_emissao")),
            "Taxa": taxa_str,
            "Prazo": row.get("prazo_label", "N/D"),
            "Status": row.get("status_vencimento", "N/D"),
        })
    return linhas


def preparar_tabela_resumo_emissor(df: pd.DataFrame) -> list[dict]:
    """
    Prepara tabela de resumo por emissor (total captado, número de emissões, spread médio).
    """
    if df.empty:
        return []

    resumo = (
        df.groupby("emissor")
        .agg(
            rating=("rating_nota_normalizado", "first"),
            n_emissoes=("tipo_lf", "count"),
            valor_total=("valor_emissao", "sum"),
            spread_medio=("spread_percentual", "mean"),
        )
        .reset_index()
        .sort_values("valor_total", ascending=False)
    )

    linhas = []
    for _, row in resumo.iterrows():
        spread_medio = row.get("spread_medio")
        linhas.append({
            "Emissor": row["emissor"],
            "Rating": row.get("rating", "N/D"),
            "Nº Emissões": int(row["n_emissoes"]),
            "Total Captado": formatar_brl_milhoes(row.get("valor_total")),
            "Spread Médio": (
                f"CDI + {spread_medio:.2f}% a.a.".replace(".", ",")
                if spread_medio is not None and pd.notna(spread_medio)
                else "N/D"
            ),
        })
    return linhas


def preparar_tabela_por_tipo(df: pd.DataFrame) -> list[dict]:
    """
    Prepara tabela comparativa de spread por tipo de LF.
    """
    if df.empty:
        return []

    tipos_presentes = df["tipo_lf"].unique()
    linhas = []
    for tipo in ["senior", "subordinada_t2", "subordinada_at1"]:
        if tipo not in tipos_presentes:
            continue
        subset = df[df["tipo_lf"] == tipo]
        label = LF_TYPES.get(tipo, {}).get("label", tipo)
        spread_min = subset["spread_percentual"].min()
        spread_max = subset["spread_percentual"].max()
        spread_med = subset["spread_percentual"].mean()
        valor_total = subset["valor_emissao"].sum()

        def fmt_sp(v):
            if v is None or pd.isna(v):
                return "N/D"
            return f"CDI + {v:.2f}% a.a.".replace(".", ",")

        linhas.append({
            "Tipo de LF": label,
            "Nº Emissões": len(subset),
            "Spread Mín.": fmt_sp(spread_min),
            "Spread Máx.": fmt_sp(spread_max),
            "Spread Médio": fmt_sp(spread_med),
            "Volume Total": formatar_brl_milhoes(valor_total),
        })
    return linhas
