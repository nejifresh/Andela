---
marp: true
theme: default
paginate: true
size: 16:9
title: CloudWaste Sentinel
description: AI-generated presentation deck for the Cloud Cost Optimizer and Remediation Engine
style: |
  section {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f7f9fc;
    color: #111827;
    padding: 52px 64px;
  }
  h1 {
    color: #0f172a;
    font-size: 54px;
    letter-spacing: 0;
  }
  h2 {
    color: #0f172a;
    font-size: 34px;
  }
  h3 {
    color: #0f766e;
    font-size: 22px;
  }
  p, li {
    color: #334155;
    font-size: 24px;
    line-height: 1.35;
  }
  small {
    color: #64748b;
  }
  code {
    background: #e2e8f0;
    color: #0f172a;
    border-radius: 6px;
    padding: 2px 6px;
  }
  pre {
    background: #0f172a;
    border-radius: 10px;
    padding: 18px;
  }
  pre code {
    background: transparent;
    color: #e2e8f0;
    padding: 0;
  }
  table {
    font-size: 20px;
  }
  th {
    color: #0f172a;
  }
  .title {
    background: linear-gradient(135deg, #0f172a 0%, #164e63 58%, #0f766e 100%);
    color: white;
  }
  .title h1, .title p, .title small {
    color: white;
  }
  .kicker {
    color: #0f766e;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 18px;
  }
  .title .kicker {
    color: #99f6e4;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 22px;
  }
  .card {
    background: white;
    border: 1px solid #dbe3ee;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  }
  .card h3 {
    margin-top: 0;
  }
  .metric {
    font-size: 44px;
    color: #0f766e;
    font-weight: 800;
  }
  .muted {
    color: #64748b;
  }
  .flow {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    align-items: stretch;
    margin-top: 28px;
  }
  .step {
    background: white;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 18px;
    text-align: center;
    font-size: 19px;
    color: #0f172a;
    font-weight: 700;
  }
  .band {
    background: #ecfdf5;
    border-left: 6px solid #0f766e;
    padding: 18px 22px;
    border-radius: 10px;
  }
  .warning {
    background: #fffbeb;
    border-left: 6px solid #b45309;
    padding: 18px 22px;
    border-radius: 10px;
  }
---

<!-- _class: title -->

<div class="kicker">Senior FDE Demo Deck</div>

# CloudWaste Sentinel

Evidence-backed FinOps remediation for AWS and Azure waste.

<small>Python FastAPI API + SQLite + Next.js dashboard | Generate-only remediation commands | Human approval workflow</small>

---

<div class="kicker">Problem</div>

## Cloud waste is easy to see, hard to safely remediate

<div class="grid">
  <div class="card">
    <h3>FinOps pressure</h3>
    <p>Teams need credible savings numbers, not another noisy cost report.</p>
  </div>
  <div class="card">
    <h3>Engineering risk</h3>
    <p>Deleting the wrong disk or VM can break production or remove data.</p>
  </div>
  <div class="card">
    <h3>Trust gap</h3>
    <p>Recommendations need evidence, confidence, pre-checks, and auditability.</p>
  </div>
</div>

<div class="band">
CloudWaste Sentinel turns exports into reviewable remediation packs, not blind delete suggestions.
</div>

---

<div class="kicker">Users</div>

## Designed for the people who must say yes

| Persona | What they need | Product answer |
|---|---|---|
| FinOps lead | Savings, prioritization, reporting | Monthly and annual savings by provider and finding type |
| Platform engineer | Proof and safe commands | Evidence fields, pre-checks, snapshots, dry-runs, risk notes |
| CTO/CFO | Credible control | Human approval flow and full audit trail |

---

<div class="kicker">Solution</div>

## The core workflow

<div class="flow">
  <div class="step">Upload exports</div>
  <div class="step">Normalize resources</div>
  <div class="step">Run deterministic rules</div>
  <div class="step">Generate remediation packs</div>
  <div class="step">Approve and simulate</div>
</div>

<br>

<div class="grid-2">
  <div class="card">
    <h3>Source of truth</h3>
    <p>Rules and command templates are deterministic. No LLM guesses decide what is waste.</p>
  </div>
  <div class="card">
    <h3>Safety posture</h3>
    <p>The MVP never executes cloud commands. It only generates and audits what would be done.</p>
  </div>
</div>

---

<div class="kicker">Architecture</div>

## API-first MVP architecture

```text
AWS/Azure CSV or JSON
        |
        v
FastAPI upload endpoint
        |
        v
Parser -> Normalizer -> SQLite
        |
        v
Rule engine -> Savings calculator -> Command generator
        |
        v
Remediation pack -> Next.js dashboard -> Audit log
```

<div class="band">
The dashboard is a client of the API. The backend remains the system of record for evidence, rules, workflow state, and audit events.
</div>

---

<div class="kicker">Data Model</div>

## Evidence-first data model

<div class="grid">
  <div class="card">
    <h3>ImportBatch</h3>
    <p>File name, detected provider, selected provider, record count, validation errors.</p>
  </div>
  <div class="card">
    <h3>CloudResource</h3>
    <p>Normalized provider, account, resource, cost, state, metrics, tags, source file, source row.</p>
  </div>
  <div class="card">
    <h3>Recommendation</h3>
    <p>Finding type, savings, confidence, risk, action, status, evidence JSON.</p>
  </div>
</div>

<br>

<div class="grid-2">
  <div class="card">
    <h3>RemediationPack</h3>
    <p>Pre-check, backup, dry-run, final command, SDK logic, warning, rollback note.</p>
  </div>
  <div class="card">
    <h3>AuditEvent</h3>
    <p>Imports, rule runs, approvals, rejections, simulations, and exports.</p>
  </div>
</div>

---

<div class="kicker">Detection Rules</div>

## Deterministic waste detection

| Rule | Signal | Confidence behavior |
|---|---|---|
| AWS unattached EBS | `available` or no `attached_to` | High when both state and attachment agree |
| Azure unattached disk | `Unattached` or no `managed_by` | High when both disk state and attachment agree |
| AWS idle EC2 | CPU p95 < 5 and network < 100 MB | Medium when metrics exist |
| Azure idle VM | CPU p95 < 5 and network < 100 MB | Medium when metrics exist |
| Missing metrics | VM has cost but no utilization | Low confidence, zero claimed savings |
| Protected tags | `keep=true`, `environment=prod`, etc. | Manual review, no destructive recommendation |

---

<div class="kicker">Trust Layer</div>

## Every recommendation explains itself

<div class="grid-2">
  <div class="card">
    <h3>Why flagged?</h3>
    <p>Provider, resource type, state, attachment field, utilization metrics, cost, tags, source file, and source row.</p>
  </div>
  <div class="card">
    <h3>How risky?</h3>
    <p>Confidence label, risk label, protected-resource guardrails, and honest missing-metrics handling.</p>
  </div>
</div>

<br>

<div class="warning">
Billing data alone does not prove VM idleness. The product marks those cases as low-confidence needs-metrics findings instead of overstating certainty.
</div>

---

<div class="kicker">Remediation</div>

## A remediation pack, not just a delete command

```bash
# AWS unattached EBS example
aws ec2 describe-volumes --volume-ids vol-0aaa111 --region us-east-1
aws ec2 create-snapshot --volume-id vol-0aaa111 --region us-east-1 \
  --description "pre-delete snapshot created by Cost Optimizer"
aws ec2 delete-volume --volume-id vol-0aaa111 --region us-east-1 --dry-run
aws ec2 delete-volume --volume-id vol-0aaa111 --region us-east-1
```

<div class="band">
Final commands are marked as requiring approval. Simulation records intent only and never invokes AWS or Azure.
</div>

---

<div class="kicker">Human Workflow</div>

## Human-in-the-loop by design

<div class="flow">
  <div class="step">DRAFT</div>
  <div class="step">REVIEWED</div>
  <div class="step">APPROVED</div>
  <div class="step">SIMULATED_EXECUTION</div>
  <div class="step">AUDITED</div>
</div>

<br>

<div class="grid-2">
  <div class="card">
    <h3>Reject path</h3>
    <p>Engineers can reject recommendations and preserve the decision in the audit trail.</p>
  </div>
  <div class="card">
    <h3>Simulation path</h3>
    <p>Simulation updates status and records that no real command was executed.</p>
  </div>
</div>

---

<div class="kicker">Dashboard</div>

## Client-facing demo screens

<div class="grid">
  <div class="card">
    <h3>Executive summary</h3>
    <p>Resources scanned, waste found, monthly savings, annual savings, provider split.</p>
  </div>
  <div class="card">
    <h3>Recommendations</h3>
    <p>Provider, resource, type, region, savings, confidence, risk, action, status.</p>
  </div>
  <div class="card">
    <h3>Remediation detail</h3>
    <p>Evidence, commands, SDK logic, risk warning, rollback note, approve/reject/simulate.</p>
  </div>
</div>

<br>

<div class="card">
  <h3>Audit log</h3>
  <p>Shows uploaded files, rule runs, approvals, rejections, simulations, and exports.</p>
</div>

---

<div class="kicker">Demo Result</div>

## Sample data produces a complete story

<div class="grid">
  <div class="card">
    <div class="metric">8</div>
    <p>Expected findings in eval fixture</p>
  </div>
  <div class="card">
    <div class="metric">$259.30</div>
    <p>Monthly savings identified in sample eval</p>
  </div>
  <div class="card">
    <div class="metric">0</div>
    <p>Missing or extra eval findings</p>
  </div>
</div>

<br>

<div class="band">
Backend tests passed: 11 tests. Frontend build passed on Next.js 16.2.9.
</div>

---

<div class="kicker">API Surface</div>

## API-first, dashboard-friendly endpoints

| Capability | Endpoint |
|---|---|
| Upload exports | `POST /api/imports/upload` |
| List resources | `GET /api/resources` |
| Run rules | `POST /api/recommendations/run` |
| View findings | `GET /api/recommendations` |
| View command pack | `GET /api/recommendations/{id}/remediation-pack` |
| Workflow | `approve`, `reject`, `simulate` |
| Reporting | `GET /api/summary`, `GET /api/export/recommendations.csv` |
| Audit | `GET /api/audit-events` |

---

<div class="kicker">Production Path</div>

## From MVP to enterprise FinOps platform

<div class="grid-2">
  <div class="card">
    <h3>Data integrations</h3>
    <p>AWS CUR, Azure Cost Management, AWS Config, Azure Resource Graph, CloudWatch, Azure Monitor.</p>
  </div>
  <div class="card">
    <h3>Workflow integrations</h3>
    <p>Jira, ServiceNow, Slack, Teams, owner-tag routing, two-person approval for production.</p>
  </div>
  <div class="card">
    <h3>Execution controls</h3>
    <p>Read-only discovery role, separate remediation role, controlled runner, least-privilege IAM.</p>
  </div>
  <div class="card">
    <h3>Platform hardening</h3>
    <p>Postgres, migrations, RBAC, observability, retention policies, SOC2-aligned audit controls.</p>
  </div>
</div>

---

<div class="kicker">Deployment</div>

## Packaged for Cloud Run or ECS

<div class="grid-2">
  <div class="card">
    <h3>FastAPI container</h3>
    <p>`backend/Dockerfile` runs the API and stores local demo data under `/data`.</p>
  </div>
  <div class="card">
    <h3>Next.js container</h3>
    <p>`frontend/Dockerfile` builds a standalone dashboard image with an API URL build argument.</p>
  </div>
</div>

<br>

<div class="warning">
SQLite is acceptable for a local or single-session demo. Production deployments should move to Postgres or Cloud SQL.
</div>

---

<div class="kicker">Close</div>

## The key design choice is trust

<div class="card">
  <p>CloudWaste Sentinel does not simply say "delete this." It shows the source evidence, confidence, risk, safer pre-checks, backup guidance, exact commands, approval state, and audit trail.</p>
</div>

<br>

<div class="grid-2">
  <div class="card">
    <h3>What works now</h3>
    <p>Upload, normalize, detect, explain, generate commands, approve, simulate, audit.</p>
  </div>
  <div class="card">
    <h3>What comes next</h3>
    <p>Live cloud inventory, metrics ingestion, RBAC, ticketing, controlled execution, and production database.</p>
  </div>
</div>

---

<div class="kicker">Appendix</div>

## Exporting this deck

This file is Marp-compatible Markdown.

```bash
npx @marp-team/marp-cli presentation_deck.md --pptx
npx @marp-team/marp-cli presentation_deck.md --pdf
```

Submission cleanup confirmation:

- No paid cloud resources were created.
- No cloud credentials are required.
- No destructive cloud commands are executed.
- All remediation actions are generated, reviewed, and simulated only.
