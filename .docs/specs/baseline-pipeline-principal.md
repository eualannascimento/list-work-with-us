# Pipeline principal de atualização da lista

**Status:** Concluído
**Data:** 2026-07-12

## 1. Resumo e Objetivo
Orquestra a atualização diária/semanal do repositório: incorpora novos itens propostos, verifica o status de todas as URLs cadastradas, ordena e deduplica a lista e regenera o `README.md` a partir do `list.csv`.

## 2. User Stories (Requisitos Funcionais)
* **US01:** Como mantenedor do repositório, quero que novos itens em `new_items.csv` sejam incorporados a `list.csv` automaticamente, para não precisar mesclar manualmente as contribuições.
* **US02:** Como mantenedor, quero que toda URL da lista seja verificada a cada execução, para que o README não acumule links quebrados.
* **US03:** Como leitor do README, quero a lista ordenada por nome da empresa e sem duplicatas, para localizar uma empresa rapidamente.

## 3. Regras de Negócio e Casos de Falha (Edge Cases)
* **Regra 01:** Item de `new_items.csv` sem `URL` ou sem `Nome da Empresa` é descartado com aviso de log, não interrompe o processamento dos demais (`main.py:process_new_items`).
* **Regra 02:** Deduplicação contra a lista existente é feita por URL normalizada via `df_operations.py:clean_url` (remove espaços e barra final); não normaliza protocolo, maiúsculas/minúsculas nem query string (`main.py:process_new_items`).
* **Regra 03:** Todo item novo aceito entra com `Status da URL: "0"` e `Data de Entrada` igual à data de execução, no formato `AAAA-MM-DD` (`main.py:process_new_items`).
* **Regra 04:** Após processar `new_items.csv`, o arquivo é reescrito contendo só o cabeçalho, esvaziando o lote de contribuições pendentes (`main.py:process_new_items`).
* **Regra 05:** A leitura completa da lista aplica `clean_url` em toda URL antes de qualquer outra etapa, garantindo que o dado em memória esteja normalizado mesmo que o CSV em disco não esteja (`file_operations.py:read_and_filter_csv`).
* **Regra 06:** A ordenação da lista é alfabética por `Nome da Empresa`, normalizado via `unidecode` (remove acentos) para não depender de localidade (`main.py:sort_and_deduplicate`).
* **Regra 07:** Deduplicação final por URL exata (pós-normalização) descarta a segunda ocorrência em diante, mesmo que os demais campos divirjam (`main.py:sort_and_deduplicate`).
* **Regra 08:** Ao salvar, os campos temporários `Data do Status`, `Data de Publicação` e `_error` são removidos da cópia gravada em CSV; eles existem só durante a execução em memória (`main.py:save_results`).
* **Regra 09:** `README.md` é gerado concatenando o conteúdo bruto de `header.md` com a tabela Markdown, sem nenhuma transformação adicional no cabeçalho (`main.py:save_results`, `md_operations.py:load_header`).
* **Regra 10:** A tabela do README expõe só 3 colunas (nome com link, segmento, plataforma); `Status da URL` e `Data de Entrada` existem no CSV mas não aparecem no README (`md_operations.py:generate_markdown_table`).
* **Falha 01:** Falhas de verificação de URL não interrompem a geração do README; entram em um relatório de falhas impresso ao final da execução, ordenado por nome (`main.py:print_failure_report`).

## 4. Estrutura de Dados e Componentes
* **Arquivos de dados:** `src/data/input/new_items.csv` (entrada de contribuições), `src/data/input/list.csv` (lista mestre), `src/data/input/header.md` (cabeçalho fixo do README).
* **Colunas de `list.csv`:** `Status da URL`, `Data de Entrada`, `Nome da Empresa`, `Segmento da Empresa`, `Plataforma`, `URL` (`main.py:FIELDNAMES`).
* **Arquitetura:** `main.py` (orquestração) chama `src/py/functions/df_operations.py` (normalização de URL), `src/py/functions/file_operations.py` (I/O de CSV) e `src/py/functions/md_operations.py` (geração de README). A verificação de URL é delegada ao domínio [[baseline-verificacao-urls]].
* **Ponto de entrada:** `python main.py`, disparado pelo workflow do domínio [[baseline-automacao-ci]].

## 5. Critérios de Aceite (verificáveis por teste)
* [x] CA01: Dado um item válido em `new_items.csv`, quando o pipeline roda, então o item aparece em `list.csv` com `Status da URL: "0"` e a data de hoje.
* [x] CA02: Dado um item cuja URL (normalizada) já existe em `list.csv`, quando o pipeline roda, então o item é reportado como duplicado e não é adicionado.
* [x] CA03: Dada uma lista com nomes de empresa fora de ordem alfabética, quando o pipeline roda, então a lista salva e o README saem ordenados por nome (ignorando acentos).
* [x] CA04: Dada uma lista com duas entradas de URL idêntica, quando o pipeline roda, então só a primeira ocorrência é mantida.
* [x] CA05: Dado qualquer resultado de verificação de URL, quando o README é gerado, então as colunas `Status da URL` e `Data de Entrada` não aparecem na tabela final.

## 6. Fora de Escopo
* Verificação de status HTTP e de existência real de vagas: ver domínio [[baseline-verificacao-urls]].
* Descoberta de novas empresas candidatas: ver domínio [[baseline-descoberta-expansao]].

## 7. Dívidas e riscos observados
* `file_operations.py:save_sorted_csv` tem nome enganoso: apesar do nome, a função não ordena nada, apenas grava os dados na ordem em que chegam. A ordenação real acontece antes, em `main.py:sort_and_deduplicate`.
* `df_operations.py:validate_url` existe e tem teste dedicado, mas não é chamada em nenhum ponto do fluxo de `main.py` nem de nenhum script em `scripts/` (confirmado por busca em todo o repositório); é código morto, candidato a remoção ou a ser conectado a algum ponto de validação de entrada.
* `requirements.txt` lista dezenas de dependências de Jupyter/ipykernel que não aparecem nos imports de `main.py` nem de `src/py/functions/`; risco de instalação desnecessária no CI.
