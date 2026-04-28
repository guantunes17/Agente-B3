# Agente B3 — Manual do Usuário

**Versão:** conforme `config/settings.py → VERSION`
**Objetivo:** Extrair, filtrar e gerar relatório profissional em Word (.docx) de Letras Financeiras (LFs) negociadas no mercado brasileiro.
**Custo recorrente:** R$ 0,00 — sem LLM, sem APIs pagas obrigatórias.

---

## 1. O que o Agente faz

O Agente B3 consulta automaticamente múltiplas fontes de dados sobre Letras Financeiras (LF Sênior, LF Subordinada T2 e LF Subordinada AT1), aplica os filtros que você configurou e entrega um relatório Word formatado com tabelas, ratings normalizados entre agências e métricas calculadas.

### Fontes de dados utilizadas

| Fonte | Acesso | Disponibilidade |
|---|---|---|
| **ANBIMA Data** | Público (sem login) | Sempre funciona — tem fallback com dados de demonstração |
| **CVM** | Público (sem login) | Sempre funciona |
| **BACEN** | Público (sem login) | Sempre funciona |
| **B3 RJLF** | Requer token B3 | Pula silenciosamente se sem credencial |
| **UP2DATA Cloud** | Requer contrato com B3 | Pula silenciosamente se sem credencial |
| **UP2DATA Client** | Software local B3 | Pula silenciosamente se sem software instalado |

> **Resumo:** o agente funciona imediatamente após a instalação, sem nenhuma credencial. As fontes premium (B3/UP2DATA) enriquecem os dados quando disponíveis, mas nunca bloqueiam a execução.

---

## 2. Instalação

### Opção A — Executável (.exe) — recomendado para uso final

1. Receba o arquivo `AgenteB3.exe` (distribuído pelo desenvolvedor).
2. Coloque em qualquer pasta de sua preferência (ex.: `C:\Ferramentas\AgenteB3\`).
3. Duplo-clique em `AgenteB3.exe` para abrir a interface gráfica.

Não é necessário instalar Python, bibliotecas ou qualquer dependência.

### Opção B — A partir do código-fonte (modo desenvolvedor)

**Requisitos:** Python 3.10 ou superior instalado.

```
# 1. Clone o repositório
git clone https://github.com/guantunes17/Agente-B3.git
cd "Agente-B3"

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute
python launcher.py             # abre a interface gráfica
```

### Gerar o executável (para distribuir)

```
python build_icon.py           # gera o ícone (uma vez)
python build.py                # gera dist\AgenteB3.exe
```

---

## 3. Primeira execução — Interface Gráfica

Ao abrir o agente (`AgenteB3.exe` ou `python launcher.py`), a janela principal exibe:

- **Barra de status no topo** — pills coloridos indicando o estado de cada fonte:
  - `● ANBIMA — público` (sempre verde)
  - `● B3 RJLF — não configurado` (cinza até inserir credencial)
  - `● UP2DATA — não configurado` (cinza até configurar Cloud ou Client)

- **Painel de filtros** — todos os critérios ajustáveis antes de executar.

- **Botão Executar** — inicia o pipeline e exibe barra de progresso em 6 etapas.

---

## 4. Filtros disponíveis

Todos os filtros são opcionais. Os valores padrão já produzem um relatório útil.

### 4.1 Rating

Selecione a faixa de rating corporativo (escala padronizada entre agências):

```
BBB-  BBB  BBB+  A-  A  A+  AA-  AA  AA+  AAA
```

O agente normaliza automaticamente notações de Fitch `(bra)`, S&P `br`, Moody's `.br` para essa escala unificada.

- **Rating mínimo:** nota mais baixa aceita (padrão: `A-`)
- **Rating máximo:** nota mais alta aceita (padrão: `A-`)
- Para uma faixa ampla, selecione ex.: mínimo `BBB-` e máximo `AA+`

### 4.2 Período

- **Últimos N meses:** deslize ou informe o número de meses retrospectivos (padrão: 12)
- **Data início / Data fim:** datas específicas no formato `YYYY-MM-DD` — quando preenchidas, ignoram o campo "meses"

### 4.3 Tipos de LF

Marque os tipos desejados (padrão: todos marcados):

| Tipo | Descrição |
|---|---|
| **LF Sênior** | Letra Financeira padrão — prioridade de pagamento |
| **LF Subordinada T2** | Absorve perdas após seniores — Nível 2 de capital |
| **LF Subordinada AT1** | Absorção de perdas preventiva — capital perpétuo (sem vencimento fixo) |

### 4.4 Valor de emissão

- **Valor mínimo (R$):** exclui emissões menores que este valor
- **Valor máximo (R$):** exclui emissões maiores que este valor
- Deixe em branco para sem restrição

### 4.5 Spread sobre CDI

- **Spread mínimo (% a.a.):** exclui emissões com remuneração abaixo deste spread
- **Spread máximo (% a.a.):** exclui emissões com remuneração acima deste spread
- Deixe em branco para sem restrição

### 4.6 Indexador

Escolha o indexador de remuneração:

| Opção | Descrição |
|---|---|
| `todos` | Inclui CDI, IPCA e prefixado (padrão) |
| `cdi` | Apenas emissões indexadas ao CDI |
| `ipca` | Apenas emissões indexadas ao IPCA |
| `pre` | Apenas emissões prefixadas |

### 4.7 Emissores específicos

- Informe um ou mais nomes de emissores separados por vírgula para restringir a busca
- Deixe em branco para todos os emissores

---

## 5. Executando e obtendo o relatório

1. Configure os filtros desejados na janela principal.
2. Clique em **Executar**.
3. Acompanhe as 6 etapas na barra de progresso:
   - Etapa 1 — Extração de todas as fontes
   - Etapa 2 — Limpeza e normalização
   - Etapa 3 — Aplicação dos filtros
   - Etapa 4 — Cálculo de métricas e enriquecimento
   - Etapa 5 — Geração do Word
   - Etapa 6 — Conclusão
4. Ao final, o caminho do arquivo `.docx` gerado é exibido na tela.
5. O relatório é salvo por padrão em: `Documentos\Relatorios LF\`

O arquivo Word contém:
- Capa com data e filtros aplicados
- Tabela de emissões selecionadas com formatação profissional (Arial, azul corporativo)
- Linhas alternadas para facilitar a leitura
- Totalizadores e métricas calculadas
- Rodapé indicando as fontes utilizadas

---

## 6. Presets — salvar e reutilizar filtros

Presets permitem salvar uma combinação de filtros com um nome e carregá-la novamente na próxima vez.

### Salvar um preset

1. Configure os filtros desejados.
2. Clique em **Presets → Salvar preset atual**.
3. Informe um nome (ex.: `LFs Subordinadas A-`).
4. O preset é salvo como arquivo JSON na pasta `presets/` do projeto.

### Carregar um preset

1. Clique em **Presets → Carregar preset**.
2. Selecione o preset na lista.
3. Os filtros são preenchidos automaticamente.

### Excluir um preset

1. Clique em **Presets → Gerenciar presets**.
2. Selecione e exclua o preset desejado.

---

## 7. Agendamento automático

O agente pode executar automaticamente em horários programados, sem interação do usuário, e salvar o relatório em `Documentos\Relatorios LF\`.

### Configurar o agendamento

1. Clique em **Ferramentas → Agendar execução automática**.
2. Escolha a frequência: **Diário**, **Semanal** ou **Mensal**.
3. Defina o horário de execução.
4. Opcionalmente, selecione um preset de filtros para a execução automática. Se nenhum for selecionado, usa os filtros padrão.
5. Clique em **Agendar**.

O agente registra uma tarefa no **Agendador de Tarefas do Windows** (schtasks). O computador precisa estar ligado e desbloqueado no horário configurado.

### Remover o agendamento

Na mesma janela de agendamento, clique em **Remover agendamento**.

### Logs de execução automática

Cada execução automática gera um arquivo de log em:
```
Documentos\Relatorios LF\logs\auto_YYYYMMDD_HHMMSS.log
```

---

## 8. Configuração de credenciais (fontes premium — opcional)

Acesse **Configurações → Credenciais** para configurar fontes adicionais.

> Todas as credenciais são armazenadas com segurança no **Cofre de Credenciais do Windows** (Windows Credential Manager / keyring). Nada é salvo em texto puro no disco.

### 8.1 B3 RJLF

Requer um token de acesso à plataforma RJLF da B3. Entre em contato com a B3 para contratação.

- **Token B3 RJLF:** informe o token fornecido pela B3.

Ao salvar, o pill `● B3 RJLF` ficará verde na janela principal.

### 8.2 ANBIMA

- **Usuário ANBIMA Data:** e-mail da conta ANBIMA Data (se aplicável)
- **Senha ANBIMA Data:** senha da conta

Sem credenciais ANBIMA, o agente usa dados públicos da ANBIMA (sem login) com fallback para dados de demonstração.

### 8.3 UP2DATA — Fonte Oficial B3 (mais completa)

A plataforma UP2DATA é a fonte de dados oficial da B3 para LFs, disponível em duas modalidades:

**Cloud (requer contrato com a B3):**
- **Client ID:** identificador OAuth2 fornecido pela B3
- **Client Secret:** segredo OAuth2 fornecido pela B3
- **Certificado .pfx:** arquivo de certificado digital fornecido pela B3 (clique em "Procurar" para selecionar)
- **Senha do certificado:** senha do arquivo .pfx
- Clique em **Testar conexão Cloud** para validar as credenciais

**Client (requer software UP2DATA instalado):**
- O software UP2DATA Client é instalado localmente pela B3 e deposita arquivos automaticamente em um diretório
- Informe o **diretório de dados** onde o software salva os arquivos (padrão: `C:\UP2DATA`)
- Clique em **Verificar diretório** para confirmar que a pasta existe e contém dados

O pill `● UP2DATA` indicará o estado ativo:
- `● UP2DATA — Cloud ativo` (verde — apenas Cloud configurado)
- `● UP2DATA — Client ativo` (verde — apenas Client configurado)
- `● UP2DATA — Cloud + Client` (verde — ambos configurados)

---

## 9. Uso via linha de comando (avançado)

O agente também pode ser executado pelo terminal, sem interface gráfica.

```
python launcher.py [opções]
```

### Exemplos

```bash
# Executar com filtros padrão
python launcher.py

# Rating A- a A+, últimos 6 meses
python launcher.py --rating-min A- --rating-max A+ --periodo 6

# Rating BBB+ a AA-, 24 meses, apenas CDI
python launcher.py --rating-min BBB+ --rating-max AA- --periodo 24 --indexador cdi

# Apenas subordinadas, spread entre 1,00% e 2,50%
python launcher.py --tipos subordinada_t2,subordinada_at1 --spread-min 1.00 --spread-max 2.50

# Emissores específicos
python launcher.py --emissores "Banco ABC Brasil,Banco Pine"

# Data customizada
python launcher.py --data-inicio 2024-01-01 --data-fim 2024-12-31

# Carregar preset salvo
python launcher.py --preset lfs_subordinadas_a_menos

# Salvar filtros como preset
python launcher.py --rating-min A- --rating-max A --salvar-preset "LFs Senior A"

# Listar presets disponíveis
python launcher.py --listar-presets

# Preview dos filtros sem gerar relatório
python launcher.py --dry-run

# Execução silenciosa (para agendamento externo)
python launcher.py --auto
```

### Parâmetros disponíveis

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `--rating-min` | `A-` | Rating mínimo |
| `--rating-max` | `A-` | Rating máximo |
| `--periodo` | `12` | Meses retrospectivos |
| `--data-inicio` | — | Data início `YYYY-MM-DD` |
| `--data-fim` | — | Data fim `YYYY-MM-DD` |
| `--tipos` | todos | `senior`, `subordinada_t2`, `subordinada_at1` |
| `--valor-min` | — | Valor mínimo de emissão em R$ |
| `--valor-max` | — | Valor máximo de emissão em R$ |
| `--spread-min` | — | Spread mínimo sobre CDI em % a.a. |
| `--spread-max` | — | Spread máximo sobre CDI em % a.a. |
| `--indexador` | `todos` | `todos`, `cdi`, `ipca`, `pre` |
| `--emissores` | todos | Nomes separados por vírgula |
| `--preset` | — | Nome do preset a carregar |
| `--salvar-preset` | — | Salvar filtros com este nome |
| `--listar-presets` | — | Lista presets e encerra |
| `--output` | automático | Caminho do `.docx` de saída |
| `--verbose` | — | Log detalhado (DEBUG) |
| `--dry-run` | — | Preview sem gerar Word |
| `--auto` | — | Execução silenciosa para agendamento |

---

## 10. Onde ficam os arquivos gerados

| Arquivo | Local |
|---|---|
| Relatórios Word (.docx) | `Documentos\Relatorios LF\` |
| Logs de execução automática | `Documentos\Relatorios LF\logs\` |
| Presets de filtros | `presets\` (na pasta do agente) |
| Cache de autenticação UP2DATA | `%USERPROFILE%\.agenteb3\up2data_cache.json` |

---

## 11. Perguntas frequentes

**O agente funciona sem acesso à internet?**
Parcialmente. As fontes ANBIMA, CVM e BACEN requerem internet. Se a ANBIMA estiver fora do ar, o agente usa dados de demonstração realistas automaticamente.

**O agente funciona sem credenciais B3 ou UP2DATA?**
Sim. As fontes premium simplesmente são ignoradas e o pipeline continua com ANBIMA, CVM e BACEN.

**Os dados mostrados são dados reais?**
Quando as fontes públicas (ANBIMA, CVM, BACEN) estão acessíveis — sim. Se a ANBIMA estiver indisponível, o relatório é gerado com dados de demonstração (indicado como "ANBIMA (mock)" na coluna Fonte).

**Como saber se o relatório usou dados reais?**
O rodapé do Word indica as fontes usadas. "ANBIMA Data" = real. "ANBIMA (mock)" = demonstração.

**Posso mudar a pasta onde os relatórios são salvos?**
Na GUI: use o seletor de pasta de destino antes de executar. Na CLI: use `--output caminho/relatorio.docx`.

**Como atualizar o agente?**
Para o .exe: solicite ao desenvolvedor uma nova versão. Para código-fonte: `git pull origin master` seguido de `pip install -r requirements.txt`.

---

## 12. Suporte e contato

Repositório: [github.com/guantunes17/Agente-B3](https://github.com/guantunes17/Agente-B3)

Para dúvidas, abra uma issue no GitHub ou entre em contato com o desenvolvedor.
