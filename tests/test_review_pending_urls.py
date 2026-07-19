import csv
from pathlib import Path

from scripts.review_pending_urls import (
    PendingCompany,
    ProbeResult,
    _manual_resolution,
    apply_approved_report,
    _extract_ats_urls,
    _extract_text,
    _is_ats_url,
    classify_probe,
    generate_review_report,
    load_pending_companies,
)


class TestLoadPendingCompanies:
    def test_loads_remaining_companies_from_first_section(self):
        pending_path = Path(__file__).parents[1] / "pendencias.md"

        companies = load_pending_companies(pending_path)

        assert [item.company for item in companies] == ["Banco do Brasil", "Passbolt"]


class TestClassifyProbe:
    def test_confirms_company_career_page_without_open_jobs(self):
        probe = ProbeResult(
            requested_url="https://example.com/careers",
            final_url="https://example.com/careers",
            status_code=200,
            title="Carreiras Empresa Exemplo",
            text="Empresa Exemplo não possui vagas abertas no momento",
        )

        result = classify_probe("Empresa Exemplo", probe)

        assert result.result == "confirmed"
        assert result.detail == "confirmed_no_openings"

    def test_rejects_200_without_company_identity(self):
        probe = ProbeResult(
            requested_url="https://example.com",
            final_url="https://example.com",
            status_code=200,
            title="Página inicial",
            text="Produtos e serviços",
        )

        result = classify_probe("Empresa Exemplo", probe)

        assert result.result == "invalid"
        assert result.detail == "missing_company_or_career_identity"

    def test_classifies_antibot_status_as_blocked(self):
        probe = ProbeResult(
            requested_url="https://example.com/careers",
            final_url="https://example.com/careers",
            status_code=403,
            title="",
            text="",
        )

        result = classify_probe("Empresa Exemplo", probe)

        assert result.result == "blocked"
        assert result.detail == "http_403"

    def test_classifies_timeout_as_blocked(self):
        probe = ProbeResult(
            requested_url="https://example.com/careers",
            final_url="https://example.com/careers",
            error="timeout",
        )

        result = classify_probe("Empresa Exemplo", probe)

        assert result.result == "blocked"
        assert result.detail == "timeout"

    def test_rejects_generic_redirect(self):
        probe = ProbeResult(
            requested_url="https://jobs.example.com/company",
            final_url="https://jobs.example.com",
            status_code=200,
            title="Portal de vagas",
            text="Encontre vagas e oportunidades",
        )

        result = classify_probe("Empresa Exemplo", probe)

        assert result.result == "invalid"
        assert result.detail == "missing_company_identity"

    def test_decodes_html_entities_in_company_name(self):
        probe = ProbeResult(
            requested_url="https://example.com/jobs",
            final_url="https://example.com/jobs",
            status_code=200,
            title="CIN&#xC9;POLIS - Trabalhe Conosco",
            text="Vagas disponíveis",
        )

        result = classify_probe("Cinépolis", probe)

        assert result.result == "confirmed"

    def test_accepts_two_letter_company_identity(self):
        probe = ProbeResult(
            requested_url="https://example.com/careers",
            final_url="https://example.com/careers",
            status_code=200,
            title="Carreiras na EY",
            text="Oportunidades profissionais",
        )

        result = classify_probe("EY", probe)

        assert result.result == "confirmed"

    def test_confirms_direct_ats_when_company_is_in_hostname(self):
        probe = ProbeResult(
            requested_url="https://ems.izirh.io",
            final_url="https://ems.izirh.io/",
            status_code=200,
            title="IziRH",
            text="",
        )

        result = classify_probe("EMS", probe)

        assert result.result == "confirmed"
        assert result.detail == "confirmed_direct_ats"

    def test_confirms_direct_ats_when_slug_splits_company_name(self):
        probe = ProbeResult(
            requested_url="https://jobs.ashbyhq.com/duck-duck-go",
            final_url="https://jobs.ashbyhq.com/duck-duck-go",
            status_code=200,
        )

        result = classify_probe("DuckDuckGo", probe)

        assert result.result == "confirmed"

    def test_confirms_direct_ats_with_documented_company_alias(self):
        probe = ProbeResult(
            requested_url="https://wd3.myworkdaysite.com/en-US/recruiting/mdlz/External",
            final_url="https://wd3.myworkdaysite.com/en-US/recruiting/mdlz/External",
            status_code=200,
        )

        result = classify_probe("Mondelez Internacional", probe)

        assert result.result == "confirmed"

    def test_classifies_cloudflare_challenge_as_blocked(self):
        probe = ProbeResult(
            requested_url="https://example.com/careers",
            final_url="https://example.com/careers",
            status_code=200,
            title="Attention Required! | Cloudflare",
            text="Sorry, you have been blocked",
        )

        result = classify_probe("Empresa Exemplo", probe)

        assert result.result == "blocked"
        assert result.detail == "antibot_challenge"

    def test_extract_text_keeps_embedded_application_data(self):
        html = (
            '<script type="application/json">{"company":"Notion",'
            '"jobs":[{"title":"Engineer"}]}</script>'
        )

        assert "Notion" in _extract_text(html)


class TestAtsDiscovery:
    def test_extracts_direct_ats_link_from_institutional_page(self):
        html = (
            '<a href="https://job-boards.greenhouse.io/stone">'
            "Confira as vagas</a>"
        )

        assert _extract_ats_urls(html) == ["https://job-boards.greenhouse.io/stone"]

    def test_recognizes_existing_ats_url(self):
        assert _is_ats_url("https://jobs.quickin.io/empresa/jobs") is True
        assert _is_ats_url("https://empresa.example/carreiras") is False

    def test_returns_curated_direct_ats_found_on_official_page(self):
        item = PendingCompany(
            "Santander", "Site", "https://www.santander.com.br/hotsite/carreiras"
        )

        resolution = _manual_resolution(item)

        assert resolution is not None
        assert resolution["candidate_url"] == (
            "https://santander.wd3.myworkdayjobs.com/pt-BR/SantanderCareers"
        )
        assert resolution["proposed_platform"] == "Workday"
        assert "santander.com.br/hotsite/carreiras" in resolution["evidence"]

    def test_keeps_custom_career_portal_when_it_lists_jobs_directly(self):
        item = PendingCompany("Belvo", "Site", "https://belvo.com/careers")

        resolution = _manual_resolution(item)

        assert resolution is not None
        assert resolution["candidate_url"] == "https://belvo.com/careers"
        assert resolution["proposed_platform"] == "Site"


class TestGenerateReviewReport:
    def test_generates_report_without_modifying_inputs(self, tmp_path):
        pending_path = tmp_path / "pendencias.md"
        list_path = tmp_path / "list.csv"
        report_path = tmp_path / "report.csv"
        pending_path.write_text(
            "# Empresas com Pendência\n\n"
            "## Ainda Não Processadas\n"
            "| Empresa | Plataforma | URL (com problema apontado) |\n"
            "|---|---|---|\n"
            "| Empresa A | Site | https://a.example/carreiras |\n\n"
            "## Processadas mas 'Sem Solução'\n| Empresa |\n|---|\n| Empresa B |\n",
            encoding="utf-8",
        )
        with list_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "Status da URL",
                    "Data de Entrada",
                    "Nome da Empresa",
                    "Segmento da Empresa",
                    "Plataforma",
                    "URL",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Status da URL": "1",
                    "Data de Entrada": "2025-01-01",
                    "Nome da Empresa": "Empresa A",
                    "Segmento da Empresa": "Tecnologia",
                    "Plataforma": "Site",
                    "URL": "https://a.example/carreiras",
                }
            )
        pending_before = pending_path.read_bytes()
        list_before = list_path.read_bytes()

        def resolver(item):
            return {
                "candidate_url": item.current_url,
                "proposed_platform": item.current_platform,
                "probe": ProbeResult(
                    requested_url=item.current_url,
                    final_url=item.current_url,
                    status_code=200,
                    title="Carreiras Empresa A",
                    text="Empresa A vagas e oportunidades",
                ),
                "evidence": "title: Carreiras Empresa A",
            }

        rows = generate_review_report(
            pending_path, list_path, report_path, resolver=resolver
        )

        assert pending_path.read_bytes() == pending_before
        assert list_path.read_bytes() == list_before
        assert rows[0]["Ação"] == "keep"
        assert rows[0]["Resultado"] == "confirmed"
        assert report_path.exists()

    def test_marks_shared_candidate_url_for_manual_review(self, tmp_path):
        pending_path = tmp_path / "pendencias.md"
        list_path = tmp_path / "list.csv"
        report_path = tmp_path / "report.csv"
        pending_path.write_text(
            "## Ainda Não Processadas\n"
            "| Empresa | Plataforma | URL (com problema apontado) |\n"
            "|---|---|---|\n"
            "| Empresa A | Site | https://a.example/jobs |\n"
            "| Empresa B | Site | https://b.example/jobs |\n"
            "## Processadas mas 'Sem Solução'\n",
            encoding="utf-8",
        )
        list_path.write_text("Nome da Empresa,URL\n", encoding="utf-8")

        def resolver(item):
            return {
                "candidate_url": "https://shared.example/jobs",
                "proposed_platform": "Site",
                "probe": ProbeResult(
                    requested_url="https://shared.example/jobs",
                    final_url="https://shared.example/jobs",
                    status_code=200,
                    title=f"Carreiras {item.company}",
                    text=f"{item.company} vagas",
                ),
                "evidence": f"title: Carreiras {item.company}",
            }

        rows = generate_review_report(
            pending_path, list_path, report_path, resolver=resolver
        )

        assert [row["Ação"] for row in rows] == ["manual_review", "manual_review"]


class TestApplyApprovedReport:
    def test_updates_only_approved_rows_and_keeps_unresolved_pending_rows(self, tmp_path):
        pending_path = tmp_path / "pendencias.md"
        list_path = tmp_path / "list.csv"
        report_path = tmp_path / "report.csv"
        pending_path.write_text(
            "## Ainda Não Processadas\n"
            "| Empresa | Plataforma | URL (com problema apontado) |\n"
            "|---|---|---|\n"
            "| Empresa A | Site | https://a.example/careers |\n"
            "| Empresa B | Site | https://b.example/careers |\n"
            "## Processadas mas 'Sem Solução'\n| Empresa |\n|---|\n",
            encoding="utf-8",
        )
        list_path.write_text(
            "Status da URL,Data de Entrada,Nome da Empresa,Segmento da Empresa,Plataforma,URL\n"
            "0,2026-01-01,Empresa A,Tecnologia,Site,https://a.example/careers\n"
            "0,2026-01-01,Empresa B,Tecnologia,Site,https://b.example/careers\n",
            encoding="utf-8",
        )
        report_path.write_text(
            "Empresa,URL atual,URL candidata,Plataforma atual,Plataforma proposta,Resultado,Detalhe,Evidência,Ação\n"
            "Empresa A,https://a.example/careers,https://jobs.example/a,Site,Gupy,confirmed,ok,evidence,replace\n"
            "Empresa B,https://b.example/careers,https://b.example/careers,Site,Site,blocked,timeout,evidence,blocked\n",
            encoding="utf-8",
        )

        updated = apply_approved_report(pending_path, list_path, report_path)

        assert updated == ["Empresa A"]
        rows = list(csv.DictReader(list_path.open(encoding="utf-8")))
        assert rows[0]["Status da URL"] == "1"
        assert rows[0]["Plataforma"] == "Gupy"
        assert rows[0]["URL"] == "https://jobs.example/a"
        assert rows[1]["Status da URL"] == "0"
        assert "| Empresa A |" not in pending_path.read_text(encoding="utf-8")
        assert "| Empresa B |" in pending_path.read_text(encoding="utf-8")
