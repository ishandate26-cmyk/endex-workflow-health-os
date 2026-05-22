import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
PLAYBOOKS = ROOT / "playbooks" / "intervention_playbooks.json"


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def bool_value(value):
    return str(value).strip().lower() == "true"


def workflow_key(event):
    """Infer repeated-work patterns from behavior, not a predefined workflow field."""
    topic = event["topic"].lower()
    output_type = event["output_type"].lower()
    asset_type = event["asset_type"].lower()

    if "earnings" in topic:
        return "earnings_update"
    if "diligence" in topic or "data_room" in asset_type or "ic_memo" in output_type:
        return "diligence_or_ic_prep"
    if "monthly" in topic or "variance" in output_type:
        return "monthly_reporting"
    if "board" in topic or "board_pack" in output_type:
        return "board_reporting"
    if "model" in output_type or "excel_model" in asset_type:
        return "model_refresh"
    return "unclassified_analysis"


def score_account(events):
    total = len(events)
    completed = sum(e["event_type"] in {"analysis_generated", "workflow_rerun"} for e in events)
    reruns = sum(e["event_type"] == "workflow_rerun" for e in events)
    exports = sum(bool_value(e["exported"]) for e in events)
    citations = sum(bool_value(e["citation_opened"]) for e in events)
    memory = sum(bool_value(e["memory_reused"]) for e in events)
    overrides = sum(bool_value(e["user_override"]) for e in events)
    reviewers = sum(bool_value(e["reviewer_invited"]) or e["event_type"] == "reviewer_opened" for e in events)
    users = len({e["user_id"] for e in events})
    workflows = Counter(workflow_key(e) for e in events)

    adoption = min(100, completed * 12 + exports * 10 + reruns * 18)
    trust = min(100, citations * 8 + exports * 12 + max(0, 25 - overrides * 8))
    memory_quality = min(100, memory * 18 + reruns * 10 - overrides * 12)
    stakeholder_spread = min(100, reviewers * 18 + max(0, users - 1) * 12)
    recurrence = min(100, reruns * 35 + len([w for w, c in workflows.items() if c >= 3]) * 15)

    score = round((adoption + trust + memory_quality + stakeholder_spread + recurrence) / 5)

    return {
        "events": total,
        "completed": completed,
        "reruns": reruns,
        "exports": exports,
        "citations": citations,
        "memory": memory,
        "overrides": overrides,
        "reviewers": reviewers,
        "users": users,
        "workflows": workflows,
        "adoption": adoption,
        "trust": trust,
        "memory_quality": memory_quality,
        "stakeholder_spread": stakeholder_spread,
        "recurrence": recurrence,
        "score": max(0, min(100, score)),
    }


def recommend_actions(metrics):
    actions = []

    if metrics["completed"] > 0 and metrics["exports"] == 0:
        actions.append("generated_not_exported")
    if metrics["reruns"] == 0 and metrics["completed"] > 0:
        actions.append("saved_not_rerun")
    if metrics["overrides"] >= 2:
        actions.append("heavy_overrides")
    if metrics["users"] == 1 or metrics["reviewers"] == 0:
        actions.append("single_champion")
    if metrics["reruns"] >= 2 and metrics["memory"] >= 2 and metrics["reviewers"] >= 1 and metrics["exports"] >= 2:
        actions.append("expansion_ready")

    return actions


def health_label(score):
    if score >= 75:
        return "embedded"
    if score >= 50:
        return "developing"
    if score >= 30:
        return "at_risk"
    return "stalled"


def write_account_report(accounts, grouped_events, playbooks):
    lines = [
        "# Account Health Report",
        "",
        "This report scores whether open-ended product usage is turning into repeated work that customers trust.",
        "",
    ]

    for account in accounts:
        account_events = grouped_events.get(account["account_id"], [])
        metrics = score_account(account_events)
        actions = recommend_actions(metrics)
        workflows = ", ".join(f"{name} ({count})" for name, count in metrics["workflows"].most_common()) or "none"

        lines.extend(
            [
                f"## {account['account_name']}",
                "",
                f"- Segment: {account['segment']}",
                f"- Stage: {account['stage']}",
                f"- Primary buyer: {account['primary_buyer']}",
                f"- Health score: {metrics['score']} / 100 ({health_label(metrics['score'])})",
                f"- Inferred repeated-work patterns: {workflows}",
                f"- Signals: {metrics['reruns']} repeat-use events, {metrics['exports']} exports, {metrics['memory']} saved-preference reuse events, {metrics['overrides']} corrections/overrides, {metrics['reviewers']} reviewer signals",
                "",
            ]
        )

        if actions:
            lines.append("Recommended actions:")
            for action in actions:
                item = playbooks[action]
                lines.append(f"- **{item['signal']}**")
                lines.append(f"  - Read: {item['likely_meaning']}")
                lines.append(f"  - Next move: {item['cs_action']}")
        else:
            lines.append("Recommended actions: continue monitoring; no urgent intervention.")
        lines.append("")

    (OUTPUTS / "account_health_report.md").write_text("\n".join(lines))


def write_expansion_report(accounts, grouped_events):
    lines = [
        "# Expansion Opportunities",
        "",
        "Accounts become expansion candidates when similar work repeats, saved preferences are reused, outputs are exported, and reviewers enter the loop.",
        "",
    ]
    found = False

    for account in accounts:
        metrics = score_account(grouped_events.get(account["account_id"], []))
        if "expansion_ready" in recommend_actions(metrics):
            found = True
            top_workflow = metrics["workflows"].most_common(1)[0][0]
            lines.extend(
                [
                    f"## {account['account_name']}",
                    "",
                    f"- Expansion basis: repeated `{top_workflow}` usage with saved-preference reuse and reviewer adoption.",
                    "- Suggested next step: ask for the adjacent job owned by the same team or reviewer.",
                    "- GTM proof point: this account is no longer just testing Endex; usage has repeated across cycles.",
                    "",
                ]
            )

    if not found:
        lines.append("No expansion-ready accounts in current sample.")

    (OUTPUTS / "expansion_opportunities.md").write_text("\n".join(lines))


def write_churn_report(accounts, grouped_events):
    lines = [
        "# Churn Risk Flags",
        "",
        "Accounts are risky when usage is active but does not become trusted, exported, repeated, or multi-stakeholder.",
        "",
    ]
    found = False

    for account in accounts:
        metrics = score_account(grouped_events.get(account["account_id"], []))
        actions = recommend_actions(metrics)
        risky_actions = [a for a in actions if a in {"generated_not_exported", "saved_not_rerun", "heavy_overrides", "single_champion"}]
        if health_label(metrics["score"]) in {"stalled", "at_risk"} or risky_actions:
            found = True
            lines.extend(
                [
                    f"## {account['account_name']}",
                    "",
                    f"- Health score: {metrics['score']} / 100 ({health_label(metrics['score'])})",
                    f"- Risk indicators: {', '.join(risky_actions) if risky_actions else 'low score'}",
                    "- Suggested CS posture: diagnose whether the issue is trust, fit for the customer's work, reviewer adoption, or missing live deadline.",
                    "",
                ]
            )

    if not found:
        lines.append("No churn risks in current sample.")

    (OUTPUTS / "churn_risk_flags.md").write_text("\n".join(lines))


def main():
    OUTPUTS.mkdir(exist_ok=True)
    accounts = read_csv(DATA / "accounts.csv")
    events = read_csv(DATA / "workflow_events.csv")
    playbooks = json.loads(PLAYBOOKS.read_text())

    grouped_events = defaultdict(list)
    for event in events:
        grouped_events[event["account_id"]].append(event)

    write_account_report(accounts, grouped_events, playbooks)
    write_expansion_report(accounts, grouped_events)
    write_churn_report(accounts, grouped_events)

    print("Generated:")
    print("- outputs/account_health_report.md")
    print("- outputs/expansion_opportunities.md")
    print("- outputs/churn_risk_flags.md")


if __name__ == "__main__":
    main()
