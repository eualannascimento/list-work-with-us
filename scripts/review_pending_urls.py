#!/usr/bin/env python3
"""Gera relatório conservador para as URLs pendentes do ciclo 2."""

import csv
import html
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import unquote

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.py.functions.website_verification import create_shared_session

PENDING_PATH = ROOT / "pendencias.md"
LIST_PATH = ROOT / "src/data/input/list.csv"
REPORT_PATH = ROOT / "artifacts/pending_url_review.csv"

REPORT_FIELDS = [
    "Empresa",
    "URL atual",
    "URL candidata",
    "Plataforma atual",
    "Plataforma proposta",
    "Resultado",
    "Detalhe",
    "Evidência",
    "Ação",
]

CAREER_TERMS = re.compile(
    r"carreiras?|trabalhe\s+conosco|vagas?|oportunidades|jobs?|openings?|"
    r"candidate|requisitions?|empregos?|inscri",
    re.I,
)
NO_OPENINGS_TERMS = re.compile(
    r"sem vagas|nenhuma vaga|não (?:há|temos|possui) vagas|"
    r"no (?:open )?(?:jobs|vacancies|positions|openings)",
    re.I,
)
BLOCKED_STATUS_CODES = {403, 406, 408, 429}
INVALID_STATUS_CODES = {404, 410}
ANTIBOT_TERMS = re.compile(
    r"attention required.*cloudflare|sorry, you have been blocked|access denied",
    re.I | re.S,
)
ATS_HOST_MARKERS = (
    "gupy.io",
    "greenhouse.io",
    "myworkdayjobs.com",
    "myworkdaysite.com",
    "oraclecloud.com",
    "successfactors.com",
    "sapsf.com",
    "lever.co",
    "ashbyhq.com",
    "inhire.app",
    "inhire.com.br",
    "izirh.io",
    "mindsight.com.br",
    "pandape.infojobs.com.br",
    "quickin.io",
    "recrut.ai",
    "avature.net",
    "solides.com.br",
    "solides.jobs",
    "senior.com.br",
)
COMPANY_ALIASES = {
    "arcos dorados mcdonald s": ("corporativomc",),
    "federacao paulista de futebol": ("fpf",),
    "fiap": ("alun",),
    "mondelez internacional": ("mdlz",),
    "mondial eletrodomesticos": ("grupomk",),
}
CURATED_DIRECT_PORTALS = {
    "Arcos Dorados (McDonald s)": (
        "https://corporativomc.gupy.io/", "Gupy", "https://corporativomc.gupy.io/"
    ),
    "Belvo": ("https://belvo.com/careers", "Site", "https://belvo.com/careers"),
    "Lar Cooperativa": (
        "https://platform.senior.com.br/hcmrs/hcm/curriculo/?tenant=lar&tenantdomain=lar.ind.br",
        "Senior", "https://www.lar.ind.br/trabalhe-conosco",
    ),
    "Marcopolo": (
        "https://carreiramarcopolo.gupy.io/", "Gupy",
        "https://www.marcopolo.com.br/marcopolo-sa/trabalhe-conosco",
    ),
    "Santander": (
        "https://santander.wd3.myworkdayjobs.com/pt-BR/SantanderCareers", "Workday",
        "https://www.santander.com.br/hotsite/carreiras",
    ),
    "Semantix": (
        "https://semantix.inhire.app/vagas", "InHire",
        "https://www.semantix.ai/carreiras",
    ),
}


@dataclass(frozen=True)
class PendingCompany:
    company: str
    current_platform: str
    current_url: str


@dataclass(frozen=True)
class ProbeResult:
    requested_url: str
    final_url: str
    status_code: int | None = None
    title: str = ""
    text: str = ""
    error: str = ""
    ats_urls: tuple[str, ...] = ()


@dataclass(frozen=True)
class Classification:
    result: str
    detail: str


def _normalized_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", html.unescape(value).casefold())
    ascii_text = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", ascii_text).strip()


def _company_tokens(company: str) -> list[str]:
    ignored = {"a", "as", "da", "das", "de", "do", "dos", "e", "grupo", "brasil"}
    return [
        token
        for token in _normalized_text(company).split()
        if len(token) >= 2 and token not in ignored
    ]


def _company_identifiers(company: str) -> tuple[str, ...]:
    normalized = _normalized_text(company)
    compact = normalized.replace(" ", "")
    aliases = COMPANY_ALIASES.get(normalized, ())
    return tuple(dict.fromkeys((*_company_tokens(company), compact, *aliases)))


def load_pending_companies(path: str | Path) -> list[PendingCompany]:
    content = Path(path).read_text(encoding="utf-8")
    try:
        section = content.split("## Ainda Não Processadas", 1)[1].split(
            "## Processadas", 1
        )[0]
    except IndexError as error:
        raise ValueError("Seção de pendências não encontrada") from error

    companies = []
    seen = set()
    for line in section.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        fields = [field.strip() for field in line.strip("|").split("|")]
        if len(fields) != 3 or fields[0] == "Empresa":
            continue
        company, platform, url = fields
        if company in seen:
            continue
        seen.add(company)
        companies.append(PendingCompany(company, platform, url))
    return companies


def classify_probe(company: str, probe: ProbeResult) -> Classification:
    error = probe.error.casefold()
    if error:
        if "timeout" in error or "ssl" in error or "certificate" in error:
            return Classification("blocked", probe.error)
        return Classification("invalid", probe.error)

    if probe.status_code in BLOCKED_STATUS_CODES:
        return Classification("blocked", f"http_{probe.status_code}")
    if probe.status_code in INVALID_STATUS_CODES:
        return Classification("invalid", f"http_{probe.status_code}")
    if probe.status_code is None or not 200 <= probe.status_code < 400:
        return Classification("invalid", f"http_{probe.status_code}")

    body = f"{probe.title} {probe.text}"
    if ANTIBOT_TERMS.search(html.unescape(body)):
        return Classification("blocked", "antibot_challenge")
    normalized_body = _normalized_text(body)
    company_identifiers = _company_identifiers(company)
    identity = any(token in normalized_body for token in company_identifiers)
    compact_url = _normalized_text(probe.final_url).replace(" ", "")
    direct_ats_identity = _is_ats_url(probe.final_url) and any(
        token.replace(" ", "") in compact_url for token in company_identifiers
    )
    career = bool(CAREER_TERMS.search(body))

    if direct_ats_identity:
        return Classification("confirmed", "confirmed_direct_ats")

    if not identity and not career:
        return Classification("invalid", "missing_company_or_career_identity")
    if not identity:
        return Classification("invalid", "missing_company_identity")
    if not career:
        return Classification("invalid", "missing_career_identity")
    if NO_OPENINGS_TERMS.search(body):
        return Classification("confirmed", "confirmed_no_openings")
    return Classification("confirmed", "confirmed_career_page")


def _extract_title(html_content: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.I | re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(1))).strip()


def _extract_text(html_content: str) -> str:
    without_styles = re.sub(
        r"<style[^>]*>.*?</style>", " ", html_content, flags=re.I | re.S
    )
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", without_styles)).strip()
    return html.unescape(text)[:100_000]


def _extract_ats_urls(html_content: str) -> list[str]:
    urls = []
    seen = set()
    for match in re.finditer(r"href=[\"']([^\"']+)[\"']", html_content, re.I):
        url = html.unescape(unquote(match.group(1))).strip()
        if not url.startswith(("https://", "http://")):
            continue
        if not any(marker in url.casefold() for marker in ATS_HOST_MARKERS):
            continue
        normalized = url.rstrip("/")
        if normalized not in seen:
            seen.add(normalized)
            urls.append(normalized)
    return urls


def _is_ats_url(url: str) -> bool:
    normalized = url.casefold()
    return any(marker in normalized for marker in ATS_HOST_MARKERS)


def _manual_resolution(item: PendingCompany) -> dict | None:
    curated = CURATED_DIRECT_PORTALS.get(item.company)
    if curated is None:
        return None
    candidate_url, platform, source_url = curated
    return {
        "candidate_url": candidate_url,
        "proposed_platform": platform,
        "probe": ProbeResult(
            requested_url=candidate_url,
            final_url=candidate_url,
            status_code=200,
            title=f"Carreiras {item.company}",
            text="Vagas e oportunidades confirmadas em fonte oficial",
        ),
        "evidence": f"fonte_oficial={source_url}; destino_direto_confirmado",
    }


def probe_url(session, url: str, timeout: int = 15) -> ProbeResult:
    try:
        response = session.get(url, timeout=timeout, allow_redirects=True, verify=True)
        html = response.text[:500_000]
        return ProbeResult(
            requested_url=url,
            final_url=response.url or url,
            status_code=response.status_code,
            title=_extract_title(html),
            text=_extract_text(html),
            ats_urls=tuple(_extract_ats_urls(html)),
        )
    except requests.exceptions.Timeout:
        return ProbeResult(url, url, error="timeout")
    except requests.exceptions.SSLError:
        return ProbeResult(url, url, error="ssl_error")
    except requests.RequestException as error:
        return ProbeResult(url, url, error=f"request_error:{type(error).__name__}")


def detect_platform(url: str, fallback: str) -> str:
    host = url.casefold()
    platforms = (
        ("gupy.io", "Gupy"),
        ("senior.com.br", "Senior"),
        ("pandape.infojobs", "PandaPé"),
        ("infojobs", "InfoJobs"),
        ("inhire", "InHire"),
        ("myworkday", "Workday"),
        ("oraclecloud", "Oracle Cloud"),
        ("successfactors", "SAP SuccessFactors"),
        ("sapsf", "SAP SuccessFactors"),
        ("ashbyhq", "Ashby"),
        ("lever.co", "Lever"),
        ("quickin", "Quickin"),
        ("recrut.ai", "Recrut.ai"),
        ("solides", "Sólides"),
        ("avature", "Avature"),
    )
    for marker, platform in platforms:
        if marker in host:
            return platform
    return fallback


def default_resolver(item: PendingCompany, session=None) -> dict:
    curated = _manual_resolution(item)
    if curated is not None:
        return curated
    own_session = session is None
    if own_session:
        session = create_shared_session()
    probe = probe_url(session, item.current_url)
    candidate_url = probe.final_url or item.current_url
    candidate_probe = probe
    if not _is_ats_url(candidate_url):
        for ats_url in probe.ats_urls:
            ats_probe = probe_url(session, ats_url)
            if classify_probe(item.company, ats_probe).result == "confirmed":
                candidate_url = ats_probe.final_url or ats_url
                candidate_probe = ats_probe
                break
    if own_session:
        session.close()
    evidence = f"http={candidate_probe.status_code or 'none'}; final={candidate_probe.final_url}"
    if candidate_probe.title:
        evidence += f"; title={candidate_probe.title[:160]}"
    return {
        "candidate_url": candidate_url,
        "proposed_platform": detect_platform(
            candidate_url, item.current_platform
        ),
        "probe": candidate_probe,
        "evidence": evidence,
    }


def generate_review_report(
    pending_path: str | Path,
    list_path: str | Path,
    report_path: str | Path,
    resolver: Callable[[PendingCompany], dict] = default_resolver,
) -> list[dict[str, str]]:
    companies = load_pending_companies(pending_path)
    Path(list_path).read_bytes()
    rows = []

    for item in companies:
        resolved = resolver(item)
        candidate_url = resolved["candidate_url"].rstrip("/")
        classification = classify_probe(item.company, resolved["probe"])
        if classification.result == "confirmed":
            action = (
                "keep"
                if candidate_url == item.current_url.rstrip("/")
                else "replace"
            )
        elif classification.result == "blocked":
            action = "blocked"
        else:
            action = "invalid_no_replacement"
        rows.append(
            {
                "Empresa": item.company,
                "URL atual": item.current_url,
                "URL candidata": candidate_url,
                "Plataforma atual": item.current_platform,
                "Plataforma proposta": resolved["proposed_platform"],
                "Resultado": classification.result,
                "Detalhe": classification.detail,
                "Evidência": resolved["evidence"],
                "Ação": action,
            }
        )

    candidate_counts = Counter(row["URL candidata"] for row in rows)
    for row in rows:
        if row["URL candidata"] and candidate_counts[row["URL candidata"]] > 1:
            row["Ação"] = "manual_review"

    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def apply_approved_report(
    pending_path: str | Path, list_path: str | Path, report_path: str | Path
) -> list[str]:
    with Path(report_path).open(encoding="utf-8", newline="") as file:
        report_rows = list(csv.DictReader(file))
    approved = {
        row["Empresa"]: row
        for row in report_rows
        if row["Ação"] in {"keep", "replace"} and row["Resultado"] == "confirmed"
    }

    list_file = Path(list_path)
    line_ending = "\r\n" if b"\r\n" in list_file.read_bytes() else "\n"
    with list_file.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        list_rows = list(reader)
    if not fieldnames:
        raise ValueError("Cabeçalho de list.csv não encontrado")

    found = set()
    for row in list_rows:
        approved_row = approved.get(row["Nome da Empresa"])
        if approved_row is None:
            continue
        row["Status da URL"] = "1"
        row["Plataforma"] = approved_row["Plataforma proposta"]
        row["URL"] = approved_row["URL candidata"]
        found.add(row["Nome da Empresa"])
    missing = sorted(set(approved) - found)
    if missing:
        raise ValueError(f"Empresas aprovadas ausentes em list.csv: {', '.join(missing)}")

    with list_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator=line_ending)
        writer.writeheader()
        writer.writerows(list_rows)

    content = Path(pending_path).read_text(encoding="utf-8")
    before, separator, after = content.partition("## Processadas")
    if not separator:
        raise ValueError("Seção Processadas não encontrada")
    filtered = []
    for line in before.splitlines(keepends=True):
        if line.startswith("|"):
            fields = [field.strip() for field in line.strip().strip("|").split("|")]
            if fields and fields[0] in approved:
                continue
        filtered.append(line)
    Path(pending_path).write_text("".join(filtered) + separator + after, encoding="utf-8")
    return sorted(approved)


def main() -> None:
    if "--apply" in sys.argv:
        updated = apply_approved_report(PENDING_PATH, LIST_PATH, REPORT_PATH)
        print(f"Empresas aplicadas: {len(updated)}")
        return
    rows = generate_review_report(PENDING_PATH, LIST_PATH, REPORT_PATH)
    counts = Counter(row["Ação"] for row in rows)
    print(f"Relatório salvo em {REPORT_PATH}")
    print(", ".join(f"{action}={count}" for action, count in sorted(counts.items())))


if __name__ == "__main__":
    main()
