import json
from collections import Counter
from pathlib import Path


def load_events(events_path: Path) -> list[dict]:
    with events_path.open(encoding="utf-8") as f:
        data = json.load(f)
    events = data.get("events", [])
    if not isinstance(events, list):
        raise ValueError("Expected 'events' to be a list in events.json")
    return events


def gather_agent_counts(events: list[dict]) -> Counter:
    counts: Counter = Counter()
    for event in events:
        agents = event.get("agents")
        if agents is None:
            agents = event.get("agents_involved")
        if not agents:
            continue
        if isinstance(agents, str):
            agents = [agents]
        for agent in agents:
            if agent:
                counts[agent] += 1
    return counts


def gather_action_type_counts(events: list[dict]) -> Counter:
    counts: Counter = Counter()
    for event in events:
        action_type = event.get("type") or "Unknown"
        counts[action_type] += 1
    return counts


def main() -> None:
    events_path = Path(__file__).resolve().parent / ".." / "village-event-log" / "events.json"
    events = load_events(events_path)

    total_events = len(events)
    agent_counts = gather_agent_counts(events)
    action_type_counts = gather_action_type_counts(events)

    report_lines = [
        "# Event Log Analysis",
        "",
        "## Total Number of Events",
        f"- Total events: {total_events}",
        "",
        "## Top 5 Agents by Event Count",
    ]

    top_agents = agent_counts.most_common(5)
    if top_agents:
        report_lines.extend(
            [
                "| Agent | Event Count |",
                "| --- | --- |",
                *[f"| {agent} | {count} |" for agent, count in top_agents],
            ]
        )
    else:
        report_lines.append("_No agent data available._")

    report_lines.extend(
        [
            "",
            "## Distribution of Action Types",
        ]
    )

    if action_type_counts:
        sorted_action_types = sorted(action_type_counts.items(), key=lambda item: (-item[1], item[0]))
        report_lines.extend(
            [
                "| Action Type | Count |",
                "| --- | --- |",
                *[f"| {action_type} | {count} |" for action_type, count in sorted_action_types],
            ]
        )
    else:
        report_lines.append("_No action type data available._")

    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
