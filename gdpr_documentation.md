# GDPR Documentation — Tender Intelligence Agent

**Phase 16** · Checkpoint 2 · prepared 7 October 2026 by Dr.-Ing. Walid Barakat, i@work UG
**Builds on:** the separate GDPR lab audit of this system (*GDPR Audit of Project 3*, 24 August 2026, repository `GDPR_Privacy_Lab_EU_Tender_Agent_Walid_Barakat`), updated here for the Checkpoint 2 changes.
**Status:** first-pass assessment, not legal advice or a completed DPIA. Assessed separately from the EU AI Act (`eu_ai_act_compliance.md`).

> **Bottom line: proceed with conditions.** The system decides about *organisations*, but it still processes personal data: names and contact details of contracting-authority officers in tender notices, people named in tender documents and CVs, the client's own users, and system logs. The highest-risk processing is sending free-text tender documents to non-EU LLM and vector providers. Checkpoint 2 does not add a new category of personal data: the decision engine works only on organisation-level fields. It does add one new record, the approver's identity and decision in Stage 10. Before live documents are processed in a pilot, three things are required: processor agreements, personal-data stripping before LLM and vector calls, and a retention schedule.

---

## 1. Data flows

```text
EU Funding & Tenders Portal (public)                         Client firm users
        │  Stage 1 search API: notice metadata                     │  Slack / Notion accounts
        ▼                                                          ▼
n8n control plane (self-hosted) ──► Stage 2 LLM triage ──────► Anthropic API (processor)
        │                                                          
        ├──► FastAPI / LangGraph (self-hosted)
        │       ├─ Stage 3 ReAct agent ──► MCP tools ──► ec.europa.eu pages and documents
        │       ├─ Stage 4 document text ──► OpenAI embeddings (processor) ──► Pinecone (processor)
        │       ├─ Stage 5 retrieval ◄── Pinecone
        │       └─ Stages 6–9 assessment and report (LLM summaries via Anthropic)
        │
        ├──► Stage 10 decision engine (self-hosted; organisation-level fields only)
        │       └─ approval request ──► Slack ──► approver ──► n8n Wait node (approver ID + decision logged)
        │
        └──► Publication: PDF ──► Google Drive · decision record ──► Notion · notification ──► Slack
```

## 2. Personal data involved

| Data category | Example | Source | Stages | Necessary? |
|---|---|---|---|---|
| Contracting-authority contacts | Name, functional email, phone in a notice | EU portal notice | 1–4, stored in Pinecone and reports | Rarely: the authority name is enough. **Strip before LLM and vector use** |
| People named in tender documents | Project officers, authors, experts, CVs in annexes, signatures | Annex PDFs | 3–5 | No, for a bid decision. **Strip or quarantine** |
| Incidental special-category data | Health, nationality or political details in CVs or biographies | Annex PDFs | 3–5 | **Never.** No Article 9 condition applies; detect and delete |
| Client user data | Names, Slack and Notion user IDs, email | Client workspace | 9–10 | Yes, to deliver and approve |
| **New in Checkpoint 2:** approver record | Approver identity, decision, timestamp, any rationale | Stage 10 Wait node | 10 | Yes: accountability for the decision, and the human-oversight evidence |
| Technical logs | IP addresses, request IDs, n8n execution data, LLM prompts containing the above | n8n, FastAPI, providers | All | Yes, for security and troubleshooting, with short retention |
| **Not personal data:** decision-engine inputs | Tender ID, value, deadline, status, CPV code, company profile | Stage 9 output | 10 | — |

## 3. Legal bases

| Purpose | Lawful basis | One-line justification | Needs legal review? |
|---|---|---|---|
| Discover and assess tenders, including incidental contact data in notices | Art. 6(1)(f), legitimate interests | i@work and its clients need to find and evaluate public business opportunities; the data is published by public bodies for that purpose | Yes: confirm the LIA and the Article 14 position |
| Deliver the assessment to the client | Art. 6(1)(b) contract (with the client firm), and Art. 6(1)(f) for client staff data | Needed to perform the managed service | Yes, for scope and minimisation |
| Stage 10 approval record | Art. 6(1)(f), and Art. 6(1)(c) where the client must keep decision records | Accountability and human-oversight evidence | No, if retention is limited |
| Security and troubleshooting logs | Art. 6(1)(f) | Proportionate logging to protect the service | No, with short retention |
| Training or improving a general model | **None assumed. Prohibited** | A separate purpose, incompatible without a new basis | Yes, before any such use |

**Legitimate interests assessment (summary).** *Purpose:* finding and assessing business opportunities is a specific, lawful interest. *Necessity:* the decision needs organisation-level data; personal data in notices and annexes is incidental and can mostly be removed before LLM and vector processing. *Balance:* public officials can reasonably expect limited professional use of contact details published in a tender notice. They would not expect model training, indefinite storage in a vector index, or redistribution into commercial channels. Minimisation, short retention and an objection route tip the balance in favour of processing. **Article 14** applies because the data is collected indirectly. The Article 14(5)(b) exemption (disproportionate effort) is arguable for incidental officer contacts, but it must be documented, with the safeguards above. This remains open, as recorded in the audit pack.

## 4. Highest-risk processing

1. **Free-text annexes sent to non-EU LLM and embedding providers, then stored as vectors in Pinecone.** This is where incidental CVs, biographies and special-category data can leave the EU and persist in a store that is hard to search and erase. *Treatment:* strip names, emails, phone numbers and signatures, and detect CV-like sections, before Stage 3 tool observations go to the LLM and before Stage 4 embedding. Namespace vectors per tender so a tender's vectors can be deleted together.
2. **Replication into Notion, Slack and Google Drive.** Every published copy is another place to find for access and erasure requests. *Treatment:* publish organisation-level summaries only, never raw annex text; record the destination IDs per run so copies can be found later.
3. **Future person-level features** (named experts in proposal outlines) would turn incidental data into processing that targets people, and would also change the AI Act classification. *Treatment:* out of scope; re-assess before any such feature.

## 5. Short DPIA

**Screening against the EDPB criteria** (two or more met normally means a DPIA is required):

| Criterion | Met? | Reason |
|---|---|---|
| Evaluation or scoring | Partly | Scores tenders and organisations, not people; person-level scoring is out of scope |
| Automated decision with legal or similar effect | No | Organisation-level decision, with human approval in Stage 10 |
| Systematic monitoring | No | Researches tenders, not individuals over time |
| Sensitive or highly personal data | Not intended | Can appear in CVs; must be filtered |
| Large scale | No | Bounded batches of tender records |
| Matching or combining datasets | **Yes** | Portal records, annexes, retrieval corpus and company profile are combined |
| Vulnerable data subjects | No | — |
| Innovative technology | **Yes** | LLM agents, ReAct tool use, vector retrieval |
| Prevents the exercise of rights or use of a service | Potentially | Distributed vendors make access and erasure harder without lineage records |

**Result:** two criteria are met, and a third may be, so a **DPIA is the prudent release condition** for a commercial pilot. In outline:

| DPIA element | Content |
|---|---|
| Description | §1 and §2 above |
| Necessity and proportionality | Organisation-level decision; personal data incidental and removable; minimisation by stripping; no model training |
| Risks to individuals | (a) Officers' or experts' data persisting in vector stores and third-country systems; (b) inaccurate or out-of-date information about named people repeated in reports; (c) difficulty exercising access and erasure rights across six systems |
| Measures | Pre-processing PII filter; per-tender vector namespaces with linked deletion; retention limits (§6); processor agreements and transfer tools (§7); publication of organisation-level summaries only; a rights-request runbook |
| Residual risk | **Low to medium** once the measures are in place. Providers' own retention and sub-processing remain outside i@work's direct control |
| Decision | Proceed to the pilot after the PII filter, DPAs and retention are in place. Re-run the DPIA if person-level features are added |

**Proposed retention:** tender-derived data for the tender's life cycle plus 24 months; Stage 10 approval records for 6 years if the client must keep commercial decision records, otherwise 24 months; technical logs 90 days; Pinecone vectors deleted with the tender namespace when the tender closes.

## 6. Data-subject rights

| Right | Difficulty in this system | Current support | Required for the pilot |
|---|---|---|---|
| Information (Art. 13/14) | Data collected indirectly from public notices | Not evidenced | Privacy notice on the i@work site; documented Article 14(5)(b) assessment for incidental contacts |
| Access (Art. 15) | A person's data may sit in prompts, logs, vectors, reports and collaboration tools | Not evidenced | Lineage key (tender ID) on every record; search runbook across n8n, Pinecone, Notion, Drive and Slack |
| Rectification (Art. 16) | Corrections must reach already-published reports | Partial: source review | Version reports; re-publish corrected versions |
| Erasure (Art. 17) | Embeddings, backups and published copies | Not evidenced | Delete by tender namespace; delete published copies via recorded destination IDs |
| Restriction (Art. 18) | Pausing use while a dispute is open | Not evidenced | Hold flag on a tender ID that every stage checks |
| Objection (Art. 21) | Objection to legitimate-interest processing | Manual, not documented | Named owner; balancing record |
| Automated decisions (Art. 22) | — | **Not applicable on current facts.** The decision concerns an organisation, not an individual, and a human approves in Stage 10 | Keep the approval step; reassess if person-level features are added |

Response deadline: one month (extendable by two). The client firm, as controller for its own use, receives the requests; i@work assists as processor.

## 7. Processors, providers and third-party transfers

| Provider | Role | Data received | Location / transfer | Status |
|---|---|---|---|---|
| Anthropic (Claude API) | Processor | Notice text, tool observations, prompts | Outside the EEA unless an EU processing option is contracted; transfer tool: EU–US Data Privacy Framework if the provider is certified, otherwise SCCs plus a transfer assessment | **DPA not evidenced**; verify the DPF listing |
| OpenAI (embeddings) | Processor | Annex text chunks | As above | **DPA not evidenced**; verify the region option and DPF listing |
| Pinecone | Processor | Embeddings and stored chunk text | Region set per index; choose an EU region where offered | **DPA not evidenced**; confirm the index region |
| Notion, Slack, Google Drive | Processors (of the client or i@work) | Published summaries, approver identity, user IDs | Often already contracted by the client; verify the transfer tool for each | Verify per client |
| Hosting provider (n8n, FastAPI) | Processor | Everything in transit, logs | Choose EU hosting for the pilot | Development used a local machine and temporary tunnels, **not acceptable for production** |
| EU Funding & Tenders Portal | Separate controller (source) | — (the agent reads only) | EU | Not a processor; follow the portal's terms of use |

**Transfers.** A provider's general claim of GDPR compliance is not a transfer mechanism. For each non-EEA processor, use either the adequacy decision for the EU–US Data Privacy Framework (only if the specific provider is certified and the service is in scope) or the 2021 Standard Contractual Clauses, with a transfer impact assessment and supplementary measures. In this system the PII filter is the main supplementary measure, because it reduces what is transferred.

## 8. Checkpoint 2 changes, and actions before the pilot

| Change or action | GDPR effect | Owner and status |
|---|---|---|
| Decision engine (Stage 10) | None: organisation-level fields only. Verified in code: the engine reads the tender ID, identifier, title, description (for keyword matching only), value, deadline, status, procedure type, CPV code, URL, the Stage 2 relevance score and the company profile | Done |
| Approval step records the approver's identity and decision | New personal data; lawful under Art. 6(1)(f); retention as in §5 | Pilot |
| Draft proposal outlines | List roles only, not named people. Keep it that way | Done, by design |
| PII filter before LLM and embedding calls | Main risk reduction | **Required before the pilot** |
| Executed DPAs and transfer tools for Anthropic, OpenAI, Pinecone and the hosting provider | Article 28 and Chapter V | **Required before the pilot** |
| Retention schedule implemented (Pinecone namespace deletion, log rotation) | Storage limitation | **Required before the pilot** |
| Record of processing activities (Art. 30), privacy notice, breach procedure | Accountability | Pilot, month 1 |
