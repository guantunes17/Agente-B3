"""
Configurações do UP2DATA — canais, mapeamento de colunas e paths.
"""
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# API do UP2DATA Cloud
# ═══════════════════════════════════════════════════════════════

UP2DATA_API_BASE = "https://api.up2data.com.br"
UP2DATA_TOKEN_ENDPOINT = "/api/oauth/token"
UP2DATA_SAS_ENDPOINT = "/api/sas-keys"

# Validade do token JWT: 24 horas (gerar apenas 1x/dia conforme boas práticas B3)
TOKEN_CACHE_HOURS = 24

# Validade das chaves SAS: 90 dias (renovar 5 dias antes)
SAS_VALIDITY_DAYS = 90

# ═══════════════════════════════════════════════════════════════
# Canais e pastas relevantes para Letras Financeiras
# ═══════════════════════════════════════════════════════════════

CANAIS_LF = {
    "negocio_a_negocio_rf": {
        "canal": "TradeByTrade_FixedIncome",
        "subcanal": "LF",
        "descricao": "Negócio a negócio — Renda Fixa — Letras Financeiras",
    },
    "cadastro_instrumento": {
        "canal": "MarketInformation",
        "subcanal": "FixedIncome/InstrumentFile",
        "descricao": "Cadastro de instrumento — Renda Fixa",
    },
    "info_negocios": {
        "canal": "MarketInformation",
        "subcanal": "FixedIncome/TradeInformation",
        "descricao": "Informações de negócios — Renda Fixa",
    },
    "lf_exclusivo": {
        "canal": "LF",
        "subcanal": "",
        "descricao": "Canal exclusivo de Letras Financeiras",
    },
}

# ═══════════════════════════════════════════════════════════════
# Mapeamento de colunas — do UP2DATA para o esquema do agente
#
# Chave: nome no esquema do agente
# Valor: lista de possíveis nomes de coluna no UP2DATA (tenta na ordem)
#
# NOTA: nomes abaixo são estimativas do Catálogo de Taxonomia público.
# Ajustar com os nomes reais quando o UP2DATA for contratado.
# ═══════════════════════════════════════════════════════════════

COLUMN_MAP = {
    "emissor":          ["IssrNm", "Issuer", "NmEmissor", "emissor", "Emitente"],
    "cnpj":             ["IssrCNPJ", "CNPJ", "TaxIdNb", "cnpj_emissor"],
    "tipo_lf":          ["InstrmTp", "InstrumentType", "TpInstrumento", "tipo"],
    "data_emissao":     ["IsseDt", "IssueDt", "DtEmissao", "data_emissao"],
    "data_vencimento":  ["MtrtyDt", "MaturityDt", "DtVencimento", "data_vencimento"],
    "valor_emissao":    ["NmnlVal", "NominalValue", "VlrNominal", "valor_nominal"],
    "indexador":        ["IndxCd", "IndexCode", "CdIndexador", "indexador"],
    "spread_percentual":["SprdRate", "SpreadRate", "TxSpread", "spread"],
    "isin":             ["ISIN", "Isin", "CdISIN"],
    "serie":            ["SrsNb", "SeriesNumber", "NrSerie", "serie"],
    "preco":            ["PricVal", "Price", "VlrPreco", "preco"],
    "volume":           ["TradQty", "TradeQuantity", "QtdNegociada", "volume"],
    "taxa":             ["Rate", "TxRate", "Taxa", "taxa"],
    "data_negocio":     ["TradDt", "TradeDate", "DtNegocio", "data_referencia"],
}

# ═══════════════════════════════════════════════════════════════
# Paths padrão para UP2DATA Client (diretório local)
# ═══════════════════════════════════════════════════════════════

DEFAULT_CLIENT_PATH = Path("C:/UP2DATA")

# Formatos suportados (em ordem de preferência para parsing)
FORMATOS_PREFERENCIA = ["csv", "json", "xml", "txt"]
