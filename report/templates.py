"""
Templates de texto parametrizados para o relatório de Letras Financeiras.
Todo o texto é gerado em Python — sem LLM.
Linguagem executiva em português do Brasil.
"""
from datetime import date
from typing import Any
import pandas as pd
from config.filters import FiltrosConsulta
from config.settings import LF_TYPES
from utils.helpers import (
    formatar_brl_milhoes,
    formatar_percentual,
    formatar_data,
    formatar_spread,
)


def gerar_titulo_relatorio(filtros: FiltrosConsulta) -> str:
    """Retorna o título principal do relatório."""
    return (
        f"LETRAS FINANCEIRAS\n"
        f"Sênior & Subordinadas\n"
        f"Financeiras com Rating Corporativo {filtros.descricao_rating()} "
        f"| {filtros.descricao_periodo()}"
    )


def gerar_cabecalho_header(filtros: FiltrosConsulta) -> str:
    """Retorna texto para o cabeçalho (header) do documento Word."""
    return (
        f"ANÁLISE DE LETRAS FINANCEIRAS — RATING {filtros.descricao_rating()} "
        f"| Período: {filtros.descricao_periodo()}"
    )


def gerar_nota_metodologica(
    filtros: FiltrosConsulta,
    fontes_usadas: list[str],
    total_registros: int,
    total_antes_filtro: int,
) -> str:
    """
    Gera nota metodológica descrevendo os critérios aplicados e as fontes consultadas.
    """
    tipos_labels = [LF_TYPES[t]["label"] for t in filtros.obter_tipos_lf() if t in LF_TYPES]
    tipos_texto = ", ".join(tipos_labels) if tipos_labels else "todos os tipos"

    filtros_desc = [
        f"Rating corporativo: {filtros.descricao_rating()}",
        f"Período de análise: {filtros.descricao_periodo()}",
        f"Tipos de LF: {tipos_texto}",
    ]

    if filtros.valor_minimo is not None or filtros.valor_maximo is not None:
        v_min = formatar_brl_milhoes(filtros.valor_minimo) if filtros.valor_minimo else "sem mínimo"
        v_max = formatar_brl_milhoes(filtros.valor_maximo) if filtros.valor_maximo else "sem máximo"
        filtros_desc.append(f"Valor de emissão: {v_min} a {v_max}")

    if filtros.spread_minimo is not None or filtros.spread_maximo is not None:
        s_min = f"{filtros.spread_minimo:.2f}%" if filtros.spread_minimo is not None else "sem mínimo"
        s_max = f"{filtros.spread_maximo:.2f}%" if filtros.spread_maximo is not None else "sem máximo"
        filtros_desc.append(f"Spread sobre CDI: {s_min} a {s_max} a.a.")

    if filtros.indexador != "todos":
        filtros_desc.append(f"Indexador: {filtros.indexador.upper()}")

    if filtros.emissores:
        filtros_desc.append(f"Emissores: {', '.join(filtros.emissores)}")

    filtros_texto = "\n".join(f"  • {f}" for f in filtros_desc)
    fontes_texto = ", ".join(fontes_usadas) if fontes_usadas else "ANBIMA Data"

    return (
        f"NOTA METODOLÓGICA\n\n"
        f"O presente relatório foi elaborado a partir da consolidação e análise de dados "
        f"públicos de emissões de Letras Financeiras (LFs), coletados das seguintes fontes: "
        f"{fontes_texto}.\n\n"
        f"Critérios de seleção aplicados:\n"
        f"{filtros_texto}\n\n"
        f"Universo: {total_antes_filtro} emissões identificadas no período. "
        f"Após aplicação dos filtros, {total_registros} emissões "
        f"{'foi selecionada' if total_registros == 1 else 'foram selecionadas'} para análise.\n\n"
        f"As classificações de rating utilizadas seguem a escala nacional harmonizada "
        f"(Fitch Nacional, S&P Escala Nacional e Moody's Local Brasil), normalizadas para "
        f"uma escala comparativa única: BBB- | BBB | BBB+ | A- | A | A+ | AA- | AA | AA+ | AAA.\n\n"
        f"O custo operacional deste agente é R$ 0,00 — nenhuma API de inteligência artificial "
        f"foi utilizada na geração deste relatório."
    )


def gerar_sumario_executivo(
    df: pd.DataFrame,
    filtros: FiltrosConsulta,
    total_antes_filtro: int,
) -> str:
    """
    Gera o sumário executivo do relatório com base nos dados filtrados.
    """
    if df.empty:
        return (
            f"SUMÁRIO EXECUTIVO\n\n"
            f"A análise do período {filtros.descricao_periodo()} não identificou emissões de "
            f"Letras Financeiras com os critérios selecionados (rating {filtros.descricao_rating()}).\n\n"
            f"Recomenda-se ampliar o período de análise ou ajustar os filtros de rating para "
            f"capturar um universo mais amplo de emissores."
        )

    n = len(df)
    emissores_unicos = df["emissor"].nunique()
    valor_total = df["valor_emissao"].sum()
    spread_medio = df["spread_percentual"].mean()

    # Contagem por tipo
    contagem_tipo = df["tipo_lf"].value_counts()
    n_senior = contagem_tipo.get("senior", 0)
    n_t2 = contagem_tipo.get("subordinada_t2", 0)
    n_at1 = contagem_tipo.get("subordinada_at1", 0)

    partes_tipo = []
    if n_senior > 0:
        partes_tipo.append(f"{n_senior} Sênior")
    if n_t2 > 0:
        partes_tipo.append(f"{n_t2} Subordinada T2")
    if n_at1 > 0:
        partes_tipo.append(f"{n_at1} Subordinada AT1")
    tipo_texto = ", ".join(partes_tipo)

    # Maior emissão
    idx_maior = df["valor_emissao"].idxmax() if df["valor_emissao"].notna().any() else None
    maior_texto = ""
    if idx_maior is not None:
        row = df.loc[idx_maior]
        maior_texto = (
            f" A maior operação do período foi a emissão de "
            f"{formatar_brl_milhoes(row['valor_emissao'])} pelo {row['emissor']}, "
            f"registrada em {formatar_data(row['data_emissao'])}."
        )

    # Spread médio
    spread_texto = ""
    if pd.notna(spread_medio):
        spread_texto = (
            f" O spread médio sobre o CDI das emissões selecionadas foi de "
            f"{spread_medio:.2f}% a.a.".replace(".", ",")
        )

    return (
        f"SUMÁRIO EXECUTIVO\n\n"
        f"No período analisado ({filtros.descricao_periodo()}), foram identificadas "
        f"{n} {'emissão' if n == 1 else 'emissões'} de Letras Financeiras de "
        f"instituições financeiras com rating corporativo {filtros.descricao_rating()}, "
        f"totalizando {formatar_brl_milhoes(valor_total)} em captações. "
        f"O universo consultado contemplou {total_antes_filtro} registros, "
        f"dos quais {n} atenderam aos critérios estabelecidos.\n\n"
        f"As operações abrangeram {emissores_unicos} "
        f"{'emissor' if emissores_unicos == 1 else 'emissores'} distintos, "
        f"distribuídas entre: {tipo_texto}.{spread_texto}{maior_texto}\n\n"
        f"A presente análise tem caráter estritamente informativo e não constitui "
        f"recomendação de investimento."
    )


def gerar_analise_emissor(emissor_dict: dict[str, Any]) -> str:
    """
    Gera análise textual de um emissor específico.

    Parâmetros esperados em emissor_dict:
        nome, rating, emissoes (lista de dicts com tipo_lf, valor_emissao,
        data_emissao, indexador, spread_percentual, prazo_label)
    """
    nome = emissor_dict.get("nome", "N/D")
    rating = emissor_dict.get("rating", "N/D")
    emissoes = emissor_dict.get("emissoes", [])

    if not emissoes:
        return f"{nome} (Rating: {rating})\n\nNenhuma emissão identificada no período analisado."

    valor_total = sum(e.get("valor_emissao", 0) or 0 for e in emissoes)
    n = len(emissoes)

    linhas_emissoes = []
    for e in emissoes:
        tipo_label = LF_TYPES.get(e.get("tipo_lf", ""), {}).get("label", e.get("tipo_lf", ""))
        spread = e.get("spread_percentual")
        idx = e.get("indexador", "CDI")
        prazo = e.get("prazo_label", "N/D")
        data_str = formatar_data(e.get("data_emissao"))
        valor_str = formatar_brl_milhoes(e.get("valor_emissao"))

        if str(idx).upper() in ("CDI", "DI"):
            taxa_str = formatar_spread(spread)
        else:
            taxa_str = f"{idx} + {spread:.2f}% a.a.".replace(".", ",") if spread else f"{idx}"

        linhas_emissoes.append(
            f"  • {tipo_label}: {valor_str} | {data_str} | {taxa_str} | Prazo: {prazo}"
        )

    emissoes_texto = "\n".join(linhas_emissoes)

    return (
        f"{nome} — Rating {rating}\n\n"
        f"No período analisado, {nome} realizou {n} "
        f"{'emissão' if n == 1 else 'emissões'} de Letras Financeiras, "
        f"totalizando {formatar_brl_milhoes(valor_total)} em captações:\n\n"
        f"{emissoes_texto}"
    )


def gerar_contexto_macro() -> str:
    """
    Gera o contexto macroeconômico padronizado do mercado de LFs no Brasil.
    """
    ano_atual = date.today().year
    return (
        f"CONTEXTO MACROECONÔMICO E DO MERCADO DE LETRAS FINANCEIRAS\n\n"
        f"As Letras Financeiras (LFs) constituem o principal instrumento de captação de "
        f"médio e longo prazo para instituições financeiras no Brasil, regulamentadas pela "
        f"Lei nº 12.249/2010 e pela Resolução CMN nº 4.123/2012. O mercado de LFs tem "
        f"apresentado crescimento consistente nos últimos anos, impulsionado tanto pela "
        f"demanda dos investidores institucionais por instrumentos com maior prazo e "
        f"rentabilidade diferenciada, quanto pela necessidade das instituições financeiras "
        f"de alongar o perfil de suas captações.\n\n"
        f"As LFs Subordinadas — Nível 2 (T2) e Adicionais de Nível 1 (AT1) — têm ganhado "
        f"relevância crescente no contexto de enquadramento às regras de Basileia III, "
        f"implementadas no Brasil pelo Banco Central por meio da Resolução CMN nº 4.192/2013. "
        f"As emissões subordinadas, especialmente as AT1 (perpétuas), oferecem spreads mais "
        f"elevados em compensação à sua posição na estrutura de capital e à cláusula de "
        f"absorção de perdas.\n\n"
        f"No ambiente de {ano_atual}, o nível da taxa Selic e as perspectivas de política "
        f"monetária têm influência direta sobre o custo de captação via LFs, "
        f"especialmente para aquelas indexadas ao CDI. Instituições com ratings mais elevados "
        f"tendem a captar com spreads menores, refletindo o menor risco percebido pelo mercado.\n\n"
        f"A qualidade creditícia dos emissores, medida pelo rating corporativo nas escalas "
        f"nacionais (Fitch, S&P e Moody's Local Brasil), é fator determinante tanto no "
        f"volume captado quanto nas condições (prazo, spread) obtidas nas emissões."
    )


def gerar_consideracoes_finais(df_resumo: pd.DataFrame, filtros: FiltrosConsulta) -> str:
    """
    Gera as considerações finais adaptadas à faixa de rating e período analisados.
    """
    n = len(df_resumo)
    rating_desc = filtros.descricao_rating()
    periodo_desc = filtros.descricao_periodo()

    if df_resumo.empty:
        return (
            f"CONSIDERAÇÕES FINAIS\n\n"
            f"A análise do mercado de Letras Financeiras para o perfil de rating {rating_desc} "
            f"no período {periodo_desc} não resultou em registros suficientes para análise "
            f"comparativa. Sugere-se ampliar o horizonte temporal ou revisar os critérios de filtragem."
        )

    emissores_unicos = df_resumo["emissor"].nunique()
    valor_total = df_resumo["valor_emissao"].sum()

    # Spread médio por tipo
    por_tipo = df_resumo.groupby("tipo_lf")["spread_percentual"].mean()
    spread_senior = por_tipo.get("senior")
    spread_t2 = por_tipo.get("subordinada_t2")
    spread_at1 = por_tipo.get("subordinada_at1")

    partes_spread = []
    if spread_senior is not None and pd.notna(spread_senior):
        partes_spread.append(f"LFs Sênior: CDI + {spread_senior:.2f}% a.a. em média".replace(".", ","))
    if spread_t2 is not None and pd.notna(spread_t2):
        partes_spread.append(f"LFs T2: CDI + {spread_t2:.2f}% a.a. em média".replace(".", ","))
    if spread_at1 is not None and pd.notna(spread_at1):
        partes_spread.append(f"LFs AT1: CDI + {spread_at1:.2f}% a.a. em média".replace(".", ","))

    spread_texto = ""
    if partes_spread:
        spread_texto = (
            f" As condições médias de precificação observadas foram: "
            f"{'; '.join(partes_spread)}."
        )

    return (
        f"CONSIDERAÇÕES FINAIS\n\n"
        f"A análise das Letras Financeiras emitidas por instituições com rating {rating_desc} "
        f"no período {periodo_desc} evidenciou {n} "
        f"{'operação' if n == 1 else 'operações'} de {emissores_unicos} "
        f"{'emissor' if emissores_unicos == 1 else 'emissores'} distintos, "
        f"totalizando {formatar_brl_milhoes(valor_total)} em captações.{spread_texto}\n\n"
        f"O mercado de LFs para a faixa de rating {rating_desc} demonstra profundidade e "
        f"liquidez adequadas para investidores institucionais com horizonte de médio/longo prazo. "
        f"As emissões subordinadas (T2 e AT1) representam oportunidade de retorno adicional "
        f"para investidores qualificados dispostos a assumir o risco de subordinação estrutural.\n\n"
        f"As informações contidas neste relatório são baseadas em dados públicos e têm "
        f"caráter estritamente informativo. Não constituem recomendação de investimento, "
        f"compra ou venda de quaisquer valores mobiliários. Decisões de investimento devem "
        f"ser tomadas com base em análise própria e assessoria especializada."
    )
