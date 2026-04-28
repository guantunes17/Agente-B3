"""Funções utilitárias do Agente B3."""
from datetime import date, datetime
from typing import Any
import locale
import math


def formatar_brl(valor: float | None, casas: int = 0) -> str:
    """Formata um valor em Reais (R$) com separadores de milhar."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "N/D"
    try:
        if casas == 0:
            return f"R$ {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "N/D"


def formatar_brl_milhoes(valor: float | None) -> str:
    """Formata valor em Reais abreviado em milhões (R$ X,X mi)."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "N/D"
    try:
        milhoes = valor / 1_000_000
        return f"R$ {milhoes:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "N/D"


def formatar_percentual(valor: float | None, casas: int = 2) -> str:
    """Formata um valor como percentual."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "N/D"
    try:
        return f"{valor:.{casas}f}%".replace(".", ",")
    except (ValueError, TypeError):
        return "N/D"


def formatar_spread(valor: float | None) -> str:
    """Formata spread sobre CDI (ex: CDI + 0,90% a.a.)."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "N/D"
    try:
        return f"CDI + {valor:.2f}% a.a.".replace(".", ",")
    except (ValueError, TypeError):
        return "N/D"


def formatar_data(dt: date | datetime | None, formato: str = "%d/%m/%Y") -> str:
    """Formata data para exibição."""
    if dt is None:
        return "N/D"
    try:
        return dt.strftime(formato)
    except (AttributeError, ValueError):
        return "N/D"


def calcular_prazo_anos(data_emissao: date, data_vencimento: date | None) -> str:
    """Calcula prazo entre datas e retorna como texto."""
    if data_vencimento is None:
        return "Perpétuo"
    try:
        delta = data_vencimento - data_emissao
        anos = delta.days / 365.25
        if anos < 1:
            meses = round(delta.days / 30.44)
            return f"{meses} meses"
        return f"{anos:.1f} anos".replace(".", ",")
    except (TypeError, AttributeError):
        return "N/D"


def calcular_prazo_meses(data_emissao: date, data_vencimento: date | None) -> int | None:
    """Calcula prazo em meses entre duas datas."""
    if data_vencimento is None:
        return None
    try:
        delta = data_vencimento - data_emissao
        return round(delta.days / 30.44)
    except (TypeError, AttributeError):
        return None


def normalizar_nome_emissor(nome: str) -> str:
    """Normaliza nome de emissor para comparação."""
    return nome.strip().upper()


def match_emissor(nome_df: str, filtro: str) -> bool:
    """Verifica se um nome de emissor contém o texto do filtro (case-insensitive)."""
    return filtro.strip().upper() in nome_df.strip().upper()


def timestamp_arquivo() -> str:
    """Retorna timestamp formatado para usar em nomes de arquivo."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def pluralizar(quantidade: int, singular: str, plural: str) -> str:
    """Retorna singular ou plural conforme quantidade."""
    return singular if quantidade == 1 else plural


def valor_ou_nd(valor: Any, formatador=None) -> str:
    """Retorna valor formatado ou 'N/D' se None/NaN."""
    if valor is None:
        return "N/D"
    try:
        import math
        if isinstance(valor, float) and math.isnan(valor):
            return "N/D"
    except (TypeError, ValueError):
        pass
    if formatador:
        return formatador(valor)
    return str(valor)
