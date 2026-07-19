# Correção de URLs pendentes do ciclo 2

**Status:** Em Desenvolvimento
**Data:** 2026-07-19

## 1. Resumo e objetivo

Revalidar as 50 empresas únicas da seção "Ainda Não Processadas" de `pendencias.md`, corrigir URLs e plataformas quando houver evidência suficiente e registrar os casos inconclusivos. A lista deve priorizar a URL direta do portal de recrutamento que expõe as vagas, em vez de uma página institucional que apenas aponta para esse portal.

## 2. User stories

* **US01:** Como mantenedor, quero revisar cada pendência com evidências reproduzíveis, para evitar trocar uma URL válida por um palpite.
* **US02:** Como mantenedor, quero validadores específicos para as plataformas presentes no lote, para reduzir falsos positivos da heurística genérica.
* **US03:** Como mantenedor, quero revisar um relatório antes da aplicação, para decidir sobre casos inconclusivos sem alterar a lista mestre.
* **US04:** Como usuário da lista, quero que cada link confirmado leve ao portal de carreiras da empresa correta, mesmo quando não houver vagas abertas.
* **US05:** Como usuário da lista, quero abrir diretamente o ATS que lista as vagas, para não depender de navegação adicional dentro do site institucional.

## 3. Regras de negócio e casos de falha

* **Regra 01:** O lote contém as 50 empresas únicas da primeira seção de `pendencias.md`. A segunda ocorrência de Camil Alimentos é duplicada e não cria uma nova unidade de trabalho.
* **Regra 02:** Uma URL só recebe a classificação `confirmed` quando a resposta ou o conteúdo identifica a empresa e caracteriza uma página de carreira ou portal de vagas.
* **Regra 03:** Um portal identificado da empresa continua `confirmed` quando não houver vaga aberta. A ausência de vagas deve ser registrada no detalhe, sem transformar a URL em inválida.
* **Regra 04:** HTTP 2xx ou 3xx, isoladamente, não confirma uma URL. Redirecionamento para homepage, login genérico, portal genérico ou página de outra empresa deve ser rejeitado.
* **Regra 05:** HTTP 403, 406, 408, 429, timeout e erro SSL resultam em `blocked`, salvo quando outra evidência específica da plataforma confirmar a identidade do portal. Esses resultados não contam como `confirmed` nem como `invalid`.
* **Regra 06:** HTTP 404 ou 410, erro de DNS e redirecionamento para página genérica resultam em `invalid` quando confirmados após as tentativas previstas pelo verificador.
* **Regra 07:** Uma URL substituta deve vir de fonte oficial da empresa ou de portal ATS que identifique a empresa. Palpites por slug podem gerar candidatos, mas nunca aprovação automática.
* **Regra 07A:** Quando uma página institucional confirmada apontar para um ATS de vagas identificado, a URL do ATS tem precedência e deve ser usada como candidata da lista.
* **Regra 07B:** A URL institucional só pode ser mantida quando não houver portal de vagas direto identificável ou quando ela própria exibir as vagas sem redirecionar o usuário.
* **Regra 07C:** ATS aceitos incluem, entre outros, Gupy, Greenhouse, Workday, Oracle Cloud, SAP SuccessFactors, Lever, Ashby, InHire, PandaPé, Quickin, Recrut.ai, Avature e Sólides. O domínio ou o conteúdo do portal deve vincular o ATS à empresa.
* **Regra 08:** A plataforma deve ser recalculada a partir da URL confirmada. Grafias equivalentes, como `Infojobs`/`InfoJobs`, `Solides`/`Sólides` e `Inhire`/`InHire`, devem usar o nome canônico adotado pelo projeto.
* **Regra 09:** Cada empresa deve receber uma classificação final: `keep`, `replace`, `blocked`, `invalid_no_replacement` ou `manual_review`.
* **Regra 10:** O relatório deve ser produzido antes de qualquer escrita em `list.csv` e deve conter empresa, URL atual, URL candidata, plataforma atual, plataforma proposta, resultado, detalhe, evidência e ação.
* **Regra 11:** Apenas linhas com ação `keep` ou `replace` e evidência suficiente podem ser aplicadas automaticamente. `blocked`, `invalid_no_replacement` e `manual_review` permanecem em `pendencias.md`.
* **Regra 12:** Ao aplicar uma substituição, devem ser preservados `Data de Entrada`, `Nome da Empresa` e `Segmento da Empresa`. `Status da URL` passa a `1` somente para URL confirmada.
* **Regra 13:** Uma pendência resolvida deve ser removida da primeira seção de `pendencias.md`. O restante do arquivo não deve ser alterado nesta entrega.
* **Regra 14:** Nenhuma URL conhecida ou candidata pode provocar alteração na lista durante a etapa de geração do relatório.
* **Limite 01:** Toda requisição deve ter timeout explícito e quantidade finita de tentativas.
* **Falha 01:** Erro em uma empresa não interrompe o lote. O relatório registra a falha e continua.
* **Falha 02:** Se duas empresas resolverem para a mesma URL canônica, ambas vão para `manual_review`; a deduplicação não decide qual linha manter.

## 4. Estrutura de dados e componentes

* **Entrada:** primeira seção de `pendencias.md` e linhas correspondentes de `src/data/input/list.csv`.
* **Relatório:** `artifacts/pending_url_review.csv`, sem escrita em `list.csv` durante sua geração.
* **Aplicação:** comando separado que lê o relatório aprovado e atualiza `src/data/input/list.csv` e `pendencias.md`.
* **Verificação:** extensão de `src/py/functions/portal_verification.py` com estratégias para os ATS presentes no lote e código de orquestração em `scripts/`.
* **Testes:** novos testes em `tests/` para classificação, identidade da empresa, redirecionamentos, bloqueios, ausência de vagas, geração do relatório e aplicação.
* **CSV do relatório:** `Empresa`, `URL atual`, `URL candidata`, `Plataforma atual`, `Plataforma proposta`, `Resultado`, `Detalhe`, `Evidência`, `Ação`.

## 5. Critérios de aceite

* [ ] **CA01:** Dado o `pendencias.md` atual, quando o lote é carregado, então são geradas 50 unidades únicas e Camil Alimentos aparece uma vez.
* [ ] **CA02:** Dada uma página com HTTP 200 sem identidade da empresa ou sinais de carreira, quando validada, então não recebe `confirmed`.
* [ ] **CA03:** Dado um portal que identifica a empresa e informa zero vagas, quando validado, então recebe `confirmed` com o detalhe de ausência de vagas.
* [ ] **CA04:** Dado HTTP 403, 406, 408, 429, timeout ou erro SSL sem evidência adicional, quando validado, então recebe `blocked`.
* [ ] **CA05:** Dada uma URL que redireciona para portal genérico ou empresa diferente, quando validada, então recebe `invalid`.
* [ ] **CA06:** Dado um candidato gerado por slug sem confirmação de identidade, quando avaliado, então não pode gerar ação `replace`.
* [ ] **CA06A:** Dada uma página institucional que aponta para um ATS confirmado da empresa, quando o relatório é gerado, então a URL candidata é a do ATS e a ação é `replace`.
* [ ] **CA06B:** Dada uma página institucional sem link para ATS e que não lista vagas, quando o relatório é gerado, então ela não pode ser confirmada como URL final por inferência.
* [ ] **CA07:** Quando o relatório é gerado, `list.csv` e `pendencias.md` permanecem byte a byte iguais.
* [ ] **CA08:** Dado um relatório aprovado com ações `keep` e `replace`, quando o comando de aplicação roda, então somente essas linhas são atualizadas ou removidas das pendências.
* [ ] **CA09:** Dado um relatório com `blocked`, `invalid_no_replacement` ou `manual_review`, quando aplicado, então essas empresas permanecem em `pendencias.md` e não recebem status ativo por inferência.
* [ ] **CA10:** Dadas duas empresas com a mesma URL canônica, quando o relatório é gerado, então ambas recebem `manual_review`.
* [ ] **CA11:** Quando a entrega é concluída, `pytest -v --tb=short` passa sem regressões.
* [ ] **CA12:** O relatório contém exatamente as 50 empresas do escopo, com uma ação e uma evidência ou motivo de ausência de evidência para cada uma.

## 6. Fora de escopo

* Revalidar as 225 empresas da seção "Processadas mas 'Sem Solução'".
* Adicionar empresas novas.
* Alterar o formato de `list.csv` ou do README.
* Executar a correção automaticamente no GitHub Actions.
* Remover scripts antigos que não participem desta entrega.
* Fazer push, merge ou commit direto em `main`.

## 7. Sequência de entrega

1. Criar testes de classificação e geração de relatório.
2. Implementar os validadores e o gerador do relatório.
3. Executar a revisão das 50 empresas e apresentar o relatório.
4. Após aprovação do relatório, criar testes e implementar a aplicação.
5. Rodar a suíte, revisar o diff e preparar micro-commits em branch própria.
