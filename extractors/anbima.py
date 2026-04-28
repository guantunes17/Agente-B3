"""
Extrator ANBIMA Data — dados públicos de Letras Financeiras.
Utiliza fallback com dados mock realistas quando a API não retorna dados.
"""
import logging
import pandas as pd
from datetime import date, timedelta
from config.filters import FiltrosConsulta
from extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

# URL pública da ANBIMA para busca de debêntures/LFs (ajustar conforme disponibilidade)
ANBIMA_URL = "https://data.anbima.com.br/debentures/busca"


def _gerar_dados_mock(filtros: FiltrosConsulta) -> pd.DataFrame:
    """
    Gera dados mock realistas para testes quando a API não está disponível.
    Inclui 6 emissores com ratings e tipos variados para testar todos os filtros.
    """
    logger.warning(
        "ANBIMA: usando dados mock — API indisponível ou sem retorno para o período selecionado."
    )

    data_inicio = filtros.obter_data_inicio()
    data_fim = filtros.obter_data_fim()

    # Referência de datas das emissões mock
    def d(ano, mes, dia):
        dt = date(ano, mes, dia)
        return dt if data_inicio <= dt <= data_fim else None

    registros = [
        # 1. Banco ABC Brasil — A-(bra) Fitch
        {
            "emissor": "Banco ABC Brasil S.A.",
            "cnpj": "28.195.667/0001-06",
            "rating_agencia": "Fitch",
            "rating_nota": "A-(bra)",
            "tipo_lf": "senior",
            "data_emissao": d(2024, 1, 15),
            "data_vencimento": date(2026, 1, 25),
            "valor_emissao": 600_200_000.0,
            "indexador": "CDI",
            "spread_percentual": 0.90,
            "prazo_dias": 740,
            "serie": "1ª",
            "modalidade": "LF Sênior",
            "fonte": "ANBIMA (mock)",
        },
        {
            "emissor": "Banco ABC Brasil S.A.",
            "cnpj": "28.195.667/0001-06",
            "rating_agencia": "Fitch",
            "rating_nota": "A-(bra)",
            "tipo_lf": "subordinada_t2",
            "data_emissao": d(2024, 1, 20),
            "data_vencimento": date(2029, 1, 20),
            "valor_emissao": 250_200_000.0,
            "indexador": "CDI",
            "spread_percentual": 1.75,
            "prazo_dias": 1827,
            "serie": "2ª",
            "modalidade": "LF Subordinada T2",
            "fonte": "ANBIMA (mock)",
        },
        {
            "emissor": "Banco ABC Brasil S.A.",
            "cnpj": "28.195.667/0001-06",
            "rating_agencia": "Fitch",
            "rating_nota": "A-(bra)",
            "tipo_lf": "subordinada_at1",
            "data_emissao": d(2024, 3, 10),
            "data_vencimento": None,  # Perpétua
            "valor_emissao": 500_000_000.0,
            "indexador": "CDI",
            "spread_percentual": 3.00,
            "prazo_dias": None,
            "serie": "1ª",
            "modalidade": "LF Subordinada AT1",
            "fonte": "ANBIMA (mock)",
        },
        # 2. Banco Pine — A-.br Moody's
        {
            "emissor": "Banco Pine S.A.",
            "cnpj": "62.144.175/0001-20",
            "rating_agencia": "Moody's",
            "rating_nota": "A-.br",
            "tipo_lf": "subordinada_t2",
            "data_emissao": d(2024, 1, 25),
            "data_vencimento": date(2029, 1, 25),
            "valor_emissao": 180_000_000.0,
            "indexador": "CDI",
            "spread_percentual": 1.85,
            "prazo_dias": 1827,
            "serie": "75ª",
            "modalidade": "LF Subordinada T2",
            "fonte": "ANBIMA (mock)",
        },
        {
            "emissor": "Banco Pine S.A.",
            "cnpj": "62.144.175/0001-20",
            "rating_agencia": "Moody's",
            "rating_nota": "A-.br",
            "tipo_lf": "senior",
            "data_emissao": d(2024, 6, 10),
            "data_vencimento": date(2027, 6, 10),
            "valor_emissao": 320_000_000.0,
            "indexador": "CDI",
            "spread_percentual": 0.95,
            "prazo_dias": 1096,
            "serie": "76ª",
            "modalidade": "LF Sênior",
            "fonte": "ANBIMA (mock)",
        },
        # 3. Caixa Econômica Federal — AA(bra) Fitch (fora da faixa A-)
        {
            "emissor": "Caixa Econômica Federal",
            "cnpj": "00.360.305/0001-04",
            "rating_agencia": "Fitch",
            "rating_nota": "AA(bra)",
            "tipo_lf": "senior",
            "data_emissao": d(2024, 11, 5),
            "data_vencimento": date(2027, 5, 5),
            "valor_emissao": 4_600_000_000.0,
            "indexador": "CDI",
            "spread_percentual": 0.70,
            "prazo_dias": 912,
            "serie": "10ª",
            "modalidade": "LF Sênior",
            "fonte": "ANBIMA (mock)",
        },
        # 4. Banco Daycoval — A.br Moody's (faixa A- a A)
        {
            "emissor": "Banco Daycoval S.A.",
            "cnpj": "62.232.889/0001-90",
            "rating_agencia": "Moody's",
            "rating_nota": "A.br",
            "tipo_lf": "senior",
            "data_emissao": d(2024, 9, 3),
            "data_vencimento": date(2026, 9, 3),
            "valor_emissao": 750_000_000.0,
            "indexador": "CDI",
            "spread_percentual": 0.85,
            "prazo_dias": 731,
            "serie": "5ª",
            "modalidade": "LF Sênior",
            "fonte": "ANBIMA (mock)",
        },
        {
            "emissor": "Banco Daycoval S.A.",
            "cnpj": "62.232.889/0001-90",
            "rating_agencia": "Moody's",
            "rating_nota": "A.br",
            "tipo_lf": "subordinada_t2",
            "data_emissao": d(2024, 12, 2),
            "data_vencimento": date(2029, 12, 2),
            "valor_emissao": 400_000_000.0,
            "indexador": "CDI",
            "spread_percentual": 1.60,
            "prazo_dias": 1827,
            "serie": "6ª",
            "modalidade": "LF Subordinada T2",
            "fonte": "ANBIMA (mock)",
        },
        # 5. Banco Votorantim — AA-(bra) Fitch, IPCA
        {
            "emissor": "Banco Votorantim S.A.",
            "cnpj": "59.588.111/0001-03",
            "rating_agencia": "Fitch",
            "rating_nota": "AA-(bra)",
            "tipo_lf": "senior",
            "data_emissao": d(2024, 8, 12),
            "data_vencimento": date(2027, 8, 12),
            "valor_emissao": 1_200_000_000.0,
            "indexador": "IPCA",
            "spread_percentual": 5.50,
            "prazo_dias": 1096,
            "serie": "8ª",
            "modalidade": "LF Sênior IPCA",
            "fonte": "ANBIMA (mock)",
        },
        # 6. Banco BMG — BBB+(bra) Fitch (abaixo de A-)
        {
            "emissor": "Banco BMG S.A.",
            "cnpj": "61.186.680/0001-74",
            "rating_agencia": "Fitch",
            "rating_nota": "BBB+(bra)",
            "tipo_lf": "senior",
            "data_emissao": d(2024, 7, 8),
            "data_vencimento": date(2026, 7, 8),
            "valor_emissao": 200_000_000.0,
            "indexador": "CDI",
            "spread_percentual": 1.40,
            "prazo_dias": 731,
            "serie": "3ª",
            "modalidade": "LF Sênior",
            "fonte": "ANBIMA (mock)",
        },
    ]

    # Filtrar registros com data_emissao fora do período (retornaram None)
    registros_validos = [r for r in registros if r["data_emissao"] is not None]

    if not registros_validos:
        logger.warning(
            f"Nenhum dado mock dentro do período {data_inicio} a {data_fim}. "
            "Use --periodo maior (ex: --periodo 24) para capturar os dados de demonstração."
        )
        return pd.DataFrame(columns=[
            "emissor", "cnpj", "rating_agencia", "rating_nota", "tipo_lf",
            "data_emissao", "data_vencimento", "valor_emissao", "indexador",
            "spread_percentual", "prazo_dias", "serie", "modalidade", "fonte",
        ])

    df = pd.DataFrame(registros_validos)
    df["data_emissao"] = pd.to_datetime(df["data_emissao"])
    df["data_vencimento"] = pd.to_datetime(df["data_vencimento"])
    logger.info(f"ANBIMA mock: {len(df)} emissões carregadas para o período.")
    return df


class AnbimaExtractor(BaseExtractor):
    """Extrator de dados ANBIMA Data para Letras Financeiras."""

    @property
    def source_name(self) -> str:
        return "ANBIMA Data"

    def extract(self, filtros: FiltrosConsulta) -> pd.DataFrame:
        """
        Tenta extrair dados da ANBIMA. Em caso de falha, usa dados mock realistas.
        """
        data_inicio = filtros.obter_data_inicio()
        data_fim = filtros.obter_data_fim()
        logger.info(
            f"ANBIMA: iniciando extração para o período {data_inicio} a {data_fim}..."
        )

        try:
            df = self._extrair_api(data_inicio, data_fim)
            if df is not None and len(df) > 0:
                logger.info(f"ANBIMA API: {len(df)} registros obtidos.")
                return self._garantir_colunas(df)
        except Exception as exc:
            logger.warning(f"ANBIMA API falhou: {exc}. Ativando fallback mock.")

        return _gerar_dados_mock(filtros)

    def _extrair_api(self, data_inicio, data_fim) -> pd.DataFrame | None:
        """
        Tenta extrair dados reais da ANBIMA.
        Retorna None se indisponível.
        """
        import requests
        from config.settings import USER_AGENT, REQUEST_TIMEOUT

        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        params = {
            "dataInicio": data_inicio.strftime("%Y-%m-%d"),
            "dataFim": data_fim.strftime("%Y-%m-%d"),
            "tipoAtivo": "LF",
        }

        resposta = requests.get(
            ANBIMA_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT
        )

        if resposta.status_code != 200:
            logger.warning(f"ANBIMA API retornou status {resposta.status_code}.")
            return None

        dados = resposta.json()
        if not dados:
            return None

        # Mapeamento dos campos da API ANBIMA para o schema padronizado
        registros = []
        for item in dados:
            registros.append({
                "emissor": item.get("nomeEmissor", ""),
                "cnpj": item.get("cnpjEmissor", ""),
                "rating_agencia": item.get("agenciaRating", ""),
                "rating_nota": item.get("rating", ""),
                "tipo_lf": self._mapear_tipo(item.get("modalidade", "")),
                "data_emissao": item.get("dataEmissao"),
                "data_vencimento": item.get("dataVencimento"),
                "valor_emissao": item.get("valorEmissao"),
                "indexador": item.get("indexador", ""),
                "spread_percentual": item.get("spread"),
                "prazo_dias": item.get("prazoDias"),
                "serie": item.get("serie", ""),
                "modalidade": item.get("modalidade", ""),
                "fonte": "ANBIMA Data",
            })

        df = pd.DataFrame(registros)
        df["data_emissao"] = pd.to_datetime(df["data_emissao"], errors="coerce")
        df["data_vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce")
        return df

    def _mapear_tipo(self, modalidade: str) -> str:
        """Mapeia a modalidade textual para os tipos internos."""
        m = modalidade.upper()
        if "SUBORDINAD" in m and ("AT1" in m or "PERPÉTUA" in m or "PERPETUA" in m or "NÍVEL 1" in m):
            return "subordinada_at1"
        if "SUBORDINAD" in m and ("T2" in m or "NÍVEL 2" in m or "NIVEL 2" in m):
            return "subordinada_t2"
        return "senior"
