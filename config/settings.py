"""Configurações centrais do Agente B3."""
from pathlib import Path

# Diretórios do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRESETS_DIR = PROJECT_ROOT / "presets"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = PROJECT_ROOT / "logs"

# Classificação de tipos de LF
LF_TYPES = {
    "senior": {
        "label": "Sênior (Quirografária)",
        "prazo_min_meses": 24,
        "valor_min": 50000,
        "capital": None,
    },
    "subordinada_t2": {
        "label": "Subordinada Nível 2 (T2)",
        "prazo_min_meses": 60,
        "valor_min": 300000,
        "capital": "Nível 2",
    },
    "subordinada_at1": {
        "label": "Subordinada AT1 (Perpétua)",
        "prazo_min_meses": None,
        "valor_min": 300000,
        "capital": "Nível 1 / AT1",
    },
}

# Faixas de spread típicas por tipo e faixa de rating (em % a.a., sobre CDI)
SPREAD_RANGES = {
    "senior": {"min": 0.50, "max": 1.30},
    "subordinada_t2": {"min": 1.20, "max": 2.50},
    "subordinada_at1": {"min": 2.00, "max": 3.50},
}

# Mapeamento de indexadores
INDEXADORES = {
    "cdi": ["CDI", "DI", "% do CDI", "CDI+"],
    "ipca": ["IPCA", "IPCA+", "IGP-M"],
    "pre": ["PRÉ", "PRE", "PREFIXADO", "TAXA FIXA"],
}

# User-Agent para requests HTTP
USER_AGENT = "AgenteB3/2.0 (Pesquisa institucional)"

# Timeout para requests (segundos)
REQUEST_TIMEOUT = 30

# Versão do agente
VERSION = "2.0"
