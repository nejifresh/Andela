# Five-Minute Demo Script

1. Open with the problem: cloud waste is expensive, but remediation is risky because engineers need proof before deleting anything.
2. Show the dashboard upload control and upload `aws_resources.csv` plus `azure_resources.csv`.
3. Run recommendations and point out resources scanned, monthly savings, annual savings, and status counts.
4. Open an AWS unattached EBS recommendation. Explain the evidence: source row, state, attachment, tags, and cost.
5. Show the remediation pack: pre-check, snapshot, dry-run, final command, SDK logic, risk warning, and rollback note.
6. Approve the recommendation, then simulate it. Emphasize that no real command is executed.
7. Open an idle VM candidate and explain the metric thresholds.
8. Open or mention the missing-metrics recommendation and explain that the system refuses to overclaim idleness.
9. Show the protected-resource guardrail and the audit log.
10. Close with the production path: real cost exports, monitor metrics, RBAC, ticketing, two-person approval, and controlled runners.

Closing line:

CloudWaste Sentinel is designed around trust. It does not just say "delete this"; it shows evidence, confidence, risk, safer checks, and exact commands for human review.
