# Endex Workflow Health OS

Companion artifact for the Endex case assessment.

This repo does **not** attempt to rebuild Endex. It sketches the operating layer I would build around Endex customer usage to answer one question:

> Which customers are merely impressed by the product, and which customers are becoming dependent on recurring Endex workflows?

## Why This Exists

Endex users will not always enter through a clean, predefined workflow. A hedge fund analyst, PE associate, or enterprise finance user may start by asking questions, uploading files, reconciling models, drafting summaries, checking citations, or generating outputs in a fairly open-ended way.

Customer Success should not force every customer into a rigid workflow too early. Instead, it should observe usage, detect where behavior starts repeating, and then help convert that pattern into a durable workflow.

The motion:

1. Users explore Endex flexibly.
2. Product events reveal repeated behavior.
3. Endex infers likely workflows.
4. CS confirms and hardens the workflow.
5. Reuse, trust, stakeholder spread, and expansion are tracked over time.

## What This Prototype Does

The script in `src/score_workflow_health.py` reads synthetic account, user, and event data, then generates:

- account health scores
- inferred workflow clusters
- churn risk flags
- expansion opportunities
- CS intervention recommendations
- GTM proof points

## Repo Structure

```text
endex-workflow-health-os/
  data/
    accounts.csv
    users.csv
    workflow_events.csv
  playbooks/
    intervention_playbooks.json
  research/
    operating_thesis.md
  src/
    score_workflow_health.py
  outputs/
    account_health_report.md
    expansion_opportunities.md
    churn_risk_flags.md
```

## Run It

From this directory:

```bash
python3 src/score_workflow_health.py
```

The script writes reports into `outputs/`.

## Case Study Tie-In

The case prompt asks for a system to flag and intervene on sub-optimal user and enterprise experiences.

My answer: build Customer Success around **workflow health**, not generic account sentiment.

The important distinction:

- Product events tell us what users did.
- Workflow inference tells us what users are starting to depend on.
- CS interventions turn emerging patterns into retained, expanding account behavior.
- GTM uses repeated workflow proof to expand into adjacent teams and use cases.

