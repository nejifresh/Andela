# Cloud Cost Optimizer & Remediation Engine

## 1. Title
CloudWaste Sentinel: evidence-backed FinOps remediation.

## 2. Problem
Cloud waste is visible in reports, but safe remediation is hard. Teams need savings, proof, and controlled execution.

## 3. Personas
FinOps leads need savings. Platform engineers need evidence and safe commands. CTO/CFO stakeholders need credible annual impact.

## 4. Solution
Upload AWS/Azure exports, normalize resources, run deterministic rules, generate remediation packs, and audit human approval.

## 5. Architecture
FastAPI, SQLite, SQLAlchemy, deterministic rules, command templates, Next.js dashboard.

## 6. Ingestion
CSV and JSON support for AWS and Azure with provider detection, validation errors, and source row tracking.

## 7. Rules
Unattached disks, idle VMs with metrics, missing metrics warnings, protected resource guardrails.

## 8. Remediation Packs
Each recommendation includes pre-check, backup/snapshot, dry-run where supported, final command, SDK logic, risk warning, and rollback note.

## 9. Human Workflow
Recommendations move through draft, approved, rejected, and simulated execution states. Simulation never executes cloud commands.

## 10. Dashboard
Executive savings, recommendations table, evidence detail, command pack, approval controls, and audit log.

## 11. Testing
Parser, normalization, rule, command, API, and eval coverage validate expected sample outcomes.

## 12. Production Roadmap
AWS CUR, Azure Cost Management, CloudWatch, Azure Monitor, RBAC, Jira/ServiceNow, Slack/Teams, controlled runners, Postgres, observability, SOC2 controls.

## 13. Demo Flow
Upload samples, run recommendations, inspect EBS finding, approve, simulate, show audit trail.

## 14. Cleanup
No paid cloud resources were created. All behavior is local and generate-only.
