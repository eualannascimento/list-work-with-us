# Automação de CI

**Status:** Concluído
**Data:** 2026-07-12

## 1. Resumo e Objetivo
Executa o pipeline principal ([[baseline-pipeline-principal]]) automaticamente via GitHub Actions e commita o resultado (`list.csv` e `README.md` atualizados) de volta no repositório, sem intervenção manual.

## 2. User Stories (Requisitos Funcionais)
* **US01:** Como mantenedor, quero que o README seja atualizado automaticamente a cada push em `main` e semanalmente, para que a lista não fique defasada mesmo sem contribuições novas (links podem cair a qualquer momento).
* **US02:** Como mantenedor, quero disparar manualmente a expansão da lista com grandes empresas brasileiras, para incorporar lotes descobertos pelo pipeline de expansão sem esperar uma contribuição externa.

## 3. Regras de Negócio e Casos de Falha (Edge Cases)
* **Regra 01:** `verify-and-update-list.yml` roda em três gatilhos: push em `main`, disparo manual (`workflow_dispatch`) e agendamento semanal às segundas 04:00 UTC (`cron: "0 4 * * 1"`) (`.github/workflows/verify-and-update-list.yml`).
* **Regra 02:** O job roda em `ubuntu-latest` com Python 3.10, instala `requirements.txt` e executa `python main.py`; o commit do resultado usa `stefanzweifel/git-auto-commit-action@v4` com mensagem fixa "Update files (career-websites.csv and README.md)" (`.github/workflows/verify-and-update-list.yml`).
* **Regra 03:** Esse workflow não declara bloco `permissions:` explícito; depende da permissão padrão do repositório (`default_workflow_permissions: write`, confirmado via `gh api repos/.../actions/permissions/workflow`) para o auto-commit funcionar.
* **Regra 04:** `expand-large-companies.yml` só roda por disparo manual, com input opcional `workers` (paralelismo de descoberta de URL, default `'20'`) (`.github/workflows/expand-large-companies.yml`).
* **Regra 05:** Esse workflow declara `permissions: contents: write` explicitamente, executa `scripts/expand_large_companies_br.py` (ver [[baseline-descoberta-expansao]]) e depois `python main.py` para reconstruir o README antes do commit automático, com mensagem fixa `'chore: expand large-company list via workflow_dispatch'` (`.github/workflows/expand-large-companies.yml`).
* **Falha 01:** Nenhum dos dois workflows roda a suíte `pytest` antes de commitar; uma regressão introduzida em `main.py` ou nos módulos de `src/py/functions/` só seria percebida depois do commit automático, não antes.

## 4. Estrutura de Dados e Componentes
* **Arquivos:** `.github/workflows/verify-and-update-list.yml`, `.github/workflows/expand-large-companies.yml`.
* **Dependência:** ambos instalam `requirements.txt` completo (ver dívida sobre dependências não usadas em [[baseline-pipeline-principal]]).

## 5. Critérios de Aceite (verificáveis por teste)
* [x] CA01: Dado um push em `main`, quando o workflow `verify-and-update-list` roda, então `README.md` e `list.csv` são regenerados e commitados automaticamente.
* [x] CA02: Dado um disparo manual de `expand-large-companies` com `workers=10`, quando o workflow roda, então `scripts/expand_large_companies_br.py` recebe `WORKERS=10` via variável de ambiente.
* [ ] CA03: Dado que os testes `pytest` falhem no código de `main.py`, quando qualquer um dos workflows roda, então o commit automático NÃO deve ocorrer. (Não implementado hoje: nenhum workflow roda `pytest` antes do commit.)

## 6. Fora de Escopo
* Lógica de negócio executada pelos scripts (delegada a [[baseline-pipeline-principal]] e [[baseline-descoberta-expansao]]).

## 7. Dívidas e riscos observados
* Nenhum dos workflows executa a suíte de testes antes de commitar; uma regressão pode ir direto para `main` via auto-commit.
* `verify-and-update-list.yml` não declara `permissions:` explícito, diferente de `expand-large-companies.yml`; funciona hoje porque a permissão default do repositório é `write`, mas fica implícito e frágil a uma mudança futura nas settings do GitHub. Vale padronizar com `permissions: contents: write` explícito.
* Sem linter/formatter no CI (nenhum step de lint em nenhum dos dois workflows).
