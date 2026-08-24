# Curadoria e expansão da lista de empresas

Data da pesquisa: 2026-08-23

## Resultado

Foram aprovadas e adicionadas 240 empresas novas a `src/data/input/list.csv`. A lista original tinha 1.465 registros e passou a ter 1.705. A curadoria cobre 12 segmentos:

| Segmento | Novas empresas |
| --- | ---: |
| Financeiro | 43 |
| Serviços e Outros | 40 |
| Tecnologia | 37 |
| Construção e Imóveis | 21 |
| Saúde | 20 |
| Varejo e Consumo | 19 |
| Indústria | 17 |
| Mídia e Entretenimento | 13 |
| Educação | 13 |
| Agro e Alimentos | 9 |
| Logística e Mobilidade | 6 |
| Energia e Utilities | 2 |

O lote excede o mínimo solicitado de 100 empresas e permanece abaixo do limite de 1.000. As 45 entradas que ficaram em bloqueio técnico, erro, timeout, DNS, TLS ou redirecionamento não foram adicionadas nesta etapa.

## Critérios de inclusão

- A empresa não podia ter o mesmo nome normalizado no CSV existente.
- A URL precisava ser uma página oficial de carreira, página institucional de candidatura ou ATS associado à empresa.
- Foram priorizadas páginas com vagas, banco de talentos, cadastro de currículo ou instruções explícitas para candidatura.
- URLs repetidas foram removidas mesmo quando o nome comercial era diferente. Isso excluiu, por exemplo, Creditas/Bcredi, Brasilseg/BB Seguridade, Grupo Positivo/Positivo Tecnologia e Hospital Alemão Oswaldo Cruz/Hospital Oswaldo Cruz, que já apontavam para URLs presentes na lista.
- Na revisão semântica, também foram removidas marcas, subsidiárias ou nomes abreviados já representados, incluindo BP-Beneficência Portuguesa, Itaú, Safra, Decathlon, Shopee, Le Biscuit Varejo, Agrária, DIA, Porto e Kroton/Cogna.
- A rodada seguinte aplicou a mesma regra antes da inclusão: comparação de grupo, marca, subsidiária, domínio da carreira e nome alternativo. Empresas sem evidência clara de candidatura foram deixadas de fora, mesmo quando apareciam em resultados de busca.
- As empresas aprovadas foram incorporadas com `Status da URL = 1` e data de entrada `2026-08-23`; o lote intermediário `new_items.csv` foi esvaziado após a incorporação.

## Cobertura e evidências

As fontes foram pesquisadas por blocos setoriais em páginas primárias das próprias empresas e seus ATS. Exemplos de fontes verificadas:

- Financeiro: [Goldman Sachs Brasil](https://www.goldmansachs.com/worldwide/brazil/careers/), [Banco BOCOM BBM](https://www.bocombbm.com.br/trabalhe-conosco/), [WTW](https://careers.wtwco.com/pt/jobs/search), [Marsh](https://careers.marsh.com/br/pt) e [Uniprime](https://www.uniprime.com.br/singular/uniprime-do-iguacu/p/oportunidades-de-trabalho).
- Tecnologia: [Amdocs](https://jobs.amdocs.com/careers?location=Brazil), [Palo Alto Networks](https://jobs.paloaltonetworks.com/en/location/brazil-jobs/47263/3469034/2), [Kantar](https://careers.kantar.com/br/job-search), [NIQ](https://nielseniq.com/global/en/jobs/) e [Temenos](https://www.temenos.com/about-us/careers/).
- Serviços: [Grupo GPS](https://gpssa.pandape.infojobs.com.br/), [TTEC](https://www.ttecjobs.com/pt-br/localiza%C3%A7%C3%A3o/sao-paulo-bresil-jobs/44028/3469034-3448433/3), [G4S Brasil](https://careers.g4s.com/pt-pt/localiza%C3%A7%C3%A3o/brazil-jobs/3072/3469034/2), [Ipsos](https://www.ipsos.com/pt-br/oportunidades-na-ipsos) e [Henkel Brasil](https://www.henkel.com.br/carreiras/vagas-e-cadastro).
- Indústria, energia e agro: [Repsol Sinopec Brasil](https://portalrepsin01d.cloudapp.repsol.com/trabalhe-conosco/), [Wabtec](https://careers.wabtec.com/pt/jobs), [Alstom](https://jobsearch.alstom.com/viewalljobs/?locale=pt_BR), [Midea Carrier](https://mideacarrier.gupy.io/) e [Korin](https://korinagricultura.com.br/trabalhe-na-korin/).
- Construção e logística: [Tegra](https://tegraincorporadora.gupy.io/), [Sacyr](https://sacyrpeople.sacyr.com/pt), [Timenow](https://timenow.com.br/carreiras/vagas/), [Porto Itapoá](https://www.portoitapoa.com/trabalhe_conosco/) e [Estoca](https://estoca.com.br/carreiras).
- Saúde e educação: [Instituto Butantan](https://butantan.gov.br/trabalhe-conosco), [Hospital São Camilo](https://www.hospitalsaocamilo.org.br/trabalhe-conosco/), [Grupo Orizonti](https://atracaodetalentos.totvs.app/grupoorizonti/extended), [Gran Cursos Online](https://vemsergran.gupy.io/) e [FIA Business School](https://fia.com.br/trabalhe-conosco/).
- Varejo, alimentos e hospitalidade: [Grupo Koch](https://grupokoch.jobs.recrut.ai/), [Farmácias São João](https://farmaciasaojoao.gupy.io/), [Grupo Muffato](https://muffato.jobs.recrut.ai/), [Tirolez](https://tirolez.gupy.io/), [Vila Galé](https://recrutamento.vilagale.com/) e [Tauá Resorts](https://tauaresorts.com.br/trabalhe-conosco).
- Segunda rodada de tecnologia e telecom: [Equinix](https://careers.equinix.com/jobs/search), [Scala Data Centers](https://scaladatacenters.gupy.io/), [Ascenty](https://ascenty.com/sobre/ascenty/trabalhe-conosco/), [NIC.br](https://nic.br/vagas/), [Zscaler](https://www.zscaler.com/br/careers) e [NICE](https://www.nice.com/careers/apply).
- Segunda rodada financeira: [Oliveira Trust](https://www.oliveiratrust.com.br/trabalhe-conosco), [Zurich Seguros](https://www.zurich.com.br/a-zurich/trabalhe-na-zurich), [Deutsche Bank](https://careers.db.com/), [BlackRock](https://careers.blackrock.com/) e [S&P Global](https://www.spglobal.com/en/careers).
- Segunda rodada de serviços e logística: [SGS](https://www.sgs.com/pt-br/a-empresa/carreiras-na-sgs/oportunidades-de-emprego), [Bureau Veritas](https://careers.bureauveritas.com/Brazil/?locale=en_US), [Iron Mountain](https://ironmountain.pandape.infojobs.com.br/), [CBRE](https://careers.cbre.com/pt_BR/careers/SearchJobs) e [JLL](https://www.jll.com/careers).
- Terceira rodada: [Grupo Santa Joana](https://santajoana.com.br/trabalhe-conosco/), [PUCRS](https://pucrs.gupy.io/), [Kicaldo](https://kicaldo.com.br/trabalhe-conosco), [Panasonic Brasil](https://holdings.panasonic/global/corporate/careers.html), [Portonave](https://www.portonave.com.br/trabalhe-conosco/) e [Meliá](https://careers.melia.com/).
- Quarta rodada: [Ciena](https://www.ciena.com/careers/working-at-ciena), [Intertek Brasil](https://www.intertek-br.com/carreiras/), [DNV](https://www.dnv.com.br/careers/), [Eurofins](https://careers.eurofins.com/), [WSP](https://www.wsp.com/pt-br/carreiras/oportunidades-de-emprego?country=BR), [Biomm](https://biomm.vagas.solides.com.br/), [UNIP](https://www.unip.br/universidade/trabalhe_conosco.aspx), [Grupo Bahamas](https://bahamas.jobs.recrut.ai/) e [Sisprime](https://sisprimedobrasil.gupy.io/).
- Quinta rodada auditada: [Krones](https://career.krones.com/?locale=pt_BR), [KSB](https://www.ksb.com/pt-br/sobre-a-ksb/carreira), [Konecranes](https://konecranes.careers/pt-br), [Atvos](https://vagas.atvos.com/), [Coopavel](https://coopavel.com.br/trabalheconosco/), [Patrimar](https://www.patrimar.com.br/fale-conosco/trabalhe-conosco/) e [Wyndham](https://careers.wyndhamhotels.com/content/LATAMC/?locale=en_US).
- A auditoria HTTP externa percorreu as 298 URLs candidatas antes da limpeza final. Treze foram removidas por retorno 404 ou caminho de carreira claramente desatualizado; das 285 restantes, 240 retornaram HTTP 2xx e foram incorporadas. As respostas 403, 406, 429, 308 e erros de TLS foram mantidas fora desta etapa por exigirem nova validação manual.

Cada linha adicionada mantém no próprio CSV a URL da fonte de carreira ou candidatura usada na validação. Páginas dinâmicas de ATS podem mudar o número de vagas depois da data desta pesquisa; por isso a curadoria valida o canal oficial, não promete que toda empresa terá uma vaga aberta permanentemente.

## Limitações da validação

Foi feita uma checagem estrutural local contra os 1.465 registros existentes, incluindo nomes normalizados e URLs normalizadas, e outra contra as 285 linhas candidatas do lote. A checagem HTTP automatizada local foi complementada por uma auditoria externa de status e redirecionamento. As 240 entradas aprovadas foram incorporadas com status ativo; a lista mantém uma duplicidade histórica de nome normalizado, `Meliuz`/`Méliuz`, já presente antes desta expansão, sem duplicidade de URL.
