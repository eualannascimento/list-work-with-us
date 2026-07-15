# Diário de Adoção SDD - lista-trabalhe-conosco

## Etapa atual
Etapa A - Inventário (em andamento)

## Contexto
Repo clonado em /Users/eualannascimento/Development/lista-trabalhe-conosco a partir de
https://github.com/eualannascimento/lista-trabalhe-conosco.git

## Stack detectada
- Python 3.10.2 (.python-version)
- requirements.txt: requests, pandas, numpy, Unidecode, pytest 7.4.4 (resto são deps de Jupyter/ipykernel, aparentemente não usadas em produção)
- pytest.ini: testpaths=tests, python_files=test_*.py
- Sem framework web, sem banco de dados. Serviços externos: HTTP requests para sites de carreiras de empresas (verificação de URL), possivelmente Playwright (scripts/playwright_scraper.py) e busca (scripts/test_gsearch.py, test_ddg_status.py, test_yahoo.py).

## Arquitetura (visão inicial)
- main.py: orquestra o pipeline principal (novos itens → dedup → verificação de URL → sort/dedup → salvar CSV + gerar README.md).
- src/py/functions/: módulos de domínio (df_operations, file_operations, md_operations, portal_verification, website_verification).
- scripts/: pipeline paralelo/manual de descoberta e expansão de empresas candidatas (não roda no CI principal, aparentemente rodado manualmente ou por workflow separado expand-large-companies.yml).
- .github/workflows/: verify-and-update-list.yml (CI principal, push+semanal) e expand-large-companies.yml.
- data/seeds/*.yaml: dados de apoio para os scripts de expansão.
- tests/: cobre main, df_operations, file_operations, md_operations, portal_verification, website_verification, verification (genérico).

## Domínios candidatos (rascunho, aguardando confirmação do usuário)
1. Pipeline principal de atualização da lista (main.py + df/file/md_operations)
2. Verificação de URLs/portais (website_verification.py, portal_verification.py)
3. Descoberta e expansão de empresas candidatas (scripts/ + data/seeds/)
4. Automação CI (.github/workflows/)

## Inventário consolidado (subagent aa67d8b0d248f9761 retornou)

### Qualidade atual
- Suíte pytest cobre: main (parcial), df_operations, file_operations, md_operations, portal_verification (parcial, só Gupy generico), website_verification/verification (possível redundância entre os dois arquivos de teste).
- Nenhum teste cobre os scripts/ (pipeline de descoberta/expansão).
- Sem linter/formatter configurado (não encontrado).
- CI: verify-and-update-list.yml (push+semanal, roda main.py e faz commit automático) e expand-large-companies.yml (manual, roda scripts/expand_large_companies_br.py + main.py).

### Dívidas observadas (candidatas à seção 7 dos specs baseline)
- file_operations.py:save_sorted_csv tem nome enganoso (não ordena nada).
- tests/test_verification.py vs tests/test_website_verification.py parecem redundantes (estilos diferentes de teste para o mesmo módulo).
- portal_verification.py (Greenhouse e fallback genérico) sem teste dedicado.
- scripts/ inteiro sem cobertura de teste.
- requirements.txt tem muitas deps de Jupyter/ipykernel aparentemente não usadas em produção.

## Domínios confirmados (proposta final antes do gate)
1. baseline-pipeline-principal: main.py + df_operations, file_operations, md_operations
2. baseline-verificacao-urls: website_verification.py, portal_verification.py
3. baseline-descoberta-expansao: scripts/*.py, data/seeds/*.yaml, workflow expand-large-companies.yml
4. baseline-automacao-ci: .github/workflows/verify-and-update-list.yml (e referência cruzada ao workflow de expansão, já coberto no domínio 3)

## Gate Etapa A
Usuário confirmou os 4 domínios em 2026-07-12. Seguindo para Etapa B (engenharia reversa).

## Checkpoint Etapa B
- [x] baseline-pipeline-principal.md escrito (.docs/specs/)
- [x] baseline-verificacao-urls.md escrito (.docs/specs/)
- [x] baseline-automacao-ci.md escrito (.docs/specs/)
- [ ] baseline-descoberta-expansao.md (em andamento; scripts/expand_large_companies_br.py tem 1875 linhas, precisa de subagent dedicado antes de escrever)
- [ ] .docs/architecture.md

- [x] baseline-descoberta-expansao.md escrito (.docs/specs/)
- [x] .docs/architecture.md escrito

## Etapa C - Instalação do template (concluída)
Copiados de ai-workflow-template: .rules/anti-ai-style.md, .rules/context-management.md, .prompts/*.md, .claude/skills/sdd/SKILL.md, .claude/agents/reviewer.md, .docs/specs/_TEMPLATE.md, .cursorrules, AGENTS.md.
Escritos customizados para este projeto: CLAUDE.md (referencia os 4 specs baseline), .rules/global.md (adaptado: Python 3.10, pytest, sem linter configurado, CI sem gate de teste, commits mistos com uso real de Conventional Commits).

## Itens [INCERTO] pendentes de resposta do usuário (Etapa D, estilo Grilling)
1. [RESOLVIDO 2026-07-12] validate_url: confirmado por grep em todo o repo que é código morto (só usada em teste). Spec atualizado.
2. [RESOLVIDO 2026-07-12] Confirmado via `gh api`: default_workflow_permissions=write. Spec atualizado.
3. [RESPONDIDO 2026-07-12] Usuário confirmou: expand_large_companies_br.py foi tentativa que não foi eficaz. Registrado como débito + candidato a feature futura (reaproveitar portal_verification.py, fix_vagas_urls_guesser.py, scoring_utils.py). NÃO iniciar essa feature agora - fica para um /sdd <ideia> futuro, com Grilling completo.
4. [RESOLVIDO 2026-07-12] Investigado via git log: ambos aparecem só em 1-2 commits (f11d69e, 0ea021e), sem referência em workflow/script. Correção pontual já aplicada e commitada. Marcados como candidatos a remoção no spec. Usuário pediu para eu tomar ação com base na utilidade - conclusão registrada, remoção do arquivo não feita (fora de escopo desta adoção, que é só documentação).

## Todos os itens INCERTO resolvidos - pronto para gate de aprovação da baseline

## Próxima ação
Apresentar ao usuário: specs baseline gerados, itens INCERTO acima (um por vez, estilo Grilling) e as dívidas encontradas (seção 7 de cada spec). Depois do gate de aprovação da baseline, propor micro-commits (docs/config apenas).
