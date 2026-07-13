# Verificação de URLs e portais de carreira

**Status:** Concluído
**Data:** 2026-07-12

## 1. Resumo e Objetivo
Determina se a URL de uma empresa ainda está acessível (verificação de status HTTP) e, para o pipeline de descoberta, se a página realmente lista vagas abertas (verificação forte por plataforma de ATS).

## 2. User Stories (Requisitos Funcionais)
* **US01:** Como mantenedor, quero saber se uma URL de carreira está fora do ar, para poder marcar `Status da URL: "0"` sem depender de checagem manual.
* **US02:** Como responsável pela descoberta de novas empresas ([[baseline-descoberta-expansao]]), quero confirmar que uma URL candidata realmente lista vagas (e não é uma página genérica ou 404 disfarçado), para não poluir a lista com falsos positivos.

## 3. Regras de Negócio e Casos de Falha (Edge Cases)
### Verificação de status (`website_verification.py`)
* **Regra 01:** Tenta primeiro `HEAD`, com fallback para `GET` se o `HEAD` for bloqueado ou retornar 404, para economizar banda quando possível (`website_verification.py:verify_website_status`).
* **Regra 02:** Códigos 403, 406, 408 e 429 são tratados como sucesso: são respostas típicas de proteção anti-bot (WAF/Cloudflare) e não indicam que a página não existe (`website_verification.py:_check_status`).
* **Limite 01:** `SSLError` e `Timeout` também são tratados como sucesso, sob a mesma suposição de bloqueio anti-bot em vez de site fora do ar (`website_verification.py:verify_website_status`). Risco: um site genuinamente fora do ar por erro de certificado ou indisponibilidade real é classificado como ativo.
* **Regra 03:** Até 2 tentativas por URL, com espera crescente entre tentativas (`RETRY_DELAY * attempt`) (`website_verification.py:verify_website_status`).
* **Regra 04:** Verificação roda concorrente com até 15 workers, reaproveitando uma única sessão HTTP com Keep-Alive para todas as threads (`website_verification.py:verify_websites_concurrent`, `create_shared_session`).
* **Falha 01:** Item com falha final de verificação recebe `Status da URL: "0"` e campo temporário `_error` com a mensagem de diagnóstico, consumido pelo relatório de falhas do domínio [[baseline-pipeline-principal]].

### Verificação forte de portal (`portal_verification.py`)
* **Regra 05:** Só considera a página válida se o `GET` retornar 2xx/3xx; baixa no máximo os primeiros 500 KB do corpo (`portal_verification.py:_fetch_page`).
* **Regra 06:** Para portais Gupy, extrai o JSON embutido em `__NEXT_DATA__` e procura contagem de vagas nas chaves `jobs`, `jobList`, `openJobs`, `vacancies` ou um objeto `job` com `id` (`portal_verification.py:_parse_next_data`, `_gupy_job_count`).
* **Regra 07:** Antes de aceitar um resultado Gupy, verifica se a URL redirecionou para o portal genérico `carreiras.gupy.io` sem o slug da empresa, ou se o `<title>` da página bate com títulos genéricos conhecidos (`GENERIC_GUPY_TITLES`); nesses casos, considera que a empresa não tem vagas reais, mesmo que a página responda 200 (`portal_verification.py:_gupy_is_generic_portal`). Motivo inferido pela implementação: portais Gupy costumam redirecionar para a home genérica quando a empresa não tem mais vagas ou o slug está errado, o que geraria falso positivo se só o status HTTP fosse checado.
* **Regra 08:** Subdomínios dedicados `*.gupy.io` (exceto `carreiras`, `portal` e `www`) são aceitos se o título não for genérico e o HTML contiver palavras-chave de vaga (`portal_verification.py:_gupy_has_jobs`).
* **Regra 09:** Para Greenhouse, aceita se o HTML contém palavras-chave de vaga, OU se um `HEAD` na URL final retorna 2xx/3xx, OU se retorna 406 (bloqueio anti-bot conhecido nesse domínio) (`portal_verification.py:_greenhouse_has_jobs`).
* **Regra 10:** Para os demais ATS conhecidos (`myworkdayjobs.com`, `lever.co`, `inhire`, `successfactors`, `pandape.infojobs`, `vagas.com.br`, `workable.com`) e qualquer URL não reconhecida, usa a heurística genérica: aceita se houver 2 ou mais ocorrências de palavras-chave de vaga (regex `vagas?|oportunidades|carreiras|trabalhe|jobs|emprego|candidate|inscri`), ou 1 ocorrência acompanhada de um termo de ação (`apply|candidat|inscri|search|requisition|opening`) (`portal_verification.py:_generic_has_jobs`, `verify_portal_has_jobs`).
* **Falha 02:** URL vazia ou sem prefixo `http` é rejeitada sem tentar rede (`portal_verification.py:verify_portal_has_jobs`).

## 4. Estrutura de Dados e Componentes
* **Arquitetura:** `website_verification.py` (verificação leve, usada no pipeline principal via `main.py:verify_urls`) e `portal_verification.py` (verificação forte, usada pelo pipeline de descoberta, ver [[baseline-descoberta-expansao]]). `portal_verification.py` reaproveita `create_shared_session` de `website_verification.py`.
* **Cache:** o pipeline de descoberta mantém `artifacts/url_cache.json` para evitar reverificar a mesma URL repetidamente (consumido fora deste domínio, ver [[baseline-descoberta-expansao]]).

## 5. Critérios de Aceite (verificáveis por teste)
* [x] CA01: Dada uma URL que responde HTTP 403, quando verificada por `website_verification`, então é classificada como sucesso (`Status da URL: "1"`).
* [x] CA02: Dada uma URL que gera `Timeout` em todas as tentativas, quando verificada, então é classificada como sucesso.
* [x] CA03: Dada uma URL Gupy cujo `__NEXT_DATA__` não contém vagas e que redireciona para `carreiras.gupy.io` sem slug, quando verificada por `verify_portal_has_jobs`, então retorna `False`.
* [x] CA04: Dada uma URL Greenhouse sem palavras-chave de vaga no HTML mas com `HEAD` retornando 200, quando verificada, então retorna `True`.
* [ ] CA05: Dada uma URL de plataforma genérica com só 1 ocorrência de palavra-chave e nenhum termo de ação, quando verificada, então retorna `False`. (Comportamento implementado, sem teste dedicado localizado.)

## 6. Fora de Escopo
* Descoberta de URLs candidatas (busca, heurísticas de slug): ver domínio [[baseline-descoberta-expansao]].
* Decisão de quando rodar a verificação (agendamento, CI): ver domínio [[baseline-automacao-ci]].

## 7. Dívidas e riscos observados
* `tests/test_verification.py` e `tests/test_website_verification.py` parecem cobrir o mesmo módulo (`website_verification.py`) com estilos de teste diferentes (`unittest.TestCase` vs. classe por função); possível redundância a consolidar.
* `portal_verification.py` só tem teste dedicado para a detecção de portal genérico Gupy (`tests/test_portal_verification.py:TestGupyGenericPortal`); a lógica de Greenhouse e o fallback genérico não têm teste localizado.
* A suposição de que 403/406/408/429/SSLError/Timeout sempre significam bloqueio anti-bot (e não site real fora do ar) não está documentada em nenhum lugar além do comentário no código; é uma decisão de produto implícita que pode mascarar sites genuinamente inativos.
