# Arquitetura - lista-trabalhe-conosco

**Data da varredura:** 2026-07-12

## Visão geral
Repositório Python que mantém uma lista curada de empresas brasileiras com portal de vagas "trabalhe conosco", publicada como tabela Markdown em `README.md`. Não tem servidor, API nem banco de dados: todo o estado vive em arquivos CSV/YAML versionados no próprio repositório, e a atualização roda via GitHub Actions.

## Stack
* Linguagem: Python 3.10.2 (`.python-version`).
* Dependências reais: `requests`, `pandas`, `numpy`, `Unidecode`, `pytest`. `requirements.txt` também lista dezenas de pacotes de Jupyter/ipykernel não usados em produção (ver dívida em [[baseline-pipeline-principal]]).
* Sem framework web, sem banco de dados, sem fila.
* Serviços externos: requisições HTTP para os próprios sites de carreira das empresas (verificação de status e de conteúdo) e para `brapi.dev` (lista de ações da B3, usada na descoberta de candidatos).
* CI: GitHub Actions (dois workflows, ver [[baseline-automacao-ci]]).
* Teste: `pytest` (`pytest.ini`: `testpaths=tests`).

## Diagrama de módulos (texto)

```
main.py (pipeline principal)
  -> src/py/functions/df_operations.py      (clean_url, validate_url)
  -> src/py/functions/file_operations.py    (read_csv, read_and_filter_csv, save_sorted_csv)
  -> src/py/functions/md_operations.py      (generate_markdown_table, load_header)
  -> src/py/functions/website_verification.py (verify_websites_concurrent)

src/py/functions/portal_verification.py
  -> usa website_verification.create_shared_session
  -> consumido só pelo pipeline de descoberta (scripts/), não por main.py

scripts/ (descoberta e expansao, dois caminhos independentes)
  Caminho canonico (run_expansion_batch.py, via subprocess):
    build_candidate_universe.py
      -> company_seeds_data.py (COMPANY_SEEDS)
      -> segment_macro_map.py (to_macro)
    score_candidates.py
      -> scoring_utils.py (normalize_name, compute_score, load_scoring_config)
      -> data/seeds/scoring.yaml
    discover_career_urls.py
      -> src/py/functions/website_verification.py
      -> src/py/functions/portal_verification.py
      -> fix_vagas_urls_guesser.py (importlib)
      -> data/seeds/known_career_urls.yaml, b3_slug_aliases.yaml
    expand_ready_from_profiles.py
      -> add_verified_companies.py (CANDIDATES)
      -> fix_inactive_and_expand.py (importlib)
    probe_seed_urls.py
      -> discover_career_urls.py (detect_platform, _slug_matches_url)
    ingest_batch.py
      -> main.py (subprocess)

  Caminho paralelo (so este roda no CI):
    expand_large_companies_br.py
      -> segment_macro_map.py (to_macro)
      -> src/py/functions/df_operations.py (clean_url)
      -> escreve direto em src/data/input/list.csv
      -> NAO usa portal_verification.py nem website_verification.py

  Scripts de suporte isolados (auditoria/correcao, sem cadeia formal de chamada):
    audit_hygiene.py, apply_list_csv_audit.py, reconcile_urls.py,
    probe_seed_urls.py, update_metadata.py, fix_vagas.py

.github/workflows/
  verify-and-update-list.yml   -> python main.py (push/schedule/manual)
  expand-large-companies.yml   -> python scripts/expand_large_companies_br.py + python main.py (manual)
```

## Fluxo de dados
1. Contribuição externa (PR editando `new_items.csv`) ou descoberta automática (scripts/) alimenta `list.csv`.
2. `main.py` normaliza, verifica status HTTP de cada URL, ordena e deduplica.
3. `README.md` é regenerado a partir de `list.csv` + `header.md`.
4. GitHub Actions commita o resultado de volta em `main` automaticamente.

## Domínios documentados
* [[baseline-pipeline-principal]]
* [[baseline-verificacao-urls]]
* [[baseline-descoberta-expansao]]
* [[baseline-automacao-ci]]

## O que ficou fora da varredura
* Conteúdo detalhado dos scripts de teste manual/exploratório (`test_ats_brute.py`, `test_ddg_status.py`, `test_gsearch.py`, `test_gupy_dns.py`, `test_playwright_dev.py`, `test_search.py`, `test_yahoo.py`, `playwright_scraper.py`): lidos só pelo nome, não pelo conteúdo.
* Conteúdo linha a linha de `audit_hygiene.py`, `apply_list_csv_audit.py`, `reconcile_urls.py`, `probe_seed_urls.py`, `update_metadata.py`, `fix_inactive_and_expand.py`, `fix_vagas.py`: lidos parcialmente, propósito confirmado mas regras internas completas não documentadas linha a linha.
* Conteúdo de `artifacts/*.csv` e `*.json` (são saída, não código-fonte).
