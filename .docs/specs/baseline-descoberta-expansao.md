# Descoberta e expansão de empresas candidatas

**Status:** Concluído
**Data:** 2026-07-12

## 1. Resumo e Objetivo
Encontra novas empresas brasileiras com portal de vagas ativo e as incorpora a `list.csv`, fora do fluxo de contribuição manual via `new_items.csv`. Existem dois caminhos paralelos e independentes para isso: o pipeline "canônico" (`run_expansion_batch.py`) e o script isolado `expand_large_companies_br.py` (o único que roda no CI).

## 2. User Stories (Requisitos Funcionais)
* **US01:** Como mantenedor, quero gerar um universo de empresas candidatas a partir de ações da B3 e listas de grandes empresas, para não depender só de contribuições externas.
* **US02:** Como mantenedor, quero que candidatos sejam pontuados e filtrados antes de qualquer tentativa de rede, para não gastar tempo verificando empresas pequenas ou já presentes na lista.
* **US03:** Como mantenedor, quero que toda URL de carreira descoberta seja confirmada por verificação forte (não só HTTP 200) antes de entrar em `list.csv`, para evitar poluir a lista com portais genéricos ou vazios.
* **US04:** Como mantenedor, quero disparar uma expansão rápida direto do GitHub Actions sem depender do pipeline completo em várias etapas, para casos em que só quero acrescentar grandes empresas conhecidas de uma lista fixa.

## 3. Regras de Negócio e Casos de Falha (Edge Cases)

### Pipeline canônico (`run_expansion_batch.py`, orquestrador via subprocess)
Ordem de execução: `build_candidate_universe.py` → `score_candidates.py` → `discover_career_urls.py` → `expand_ready_from_profiles.py` → `probe_seed_urls.py` → `ingest_batch.py` (`run_expansion_batch.py`). `expand_large_companies_br.py` NÃO faz parte desta cadeia.

* **Regra 01:** Universo de candidatos é montado a partir de `company_seeds_data.py:COMPANY_SEEDS` (dados estáticos com sinais `b3`/`top`/`revenue` hardcoded por empresa) e ações B3 via `build_candidate_universe.py:load_brapi_stocks`, com nomes de ações limpos por `format_brapi_name` (remove "S.A.", "BOLSA...", expande "BCO"→"Banco", "CIA"→"Companhia"); grava `artifacts/candidates_raw.csv`.
* **Regra 02:** Candidatos são excluídos se o nome bater em `exclude_name_patterns` de `data/seeds/scoring.yaml` (via `should_exclude_name`, ex.: "consulting", "wordpress-proxy") ou se já existirem em `list.csv` por nome normalizado (`scoring_utils.py:normalize_name`, remove sufixos societários S/A, LTDA, Holding, Grupo, Brasil, via `unidecode`) (`score_candidates.py`).
* **Regra 03:** Score é a soma ponderada dos sinais presentes (pesos em `scoring.yaml`: `b3`=3, `revenue`=2, `employees`=2, `top`=2, `fortune`=2, via `scoring_utils.py:compute_score`); só passam candidatos com `score >= min_score` (4, valor em `scoring.yaml`). Resultado ordenado por `-score, nome`, gravado em `artifacts/candidates_scored.csv`.
* **Regra 04:** `discover_career_urls.py` processa só as primeiras `DISCOVER_LIMIT` linhas (env var, default 350) de `candidates_scored.csv`, na ordem do arquivo, com até 10 workers (`MAX_WORKERS=10`, hardcoded) (`discover_career_urls.py`).
* **Regra 05:** Uma URL só é aceita como "ready" se passar em duas checagens em sequência: `website_verification.py:verify_website_status` (status "1") E `portal_verification.py:verify_portal_has_jobs` (True). Subdomínios Gupy cujo slug não corresponde ao nome da empresa são rejeitados mesmo que ambas as checagens passem (`discover_career_urls.py:discover_one`, `_slug_matches_url`).
* **Regra 06:** Se nenhuma URL testada passar nas duas checagens, a empresa vai para `artifacts/pending_companies.csv` com `motivo: "no_url_strong_verify"` (único motivo categorizado no código atual) (`discover_career_urls.py:discover_one`).
* **Regra 07:** Mesmo uma URL "forte" aprovada em `discover_one` pode não ir para `ready.csv`: há uma segunda deduplicação em `main()` contra `existing_urls` (carregado de `list.csv`); se a URL normalizada já existir, o resultado é descartado silenciosamente, sem ir para `ready` nem para `pending` (`discover_career_urls.py:main`).
* **Regra 08:** Resultados positivos e negativos (`{"pending": True}`) são cacheados em `artifacts/url_cache.json`, chaveado por `normalize_name(nome)`; não há expiração de cache visível no código, então uma empresa marcada "pending" numa execução não é re-testada em execuções futuras a menos que o cache seja apagado manualmente.
* **Regra 09:** `ingest_batch.py` lê `artifacts/ready_to_add.csv`, deduplica contra `list.csv` via `clean_url` (mesma função do domínio [[baseline-pipeline-principal]]), escreve o lote em `src/data/input/new_items.csv` no formato esperado por `main.py`, e invoca `main.py` como subprocesso, reaproveitando o pipeline principal completo (dedup, verificação HTTP leve, ordenação, README) em vez de duplicar essa lógica.

### Caminho paralelo (`expand_large_companies_br.py`, único script chamado pelo workflow de CI)
* **Regra 10:** É totalmente autocontido: não importa `build_candidate_universe.py`, `score_candidates.py` nem `discover_career_urls.py`. Usa uma lista hardcoded `COMPANIES` (~1500 tuplas nome/segmento) embutida no próprio arquivo (`expand_large_companies_br.py`, linhas 160-1779) e não usa `portal_verification.py` (só testa status HTTP, não confirma vagas reais).
* **Regra 11:** Dedup contra `list.csv` é feita por nome exato (lowercased, sem normalização fuzzy) e por host de URL: hosts compartilhados (`carreiras.gupy.io`, `boards.greenhouse.io`, `job-boards.greenhouse.io`, `jobs.lever.co`, `jobs.kenoby.com`) são permitidos mesmo repetidos (porque o path diferencia a empresa); qualquer outro host já presente em `list.csv` descarta o candidato mesmo com path diferente (`expand_large_companies_br.py:main`).
* **Regra 12:** Para cada candidato, tenta 4 padrões de URL fixos por slug (Gupy, Kenoby, Lever, Teamtailor) e aceita a PRIMEIRA que responder 2xx/3xx com `verify=False` (TLS não verificado) e que não seja um redirect para portal genérico conhecido (`expand_large_companies_br.py:try_url`, `find_url_for`, `candidate_urls`).
* **Regra 13:** Paralelismo controlado por `WORKERS` (env var, default `20`) via `ThreadPoolExecutor`, sem limite de quantidade de candidatos processados por execução (tenta todos os não deduplicados do batch hardcoded) (`expand_large_companies_br.py:main`).
* **Falha 01:** Qualquer exceção durante a busca de URL de um candidato é capturada e silenciada (`except Exception: url = None`), sem log individual do erro (`expand_large_companies_br.py:work`).
* **Regra 14:** Ao final, escreve DIRETO em `src/data/input/list.csv` (sobrescreve o arquivo inteiro), sem gerar artifacts intermediários, sem passar por `new_items.csv` nem por `ingest_batch.py`. O workflow de CI chama `main.py` como step separado depois, só para regenerar o README (`.github/workflows/expand-large-companies.yml`, ver [[baseline-automacao-ci]]).

### Scripts de suporte (auditoria, correção e dados)
* `audit_hygiene.py`: identifica entradas de "empresa pequena" em `list.csv` via regex `SMALL_PATTERNS` + config de `scoring.yaml`; só gera relatório (`artifacts/review_remove.csv`), não altera `list.csv`.
* `apply_list_csv_audit.py`: remove um conjunto hardcoded de URLs conhecidas como inválidas (`URLS_TO_REMOVE`) direto de `list.csv`.
* `reconcile_urls.py`: revalida URLs existentes e tenta corrigi-las via `fix_vagas_urls_guesser.py`.
* `probe_seed_urls.py`: testa URLs de `data/seeds/*.yaml` e gera `ready_to_add.csv`, reaproveitando `detect_platform`/`_slug_matches_url` de `discover_career_urls.py`.
* `update_metadata.py`: extrai data de publicação de vaga a partir do payload Next.js de portais Gupy; não referenciado por nenhum outro script.
* `fix_inactive_and_expand.py`: corrige URLs com `Status da URL == "0"` e insere empresas do mesmo perfil da lista; carregado dinamicamente por `expand_ready_from_profiles.py`.
* `fix_vagas.py`: compara `list.csv` contra uma versão de um commit git específico hardcoded; parece script de uso único para recuperar uma regressão pontual, não reutilizável.
* `fix_vagas_urls_guesser.py`: módulo utilitário de geração de slugs e teste contra Gupy/Kenoby/Solides/Empregare; é o módulo de suporte mais reutilizado do repositório (carregado via `importlib` por 4 scripts diferentes).
* `add_verified_companies.py`: adiciona lista hardcoded `CANDIDATES` já verificada manualmente direto em `list.csv`.
* `expand_ready_from_profiles.py`: gera `ready_to_add.csv` a partir de `CANDIDATES` (de `add_verified_companies.py`) e de `fix_inactive_and_expand.py` (via importlib).
* `segment_macro_map.py`: mapeia segmentos detalhados para as 12 categorias macro fixas (`to_macro`), usado por praticamente todo script que grava linhas em `list.csv`.
* `scoring_utils.py`: utilitários compartilhados (`load_scoring_config`, `normalize_name`, `compute_score`).
* `company_seeds_data.py`: dados estáticos de `COMPANY_SEEDS` com sinais hardcoded por empresa.
* Scripts de teste manual/exploratório (`test_ats_brute.py`, `test_ats_redirect.py`, `test_ddg_status.py`, `test_gsearch.py`, `test_gupy_dns.py`, `test_playwright_dev.py`, `test_search.py`, `test_yahoo.py`, `playwright_scraper.py`): experimentos de busca (DuckDuckGo, Google, Yahoo) e DNS/brute-force de ATS para achar URLs quando as heurísticas de slug falham. Não fazem parte de nenhuma cadeia de execução formal (nem import, nem subprocess); não lidos em detalhe, propósito inferido pelo nome.

## 4. Estrutura de Dados e Componentes
* **Config:** `data/seeds/scoring.yaml` (pesos e min_score), `data/seeds/known_career_urls.yaml`, `data/seeds/b3_slug_aliases.yaml`, `data/seeds/associations_extra.yaml`, `data/seeds/varejo_industria_slugs.yaml`.
* **Artifacts intermediários (pipeline canônico):** `artifacts/candidates_raw.csv`, `artifacts/candidates_scored.csv`, `artifacts/ready_to_add.csv`, `artifacts/pending_companies.csv`, `artifacts/url_cache.json`, `artifacts/review_remove.csv`, `artifacts/url_reconcile_report.csv`, `artifacts/fix_inactive_report.csv`.
* **Arquitetura:** dois caminhos independentes de escrita em `list.csv`: (a) `run_expansion_batch.py` → ... → `ingest_batch.py` → `main.py` (subprocess), reaproveitando o domínio [[baseline-pipeline-principal]]; (b) `expand_large_companies_br.py` escrevendo direto em `list.csv`, disparado só pelo workflow de CI do domínio [[baseline-automacao-ci]]. Ambos usam `df_operations.py:clean_url` e `segment_macro_map.py:to_macro`.
* **Verificação:** o pipeline canônico usa a verificação forte completa ([[baseline-verificacao-urls]]); `expand_large_companies_br.py` usa só checagem de status HTTP simplificada própria (`try_url`), não delega a `website_verification.py` nem `portal_verification.py`.

## 5. Critérios de Aceite (verificáveis por teste)
* [ ] CA01: Dado um candidato cujo score fica abaixo de `min_score`, quando `score_candidates.py` roda, então ele não aparece em `candidates_scored.csv`. (Sem teste `pytest` localizado; nenhum script de `scripts/` tem cobertura de teste.)
* [ ] CA02: Dada uma empresa cuja única URL testada responde 200 mas não lista vagas reais, quando `discover_career_urls.py` roda, então ela vai para `pending_companies.csv` com `motivo: "no_url_strong_verify"`.
* [ ] CA03: Dada uma URL já presente em `list.csv`, quando `expand_large_companies_br.py` roda e a encontra num host não compartilhado, então o candidato é descartado mesmo com path diferente.
* [ ] CA04: Dado um lote em `ready_to_add.csv`, quando `ingest_batch.py` roda, então as empresas aparecem em `list.csv` só depois de passar pela dedup e verificação do pipeline principal.

## 6. Fora de Escopo
* Verificação de status HTTP e de vagas reais em si: ver domínio [[baseline-verificacao-urls]] (o pipeline canônico consome esse domínio; `expand_large_companies_br.py` não).
* Geração do README e commit automático: ver domínios [[baseline-pipeline-principal]] e [[baseline-automacao-ci]].

## 7. Dívidas e riscos observados
* Nenhum script em `scripts/` tem cobertura de teste `pytest`; todo o pipeline de descoberta/expansão roda sem rede de segurança automatizada.
* Existem dois caminhos paralelos e não sincronizados para adicionar empresas (`run_expansion_batch.py` vs. `expand_large_companies_br.py`), com regras de dedup, verificação e limites de paralelismo diferentes entre si; risco de resultados inconsistentes dependendo de qual caminho é usado. Segundo o usuário, `expand_large_companies_br.py` foi uma tentativa de expandir a lista que não se mostrou eficaz; é candidato a virar uma feature nova no fluxo SDD (Grilling completo) reaproveitando `portal_verification.py`, `fix_vagas_urls_guesser.py` e `scoring_utils.py`, em vez de manter a checagem própria e mais fraca desse script.
* `expand_large_companies_br.py` usa `verify=False` (TLS não verificado) e uma verificação de vaga própria e mais fraca que `portal_verification.py`, mas é o único script executado automaticamente pelo CI: ele não passa pela verificação forte do domínio [[baseline-verificacao-urls]].
* Exceções em `expand_large_companies_br.py:work` são silenciadas sem log individual, dificultando diagnóstico de falhas específicas por empresa.
* `fix_vagas.py` depende de um hash de commit git hardcoded; é candidato a remoção ou a virar script de uso único documentado como tal.
* `artifacts/url_cache.json` não tem TTL ou mecanismo de invalidação visível: uma empresa marcada "pending" fica presa nesse estado indefinidamente entre execuções, a menos que o cache seja apagado manualmente.
* `apply_list_csv_audit.py` e `reconcile_urls.py` não são disparados por nenhum workflow, nem referenciados por outro script: aparecem só em 1-2 commits cada no histórico (`f11d69e`, `0ea021e`), com mensagens que indicam correção pontual já aplicada e commitada em `list.csv`. Não fazem parte de nenhum processo recorrente; são candidatos a remoção, já que seu efeito único já está incorporado à lista atual.
* Vários scripts de suporte (`fix_vagas.py`, `update_metadata.py`, `test_*.py` de busca/DNS) não são referenciados por nenhum outro script nem workflow; parecem ferramentas ad-hoc de uso pontual, candidatas a mover para uma pasta separada de "scratch" ou a remover.
