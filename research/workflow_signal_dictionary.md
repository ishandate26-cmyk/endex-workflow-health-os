# Workflow Signal Dictionary

This is the lightweight event vocabulary I would want Customer Success and GTM to share.

## Raw Usage Events

- `file_uploaded`: user brought a live asset into Endex.
- `analysis_generated`: Endex produced an output.
- `output_exported`: user moved the output into real work.
- `citation_opened`: user checked source traceability.
- `reviewer_invited`: user brought a stakeholder into the workflow.
- `reviewer_opened`: stakeholder consumed the output.
- `workflow_rerun`: the strongest signal that the product is becoming part of a recurring process.
- `user_override`: user corrected or rewrote the output, memory, assumptions, mapping, or format.

## Interpreted CS Signals

- **Exploration:** usage exists but has not repeated.
- **Trust gap:** output is generated but not exported, or citations are opened repeatedly without acceptance.
- **Memory gap:** user overrides saved preferences or outputs repeatedly.
- **Champion risk:** one user is active but no reviewer or second user enters the loop.
- **Workflow adoption:** same pattern repeats across a live business cycle.
- **Expansion readiness:** workflow repeats, memory is reused, output is exported, and a reviewer enters the process.

## Why This Matters

Endex customers may not name their workflow cleanly upfront. The system should infer workflow patterns from behavior first, then let CS confirm and harden those workflows with the customer.

