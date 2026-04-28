# Agente B3

## O que é
Agente Python que extrai dados de Letras Financeiras (LFs) de fontes públicas brasileiras,
filtra dinamicamente por múltiplos critérios, e gera relatório profissional em Word (.docx).

## Stack
- Python 3.10+
- pandas para tratamento de dados
- python-docx para geração de Word
- requests + BeautifulSoup para extração web
- pytest para testes

## Estrutura
- config/filters.py: dataclass FiltrosConsulta + presets + normalização de ratings
- extractors/: módulos de extração por fonte (ANBIMA, CVM, BACEN, B3)
- processors/filter_engine.py: motor de filtros dinâmicos
- processors/: limpeza, enriquecimento
- report/: templates de texto, tabelas, montagem do docx
- utils/: logger, helpers

## Comandos
- Executar (padrão): `python main.py`
- Com filtros: `python main.py --rating-min A- --rating-max A+ --periodo 6 --indexador cdi`
- Com preset: `python main.py --preset "lfs_subordinadas_a_menos"`
- Testes: `pytest tests/ -v`
- Dry run: `python main.py --dry-run`

## Regras
- Usar pathlib.Path para caminhos (cross-platform)
- Encoding UTF-8 em todos os open()
- NENHUM filtro é hardcoded — tudo vem de FiltrosConsulta
- Não usar nenhuma API de LLM
- Templates de texto em português executivo
