# Pensana Plc in US company disclosures and SEC filings (research as at 19 Oct 2026)

Method note: the SEC EDGAR full-text search API (efts.sec.gov) was queried directly with curl and a User-Agent header. Raw JSON and downloads are in /tmp/claude-0/-home-user-Pensana-Project/3def86ec-0eba-5494-abcb-654f78abfd60/scratchpad/sec_dl/. EDGAR full-text search covers filings and their exhibits from 2001 onward.

## 1. Which SEC filings mention Pensana?

### Takeaway
Only one operating-company filing in 2024–2026 names Pensana: Energy Fuels' (NYSE American: UUUU) July 2026 investor deck, which lists Pensana as one of VAC's MOU partners. No American Resources/ReElement filing mentions Pensana, Pensana has no SEC registrant record (so no F-1, 20-F, public DRS or Form D), and the rest of the 176 hits are US funds holding PRE shares.

### Cited Findings
- EDGAR full-text search for "Pensana" from 1 Jan 2024 to 19 Oct 2026 returned **176 hits**. Nearly all are fund holdings reports (NPORT-P, N-CSR/N-CSRS, N-PX) from Sprott Funds Trust (rare-earth/critical-materials ETFs), SPDR Index Shares Funds, DFA Investment Dimensions Group and Empower. These show US ETFs and funds hold PRE, not any commercial relationship. — [EDGAR FTS query](https://efts.sec.gov/LATEST/search-index?q=%22Pensana%22&dateRange=custom&startdt=2024-01-01&enddt=2026-10-19)
- Restricted to operating-company forms (8-K, 10-Q, 10-K, S-1, F-1, DRS, 20-F, 6-K, D, 424B4, 425, S-4, F-4), "Pensana" returns 4 hits across all years. Only one falls in 2024–2026: an **Energy Fuels Inc. 8-K, Exhibit 99.1, filed 14 July 2026**. The other three are a 2022 Polestar 6-K and 2022–23 IperionX filings, which predate this review and are unrelated to the US plan. — [EDGAR FTS forms query](https://efts.sec.gov/LATEST/search-index?q=%22Pensana%22&forms=8-K,10-Q,10-K,S-1,F-1,DRS,20-F,6-K,D,424B4,425,S-4,F-4)
- The Energy Fuels exhibit is the July 2026 corporate deck, "A Global, Diversified and Vertically Integrated Critical Materials Company". On the VAC slide it says VAC has "Numerous MOUs in place with upstream rare earth companies including Torngat Metals, Aclara Resources, Cyclic Materials, and Pensana." — [Energy Fuels 8-K Ex 99.1, 14 Jul 2026](https://www.sec.gov/Archives/edgar/data/1385849/000106299326003630/exhibit99-1.htm)
- "Vacuumschmelze" AND "Pensana" returns only that same Energy Fuels exhibit. — [EDGAR FTS](https://efts.sec.gov/LATEST/search-index?q=%22Vacuumschmelze%22%20%22Pensana%22)
- American Resources Corp (CIK 1590715): a full-text search for "Pensana" restricted to that CIK returns **0 hits**. Its 8-Ks, 10-Qs and 10-K do not name Pensana. — [EDGAR FTS ciks=0001590715](https://efts.sec.gov/LATEST/search-index?q=%22Pensana%22&ciks=0001590715)
- "ReElement" AND "Angola" returns only three John Hancock fund reports (N-CSR/N-CSRS), with no AREC filing among them. — [EDGAR FTS](https://efts.sec.gov/LATEST/search-index?q=%22ReElement%22%20%22Angola%22&dateRange=custom&startdt=2024-01-01&enddt=2026-10-19)
- EDGAR company search for "pensana" returns "No matching companies". Pensana Plc, and any entity with Pensana in its name, has no CIK, so there is no F-1, F-4, 20-F, 6-K or Form D. The EDGAR entity-name lookup also returns 0. — [EDGAR company search](https://www.sec.gov/cgi-bin/browse-edgar?company=pensana&type=&dateb=&owner=include&count=40&action=getcompany)
- "Pensana" in Form D filings: 0 hits. "Cascade Natural Resources": 0 hits from 2024 onward. "Sable Min": 0 hits. "eVAC" AND "Angola": 0 hits. — [EDGAR FTS](https://efts.sec.gov/LATEST/search-index?q=%22Cascade%20Natural%20Resources%22&dateRange=custom&startdt=2024-01-01&enddt=2026-10-19)

### Inferences
- A confidential draft registration (DRS) by a foreign private issuer is not public until shortly before a roadshow, so this check cannot rule out a non-public submission. Still, after more than a year of "preparations", Pensana has no CIK and no public filing. A US listing would normally need at least a public F-1 or Form 20-F/8-A at least 15 days before a roadshow, so nothing suggests a Nasdaq listing is imminent.
- The only US-registrant confirmation of a Pensana relationship comes from VAC's acquirer (Energy Fuels), not from ReElement/AREC. Energy Fuels presents Pensana as one of several VAC MOUs, not as a key supplier.

### Gaps
- One EDGAR query for "Ozango" returned a server error and was not retried successfully, so its result is unknown.
- Confidential DRS submissions cannot be checked publicly.

## 2. What have ReElement Technologies and American Resources said about Pensana? Is the MOU live?

### Takeaway
American Resources/ReElement issued one press release on the Pensana MOU (23 June 2025). No later statement mentioning Pensana was found, and AREC's SEC filings never mention it. AREC has since deconsolidated ReElement, so the counterparty is no longer an AREC subsidiary. Nobody has said the MOU was terminated, but no evidence shows it is still active.

### Cited Findings
- On 23 June 2025, American Resources Corporation (NASDAQ: AREC) announced, through ACCESS Newswire and on behalf of ReElement Technologies Corporation, a **Memorandum of Understanding** with Pensana that "outlines a framework" for a partnership. The release says it covers a *proposed* offtake of up to 20,000 tpa of MREC from Longonjo over five years, "pricing to be agreed". It cites ReElement's Noblesville, Indiana refinery (commercial since 2023) and a larger site under development in Marion, Indiana. — [ACCESS Newswire via Finviz](https://finviz.com/news/85756/reelement-technologies-corporation-and-pensana-plc-join-forces-to-advance-one-of-largest-global-rare-earth-oxide-supply-chain-partnerships); [ACCESS Newswire original](https://www.accessnewswire.com/newsroom/en/metals-and-mining/reelement-technologies-corporation-and-pensana-plc-join-forces-to-advance-one-of-1041768)
- Mark Jensen, CEO and Chairman of ReElement, said the deal "represents a major advancement toward building a true mine-to-magnet global rare earth supply chain." — [Finviz](https://finviz.com/news/85756/reelement-technologies-corporation-and-pensana-plc-join-forces-to-advance-one-of-largest-global-rare-earth-oxide-supply-chain-partnerships)
- AREC did not file an 8-K naming Pensana for this release (see Q1: 0 EDGAR hits on AREC's CIK). — [EDGAR FTS](https://efts.sec.gov/LATEST/search-index?q=%22Pensana%22&ciks=0001590715)
- A search summary reports that AREC filed its 2025 10-K in May 2026 with US$55.4m net income driven by a "gain on deconsolidation" of legacy operations and ReElement, while "maintaining a strategic ownership interest and partnership position". The primary release (ACCESS Newswire 1168485) returned HTTP 403 to the fetch tool, so this is unverified at source. — [ACCESS Newswire (403 on fetch)](https://www.accessnewswire.com/newsroom/en/metals-and-mining/american-resources-corporation-advances-rare-earth-and-critical-mineral-platform-1168485)
- Mergermarket reported AREC starting a minority stake sale in ReElement. Only the headline was seen. — [ION Analytics/Mergermarket](https://ionanalytics.com/insights/mergermarket/american-resources-kicks-off-minority-stake-sale-in-reelement-technologies-amid-rising-strategic-interest-ceo/)
- ReElement's widely reported offtake/partnership with POSCO for separated oxides (not Pensana feedstock) appears in US coverage; the year of that article was not confirmed in the snippet. — [iTiger](https://www.itiger.com/news/1110049974)
- Pensana's own FY2025 annual report also lists Hanwa and Toyota Tsusho as each proposing up to 100% of Phase 1 output (~20 ktpa MREC). The MOUs therefore overlap and together exceed Longonjo's planned output. — [Pensana AR 2025](https://pensana.co.uk/wp-content/uploads/2025/10/Pensana-integrated-annual-report-2025.pdf)
- Stonegate Capital Partners, a US paid-research firm, initiated coverage of Pensana on 16 Oct 2025 and cited the ReElement MOU as a route for refining in the US. — [Newsfile via Sherbrooke Record](https://business.sherbrookerecord.com/sherbrookerecord/article/newsfile-2025-10-16-stonegate-capital-partners-initiates-coverage-on-pensana-plc-pre)

### Inferences
- The ReElement MOU looks dormant on the US side. Its only public trace is a single 2025 press release. AREC has not repeated it in SEC filings, and ReElement now sits outside AREC's consolidated group. Its "live" status rests only on Pensana's own RNS listing of offtake MOUs (8 Jun 2026, per the context report).

### Gaps
- reelement.tech and americanresourcescorp.com were not fetched (budget), and no AREC earnings-call transcript from 2025–26 was found. Whether ReElement still lists Pensana in its investor deck is unknown.
- AREC's remaining ownership percentage in ReElement was not verified.

## 3. What have VAC/eVAC said about Pensana, and who else supplies eVAC?

### Takeaway
VAC signed a non-binding MOU with Pensana on 22 Oct 2025 covering eVAC's Sumter, South Carolina magnet plant. In June 2026 Energy Fuels agreed to buy VAC, and its deck now presents Pensana as one of several upstream MOUs, alongside Torngat, Aclara and Cyclic Materials. Energy Fuels' own feedstock plan for White Mesa is monazite from Chemours (US), Donald (Australia), Vara Mada (Madagascar) and Bahia (Brazil). Angola is not part of it.

### Cited Findings
- The Pensana–VAC MoU (22 Oct 2025) proposes an initial five-year offtake of MREC from Longonjo, "subject to extension", pricing to be agreed. It is framed around the 2027 US defence restriction on Chinese rare earths and eVAC's Sumter, SC plant (2,000 tpa magnets initially, rising to 12,000 tpa by 2029). — [Mining Weekly](https://www.miningweekly.com/article/pensana-german-company-seek-to-establish-mine-to-magnet-supply-chain-in-the-us-2025-10-22); [Mining Technology](https://www.mining-technology.com/news/pensana-and-vac-sign-mou/)
- Energy Fuels agreed on 23 June 2026 to acquire VAC from Ara Partners. Adamas Intelligence values the deal at about US$1.9bn enterprise value, and it is expected to close in early 2027 subject to foreign-investment and antitrust approvals. The same report says the Pentagon committed US$725m to a US separation facility. — [Adamas Intelligence](https://www.adamasintel.com/energy-fuels-agrees-1-9b-vac-acquisition-pentagon-commits-725m-to-u-s-separation-facility/); [Metal Tech News](https://www.metaltechnews.com/story/2026/06/24/tech-metals/energy-fuels-to-acquire-vac-for-19b/2809.html)
- Energy Fuels is separately acquiring Australian Strategic Materials (ASM) through a scheme agreed 20 Jan 2026 and amended 12 Mar 2026. The scheme meetings were postponed from 22 June 2026. — [Energy Fuels 10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/0001385849/000138584926000029/efr-20260630.htm)
- Energy Fuels' deck: VAC has "Numerous MOUs … including Torngat Metals, Aclara Resources, Cyclic Materials, and Pensana", and "ASM is a current producer of REE metals and alloys which is able to supply raw materials for VAC's hard magnet products." — [Energy Fuels 8-K Ex 99.1](https://www.sec.gov/Archives/edgar/data/1385849/000106299326003630/exhibit99-1.htm)
- Energy Fuels' feedstock: monazite from Chemours (southeast US), Donald (Australia), Vara Mada (Madagascar) and Bahia (Brazil), processed at White Mesa Mill, Utah. — [Adamas Intelligence](https://www.adamasintel.com/energy-fuels-agrees-1-9b-vac-acquisition-pentagon-commits-725m-to-u-s-separation-facility/)
- The Energy Fuels Q2 2026 10-Q does not mention Pensana. The EDGAR full-text search for "Pensana" returned only the 8-K exhibit from Energy Fuels. — [EDGAR FTS](https://efts.sec.gov/LATEST/search-index?q=%22Pensana%22&forms=8-K,10-Q,10-K,S-1,F-1,DRS,20-F,6-K,D,424B4,425,S-4,F-4)

### Inferences
- Once Energy Fuels completes the VAC deal, eVAC will have an in-house, vertically integrated feedstock route (Donald, White Mesa, ASM metals, VAC magnets). That probably lowers the priority of Pensana's Angolan MREC, which also still needs separation, a step Pensana has no US capacity for. The MOU has not been cancelled, but the counterparty's strategy has moved toward its own supply.
- No public eVAC statement naming MP Materials, Lynas or USA Rare Earth as feedstock suppliers was found in this pass.

### Gaps
- vacuumschmelze.com and the eVAC pages were not fetched directly. No VAC-originated press release on Pensana was confirmed; coverage cites Pensana's RNS.
- The other upstream MOUs mentioned in VAC/eVAC reporting (for example Lynas or USA Rare Earth) were not verified.

## 4. Has Pensana named a US site, state, subsidiary or partner? Nasdaq status?

### Takeaway
No. Pensana's most recent US-focused RNS (10 Aug 2026) names no US site, state or subsidiary. Its US content is a White House briefing, a conversation with an NSC official and a statement that the briefing is "very supportive of our U.S. Mine to magnet strategy and NASDAQ listing." No US entity was found, no state economic-development announcement was found, and Pensana has no SEC registration.

### Cited Findings
- RNS of 10 Aug 2026: Tim George attended a private briefing with President Trump, Secretary of State Rubio and State Department officials. Afterwards he "had the opportunity to discuss the Company's role … with David Copley of the Executive Office of the President and National Security Council." The RNS gives Longonjo as a "US$250 million development … approximately 25% complete with first MREC production scheduled for 2028". George is quoted: "very supportive of our U.S. Mine to magnet strategy and NASDAQ listing." No US site, state or subsidiary is named. — [Pensana RNS PDF 10 Aug 2026](https://pensana.co.uk/wp-content/uploads/2026/08/Trump-announces-US3-billion-support-for-U.S.-critical-minerals-supply-chains.pdf)
- Document metadata of that RNS PDF: Author "Andre Pienaar", created 9 Aug 2026 20:44 UTC in Microsoft Word 365 (read with pdfinfo). — [Pensana RNS PDF](https://pensana.co.uk/wp-content/uploads/2026/08/Trump-announces-US3-billion-support-for-U.S.-critical-minerals-supply-chains.pdf)
- Nasdaq timeline from press: "eyes Nasdaq listing in 2026" (Oct 2025), "ahead of Nasdaq listing" (Dec 2025, when shareholders reaffirmed support). An unofficial forum post quotes the 8 June 2026 RNS as saying the board is "actively evaluating a potential listing". — [Ecofin Agency](https://www.ecofinagency.com/news/0110-49168-pensana-eyes-nasdaq-listing-in-2026-for-angola-rare-earths-project); [Mining Weekly 18 Dec 2025](https://newsletter.mw.creamermedia.com/article/pensanas-shareholders-reaffirm-support-ahead-of-nasdaq-listing-2025-12-18); [LSE.co.uk forum (unofficial)](https://www.lse.co.uk/profiles/oscargolf/?page=8)
- The SEC has no company record for Pensana (see Q1). — [EDGAR company search](https://www.sec.gov/cgi-bin/browse-edgar?company=pensana&type=&dateb=&owner=include&count=40&action=getcompany)
- The US EXIM support is described only in Pensana's own release (28 Oct 2025, "U.S. EXIM debt funding to accelerate U.S. mine to magnet supply chain"), which covers the Absa-led Longonjo debt in Angola, not a US facility. — [Pensana PDF](https://pensana.co.uk/wp-content/uploads/2025/10/U.S.-EXIM-debt-funding-to-accelerate-U.S.-mine-to-magnet-supply-chain-.pdf)

### Inferences
- The "Andre Pienaar" author tag suggests the release was drafted outside Pensana's named staff. A person of that name founded C5 Capital, a London/Washington investor with national-security connections. This identification is **unverified** and may be a different person. The report writer should treat it only as a lead.
- Pensana's "US mine-to-magnet" plan is still a description of intent and offtake MOUs, not a US asset. The only physical US nodes in the plan belong to counterparties: ReElement in Indiana and eVAC in South Carolina.

### Gaps
- OpenCorporates: the API needs a token (HTTP 401), and the web search page returned no parseable Pensana results, so US state registries were **not verified**. Delaware, South Carolina and Indiana registries were not checked directly.
- No state economic-development announcements (SC Commerce, Indiana IEDC, etc.) naming Pensana were found in the web searches run. A targeted search was not done.

## 5. US media and think-tank coverage

### Takeaway
US-facing coverage comes mostly from trade press that repeats Pensana's RNS (Mining Weekly/Engineering News, SMM, Metal-powder.tech), plus a paid US research initiation (Stonegate). Searches found no Reuters, Bloomberg, WSJ, CSIS or Stimson piece that analyses Pensana. Rare Earth Exchanges covered the US$15m Cascade tranche sceptically, according to the context report.

### Cited Findings
- Mining Weekly / Engineering News covered the White House briefing on 11 Aug 2026, sourced to Pensana's RNS. — [Mining Weekly](https://www.miningweekly.com/article/pensana-attends-us-presidential-briefing-on-rare-earths-supply-2026-08-11)
- SMM (Shanghai Metals Market) ran "US Officials Back Independent Rare Earth Supply Chain, Pensana Advances Angola Project". — [SMM](https://news.metal.com/newscontent/104063547-us-officials-back-independent-rare-earth-supply-chain-pensana-advances-angola-project)
- Rare Earth Exchanges, "Pensana secures first $15m tranche but mine-to-magnet ambitions still face execution risk", noted that the backers were not named. — [Rare Earth Exchanges](https://rareearthexchanges.com/news/pensana-secures-first-15m-tranche-but-mine-to-magnet-ambitions-still-face-execution-risk/)
- Argus covered the Saltend cancellation and the pivot to the US. — [Argus](https://www.argusmedia.com/en/news-and-insights/latest-market-news/2743508-uk-re-hopes-dashed-as-saltend-refinery-scrapped)
- Search for Pensana combined with Reuters, CSIS or Rare Earth Exchanges for 2026 returned no Reuters or CSIS item. — (search: "Pensana rare earths United States Reuters OR CSIS OR 'Rare Earth Exchanges' 2026"; no matching URL)

### Inferences
- Pensana has little independent coverage in US policy circles. It is present in US policy rhetoric through its own RNS, not through think-tank or mainstream US press analysis.

### Gaps
- Bloomberg, WSJ, Fastmarkets and Argus US are paywalled and were not searched in depth. Stimson and CSIS sites were not searched directly.

## 6. US lobbying (LDA) and FARA filings

### Takeaway
FARA bulk data has **no entry** for Pensana, Ozango, Cascade Natural Resources, FSDEA (2020s) or Sable Min. Angola's government does have active FARA representation, through BGR Government Affairs (foreign principal registered 16 May 2025), Squire Patton Boggs and others, but the scope of that work was not checked. The LDA (lobbying) database could not be queried: the API returned 503.

### Cited Findings
- FARA bulk "All Foreign Principals" CSV (17,770 rows) contains no rows matching "Pensana", "Ozango", "Cascade Natural" or "FSDEA". — [FARA bulk data](https://efile.fara.gov/bulk/zip/FARA_All_ForeignPrincipals.csv.zip)
- Active or recent Angola foreign principals in the same file:
  - Republic of Angola, through **BGR Government Affairs, LLC** (reg. 5430; principal added 16 May 2025)
  - Government of the Republic of Angola, through **Squire Patton Boggs** (reg. 2165; added 25 Jun 2019)
  - Government of Angola, through **Millennium Technologies** (reg. 7298; 20 Jul 2023)
  - UNITA, through AO Development Company LLC (reg. 7734; 8 Jun 2026)
  - individuals Jean-Claude Bastos de Morais (reg. 7647, Sep 2025) and Francisco Higino Lopes Carneiro (reg. 7637, Aug 2025)
  - historically, "Fundo Soberano de Angola through Grayling", via Dutko Grayling (reg. 6166, terminated 26 Apr 2013)
  - [FARA bulk data](https://efile.fara.gov/bulk/zip/FARA_All_ForeignPrincipals.csv.zip)
- LDA: lda.senate.gov now redirects (301) to lda.gov, whose API returned HTTP 503 on two attempts, so no lobbying search was completed. — [lda.gov API](https://lda.gov/api/v1/filings/?client_name=pensana)

### Inferences
- Pensana's access in Washington (the White House briefing, EXIM and DFC) does not appear to run through a registered FARA agent for Pensana itself. Angola's own lobbyists (BGR, Squire Patton Boggs) could cover the Lobito Corridor and minerals, but that is not verified.

### Gaps
- LDA lobbying disclosures for Pensana, Cascade and Angola rare earths remain **unchecked** (lda.gov outage). Retry at https://lda.gov/api/v1/filings/?client_name=pensana and with filing_specific_lobbying_issues=Angola.
- The supplemental statements by BGR and Squire Patton Boggs describing Angola work (including any rare earths or Lobito content) were not read.
