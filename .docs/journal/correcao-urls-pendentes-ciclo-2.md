# Diário: correção de URLs pendentes do ciclo 2

- **Spec:** `.docs/specs/correcao-urls-pendentes-ciclo-2.md`
- **Fase:** 5
- **Último passo concluído:** Relatório aprovado e aplicado. As 48 pendências confirmadas foram removidas da primeira seção, incluindo 12 URLs substituídas por destinos diretos de vagas. Banco do Brasil e Passbolt foram preservadas. A suíte tem 108 testes aprovados.
- **Próxima ação:** Revisar o diff e preparar commit em branch própria, se solicitado.
- **Arquivos tocados:** `.docs/specs/correcao-urls-pendentes-ciclo-2.md`, `.docs/journal/correcao-urls-pendentes-ciclo-2.md`, `tests/test_review_pending_urls.py`, `scripts/review_pending_urls.py`, `artifacts/pending_url_review.csv`
- **Comando de teste:** `.venv/bin/pytest -q`
- **Decisões desta execução:** Processar primeiro as 50 empresas únicas da seção "Ainda Não Processadas"; deixar as 225 empresas sem solução para outra rodada; gerar relatório antes de alterar a lista; tratar desafio anti-bot como bloqueio, não como sucesso; priorizar URL direta de ATS confirmada.
- **Pendências/bloqueios:** Passbolt permanece bloqueada por timeout no InHire direto; Banco do Brasil não revelou ATS direto verificável. Ambas seguem na primeira seção de `pendencias.md`.
