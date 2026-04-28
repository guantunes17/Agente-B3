"""
Definição dos filtros dinâmicos do Agente B3.
Todos os critérios de consulta são configuráveis — nenhum é hardcoded.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

# Escala ordenada de ratings (do mais baixo ao mais alto)
ESCALA_RATINGS = [
    "BBB-", "BBB", "BBB+",
    "A-", "A", "A+",
    "AA-", "AA", "AA+",
    "AAA",
]

# Mapeamento de equivalências entre agências
EQUIVALENCIAS_RATING = {
    # Fitch (escala nacional)
    "BBB-(bra)": "BBB-", "BBB(bra)": "BBB", "BBB+(bra)": "BBB+",
    "A-(bra)": "A-", "A(bra)": "A", "A+(bra)": "A+",
    "AA-(bra)": "AA-", "AA(bra)": "AA", "AA+(bra)": "AA+",
    "AAA(bra)": "AAA",
    # S&P (escala nacional)
    "brBBB-": "BBB-", "brBBB": "BBB", "brBBB+": "BBB+",
    "brA-": "A-", "brA": "A", "brA+": "A+",
    "brAA-": "AA-", "brAA": "AA", "brAA+": "AA+",
    "brAAA": "AAA",
    # Moody's Local Brasil
    "Baa3.br": "BBB-", "Baa2.br": "BBB", "Baa1.br": "BBB+",
    "A3.br": "A-", "A2.br": "A", "A1.br": "A+",
    "Aa3.br": "AA-", "Aa2.br": "AA", "Aa1.br": "AA+",
    "Aaa.br": "AAA",
    # Versões com ponto (Moody's Local simplificado)
    "BBB-.br": "BBB-", "BBB.br": "BBB", "BBB+.br": "BBB+",
    "A-.br": "A-", "A.br": "A", "A+.br": "A+",
    "AA-.br": "AA-", "AA.br": "AA", "AA+.br": "AA+",
    "AAA.br": "AAA",
}


def normalizar_rating(rating_original: str) -> str | None:
    """Normaliza um rating de qualquer agência para a escala padronizada."""
    if not rating_original:
        return None
    rating = rating_original.strip()
    # Já está na escala padrão?
    if rating in ESCALA_RATINGS:
        return rating
    # Buscar equivalência
    return EQUIVALENCIAS_RATING.get(rating, None)


def rating_no_intervalo(rating_normalizado: str, minimo: str, maximo: str) -> bool:
    """Verifica se um rating normalizado está dentro do intervalo [minimo, maximo]."""
    if rating_normalizado not in ESCALA_RATINGS:
        return False
    idx = ESCALA_RATINGS.index(rating_normalizado)
    idx_min = ESCALA_RATINGS.index(minimo) if minimo in ESCALA_RATINGS else 0
    idx_max = ESCALA_RATINGS.index(maximo) if maximo in ESCALA_RATINGS else len(ESCALA_RATINGS) - 1
    return idx_min <= idx <= idx_max


@dataclass
class FiltrosConsulta:
    """Filtros dinâmicos para consulta de Letras Financeiras."""

    # Rating corporativo — faixa
    rating_minimo: str = "A-"
    rating_maximo: str = "A-"

    # Período de análise
    periodo_meses: int = 12
    data_inicio: str | None = None  # YYYY-MM-DD — se definido, ignora periodo_meses
    data_fim: str | None = None     # YYYY-MM-DD — se definido, ignora periodo_meses

    # Tipos de LF
    incluir_senior: bool = True
    incluir_subordinada_t2: bool = True
    incluir_subordinada_at1: bool = True

    # Valor da emissão (R$)
    valor_minimo: float | None = None
    valor_maximo: float | None = None

    # Spread sobre CDI (% a.a.)
    spread_minimo: float | None = None
    spread_maximo: float | None = None

    # Indexador
    indexador: str = "todos"  # "todos", "cdi", "ipca", "pre"

    # Emissores específicos
    emissores: list[str] | None = None

    # Pasta de destino
    output_dir: str | None = None

    def obter_data_inicio(self) -> date:
        """Retorna a data de início efetiva (customizada ou calculada pelo período)."""
        if self.data_inicio:
            return date.fromisoformat(self.data_inicio)
        return date.today() - relativedelta(months=self.periodo_meses)

    def obter_data_fim(self) -> date:
        """Retorna a data de fim efetiva."""
        if self.data_fim:
            return date.fromisoformat(self.data_fim)
        return date.today()

    def obter_tipos_lf(self) -> list[str]:
        """Retorna lista dos tipos de LF selecionados."""
        tipos = []
        if self.incluir_senior:
            tipos.append("senior")
        if self.incluir_subordinada_t2:
            tipos.append("subordinada_t2")
        if self.incluir_subordinada_at1:
            tipos.append("subordinada_at1")
        return tipos

    def descricao_rating(self) -> str:
        """Retorna descrição legível da faixa de rating."""
        if self.rating_minimo == self.rating_maximo:
            return self.rating_minimo
        return f"{self.rating_minimo} a {self.rating_maximo}"

    def descricao_periodo(self) -> str:
        """Retorna descrição legível do período."""
        if self.data_inicio and self.data_fim:
            return f"{self.data_inicio} a {self.data_fim}"
        inicio = self.obter_data_inicio().strftime("%d/%m/%Y")
        fim = self.obter_data_fim().strftime("%d/%m/%Y")
        return f"{inicio} a {fim} (últimos {self.periodo_meses} meses)"

    def validar(self) -> list[str]:
        """Valida os filtros. Retorna lista de erros (vazia se válido)."""
        erros = []
        if self.rating_minimo not in ESCALA_RATINGS:
            erros.append(f"Rating mínimo inválido: {self.rating_minimo}")
        if self.rating_maximo not in ESCALA_RATINGS:
            erros.append(f"Rating máximo inválido: {self.rating_maximo}")
        if self.rating_minimo in ESCALA_RATINGS and self.rating_maximo in ESCALA_RATINGS:
            if ESCALA_RATINGS.index(self.rating_minimo) > ESCALA_RATINGS.index(self.rating_maximo):
                erros.append("Rating mínimo não pode ser maior que o máximo.")
        if not any([self.incluir_senior, self.incluir_subordinada_t2, self.incluir_subordinada_at1]):
            erros.append("Selecione pelo menos um tipo de LF.")
        if self.valor_minimo is not None and self.valor_maximo is not None:
            if self.valor_minimo > self.valor_maximo:
                erros.append("Valor mínimo não pode ser maior que o máximo.")
        if self.spread_minimo is not None and self.spread_maximo is not None:
            if self.spread_minimo > self.spread_maximo:
                erros.append("Spread mínimo não pode ser maior que o máximo.")
        if self.indexador not in ("todos", "cdi", "ipca", "pre"):
            erros.append(f"Indexador inválido: {self.indexador}")
        return erros

    def to_dict(self) -> dict:
        """Serializa para dicionário (para salvar como preset JSON)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "FiltrosConsulta":
        """Cria instância a partir de dicionário."""
        campos_validos = {f for f in cls.__dataclass_fields__}
        d_filtrado = {k: v for k, v in d.items() if k in campos_validos}
        return cls(**d_filtrado)

    def salvar_preset(self, nome: str, pasta_presets: Path) -> Path:
        """Salva os filtros como preset JSON."""
        pasta_presets.mkdir(parents=True, exist_ok=True)
        nome_arquivo = nome.replace(" ", "_").lower() + ".json"
        caminho = pasta_presets / nome_arquivo
        dados = {
            "nome": nome,
            "criado_em": datetime.now().isoformat(),
            "filtros": self.to_dict(),
        }
        caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Preset salvo: {caminho}")
        return caminho

    @classmethod
    def carregar_preset(cls, caminho: Path) -> tuple["FiltrosConsulta", str]:
        """Carrega filtros de um preset JSON. Retorna (filtros, nome_do_preset)."""
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        filtros = cls.from_dict(dados.get("filtros", {}))
        nome = dados.get("nome", caminho.stem)
        return filtros, nome

    @classmethod
    def listar_presets(cls, pasta_presets: Path) -> list[dict]:
        """Lista presets disponíveis. Retorna lista de {nome, arquivo, criado_em}."""
        pasta_presets.mkdir(parents=True, exist_ok=True)
        presets = []
        for arquivo in sorted(pasta_presets.glob("*.json")):
            try:
                dados = json.loads(arquivo.read_text(encoding="utf-8"))
                presets.append({
                    "nome": dados.get("nome", arquivo.stem),
                    "arquivo": str(arquivo),
                    "criado_em": dados.get("criado_em", ""),
                })
            except Exception:
                continue
        return presets
