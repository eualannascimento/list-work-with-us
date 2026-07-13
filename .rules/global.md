# Regras Globais do Projeto (Fase 0 - System Instructions)

ESTE ARQUIVO É SEU CONTEXTO MESTRE. VOCÊ DEVE SEGUIR ESTAS REGRAS EM QUALQUER INTERAÇÃO NESTE REPOSITÓRIO:

## 1. Comportamento e Comunicação
- **Idioma:** Responda, documente e explique em Português do Brasil (PT-BR). Código, nomes de variáveis, funções e arquivos DEVEM ser em Inglês; strings de log e conteúdo do README podem ser em PT-BR, seguindo o padrão já usado neste repositório.
- **Economia de Tokens e Respostas:** Seja ultra-conciso. Sem introduções amigáveis ("Claro, posso ajudar!"). Retorne apenas o que foi pedido. Foque em fornecer Diffs de código em vez de reescrever arquivos imensos inteiros.
- **Tolerância Zero a Alucinação:** Nunca adivinhe ou assuma uma regra de negócio que não esteja claramente documentada na pasta `.docs/specs/`. Se algo faltar, PARE e pergunte ao usuário.
- **Pontuação - travessão proibido:** NUNCA use o travessão (em dash, U+2014) nem a meia-risca (en dash, U+2013), em hipótese nenhuma: nem em textos, nem em documentação, nem em mensagens de commit, nem em código. Use sempre o hífen "-" no lugar.
- **Estilo anti-IA:** todo conteúdo gerado (código, docs, commits, textos) deve passar pelos critérios de exclusão E01-E25 de `.rules/anti-ai-style.md` antes de ser entregue.
- **Resiliência de contexto:** siga o protocolo de `.rules/context-management.md` (diário de execução, checkpoints, recuperação silenciosa). Nada necessário para retomar o trabalho pode existir apenas na conversa.

## 2. Stack e Convenções Reais deste Projeto
- **Linguagem:** Python 3.10 (`.python-version`). Sem framework web, sem banco de dados; estado vive em CSV/YAML versionados.
- **Dependências:** `requirements.txt` contém pacotes não usados em produção (resíduo de Jupyter/ipykernel); ao adicionar dependência nova, confirme que ela é realmente importada antes de listá-la.
- **Testes:** `pytest` (`pytest.ini`: `testpaths=tests`, `python_files=test_*.py`, `python_classes=Test*`). Comando: `pytest -v --tb=short`. Cobertura hoje está concentrada em `main.py` e `src/py/functions/`; o pipeline de descoberta em `scripts/` não tem teste - toda feature nova nessa área deve vir com testes desde o início.
- **Linter/formatter:** nenhum configurado hoje. Não introduza um linter novo sem alinhar com o usuário primeiro.
- **CI:** GitHub Actions faz commit automático direto em `main` após rodar `main.py` (ver `.docs/specs/baseline-automacao-ci.md`); nenhum workflow roda `pytest` antes do commit. Ao mexer nesses workflows, considere adicionar o gate de teste.

## 3. Princípios de Engenharia de Software
- **Spec-Driven Development (SDD):** Você é proibido de escrever código de produção sem antes ler ou exigir um arquivo Markdown `.md` de especificação aprovado em `.docs/specs/`.
- **TDD (Test-Driven Development):** Testes primeiro. Sempre. O ciclo é Red → Green → Refactor.
- **Segurança Default:** Valide e sanitize TODOS os inputs (assuma que o usuário é malicioso), nunca logue dados sensíveis, senhas ou tokens em texto puro, e nunca versione segredos (use variáveis de ambiente). Requisições HTTP a domínios externos devem ter timeout explícito.
- **Simplicidade:** Escreva o código mínimo necessário para o teste passar. Não antecipe funcionalidades fora do Spec (YAGNI).

## 4. Versionamento (A Regra de Ouro do Git)
- É PROIBIDO agrupar dezenas de alterações em um único commit.
- Você deve dividir alterações arquiteturais e de código em entregas lógicas (Micro-commits).
- Use o padrão *Conventional Commits* (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`) - já usado em parte do histórico deste repositório (`feat:`, `chore:`); padronize as mensagens de commit automático do CI para o mesmo estilo quando tocar nesses workflows.
- Nunca faça push direto para `main`. Todo trabalho entra via Pull Request.

## 5. Máquina de Estados do Workflow
Você só pode avançar de fase com autorização explícita do usuário:
`Grilling (1) → Spec (2) → TDD (3) → Review (4) → Commits (5) → Deploy (6)`
