# prompts.md — Cloud Cost Optimizer & Remediation Engine Prompt Playbook

> Purpose: Use this as the operating playbook for the interview build. Do **not** manually code or manually patch files. Paste these prompts into the same AI coding agent end-to-end so the agent creates and maintains the repository, implementation, fixes, tests, docs, and this audit log.

---

## 0. Interview Constraints To Keep Visible

- Project: **Cloud Cost Optimizer & Remediation Engine**
- Focus: FinOps
- Required stack posture: **Python-based, API-first, free-tier database, dashboard**
- Inputs: AWS/Azure billing exports in **CSV and JSON**
- Required intelligence: identify orphaned/waste resources such as **unattached disks** and **idle VMs**
- Required output: generate **specific CLI commands and/or API logic** to decommission waste
- Workflow constraint: **No manual code edits.** The AI agent must provide all logic and fixes.
- Required audit file: `prompts.md` must capture the full prompt history.
- Timebox: MVP target 4–6 hours; maximum 16 hours.
- Final submission: GitHub repo, `prompts.md`, Tagle tag summary, AI-generated deck, and cloud-resource cleanup confirmation.

---

## 1. First Message — Required Initial Execution Prompt

Paste this as the **first message** to Claude Code, Cursor, Copilot, or the chosen AI coding agent.

```text
Lead Architect mode: ON. We are building a Python-based, API-first Cloud Cost Optimizer & Remediation Engine using a free database and a dashboard.
Rules:
● No Manual Edits: You provide all logic and fixes. I will not edit any code.
● Audit Log: You must maintain a file named prompts.md. After every turn, update that file (or provide the text block) with the prompt I just used.
● Time-Check: Start a timer. Goal is an MVP in 4-6 hours (Max window: 16h). Report 'Elapsed Time' at the end of every response. Acknowledge and let's start.
```

---

## 2. Operating Charter For The Agent

After the agent acknowledges the first message, paste this.

```text
Before writing code, create an implementation plan for the Cloud Cost Optimizer & Remediation Engine.

Act as a senior Forward Deployed Engineer, not just a coder. Optimize for a polished client-facing demo, reliable technical design, and clear FinOps business value.

Hard constraints:
1. Python-based and API-first.
2. Free database: SQLite for the MVP, with SQLAlchemy models that can later move to Postgres.
3. Dashboard included.
4. Ingest AWS and Azure billing/resource exports in CSV and JSON.
5. Detect orphaned resources and waste using deterministic rules, not LLM guesses.
6. Generate exact remediation commands and safe pre-check commands.
7. Never execute real cloud deletion commands in the MVP. Only generate commands and mark them as simulated/pending approval.
8. Add a human-in-the-loop approval flow: DRAFT → REVIEWED → APPROVED → SIMULATED_EXECUTION or REJECTED.
9. Maintain evidence: each finding must cite the source file, source row/index, relevant fields, and confidence level.
10. Keep all work local. Do not provision paid cloud resources.
11. Add tests, sample data, a README, and a demo script.
12. Maintain prompts.md after every turn.

Plan first. Do not implement yet. Return:
- proposed architecture
- data model
- API endpoints
- dashboard screens
- detection rules
- remediation command templates
- testing strategy
- 4–6 hour build sequence
- risks and mitigations
- what you need from me next

Elapsed Time: include current estimate.
```

---

## 3. Product And Client Lens Prompt

Use this before implementation to keep the build from becoming a backend-only project.

```text
Refine the plan from a client-facing FinOps perspective.

The buyer/user is a FinOps lead, cloud platform manager, or CTO who needs trust before decommissioning resources. The product must make it easy to answer:
- What waste did we find?
- How much money can we save?
- Why do we believe this resource is orphaned or idle?
- What exact command would remediate it?
- What is the blast radius/risk?
- What pre-check should an engineer run before approving?
- Is this safe to execute now, or should it require manual review?

Update the plan so the dashboard and API clearly support this business narrative. Add confidence scoring and a risk label for every recommendation.

Do not write code yet. Update prompts.md.
```

---

## 4. Architecture Decision Prompt

Use this to lock the architecture before coding.

```text
Now produce the final architecture decision record for the MVP.

Preferred implementation:
- Backend: FastAPI
- Database: SQLite using SQLAlchemy
- Validation: Pydantic
- Data parsing: pandas or Python csv/json libraries where appropriate
- Testing: pytest
- Dashboard: FastAPI-served dashboard using Jinja/HTMX or a lightweight React/Vite frontend if you can complete it within the timebox
- Charts: simple cost and recommendation visuals
- Command generation: deterministic templates
- AI use: optional only for plain-English explanations; never for source-of-truth detection or command construction

Create a repository file plan. Include exact filenames and responsibilities. Then wait for my approval before scaffolding.

Update prompts.md.
```

---

## 5. Scaffold Prompt

```text
Approved. Scaffold the repository now.

Requirements:
- Create a clean Python project structure.
- Include FastAPI app startup.
- Include SQLite database setup.
- Include SQLAlchemy models.
- Include Pydantic schemas.
- Include a sample-data directory with AWS and Azure CSV/JSON fixtures.
- Include tests directory.
- Include README.md with setup and demo instructions.
- Include prompts.md with this full audit log.
- Include .env.example.
- Include a Makefile or simple scripts for running API, tests, and demo seed.

Do not call any external cloud API. Do not create cloud resources. Keep everything local.

After scaffolding, run the tests or at least import checks. Report what passed and what failed. Update prompts.md.
```

---

## 6. Ingestion And Normalization Prompt

```text
Implement ingestion and normalization for AWS and Azure billing/resource exports.

Input support:
1. AWS CSV and JSON exports with fields such as:
   - provider
   - account_id
   - region
   - service
   - resource_id
   - resource_type
   - usage_type
   - usage_start_date
   - usage_end_date
   - cost
   - currency
   - tags
   - state
   - attached_to
   - cpu_p95
   - network_in_mb
   - network_out_mb

2. Azure CSV and JSON exports with fields such as:
   - provider
   - subscription_id
   - resource_group
   - location
   - resource_id
   - resource_type
   - meter_category
   - cost
   - currency
   - date
   - tags
   - disk_state
   - managed_by
   - power_state
   - cpu_p95
   - network_in_mb
   - network_out_mb

Important: billing exports alone do not always prove VM idleness. If utilization fields are missing, mark idle VM findings as LOW confidence or require optional metrics input.

Deliverables:
- file upload endpoint
- parser service
- normalizer service
- database persistence
- source row/index tracking
- validation errors returned clearly to user
- unit tests for AWS CSV, AWS JSON, Azure CSV, Azure JSON

Update prompts.md and report elapsed time.
```

---

## 7. Rule Engine Prompt

```text
Implement the deterministic waste detection rule engine.

Rules required for MVP:

A. AWS unattached EBS volume
- provider = aws
- resource_type in [ebs_volume, volume, AWS::EC2::Volume]
- state in [available, unattached] OR attached_to is empty/null
- monthly cost > 0
- no keep/protected tag
- confidence HIGH if state explicitly says available/unattached and attached_to is empty

B. Azure unattached managed disk
- provider = azure
- resource_type contains Microsoft.Compute/disks or disk
- disk_state = Unattached OR managed_by is empty/null
- monthly cost > 0
- no keep/protected tag
- confidence HIGH if disk_state is Unattached and managed_by is empty/null

C. AWS idle EC2 instance
- provider = aws
- resource_type in [ec2_instance, instance, AWS::EC2::Instance]
- running or stopped state is known
- If cpu_p95 < 5 and network_in_mb + network_out_mb < 100 over the sample period, mark idle candidate
- If utilization fields are missing, do not claim true idleness; mark NEEDS_METRICS with LOW confidence
- Remediation default for running idle instance should be STOP or RIGHTSIZING_REVIEW, not termination

D. Azure idle VM
- provider = azure
- resource_type contains Microsoft.Compute/virtualMachines or vm
- If cpu_p95 < 5 and network_in_mb + network_out_mb < 100, mark idle candidate
- If utilization fields are missing, mark NEEDS_METRICS with LOW confidence
- Remediation default for running idle VM should be DEALLOCATE or RIGHTSIZING_REVIEW, not deletion

E. Protected resource guardrail
- If tags include keep=true, protected=true, environment=prod, do-not-delete=true, owner=critical, or similar, suppress destructive recommendation or mark REQUIRE_MANUAL_REVIEW.

Each finding must include:
- recommendation_id
- provider
- resource_id
- resource_type
- region/location
- account/subscription
- estimated_monthly_savings
- finding_type
- confidence
- risk_level
- evidence fields
- recommended_action
- status

Add tests for all rules and edge cases. Update prompts.md.
```

---

## 8. Remediation Command Generation Prompt

```text
Implement remediation command generation.

The command generator must produce a remediation pack, not just one destructive command.

For every recommendation include:
1. Summary: human-readable explanation.
2. Pre-check command: safe command to verify state before action.
3. Backup/snapshot command where applicable.
4. Dry-run command where provider supports it.
5. Final command: destructive or cost-saving command, marked as requires approval.
6. API/SDK logic snippet or pseudocode alternative.
7. Risk warning.
8. Rollback note. If deletion has no direct rollback, say so honestly and require snapshot/backup first.

Required command templates:

AWS EBS unattached volume:
- pre-check: aws ec2 describe-volumes --volume-ids <volume_id> --region <region>
- snapshot: aws ec2 create-snapshot --volume-id <volume_id> --region <region> --description "pre-delete snapshot created by Cost Optimizer"
- dry run: aws ec2 delete-volume --volume-id <volume_id> --region <region> --dry-run
- final: aws ec2 delete-volume --volume-id <volume_id> --region <region>

AWS idle/stopped EC2:
- pre-check: aws ec2 describe-instances --instance-ids <instance_id> --region <region>
- safer action for running idle: aws ec2 stop-instances --instance-ids <instance_id> --region <region>
- high-risk final action only after approval: aws ec2 terminate-instances --instance-ids <instance_id> --region <region>

Azure unattached managed disk:
- pre-check: az disk show --ids <resource_id>
- snapshot: az snapshot create --resource-group <resource_group> --source <resource_id> --name <generated_snapshot_name>
- final: az disk delete --ids <resource_id> --yes

Azure idle VM:
- pre-check: az vm get-instance-view --ids <resource_id>
- safer action: az vm deallocate --ids <resource_id>
- high-risk final action only after approval: az vm delete --ids <resource_id> --yes

Do not execute commands. Store generated commands and expose through API/dashboard. Add tests proving commands are generated correctly and dangerous commands are flagged. Update prompts.md.
```

---

## 9. API Prompt

```text
Build the API layer.

Required endpoints:
- GET /health
- POST /api/imports/upload
- GET /api/imports
- GET /api/resources
- POST /api/recommendations/run
- GET /api/recommendations
- GET /api/recommendations/{id}
- GET /api/recommendations/{id}/remediation-pack
- POST /api/recommendations/{id}/approve
- POST /api/recommendations/{id}/reject
- POST /api/recommendations/{id}/simulate
- GET /api/summary
- GET /api/export/recommendations.csv

Rules:
- No real cloud execution.
- Simulation should only mark what would have been run.
- Return clean errors.
- API docs through OpenAPI must be usable.
- Add tests for endpoints.

Update prompts.md.
```

---

## 10. Dashboard Prompt

```text
Build the dashboard for a client-facing demo.

Minimum screens:
1. Upload screen:
   - upload AWS/Azure CSV or JSON
   - show parsing status and validation errors

2. Executive summary:
   - total resources scanned
   - waste resources found
   - estimated monthly savings
   - estimated annual savings
   - savings by provider
   - savings by finding type

3. Recommendations table:
   - provider
   - resource id
   - type
   - region/location
   - estimated savings
   - confidence
   - risk
   - recommended action
   - status
   - view remediation pack button

4. Remediation detail:
   - evidence fields
   - why flagged
   - pre-check command
   - backup/snapshot command
   - dry-run command
   - final command
   - SDK/API logic snippet
   - approve/reject/simulate buttons

5. Audit log view:
   - uploaded files
   - rule runs
   - approvals/rejections/simulations

Design principles:
- Make it obvious this is safe and human-reviewed.
- Show money saved prominently.
- Show evidence and confidence so the client can trust the result.
- Keep UI polished enough for a senior FDE demo.

Update prompts.md and include screenshots/gifs instructions in README if possible.
```

---

## 11. Tests, Evals, And Guardrails Prompt

```text
Add tests and an evaluation harness.

Testing requirements:
- Parser tests for AWS/Azure CSV/JSON.
- Rule tests for unattached disks, idle VMs, protected resources, missing metrics, zero-cost resources.
- Command generation tests for AWS and Azure remediation packs.
- API tests for upload, run recommendations, approve/reject/simulate.
- Regression fixture with expected recommendation count and expected savings.

Evaluation requirements:
- Create sample files with known expected findings.
- Add an eval script that prints precision-style results:
  - expected findings
  - actual findings
  - missing findings
  - extra findings
  - command-generation pass/fail

Guardrails:
- No command execution.
- No cloud credentials required.
- Never print secrets from uploaded files.
- Protected tags must prevent or escalate destructive actions.
- If input lacks utilization metrics, VM idle recommendations must be low confidence or needs metrics.

Run tests and fix failures using agent-generated changes only. Update prompts.md.
```

---

## 12. README And Demo Script Prompt

```text
Create a polished README.md and demo script.

README must include:
- product overview
- architecture diagram in Mermaid
- local setup commands
- how to run API
- how to run dashboard
- how to run tests
- sample data explanation
- API endpoint list
- detection rules
- remediation command examples
- safety guardrails
- limitations and future work
- cleanup statement confirming no real cloud resources are created by this MVP

Demo script must be written for a 5-minute interview walkthrough:
1. Problem: cloud waste is expensive, but deletion is risky.
2. Upload AWS/Azure export.
3. Show normalized resources.
4. Run recommendations.
5. Show savings dashboard.
6. Open an unattached disk finding.
7. Explain evidence and confidence.
8. Show pre-check, snapshot, dry-run, final command.
9. Approve and simulate.
10. Show audit trail.
11. Close with what would be next in production.

Update prompts.md.
```

---

## 13. Production Architecture Prompt

Use this to demonstrate senior thinking even if not fully implemented.

```text
Add a section to README.md called Production Readiness Roadmap.

Cover:
- real AWS CUR and Azure Cost Management ingestion
- optional CloudWatch/Azure Monitor metrics ingestion for idle detection
- IAM least privilege and read-only discovery role
- approval workflow with RBAC
- ticketing integrations such as Jira/ServiceNow
- Slack/Teams notifications
- policy-as-code for protected resources
- scheduled scans
- audit logging
- command execution through controlled runners only after approval
- multi-tenant support
- Postgres migration
- observability and error reporting
- SOC2/security considerations

Frame this as what I would tell a real client after the MVP demo.

Update prompts.md.
```

---

## 14. Bug-Fix Prompt Template

Use this whenever something breaks. Do not manually patch code.

```text
A bug occurred. Do not ask me to manually edit code.

Observed behavior:
<paste terminal output, screenshot description, API response, or test failure>

Expected behavior:
<describe what should happen>

Please:
1. Diagnose the likely root cause.
2. Identify the files that need changes.
3. Apply the fix yourself.
4. Explain the change in plain English.
5. Run the smallest relevant test first.
6. Then run the broader test suite.
7. Update prompts.md with this prompt and your fix summary.
8. Report elapsed time.
```

---

## 15. Quality Review Prompt

Use this before final submission.

```text
Perform a senior FDE quality review of the repository.

Score the project against these interview criteria:
- meets challenge requirements
- API-first design
- Python quality
- free database usage
- dashboard quality
- AWS/Azure input coverage
- orphaned resource detection quality
- idle VM detection honesty and confidence scoring
- remediation command specificity
- safety guardrails
- human-in-the-loop workflow
- tests/evals
- README/demo clarity
- client-facing business narrative
- production-readiness thinking

Then fix the top issues that can be fixed within the remaining time. Do not introduce risky rewrites. Update prompts.md.
```

---

## 16. Final Presentation Deck Prompt

Use the same AI tool to create the submission deck in Markdown or PPT-compatible format.

```text
Create an AI-generated presentation deck for the final submission.

Audience: senior Forward Deployed Engineer interview panel.

Deck sections:
1. Title: Cloud Cost Optimizer & Remediation Engine
2. Problem: cloud waste is expensive, but remediation is risky
3. User personas: FinOps lead, platform engineer, CTO/CFO
4. Solution overview
5. Architecture diagram
6. Data ingestion and normalization
7. Detection rules and confidence scoring
8. Remediation-pack generation with examples
9. Human-in-the-loop safety workflow
10. Dashboard screenshots or screen descriptions
11. Testing and evaluation results
12. Production readiness roadmap
13. Demo flow
14. Cleanup confirmation: no paid cloud resources were created; all local artifacts only

Keep it concise, polished, and client-facing. Update prompts.md.
```

---

## 17. Final Submission Checklist Prompt

```text
Prepare the final submission checklist.

Confirm:
- Tagle.ai Tag summary placeholder is present for me to fill in.
- Public GitHub repository link placeholder is present.
- prompts.md contains the full audit log.
- AI-generated deck exists.
- README has setup, demo, tests, rules, API, limitations, and cleanup statement.
- Tests pass or known issues are documented honestly.
- No cloud credentials are committed.
- No real cloud resources were created.
- Cleanup confirmation is included.

Create FINAL_SUBMISSION.md with these items and update prompts.md.
```

---

## 18. Interview Talking Points

Use these during the live walkthrough.

```text
I designed the product around trust. FinOps teams need savings, but platform teams need proof before deleting anything. That is why every recommendation has evidence, confidence, risk, pre-checks, and human approval.

I intentionally used deterministic detection rules instead of asking an LLM to infer cloud waste. The LLM/code agent helped build the system, but the product logic remains auditable.

For idle VMs, I do not pretend billing data alone proves idleness. The system supports utilization metrics, and when metrics are absent it lowers confidence or marks the recommendation as needs-metrics.

The remediation output is a pack: pre-check, backup/snapshot, dry-run where available, final command, SDK/API alternative, risk warning, and audit trail.

The MVP does not execute destructive cloud commands. In production, execution would require RBAC, approvals, ticketing integration, and a controlled runner with least-privilege IAM.
```

---

## 19. Definition Of Done

The MVP is done when:

- A user can upload AWS and Azure sample exports.
- The app normalizes the records and stores them in SQLite.
- The app finds unattached AWS EBS volumes and Azure disks.
- The app identifies idle VM candidates when utilization fields exist.
- The app handles missing utilization metrics honestly.
- The app calculates estimated monthly and annual savings.
- The dashboard shows summary metrics and recommendations.
- Each recommendation has evidence, confidence, risk, and status.
- Each recommendation generates specific AWS/Azure CLI commands.
- The app supports approve/reject/simulate, without executing real cloud commands.
- Tests and eval fixtures are present.
- README and demo script are strong enough for a client-facing walkthrough.
- prompts.md contains the full audit log.
- Final submission package is ready.

---

## 20. Implementation Prompt Used With Codex

```text
PLEASE IMPLEMENT THIS PLAN:
Build a local, API-first FinOps demo app named CloudWaste Sentinel using a FastAPI backend, SQLite database, and Next.js dashboard.

Implement:
- FastAPI backend with ImportBatch, CloudResource, Recommendation, RemediationPack, and AuditEvent models.
- AWS/Azure CSV and JSON ingestion.
- Normalization with source file and source row tracking.
- Deterministic waste detection for unattached disks, idle VMs, protected resources, and missing metrics.
- Remediation-pack generation with pre-check, backup/snapshot, dry-run where supported, final command, SDK/API logic, risk warning, rollback note, and approval requirement.
- Approval, rejection, and simulated execution workflow.
- Next.js dashboard with upload, summary, recommendations, remediation detail, and audit log.
- Tests, sample data, eval script, README, demo script, presentation deck, final checklist, .env.example, .gitignore, and Makefile.

Constraints:
- Never execute cloud commands.
- Use local SQLite only.
- No cloud credentials or paid cloud resources.
- Append this implementation audit entry to prompts.md.
```

Implementation summary:
- Created FastAPI backend under `backend/`.
- Created Next.js dashboard under `frontend/`.
- Added AWS/Azure CSV and JSON sample data.
- Added parser, normalizer, rule engine, command generator, summary, audit, API routes, tests, eval script, and documentation.
- Generated remediation commands only; no real cloud actions are executed.

---

## 21. Git And Dockerization Prompt Used With Codex

```text
Ok now lets initalize a nice git repo for the project and a dockerfile so that this can deployed on ECS or Google Cloud Run
```

Implementation summary:
- Added `backend/Dockerfile` for the FastAPI service.
- Added `frontend/Dockerfile` for the Next.js dashboard.
- Added `docker-compose.yml` for local two-service container runs.
- Added `.dockerignore`, Cloud Build configs, and `DEPLOYMENT.md` for ECS and Google Cloud Run deployment guidance.
- Added Docker Makefile targets.
- Verified backend tests, eval harness, and frontend build.
- Docker image build was attempted but could not complete because the Docker daemon was not running locally.

---

## 22. Presentation Deck Prompt Used With Codex

```text
Make the beautiful AI-generated Presentation Deck (PPT or Markdown solution).
```

Implementation summary:
- Rebuilt `presentation_deck.md` as a polished Marp-compatible Markdown presentation.
- Added visual slide styling, executive narrative, persona framing, architecture flow, data model, detection rules, trust layer, remediation example, workflow, dashboard overview, demo results, API surface, production roadmap, deployment story, and export instructions.
- Kept the deck Markdown-first so it can be exported to PPTX or PDF with Marp.
