import json
import os
import sys
from typing import Dict, List, Set, Tuple


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EVENTS_PATH = os.path.join(DATA_DIR, "events.json")
RULES_PATH = os.path.join(DATA_DIR, "protocol_rules.json")


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def index_events(events: List[Dict]) -> Dict[str, Dict]:
    return {e["id"]: e for e in events}


def canonical_timeline(events: List[Dict]) -> List[str]:
    return [e["id"] for e in sorted(events, key=lambda e: (e["timestamp"], e["id"]))]


def canonical_answers() -> Tuple[Dict[str, str], Dict[str, Set[str]]]:
    """Return (status_by_rule, witness_events_by_rule).

    status_by_rule: rule_id -> "violated" or "satisfied".
    witness_events_by_rule: for violated rules only, rule_id -> set of event IDs.
    """
    # These are hand-crafted for the specific events/protocol in data/.
    status = {
        "I1": "violated",  # Quorum before final
        "I2": "satisfied",  # One vote per member
        "I3": "violated",  # Appeals follow decisions
        "I4": "satisfied",  # Redaction requires request
        "I5": "violated",  # No unlogged overrides
        "I6": "violated",  # Enforcement after finalization
    }

    witnesses = {
        # I1: FINAL with only two votes in the log.
        # Minimal witness: the two vote_cast events and the premature mark_final.
        "I1": {"E02", "E03", "E05"},
        # I3: appeal_filed logged before mark_final.
        "I3": {"E05", "E06"},
        # I5: enforcement_started occurs while override_decision has not yet been logged as override_logged.
        # Minimal witness: override_decision, enforcement_started, override_logged (showing logging lag).
        "I5": {"E10", "E11", "E12"},
        # I6: enforcement_started while proposal is in SUSPENDED state, not FINAL or OVERRIDDEN-AND-RESUMED.
        # Minimal witness: mark_final, override_decision (to SUSPENDED), enforcement_started.
        "I6": {"E05", "E10", "E11"},
    }

    return status, witnesses


def load_submission(agent_name: str) -> Dict:
    here = os.path.dirname(__file__)
    sub_path = os.path.join(here, "submissions", agent_name, "answers.json")
    if not os.path.exists(sub_path):
        raise SystemExit(f"No answers.json found at {sub_path}")
    return load_json(sub_path)


def score_invariant_classification(sub: Dict, status_by_rule: Dict[str, str]) -> Tuple[float, List[str]]:
    violated_list = sub.get("violated_invariants", [])
    satisfied_list = sub.get("satisfied_invariants", [])

    declared_status: Dict[str, str] = {}
    notes: List[str] = []

    for item in violated_list:
        if not isinstance(item, dict):
            continue
        rid = item.get("id")
        if isinstance(rid, str):
            declared_status[rid] = "violated"

    for rid in satisfied_list:
        if isinstance(rid, str):
            if rid in declared_status and declared_status[rid] != "satisfied":
                notes.append(f"Invariant {rid} appears in both violated and satisfied lists; treating as misclassified.")
                declared_status[rid] = "conflict"
            else:
                declared_status[rid] = "satisfied"

    correct = 0
    total = len(status_by_rule)

    for rid, true_status in status_by_rule.items():
        declared = declared_status.get(rid)
        if declared == true_status:
            correct += 1
        else:
            notes.append(f"Invariant {rid}: expected {true_status}, got {declared}.")

    score = 30.0 * correct / total if total > 0 else 0.0
    return score, notes


def score_violation_localization(sub: Dict, status_by_rule: Dict[str, str], witnesses_by_rule: Dict[str, Set[str]]) -> Tuple[float, List[str]]:
    violated_items = {item.get("id"): set(item.get("events", []))
                      for item in sub.get("violated_invariants", [])
                      if isinstance(item, dict) and isinstance(item.get("id"), str)}

    true_violated = [rid for rid, s in status_by_rule.items() if s == "violated"]
    per_rule = 30.0 / len(true_violated) if true_violated else 0.0

    total_score = 0.0
    notes: List[str] = []

    for rid in true_violated:
        canonical = witnesses_by_rule.get(rid, set())
        reported = violated_items.get(rid, set())
        if not canonical:
            notes.append(f"No canonical witness set stored for {rid}; skipping.")
            continue
        if not reported:
            notes.append(f"Invariant {rid}: no events provided for violation.")
            continue

        # Fraction of canonical witness events covered.
        covered = len(canonical & reported)
        frac = covered / len(canonical)
        rule_score = per_rule * frac
        total_score += rule_score

        if frac < 1.0:
            missing = canonical - reported
            notes.append(f"Invariant {rid}: missing witness events {sorted(missing)} (covered {covered}/{len(canonical)}).")

    return total_score, notes


def score_timeline(sub: Dict, events: List[Dict]) -> Tuple[float, List[str]]:
    claimed = sub.get("timeline", [])
    if not isinstance(claimed, list):
        return 0.0, ["timeline must be a list of event IDs."]

    canonical = canonical_timeline(events)
    n = len(canonical)
    if n == 0:
        return 0.0, []

    m = 0
    for i in range(min(len(claimed), n)):
        if claimed[i] == canonical[i]:
            m += 1

    score = 10.0 * m / n
    notes = [f"Matched {m} of {n} positions in canonical timeline."]

    extra = set(claimed) - set(canonical)
    if extra:
        notes.append(f"timeline contains unknown event IDs: {sorted(extra)}")

    return score, notes


def check_narrative(sub: Dict) -> List[str]:
    notes: List[str] = []
    narrative = sub.get("narrative")
    if not isinstance(narrative, str):
        notes.append("narrative is missing or not a string.")
    else:
        length = len(narrative.split())
        notes.append(f"narrative present with ~{length} words (content scored manually).")
    return notes


def main(agent_name: str) -> None:
    events = load_json(EVENTS_PATH)
    status_by_rule, witnesses_by_rule = canonical_answers()
    sub = load_submission(agent_name)

    inv_score, inv_notes = score_invariant_classification(sub, status_by_rule)
    vio_score, vio_notes = score_violation_localization(sub, status_by_rule, witnesses_by_rule)
    time_score, time_notes = score_timeline(sub, events)
    narrative_notes = check_narrative(sub)

    total = inv_score + vio_score + time_score

    print(f"Invariant classification: {inv_score:.2f}/30")
    print(f"Violation localization: {vio_score:.2f}/30")
    print(f"Timeline reconstruction: {time_score:.2f}/10")
    print()
    print(f"AUTOMATED SCORE: {total:.2f}/70")
    print()
    print("Notes:")
    for note in inv_notes + vio_notes + time_notes + narrative_notes:
        print(f"- {note}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python challenges/challenge-18-gpt-5-1/grade.py <agent_name>")
        raise SystemExit(1)
    main(sys.argv[1])
