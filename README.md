# Agente B3 — Letras Financeiras

Agente Python que extrai dados públicos de **Letras Financeiras (LFs)** de instituições financeiras brasileiras, filtra dinamicamente por múltiplos critérios e gera relatório profissional em Word (.docx).

**Custo recorrente: R$ 0,00** — sem API de LLM, 100% Python.

---

## Pré-requisitos

- Python 3.10 ou superior
- pip

---

## Instalação

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Copie o template de variáveis de ambiente
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/macOS
```

---

## Uso

### Execução padrão (filtros padrão: rating A-, últimos 12 meses)

```bash
python main.py
```

### Com filtros dinâmicos via CLI

```bash
# Rating exato A-, últimos 6 meses, apenas LFs indexadas ao CDI
python main.py --rating-min A- --rating-max A- --periodo 6 --indexador cdi

# Faixa de rating BBB+ a A+, 24 meses, todos os indexadores
python main.py --rating-min BBB+ --rating-max A+ --periodo 24

# Apenas LFs Sênior e Subordinada T2
python main.py --tipos senior,subordinada_t2

# Com filtro de spread (entre 0.80% e 2.00% a.a.)
python main.py --spread-min 0.80 --spread-max 2.00

# Com filtro de valor de emissão (acima de R$ 200 mi)
python main.py --valor-min 200000000

# Emissores específicos
python main.py --emissores "Banco ABC Brasil,Banco Pine"

# Período customizado
python main.py --data-inicio 2024-01-01 --data-fim 2024-12-31
```

### Dry run (apenas exibe filtros, sem gerar Word)

```bash
python main.py --rating-min A- --rating-max A+ --dry-run
```

### Logging detalhado

```bash
python main.py --verbose
```

---

## Presets de Filtros

Salve filtros reutilizáveis como presets JSON:

```bash
# Salvar preset atual
python main.py --rating-min A- --rating-max A+ --periodo 12 --indexador cdi --salvar-preset "lfs_a_cdi_12m"

# Listar presets disponíveis
python main.py --listar-presets

# Executar com preset
python main.py --preset lfs_a_cdi_12m
```

Os presets são salvos em `presets/` e podem ser editados manualmente.

---

## Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_filters.py -v
pytest tests/test_processors.py -v
pytest tests/test_report.py -v
pytest tests/test_extractors.py -v
```

---

## Estrutura do Projeto

```
Agente B3/
├── main.py                      # CLI principal
├── requirements.txt
├── config/
│   ├── settings.py              # Constantes e configurações centrais
│   └── filters.py               # Dataclass FiltrosConsulta + presets + normalização de ratings
├── extractors/
│   ├── base.py                  # Classe base abstrata
│   ├── anbima.py                # ANBIMA Data (dados mock realistas incluídos)
│   ├── cvm.py                   # CVM Portal Dados Abertos
│   ├── bacen.py                 # BACEN IF.Data
│   └── b3_rjlf.py              # B3 RJLF (stub — aguardando credencial)
├── processors/
│   ├── cleaner.py               # Limpeza e normalização
│   ├── filter_engine.py         # Motor de filtros dinâmicos (7 filtros)
│   └── enricher.py              # Enriquecimento com métricas derivadas
├── report/
│   ├── templates.py             # Templates de texto parametrizados
│   ├── tables.py                # Tabelas comparativas
│   └── docx_builder.py          # Geração do Word final
├── utils/
│   ├── logger.py                # Logging colorido (console + arquivo)
│   └── helpers.py               # Formatação BRL, datas, etc.
├── presets/                     # Presets de filtros (JSON)
├── outputs/                     # Relatórios gerados (.docx)
├── logs/                        # Logs de execução
└── tests/                       # Testes pytest
```

---

## Filtros Disponíveis

| Parâmetro CLI       | Descrição                                  | Padrão     |
|---------------------|--------------------------------------------|------------|
| `--rating-min`      | Rating mínimo (BBB- até AAA)               | A-         |
| `--rating-max`      | Rating máximo (BBB- até AAA)               | A-         |
| `--periodo`         | Meses para trás                            | 12         |
| `--data-inicio`     | Data início customizada (YYYY-MM-DD)       | —          |
| `--data-fim`        | Data fim customizada (YYYY-MM-DD)          | —          |
| `--tipos`           | senior, subordinada_t2, subordinada_at1    | todos      |
| `--valor-min`       | Valor mínimo de emissão (R$)               | sem mínimo |
| `--valor-max`       | Valor máximo de emissão (R$)               | sem máximo |
| `--spread-min`      | Spread mínimo sobre CDI (% a.a.)           | sem mínimo |
| `--spread-max`      | Spread máximo sobre CDI (% a.a.)           | sem máximo |
| `--indexador`       | todos, cdi, ipca, pre                      | todos      |
| `--emissores`       | Nomes separados por vírgula                | todos      |

Escala de ratings suportada: `BBB- | BBB | BBB+ | A- | A | A+ | AA- | AA | AA+ | AAA`

Agências suportadas: **Fitch Nacional**, **S&P Escala Nacional**, **Moody's Local Brasil**

---

## Como Adicionar Novos Extratores

1. Crie `extractors/nova_fonte.py`
2. Herde de `BaseExtractor`
3. Implemente `extract(filtros)` retornando DataFrame com `COLUNAS_PADRAO`
4. Implemente `source_name` (property)
5. Adicione a instância no pipeline em `main.py → executar_agente()`

---

## Roadmap

- **Fase 2:** Integração completa com B3 RJLF (aguardando credencial)
- **Fase 3:** Interface gráfica (tkinter ou web)
- **Fase 4:** Exportação para Excel (.xlsx) além do Word
- **Fase 5:** Alertas automáticos por e-mail

---

## Tipos de Letras Financeiras

| Tipo            | Prazo Mínimo | Valor Mínimo | Composição Basileia III |
|-----------------|-------------|--------------|------------------------|
| Sênior          | 24 meses    | R$ 50.000    | Não compõe             |
| Subordinada T2  | 60 meses    | R$ 300.000   | Capital de Nível 2     |
| Subordinada AT1 | Perpétua    | R$ 300.000   | Capital Adicional N1   |

---

*Agente B3 v2.0 — Uso restrito. Não constitui recomendação de investimento.*
