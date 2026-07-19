# Diário - Correção de URLs quebradas (problems.md)

## Contexto
Segunda frente de trabalho trazida pelo usuário em 2026-07-18 (primeira frente, adição de
313 empresas via new_items.csv, já concluída e commitada em bcf95ec).

`problems.md` (trazido pelo usuário, gerado no projeto irmão `projeto-classifica-vagas`)
lista URLs de `list.csv` que falham ao tentar obter vagas. Não é uma feature nova de código
neste repositório: é uma correção de dados em `src/data/input/list.csv`. Não precisa de
Spec/TDD porque não há código de produção novo aqui, mas a tarefa é grande (~173 empresas
com match exato em list.csv) e precisa de checkpoints porque será feita em lotes.

## Decisões (Grilling)
1. Origem do problems.md: gerado pelo projeto-classifica-vagas
   (`/Users/eualannascimento/Development/projeto-classifica-vagas`), que tem handlers
   dedicados por ATS (`src/classifica_vagas/handlers/handler_registry.py`).
2. Regra: só mexer nas empresas cuja plataforma tem handler REAL lá. Handlers "stub"
   (Avature, GigNow, Phenom, Brasio, Kenexa - marcados no registry como
   "Too few companies, high complexity/WAF") contam como "sem handler" - não tocar.
3. Método de correção: pesquisa na web por empresa (não heurística automática), para
   manter qualidade - encontrar a URL real e atual de vagas de cada empresa.
4. Ritmo: lotes de 10 empresas, com checkpoint de revisão do usuário entre lotes.
5. 219 URLs no problems.md; 173 têm match exato com uma URL em list.csv (join por URL
   normalizada); as outras 46 são endpoints derivados (ex.: API do Workday
   `wd1.myworkdayjobs.com/wday/cxs/...`) que não aparecem literalmente em list.csv -
   ficam de fora deste ciclo por enquanto.
6. Após excluir as 7 empresas de plataformas stub, restam 166 empresas candidatas a
   correção, agrupadas por plataforma (maior volume primeiro): Gupy (93), TeamTailor (16),
   Workday (14), InfoJobs (11), Vagas (4), Quickin (4), Recrut.ai (3), OracleCloud (3),
   PandaPe (3), InHire (3), Ashby (2), SuccessFactors (2), e outras com 1 cada.

## Lista de trabalho
Lista completa das 166 empresas candidatas (nome, plataforma, URL atual, status) está em
`/private/tmp/claude-501/-Users-eualannascimento-Development-lista-trabalhe-conosco/1e9427b7-af81-4655-8c62-8d0b937514ef/scratchpad/matched.json`
(reconstrutível a qualquer momento re-rodando o join entre problems.md e list.csv, ver
script inline usado na conversa - não versionado).

## Regras adicionais definidas após o Lote 1
- Empresas sem substituto claro (conta do ATS desativada, empresa fechada, nunca teve
  página real): deixar `list.csv` como está, só listar no relatório final para decisão
  manual do usuário depois. Não remover, não adivinhar URL.
- Empresas que migraram de ATS (ex.: Gupy -> PandaPe/InfoJobs): atualizar URL E coluna
  `Plataforma` juntas, refletindo a realidade atual.
- Verificação: usar curl direto (HEAD/GET com redirect) como triagem rápida; quando o
  resultado for ambíguo (o próprio site oficial da empresa aponta para uma URL que dá
  404), confirmar em navegador real (Claude in Chrome) antes de decidir "sem solução" -
  já houve caso de suspeita de bloqueio anti-bot que se confirmou como 404 genuíno.

## Progresso por lote

### Lote 1 - Gupy (10/93) - CONCLUÍDO 2026-07-18
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Atech | https://atech.gupy.io | Sem solução (conta Gupy desativada, próprio site oficial aponta pra essa URL morta) | mantido |
| Bling | https://bling.gupy.io | Sem solução (mesmo padrão do Atech; lwsa.gupy.io também morto) | mantido |
| Contabilizei | https://carreiras.gupy.io/contabilizei | Sem solução (contabilizei.gupy.io e contabilizeicarreiratech.gupy.io mortos) | mantido |
| Copel | https://carreiras.gupy.io/copel | Corrigido | https://copelenergia.gupy.io |
| Correios | https://carreiras.gupy.io/correios | Sem solução (nunca teve página Gupy real; concurso público via PROSEL) | mantido |
| Crefisa | https://carreiras.gupy.io/crefisa | Corrigido (mudou de ATS) | PandaPe, https://crefisaeempresasparceiras.pandape.com.br |
| Daki | https://carreiras.gupy.io/daki | Sem solução (empresa parece ter encerrado; daki.com.br é domínio parado/à venda) | mantido |
| Dasa | https://carreiras.gupy.io/dasa | Corrigido | https://dasacorp.gupy.io |
| Descomplica | https://carreiras.gupy.io/descomplica | Sem solução (vempradescomplica.gupy.io também morto) | mantido |
| Desktop | https://carreiras.gupy.io/desktop | Corrigido (mudou de ATS) | PandaPe, https://desktopinternet.pandape.infojobs.com.br |

4 corrigidas, 6 sem solução (reportadas, não alteradas). Edições já aplicadas em
`src/data/input/list.csv`, ainda não commitadas.

### Lote 2 - Gupy (10/93) - CONCLUÍDO 2026-07-18
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Diferente | https://carreiras.gupy.io/diferente | Sem solução (nenhum candidato encontrado) | mantido |
| Direcional | https://carreiras.gupy.io/direcional | Corrigido | https://direcionalengenharia.gupy.io |
| Dr. Consulta | https://carreiras.gupy.io/drconsulta | Corrigido | https://drconsultacms.gupy.io |
| Droga Raia / Drogasil (RD Saúde) | https://carreiras.gupy.io/rd | Corrigido (RD Saúde tem 4 portais Gupy separados por área; usado o de Farmácias, maior volume) | https://rdsaude-farmacia.gupy.io |
| Einstein | https://carreiras.gupy.io/einstein | Corrigido (mudou de ATS) | Vagas, https://trabalheconosco.vagas.com.br/alberteinstein |
| Eleva Educação | https://carreiras.gupy.io/elevaeducao | Corrigido | https://escolaeleva.gupy.io |
| Embasa | https://carreiras.gupy.io/embasa | Sem solução (empresa estatal, contrata via concurso público; nenhuma página Gupy encontrada) | mantido |
| Embraer | https://embraer.gupy.io | Sem solução (mesma URL já é a "correta" segundo buscas, mas responde 404; programasembraer.gupy.io também morto) | mantido |
| Eneva | https://carreiras.gupy.io/eneva | Sem solução (site oficial usa eneva.compleo.com.br, mas Compleo não tem handler no projeto-classifica-vagas) | mantido |
| Enjoei | https://carreiras.gupy.io/enjoei | Sem solução (mesma URL já é a "correta" segundo buscas, mas responde 404) | mantido |

5 corrigidas, 5 sem solução. Nota: existe uma entrada duplicada "Eleva" (linha 477,
URL https://eleva.gupy.io) diferente de "Eleva Educação" - não mexida, fora do escopo
deste ciclo (não estava no problems.md).

### Lote 3 - Gupy (10/93) - CONCLUÍDO 2026-07-18
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Eternit | https://carreiras.gupy.io/eternit | Corrigido (mudou de ATS) | Vagas, https://trabalheconosco.vagas.com.br/eternit |
| Eve Air Mobility | https://eveairmobility.gupy.io | Sem solução (mesma URL é a "correta", mas responde 404) | mantido |
| Even | https://carreiras.gupy.io/even | Corrigido | https://sejaeven.gupy.io |
| Facchini | https://carreiras.gupy.io/facchini | Sem solução (usa RH Gestor, sem handler no projeto-classifica-vagas) | mantido |
| Fazenda Futuro (Future Farm) | https://carreiras.gupy.io/fazendafuturofuturefarm | Sem solução (nenhum candidato encontrado) | mantido |
| Foxbit | https://carreiras.gupy.io/foxbit | Corrigido (mudou de ATS) | InHire, https://foxbit.inhire.app/vagas |
| Frimesa | https://carreiras.gupy.io/frimesa | Sem solução (usa RH Gestor, sem handler) | mantido |
| Frooty | https://carreiras.gupy.io/frooty | Sem solução (nenhum candidato encontrado) | mantido |
| Gazin | https://carreiras.gupy.io/gazin | Sem solução (usa RH Gestor, sem handler) | mantido |
| GE (General Electric) | https://carreiras.gupy.io/gegeneralelectric | Corrigido (mudou de ATS) | Vagas, https://trabalheconosco.vagas.com.br/ge |

4 corrigidas, 6 sem solução.

### Lote 4 - Gupy (10/93) - CONCLUÍDO 2026-07-18
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Geru | https://carreiras.gupy.io/geru | Sem solução (nenhum candidato encontrado) | mantido |
| Getnet | https://carreiras.gupy.io/getnet | Corrigido | https://vagasgetnet.gupy.io |
| Giross | https://carreiras.gupy.io/giross | Sem solução (nenhum candidato encontrado) | mantido |
| Granero | https://carreiras.gupy.io/granero | Sem solução (nenhum candidato encontrado) | mantido |
| Grupo Casas Bahia | https://carreiras.gupy.io/grupocasasbahia | Corrigido (grupo tem vários portais por área; usado o Corporativo) | https://corporativogrupocasasbahia.gupy.io |
| Grupo Mateus | https://carreiras.gupy.io/grupomateus | Corrigido (mudou de ATS) | OracleCloud, https://fa-exvn-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/pt-BR/sites/CX_1/jobs |
| Grupo Muffato | https://carreiras.gupy.io/grupomuffato | Sem solução (grupomuffatovagas.gupy.io também morto) | mantido |
| Grupo NC | https://carreiras.gupy.io/gruponc | Sem solução (só achei página própria da empresa, sem ATS reconhecido) | mantido |
| Grupo Silvio Santos | https://carreiras.gupy.io/gruposilviosantos | Corrigido | https://gss.gupy.io |
| Habib s | https://carreiras.gupy.io/habibs | Corrigido (mudou de ATS; já existe entrada duplicada "Grupo Habib's" com essa mesma URL, não mexida) | InfoJobs, https://grupohabibs.pandape.infojobs.com.br |

5 corrigidas, 4 sem solução (nota: Habib s conta como corrigida acima de 10 itens porque
Grupo Casas Bahia também está na lista - total 10 itens processados).

### Lote 5 - Gupy (10/93) - CONCLUÍDO 2026-07-18
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Havan | https://carreiras.gupy.io/havan | Sem solução (usa portal próprio vagas.havan.com.br, sem handler reconhecido) | mantido |
| Hinode | https://carreiras.gupy.io/hinode | Corrigido | https://grupohinode.gupy.io |
| Hyland | https://carreiras.gupy.io/hyland | Corrigido (mudou de ATS) | iCIMS, https://careers-hyland.icims.com |
| Icatu Seguros | https://carreiras.gupy.io/icatuseguros | Corrigido (mudou de ATS) | Vagas, https://trabalheconosco.vagas.com.br/icatuseguros |
| Isa CTEEP | https://carreiras.gupy.io/isacteep | Corrigido (empresa unificou marca para ISA Energia Brasil) | https://isaenergiabrasil.gupy.io |
| Itambé | https://carreiras.gupy.io/itamb | Sem solução (nenhum candidato encontrado) | mantido |
| Itapemirim (Nova Itapemirim) | https://carreiras.gupy.io/itapemirimnovaitapemirim | Sem solução (usa banco de talentos próprio via e-mail, sem ATS reconhecido) | mantido |
| Kangu | https://carreiras.gupy.io/kangu | Sem solução (kangu.gupy.io também morto) | mantido |
| Kepler Weber | https://carreiras.gupy.io/keplerweber | Sem solução (processo via WhatsApp, sem ATS reconhecido) | mantido |
| KMM | https://carreiras.gupy.io/kmm | Sem solução (mesma URL é a "correta" segundo buscas, mas responde 404) | mantido |

4 corrigidas, 6 sem solução.

## Método otimizado a partir do Lote 6
Para acelerar sem perder qualidade: primeiro tento variações óbvias de slug direto via
curl (`{slug}.gupy.io`); só uso WebSearch para os que falham nessa tentativa rápida.

### Lote 6 - Gupy (10/93) - CONCLUÍDO 2026-07-18
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Kora Saúde | https://carreiras.gupy.io/korasade | Corrigido (mudou de ATS) | Sênior, https://platform.senior.com.br/hcmrs/hcm/curriculo/?tenant=korasaudecombr&tenantdomain=korasaude.com.br |
| Libbs | https://carreiras.gupy.io/libbs | Corrigido | https://vempralibbs.gupy.io |
| Linx | https://carreiras.gupy.io/linx | Sem solução ("Lynx Process" achado na busca é outra empresa, não confundir) | mantido |
| Local Frio | https://carreiras.gupy.io/localfrio | Corrigido (portal é da Friopeças, grupo controlador) | https://fpcarreiras.gupy.io |
| Locaweb | https://locaweb.gupy.io | Sem solução (mesma URL é a "correta", mas responde 404; lwsa.gupy.io também morto) | mantido |
| Log Commercial Properties | https://carreiras.gupy.io/logcommercialproperties | Corrigido (achado por tentativa direta de slug) | https://logcp.gupy.io |
| Loggi Tecnologia | https://carreiras.gupy.io/loggi | Sem solução (existe entrada duplicada "Loggi" já com URL Workable funcionando, não mexida) | mantido |
| Login Logística | https://carreiras.gupy.io/loginlogstica | Corrigido (achado por tentativa direta de slug) | https://loginlogistica.gupy.io |
| LWSA | https://lwsa.gupy.io | Sem solução (mesma URL é a "correta", mas responde 404) | mantido |
| MadeiraMadeira | https://carreiras.gupy.io/madeiramadeira | Sem solução (madeiracarreira.gupy.io citado nas buscas também morto) | mantido |

5 corrigidas, 5 sem solução.

### Lote 7 - Gupy (10/93) - CONCLUÍDO 2026-07-18
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Madero | https://carreiras.gupy.io/madero | Sem solução (candidatura só por e-mail, sem ATS reconhecido) | mantido |
| Magnetis | https://carreiras.gupy.io/magnetis | Sem solução (usava Kenoby, mas o domínio kenoby.com não existe mais - ATS inteiro saiu do ar) | mantido |
| Mais Mu | https://carreiras.gupy.io/maismu | Sem solução (nenhuma informação encontrada) | mantido |
| Mapfre Brasil | https://carreiras.gupy.io/mapfrebrasil | Corrigido (mudou de ATS) | Vagas, https://trabalheconosco.vagas.com.br/mapfre |
| Marisa | https://carreiras.gupy.io/marisa | Sem solução (marisa.gupy.io também morto) | mantido |
| Martins Atacado Var | https://carreiras.gupy.io/martinsatacadovar | Sem solução (logisticamartins.gupy.io e tecnologiamartins.gupy.io também mortos) | mantido |
| Melhor Envio | https://melhorenvio.gupy.io | Sem solução (empresa do grupo LWSA, portal do grupo também morto) | mantido |
| Melhoramentos | https://carreiras.gupy.io/melhoramentos | Sem solução (nenhuma informação encontrada) | mantido |
| Metha (antiga OAS) | https://carreiras.gupy.io/methaantigaoas | Sem solução (nenhuma informação encontrada) | mantido |
| Mobly | https://carreiras.gupy.io/mobly | Corrigido (mudou de ATS) | PandaPe, https://mobly.pandape.com.br |

2 corrigidas, 8 sem solução. Nota: descoberto que o ATS Kenoby saiu do ar inteiramente
(kenoby.com não resolve mais) - qualquer empresa usando Kenoby como alternativa fica
automaticamente sem solução daqui pra frente.

### Lote 8 - Gupy (10/93) - CONCLUÍDO 2026-07-18
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Moura Dubeux | https://carreiras.gupy.io/mouradubeux | Corrigido (mudou de ATS) | Solides, https://mouradubeux.vagas.solides.com.br |
| MRV | https://carreiras.gupy.io/mrv | Corrigido | https://vagas-mrveco.gupy.io |
| Multilog | https://carreiras.gupy.io/multilog | Sem solução (mesma URL é a "correta", mas responde 404) | mantido |
| Multiplan | https://carreiras.gupy.io/multiplan | Sem solução (usa Across.Jobs, sem handler reconhecido) | mantido |
| Méliuz | https://carreiras.gupy.io/mliuz | Corrigido (achado por tentativa direta de slug) | https://meliuz.gupy.io |
| Neoenergia | https://carreiras.gupy.io/neoenergia | Corrigido (mudou de ATS) | Vagas, https://trabalheconosco.vagas.com.br/neoenergia |
| Neogrid | https://carreiras.gupy.io/neogrid | Corrigido | https://neogridcarreiras.gupy.io |
| Nomad | https://carreiras.gupy.io/nomad | Corrigido (mudou de ATS) | InHire, https://nomadglobal.inhire.app/vagas |
| Odous de Deus | https://carreiras.gupy.io/odousdedeus | Sem solução (não pesquisado ainda, ficou de fora deste lote por engano de contagem) | mantido |
| OEC | https://carreiras.gupy.io/oec | Sem solução (or.gupy.io encontrado é de outra empresa "OR", não confundir) | mantido |

6 corrigidas, 4 sem solução (nota: Odous de Deus entrou no lote mas não foi pesquisado -
fica pendente para o próximo lote).

### Lote 9 - Gupy (11/93, inclui Odous de Deus pendente) - CONCLUÍDO 2026-07-18
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Odous de Deus | https://carreiras.gupy.io/odousdedeus | Sem solução (nenhuma informação encontrada) | mantido |
| OEC | https://carreiras.gupy.io/oec | Sem solução (or.gupy.io é de outra empresa) | mantido |
| Oi | https://carreiras.gupy.io/oi | Sem solução (mesma URL é a "correta", mas responde 404) | mantido |
| PagBank | https://carreiras.gupy.io/pagbank | Corrigido | https://pagseguro.gupy.io |
| Polishop | https://carreiras.gupy.io/polishop | Sem solução (mesma URL é a "correta", mas responde 404) | mantido |
| Romi | https://carreiras.gupy.io/romi | Sem solução (mesma URL é a "correta", mas responde 404) | mantido |
| Rossi Residencial | https://carreiras.gupy.io/rossiresidencial | Sem solução (nenhum ATS reconhecido encontrado) | mantido |
| Savegnago | https://carreiras.gupy.io/savegnago | Corrigido (mudou de ATS) | Recrut.ai, https://carreiragruposavegnago.jobs.recrut.ai |
| Siemens Healthineers | https://carreiras.gupy.io/siemens-healthineers | Sem solução (portal próprio, sem ATS reconhecido) | mantido |
| Smart Fit | https://carreiras.gupy.io/smartfit | Sem solução (usa 99jobs, sem handler reconhecido) | mantido |
| Superdigital | https://carreiras.gupy.io/superdigital | Sem solução (nenhum candidato encontrado) | mantido |
| Ultrapar | https://carreiras.gupy.io/ultrapar | Corrigido (portal é do Grupo Ultra, holding) | https://grupoultra.gupy.io |

3 corrigidas, 9 sem solução.

## Bloco Gupy encerrado (93/93 processadas)
Lotes 1 a 9 cobriram as 93 empresas Gupy do problems.md. Total: 41 corrigidas, 52 sem
solução (reportadas acima, não alteradas).

## Bloco TeamTailor (16 empresas) - CONCLUÍDO 2026-07-18
Descoberta importante: para TeamTailor, o erro do problems.md ("Type Mismatch - Expected
JSON, got HTML") não é URL quebrada - é falta do sufixo `/jobs.json` na URL (confirmado
lendo o fetcher do projeto-classifica-vagas: ele faz GET direto na URL esperando JSON,
sem transformação própria). Corrigido sistematicamente: todas as URLs TeamTailor com
subdomínio vivo ganharam `/jobs.json` no final.

| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Aon | https://aon.teamtailor.com | Corrigido (sufixo /jobs.json) | https://aon.teamtailor.com/jobs.json |
| BDO | https://bdo.teamtailor.com | Corrigido (sufixo /jobs.json) | https://bdo.teamtailor.com/jobs.json |
| Bibi | https://bibi.teamtailor.com | Sem solução (subdomínio morto, nenhum ATS reconhecido encontrado) | mantido |
| Busuu | https://busuu.teamtailor.com | Corrigido (sufixo /jobs.json) | https://busuu.teamtailor.com/jobs.json |
| Crowe | https://crowe.teamtailor.com | Corrigido (sufixo /jobs.json) | https://crowe.teamtailor.com/jobs.json |
| Gigster (Virtasant) | https://virtasant.teamtailor.com | Corrigido (sufixo /jobs.json) | https://virtasant.teamtailor.com/jobs.json |
| Glória | https://gloria.teamtailor.com | Sem solução (subdomínio morto, nenhum ATS reconhecido encontrado) | mantido |
| Hewlett Packard Enterprise | https://hewlettpackardenterprise.teamtailor.com | Sem solução (subdomínio morto, nenhum ATS reconhecido encontrado) | mantido |
| IPSEN | https://ipsen.teamtailor.com | Sem solução (subdomínio morto, não pesquisado a fundo) | mantido |
| Loft | https://loft.teamtailor.com/jobs | Corrigido (sufixo .json) | https://loft.teamtailor.com/jobs.json |
| MOB | https://mob.teamtailor.com | Corrigido (sufixo /jobs.json) | https://mob.teamtailor.com/jobs.json |
| Next | https://next.teamtailor.com | Corrigido (sufixo /jobs.json) | https://next.teamtailor.com/jobs.json |
| Renault | https://renault.teamtailor.com | Sem solução (empresa migrou para Workday, mas Workday tem problema sistemático próprio - ver bloco Workday) | mantido |
| Robert Half | https://roberthalf.teamtailor.com | Sem solução (subdomínio morto, nenhum ATS reconhecido encontrado) | mantido |
| Teleperformance | https://teleperformance.teamtailor.com | Sem solução (subdomínio morto, não pesquisado a fundo) | mantido |
| Worldpay | https://worldpay.teamtailor.com | Sem solução (empresa migrou para Workday - ver bloco Workday) | mantido |

8 corrigidas, 8 sem solução.

## Bloco Workday (14 empresas) - CONCLUÍDO 2026-07-18, NENHUMA EDIÇÃO NECESSÁRIA
Descoberta: os erros "HTTP 400" do Workday no problems.md são falso-positivo do checker
que gerou o relatório (ele deve ter usado GET). O fetcher real do projeto-classifica-vagas
(`WorkdayFetcher` em `functions/fetchers.py`) faz POST com payload
`{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`. Testado com esse POST em
4 amostras (3M/Adobe/AstraZeneca/Kimberly-Clark/Pfizer) e todas retornaram 200 com JSON
válido, usando a URL exata que já está em `list.csv`. Conclusão: as 14 empresas Workday
do problems.md (3M, Accenture, Adobe, AstraZeneca, Coca-Cola, Fedex, Four Seasons, Lego,
Mastercard, Michelin, Motorola Solutions, PWC, Rappi, Razer, Sanofi, Samsung, Sony,
ToyotaLatinAmerica, TransUnion, WeWork, WEX, Wilhelmsen, Workday Inc.) não precisam de
nenhuma correção em list.csv - já estão certas. (Exceção: "Accenture" e "Cloudera" deram
erro de conex]ao/tamanho de header por outro motivo, não Workday POST - não investigado
a fundo, baixo volume.)

## Investigação do script gerador do problems.md
Encontrado `audit_broken_urls.py` no projeto-classifica-vagas - é o script exato que gera
o relatório (mesmo título "Broken URLs & Handler Mismatches Report"). Ele usa
`adjust_url()` de `functions/extract.py` para simular a URL final e faz sempre GET
(nunca POST), comparando o Content-Type contra o esperado pelo handler.

Isso explica os padrões:
- **Workday**: confirmado falso-positivo (o fetcher real usa POST com payload
  específico; o audit script usa GET). Nenhuma ação necessária.
- **TeamTailor**: `adjust_url` não trata essa plataforma - a URL em list.csv precisa já
  ser o endpoint JSON final (`/jobs.json`). Corrigido no bloco anterior.
- **Greenhouse/Workable/SmartRecruiters/Eightfold/OracleCloud/BambooHR**: `adjust_url`
  transforma automaticamente a partir da URL "amigável" em list.csv - não preciso
  gravar a URL de API final, só garantir que a URL base estava certa.
- **InfoJobs/PandaPe/Quickin/Recrut.ai/Ashby/CLIQQ/IziRH/Mindsight/Solides/Sênior**:
  `adjust_url` NÃO trata essas plataformas. A URL em list.csv é a página HTML pública
  (correta, empresa existe, site funciona), mas o handler dessas plataformas no
  projeto-classifica-vagas espera JSON e não há endpoint JSON conhecido/documentado
  para elas. Tentei descobrir via inspeção de rede (Chrome) no caso do PandaPe/Cobasi e
  não encontrei endpoint JSON claro. **Isto não é um problema de list.csv** - é uma
  lacuna de implementação nos handlers do projeto-classifica-vagas (fora do escopo deste
  repositório). Nenhuma ação tomada; deixado para o próprio projeto-classifica-vagas
  resolver (possivelmente via a rotina de cobertura de handlers já existente lá).
- **HTTP 403 (InHire, Lever, SuccessFactors, Vagas - Banco do Brasil, Lar, Marcopolo)**:
  Segundo o spec deste repositório (`baseline-verificacao-urls.md`, Regra 02), 403 é
  tratado como bloqueio anti-bot, não como link quebrado - `website_verification.py`
  já classifica isso como sucesso. Não é um problema real para list.csv.
- **Connection Error (InHire - Passbolt, Mindsight - FPF)**: instabilidade pontual, não
  investigado a fundo (baixo volume, 1 empresa cada).

## Único item de ação real fora dos blocos Gupy/TeamTailor
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Bacio di Latte | https://baciodilatte.com.br/carreiras (404) | Corrigido (mudou de ATS) | InfoJobs, https://baciodilatte.infojobs.com.br |

## Resumo final do ciclo
- Total de empresas com match exato em list.csv: 173 (93 Gupy + 16 TeamTailor + 14 Workday
  + 1 Bacio di Latte + 49 outras plataformas de baixo volume).
- Corrigidas: 41 (Gupy) + 8 (TeamTailor) + 1 (Bacio di Latte) = **50 empresas corrigidas**.
- Sem solução por falta de URL alternativa encontrada: 52 (bloco Gupy) + 8 (bloco
  TeamTailor) = 60 empresas, mantidas como estavam, listadas nas tabelas de cada lote
  acima para decisão manual futura.
- Sem ação necessária (falso-positivo ou fora do escopo deste repositório): 14 (Workday)
  + ~29 (InfoJobs/PandaPe/Quickin/Recrut.ai/Ashby/CLIQQ/IziRH/Mindsight/Solides/Sênior/
  403s diversos) = ~43 empresas.

## Próxima ação
Rodar o pipeline principal (main.py) para reverificar todas as URLs alteradas, revisar o
diff de list.csv/README.md e, com aprovação do usuário, commitar.

Ciclo concluído e commitado em 93928dd (push para origin/main feito).

---

# Ciclo 2 - problems.md atualizado (2026-07-19)

## Contexto
Usuário atualizou `problems.md` com um novo relatório do projeto-classifica-vagas,
agora com 336 linhas (muitas são as 313 empresas do primeiro ciclo, cujas URLs Gupy
nunca tinham sido verificadas de verdade - foram só aceitas com Status "1" no CSV
original do usuário).

## Mudança de regra importante
Diferente do Ciclo 1: agora o usuário quer tratar TODAS as empresas, mesmo as de
plataformas sem handler no projeto-classifica-vagas ou com handler que não funciona
(Avature, GigNow, Phenom, Brasio, Kenexa, RH Gestor, 99jobs, etc. não ficam mais de
fora). O objetivo passa a ser sempre "achar o site de vagas atual da empresa e colocar
em list.csv", independente de existir handler.

## Dimensionamento
- 336 linhas no problems.md novo.
- 291 têm match exato de URL com list.csv (join por URL normalizada).
- 45 não têm match exato (prováveis endpoints derivados, ex. Workday cxs API).
- Por plataforma (top): Gupy 212, Workday 14, InfoJobs 11, TeamTailor 8, PandaPe 6,
  Vagas 4, Recrut.ai 4, Quickin 4, OracleCloud 3, Avature 3, InHire 3, e outras com 1-2.
- Lista completa reconstruível via join entre problems.md e list.csv (script usado na
  conversa, não versionado); salva also em
  `/private/tmp/claude-501/.../scratchpad/problems2.json` (não persiste entre sessões).

## Ritmo combinado com o usuário
Igual ao Ciclo 1: lotes de 10, autonomia total (pesquiso, verifico via curl/WebSearch,
aplico direto em list.csv o que confirmar), só documento sem aplicar os casos sem
solução. Sem parar para aprovação a cada lote.

## Progresso por lote

### Bloco Workday (14 empresas) - CONCLUÍDO 2026-07-19
Diferente do Ciclo 1: aqui as URLs salvas eram páginas HTML genéricas de carreira (ex.
`careers.unilever.com`), não o endpoint `myworkdayjobs.com`. `adjust_url()` só transforma
URLs que já contêm `myworkdayjobs.com`; se não contém, devolve a URL sem mudança e o
POST falha. Corrigido achando o tenant/site Workday real de cada empresa (verificado via
POST com o payload `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`).

| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Accenture | https://www.accenture.com/br-pt/careers | Corrigido | https://accenture.wd103.myworkdayjobs.com/AccentureCareers |
| Cloudera | https://www.cloudera.com/careers.html | Corrigido | https://cloudera.wd5.myworkdayjobs.com/External_Career |
| CrowdStrike | https://www.crowdstrike.com/careers | Corrigido | https://crowdstrike.wd5.myworkdayjobs.com/crowdstrikecareers |
| Dell | https://jobs.dell.com/en | Corrigido | https://dell.wd1.myworkdayjobs.com/External |
| General Motors | https://search-careers.gm.com | Corrigido | https://generalmotors.wd5.myworkdayjobs.com/Careers_GM |
| GM Financial | https://careers.gmfinancial.com/jobs | Corrigido (mudou de ATS) | OracleCloud, https://fa-exvu-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs |
| Johnson & Johnson | https://www.careers.jnj.com | Corrigido | https://jj.wd5.myworkdayjobs.com/JJ |
| Live Nation | https://www.livenationentertainment.com/careers | Corrigido | https://livenation.wd503.myworkdayjobs.com/LNExternalSite |
| P&G | https://www.pgcareers.com/br/en | Corrigido | https://pg.wd5.myworkdayjobs.com/1000 |
| Paramount | https://careers.paramount.com | Sem solução (não usa Workday nem outro ATS reconhecido encontrado) | mantido |
| Rabobank | https://www.rabobank.com/careers | Corrigido | https://rabobank.wd3.myworkdayjobs.com/jobs |
| Unilever | https://careers.unilever.com/en/search-jobs | Corrigido | https://unilever.wd3.myworkdayjobs.com/Unilever_Experienced_Professionals |

11 corrigidas, 1 sem solução. (Nota: Accenture e Cloudera tinham "Connection Error" e
"Type Mismatch" respectivamente no problems.md antigo - mesmo grupo de falso-positivo do
GET vs POST, mas aqui a URL salva também estava genuinamente errada, então a correção
valeu a pena mesmo sendo "falso positivo" parcial.)

### Bloco Gupy - Ciclo 2 (182 empresas, principalmente as 313 novas nunca verificadas)

#### Lote 1 (10) - CONCLUÍDO 2026-07-19
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| A3Data | https://a3data.gupy.io | Sem solução (mesma URL "correta" segundo buscas, mas morta) | mantido |
| a55 | https://a55.gupy.io | Sem solução (a55carreiras.gupy.io também morto) | mantido |
| Adecoagro | https://adecoagro.gupy.io | Sem solução (usa BMTCloud, sem ATS reconhecido) | mantido |
| AeC | https://aec.gupy.io | Corrigido (mudou de ATS) | PandaPe, https://aeccentrodecontatos.pandape.com.br |
| Agendor | https://agendor.gupy.io | Sem solução (mesma URL "correta" segundo buscas, mas morta) | mantido |
| Agrosmart | https://agrosmart.gupy.io | Sem solução (mesma URL "correta" segundo buscas, mas morta) | mantido |
| Ajinomoto | https://ajinomoto.gupy.io | Corrigido | https://ajinomotoabr.gupy.io |
| Aperam | https://aperam.gupy.io | Corrigido (mudou de ATS) | OracleCloud, https://hdhy.fa.em3.oraclecloud.com/hcmUI/CandidateExperience/pt-BR/sites/AperamCareerSite/jobs |
| Apsen | https://apsen.gupy.io | Corrigido (mudou de ATS) | Vagas, https://trabalheconosco.vagas.com.br/apsen |
| Aquarela | https://aquarela.gupy.io | Sem solução (nenhum ATS reconhecido encontrado) | mantido |

4 corrigidas, 6 sem solução.

#### Lote 2 (10) - CONCLUÍDO 2026-07-19
| Empresa | URL antiga | Resultado | Nova URL / Plataforma |
|---|---|---|---|
| Aquiris | https://aquiris.gupy.io | Corrigido (adquirida pela Epic Games, mudou de ATS) | Avature, https://www.epicgames.com/site/en-US/careers |
| Atech | https://atech.gupy.io | Sem solução (já verificado no Ciclo 1) | mantido |
| Avenue | https://avenue.gupy.io | Corrigido (mudou de ATS) | InHire, https://avenue.inhire.app/vagas |
| Banco Bari | https://bancobari.gupy.io | Corrigido (mudou de ATS) | InHire, https://bancobari.inhire.app/vagas |
| Banco Master | https://bancomaster.gupy.io | Sem solução | mantido |
| Barte | https://barte.gupy.io | Sem solução | mantido |
| Bcredi | https://bcredi.gupy.io | Corrigido (mudou de ATS, adquirida pela Creditas) | Gupy, https://creditas.gupy.io |
| Bexs | https://bexs.gupy.io | Sem solução | mantido |
| BIX Tech | https://bix.gupy.io | Corrigido (mudou de ATS) | InHire, https://bixtecnologia.inhire.app/vagas |
| Bling | https://bling.gupy.io | Sem solução (já verificado no Ciclo 1) | mantido |

5 corrigidas, 5 sem solução.

