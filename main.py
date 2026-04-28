"""
Agente B3 — Ponto de entrada CLI.
Extrai, filtra e gera relatório profissional de Letras Financeiras.
Custo recorrente: R$ 0,00 (sem API de LLM).
"""
import argparse
import sys
import time
import logging
import io
from pathlib import Path
from datetime import date

# Forçar stdout UTF-8 no Windows para suportar caracteres especiais
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Garantir que o diretório raiz do projeto está no sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.filters import FiltrosConsulta, ESCALA_RATINGS
from config.settings import PRESETS_DIR, OUTPUTS_DIR, LOGS_DIR, VERSION
from utils.logger import configurar_logger

logger = logging.getLogger(__name__)

BANNER = (
    "\n"
    "+--------------------------------------------------------------+\n"
    f"  AGENTE B3 -- Letras Financeiras v{VERSION}\n"
    "  Analise de LFs Senior & Subordinadas | Custo: R$ 0,00\n"
    "+--------------------------------------------------------------+\n"
)


def executar_agente(
    filtros: FiltrosConsulta,
    verbose: bool = False,
    callback=None,
) -> dict:
    """
    Executa o pipeline completo do Agente B3.

    Args:
        filtros: Instância de FiltrosConsulta com todos os critérios.
        verbose: Ativa logging detalhado.
        callback: Função chamada a cada etapa: callback(etapa, total, mensagem).

    Returns:
        dict com: sucesso, arquivo, emissoes, emissoes_total, tempo,
                  filtros_aplicados, erro, avisos.
    """
    inicio = time.time()
    avisos = []
    resultado = {
        "sucesso": False,
        "arquivo": None,
        "emissoes": 0,
        "emissoes_total": 0,
        "tempo": 0.0,
        "filtros_aplicados": filtros.to_dict(),
        "erro": None,
        "avisos": avisos,
    }

    def _cb(etapa, total, msg):
        logger.info(f"[{etapa}/{total}] {msg}")
        if callback:
            callback(etapa, total, msg)

    total_etapas = 6

    try:
        # ── Etapa 1: Extração ──────────────────────────────────────────────
        _cb(1, total_etapas, "Extraindo dados das fontes...")
        import pandas as pd
        from extractors.anbima import AnbimaExtractor
        from extractors.cvm import CVMExtractor
        from extractors.bacen import BacenExtractor
        from extractors.b3_rjlf import B3RjlfExtractor

        extratores = [AnbimaExtractor(), CVMExtractor(), BacenExtractor(), B3RjlfExtractor()]
        fontes_usadas = []
        frames = []

        for ext in extratores:
            try:
                df_fonte = ext.extract(filtros)
                if df_fonte is not None and len(df_fonte) > 0:
                    frames.append(df_fonte)
                    fontes_usadas.append(ext.source_name)
                    logger.info(f"Fonte '{ext.source_name}': {len(df_fonte)} registros.")
            except Exception as e:
                aviso = f"Fonte '{ext.source_name}' falhou: {e}"
                logger.warning(aviso)
                avisos.append(aviso)

        if not frames:
            resultado["erro"] = "Nenhuma fonte retornou dados. Verifique conectividade ou ajuste o período."
            resultado["tempo"] = round(time.time() - inicio, 2)
            return resultado

        df_bruto = pd.concat(frames, ignore_index=True)
        total_bruto = len(df_bruto)
        logger.info(f"Total bruto consolidado: {total_bruto} registros de {len(fontes_usadas)} fonte(s).")

        # ── Etapa 2: Limpeza ───────────────────────────────────────────────
        _cb(2, total_etapas, f"Limpando e normalizando {total_bruto} registros...")
        from processors.cleaner import limpar_dados
        df_limpo = limpar_dados(df_bruto)
        total_apos_limpeza = len(df_limpo)

        # ── Etapa 3: Filtros dinâmicos ────────────────────────────────────
        _cb(3, total_etapas, f"Aplicando filtros ({filtros.descricao_rating()}, {filtros.descricao_periodo()})...")
        from processors.filter_engine import aplicar_filtros
        df_filtrado = aplicar_filtros(df_limpo, filtros)
        total_filtrado = len(df_filtrado)
        resultado["emissoes_total"] = total_apos_limpeza
        resultado["emissoes"] = total_filtrado

        if df_filtrado.empty:
            aviso = (
                f"Nenhuma emissão encontrada com os filtros aplicados "
                f"(rating {filtros.descricao_rating()}, período {filtros.descricao_periodo()}). "
                "Tente ampliar a faixa de rating ou o período."
            )
            logger.warning(aviso)
            avisos.append(aviso)

        # ── Etapa 4: Enriquecimento ────────────────────────────────────────
        _cb(4, total_etapas, "Calculando métricas e enriquecendo dados...")
        from processors.enricher import enriquecer
        df_enriquecido = enriquecer(df_filtrado, filtros)

        # ── Etapa 5: Geração do Word ───────────────────────────────────────
        _cb(5, total_etapas, "Gerando relatório Word (.docx)...")
        from report.docx_builder import gerar_docx

        output_path = None
        if filtros.output_dir:
            output_path_dir = Path(filtros.output_dir)
            output_path_dir.mkdir(parents=True, exist_ok=True)

        caminho = gerar_docx(
            df=df_enriquecido,
            filtros=filtros,
            fontes_usadas=fontes_usadas,
            total_antes_filtro=total_apos_limpeza,
            output_path=output_path,
        )

        resultado["arquivo"] = str(caminho)
        resultado["sucesso"] = True

        # ── Etapa 6: Finalização ───────────────────────────────────────────
        resultado["tempo"] = round(time.time() - inicio, 2)
        _cb(6, total_etapas, f"Concluído em {resultado['tempo']}s — {caminho.name}")

    except Exception as exc:
        resultado["erro"] = str(exc)
        resultado["tempo"] = round(time.time() - inicio, 2)
        logger.exception(f"Erro no pipeline: {exc}")

    return resultado


def _construir_filtros_cli(args: argparse.Namespace) -> FiltrosConsulta:
    """Constrói FiltrosConsulta a partir dos argumentos CLI."""
    # Se preset informado, carregar e ignorar demais filtros
    if args.preset:
        nome = args.preset.replace(" ", "_").lower()
        if not nome.endswith(".json"):
            nome += ".json"
        caminho_preset = PRESETS_DIR / nome
        if not caminho_preset.exists():
            print(f"[ERRO] Preset não encontrado: {caminho_preset}")
            sys.exit(1)
        filtros, nome_preset = FiltrosConsulta.carregar_preset(caminho_preset)
        print(f"Preset carregado: '{nome_preset}'")
        return filtros

    # Processar tipos de LF
    incluir_senior = True
    incluir_t2 = True
    incluir_at1 = True
    if args.tipos:
        tipos = [t.strip().lower() for t in args.tipos.split(",")]
        incluir_senior = "senior" in tipos
        incluir_t2 = "subordinada_t2" in tipos
        incluir_at1 = "subordinada_at1" in tipos

    # Processar emissores
    emissores = None
    if args.emissores:
        emissores = [e.strip() for e in args.emissores.split(",") if e.strip()]

    # Processar output_dir
    output_dir = str(args.output.parent) if args.output else None

    return FiltrosConsulta(
        rating_minimo=args.rating_min,
        rating_maximo=args.rating_max,
        periodo_meses=args.periodo,
        data_inicio=args.data_inicio,
        data_fim=args.data_fim,
        incluir_senior=incluir_senior,
        incluir_subordinada_t2=incluir_t2,
        incluir_subordinada_at1=incluir_at1,
        valor_minimo=args.valor_min,
        valor_maximo=args.valor_max,
        spread_minimo=args.spread_min,
        spread_maximo=args.spread_max,
        indexador=args.indexador,
        emissores=emissores,
        output_dir=output_dir,
    )


def _exibir_resumo_filtros(filtros: FiltrosConsulta) -> None:
    """Exibe resumo dos filtros ativos antes de executar."""
    print("\n── Filtros Ativos ──────────────────────────────────────────")
    print(f"  Rating:       {filtros.descricao_rating()}")
    print(f"  Período:      {filtros.descricao_periodo()}")
    tipos = filtros.obter_tipos_lf()
    from config.settings import LF_TYPES
    tipos_labels = [LF_TYPES.get(t, {}).get("label", t) for t in tipos]
    print(f"  Tipos de LF:  {', '.join(tipos_labels)}")
    if filtros.valor_minimo is not None or filtros.valor_maximo is not None:
        v_min = f"R$ {filtros.valor_minimo:,.0f}" if filtros.valor_minimo else "sem mínimo"
        v_max = f"R$ {filtros.valor_maximo:,.0f}" if filtros.valor_maximo else "sem máximo"
        print(f"  Valor:        {v_min} a {v_max}")
    if filtros.spread_minimo is not None or filtros.spread_maximo is not None:
        s_min = f"{filtros.spread_minimo:.2f}%" if filtros.spread_minimo is not None else "sem mínimo"
        s_max = f"{filtros.spread_maximo:.2f}%" if filtros.spread_maximo is not None else "sem máximo"
        print(f"  Spread CDI:   {s_min} a {s_max} a.a.")
    if filtros.indexador != "todos":
        print(f"  Indexador:    {filtros.indexador.upper()}")
    if filtros.emissores:
        print(f"  Emissores:    {', '.join(filtros.emissores)}")
    print("────────────────────────────────────────────────────────────\n")


def main():
    parser = argparse.ArgumentParser(
        description="Agente B3 — Relatório de Letras Financeiras",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python main.py\n"
            "  python main.py --rating-min A- --rating-max A+ --periodo 6\n"
            "  python main.py --rating-min BBB+ --rating-max AA- --periodo 24 --indexador cdi\n"
            "  python main.py --preset lfs_subordinadas_a_menos\n"
            "  python main.py --tipos senior,subordinada_t2 --spread-min 0.80 --spread-max 2.00\n"
        ),
    )

    parser.add_argument("--rating-min", default="A-", metavar="RATING",
                        help=f"Rating mínimo. Opções: {', '.join(ESCALA_RATINGS)} (padrão: A-)")
    parser.add_argument("--rating-max", default="A-", metavar="RATING",
                        help="Rating máximo (padrão: A-)")
    parser.add_argument("--periodo", type=int, default=12, metavar="MESES",
                        help="Meses para trás a partir de hoje (padrão: 12)")
    parser.add_argument("--data-inicio", default=None, metavar="YYYY-MM-DD",
                        help="Data início customizada (ignora --periodo)")
    parser.add_argument("--data-fim", default=None, metavar="YYYY-MM-DD",
                        help="Data fim customizada (ignora --periodo)")
    parser.add_argument("--tipos", default=None, metavar="TIPOS",
                        help="Tipos: senior,subordinada_t2,subordinada_at1 (padrão: todos)")
    parser.add_argument("--valor-min", type=float, default=None, metavar="VALOR",
                        help="Valor mínimo de emissão em R$ (padrão: sem mínimo)")
    parser.add_argument("--valor-max", type=float, default=None, metavar="VALOR",
                        help="Valor máximo de emissão em R$ (padrão: sem máximo)")
    parser.add_argument("--spread-min", type=float, default=None, metavar="PCT",
                        help="Spread mínimo sobre CDI em %% a.a. (padrão: sem mínimo)")
    parser.add_argument("--spread-max", type=float, default=None, metavar="PCT",
                        help="Spread máximo sobre CDI em %% a.a. (padrão: sem máximo)")
    parser.add_argument("--indexador", default="todos", metavar="IDX",
                        choices=["todos", "cdi", "ipca", "pre"],
                        help="Indexador: todos, cdi, ipca, pre (padrão: todos)")
    parser.add_argument("--emissores", default=None, metavar="NOMES",
                        help="Emissores separados por vírgula (padrão: todos)")
    parser.add_argument("--preset", default=None, metavar="NOME",
                        help="Carregar filtros de preset salvo")
    parser.add_argument("--output", type=Path, default=None, metavar="PATH",
                        help="Caminho do arquivo de saída (.docx)")
    parser.add_argument("--verbose", action="store_true",
                        help="Ativa logging detalhado (DEBUG)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra preview dos filtros sem gerar Word")
    parser.add_argument("--listar-presets", action="store_true",
                        help="Lista presets salvos disponíveis")
    parser.add_argument("--salvar-preset", default=None, metavar="NOME",
                        help="Salvar filtros atuais como preset com este nome")

    args = parser.parse_args()

    # Configurar logger
    configurar_logger(verbose=args.verbose, logs_dir=LOGS_DIR)

    print(BANNER)

    # Listar presets
    if args.listar_presets:
        presets = FiltrosConsulta.listar_presets(PRESETS_DIR)
        if not presets:
            print("Nenhum preset salvo encontrado.")
        else:
            print(f"Presets disponíveis ({len(presets)}):")
            for p in presets:
                print(f"  • {p['nome']} — {p['arquivo']} ({p['criado_em'][:10]})")
        sys.exit(0)

    # Construir filtros
    filtros = _construir_filtros_cli(args)

    # Validar filtros
    erros = filtros.validar()
    if erros:
        print("[ERRO] Filtros inválidos:")
        for e in erros:
            print(f"  • {e}")
        sys.exit(1)

    # Exibir resumo dos filtros
    _exibir_resumo_filtros(filtros)

    # Salvar como preset
    if args.salvar_preset:
        caminho_preset = filtros.salvar_preset(args.salvar_preset, PRESETS_DIR)
        print(f"Filtros salvos como preset: {caminho_preset}")

    # Dry run
    if args.dry_run:
        print("[DRY-RUN] Preview dos filtros exibido. Nenhum relatório gerado.")
        sys.exit(0)

    # Executar pipeline
    print("Iniciando pipeline...\n")
    resultado = executar_agente(filtros=filtros, verbose=args.verbose)

    # Exibir resultado
    print("\n── Resultado ───────────────────────────────────────────────")
    if resultado["sucesso"]:
        print(f"  Status:       OK")
        print(f"  Emissões:     {resultado['emissoes']} selecionadas / {resultado['emissoes_total']} total")
        print(f"  Arquivo:      {resultado['arquivo']}")
        print(f"  Tempo:        {resultado['tempo']}s")
    else:
        print(f"  Status:       ERRO")
        print(f"  Erro:         {resultado['erro']}")

    if resultado["avisos"]:
        print("\n  Avisos:")
        for av in resultado["avisos"]:
            print(f"    ⚠ {av}")

    print("────────────────────────────────────────────────────────────\n")

    sys.exit(0 if resultado["sucesso"] else 1)


if __name__ == "__main__":
    main()
