# Workflow Signal Dictionary

This is the lightweight event vocabulary I would want Customer Success and GTM to share.

## Raw Usage Events

- `file_uploaded`: user brought a live workbook, model, transcript, deck, or data export into Endex.
- `analysis_generated`: Endex produced an output.
- `output_exported`: user moved the output into real work.
- `citation_opened`: user checked source traceability.
- `reviewer_invited`: user brought a stakeholder into the work.
- `reviewer_opened`: stakeholder consumed the output.
- `workflow_rerun`: shorthand in this prototype for "the same kind of job happened again." In a real product this might be inferred from similar files, prompts, outputs, timing, and saved preferences rather than a literal button.
- `user_override`: user corrected or rewrote the output, saved preference, assumption, mapping, or format.

## Interpreted CS Signals

- **Exploration:** usage exists but has not repeated.
- **Trust gap:** output is generated but not exported, or citations are opened repeatedly without acceptance.
- **Memory gap:** user corrects saved preferences or outputs repeatedly.
- **Champion risk:** one user is active but no reviewer or second user enters the loop.
- **Repeated-use adoption:** same pattern repeats across a live business cycle.
- **Expansion readiness:** similar work repeats, saved preferences are reused, output is exported, and a reviewer enters the process.

## Why This Matters

Endex customers may not name their workflow cleanly upfront. The system should infer repeated patterns from behavior first, then let CS confirm and harden those patterns with the customer.
