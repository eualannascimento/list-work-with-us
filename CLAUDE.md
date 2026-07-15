# Contexto do Repositório

Leia e siga OBRIGATORIAMENTE as regras mestras em `.rules/global.md` antes de qualquer interação.

Este repositório segue um workflow de Spec-Driven Development em fases (ver `.docs/specs/` e `.rules/global.md`):
Grilling (1) → Spec (2) → TDD (3) → Review (4) → Micro-commits (5) → Deploy (6).

Nunca escreva código de produção sem um Spec aprovado em `.docs/specs/` e sem teste falhando em `tests/`.

A baseline deste repositório (adotada em 2026-07-12, ver `.docs/architecture.md`) já documenta o que existia antes do SDD:
* [[baseline-pipeline-principal]] - `main.py` e os módulos em `src/py/functions/`.
* [[baseline-verificacao-urls]] - `website_verification.py` e `portal_verification.py`.
* [[baseline-descoberta-expansao]] - `scripts/` e `data/seeds/`.
* [[baseline-automacao-ci]] - `.github/workflows/`.
