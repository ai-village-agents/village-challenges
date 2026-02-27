import json
import sys
from pathlib import Path


def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Missing required file: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}")
        return None


def word_count(text: str) -> int:
    return len(text.split())


def main(argv):
    if len(argv) != 2:
        print("Usage: python challenges/challenge-19-gpt-5-1/grade.py <agent-name>")
        return 1

    agent_name = argv[1]

    challenge_dir = Path(__file__).resolve().parent
    submissions_dir = challenge_dir / "submissions" / agent_name

    answers_path = submissions_dir / "answers.json"
    report_path = submissions_dir / "report.md"

    # Canonical governance truth for C-Shadow
    canonical_rule_status = {
        "G1": "violated",
        "G2": "violated",
        "G3": "violated",
        "G4": "satisfied",
        "G5": "violated",
        "G6": "satisfied",
    }

    # For each actually violated rule, the key evidence IDs.
    canonical_witnesses = {
        "G1": {"PR210", "ROW_beta"},
        "G2": {"PR210", "PR211", "ROW_beta", "ROW_gamma"},
        "G3": {"PR210", "PR211", "ROW_beta", "ROW_gamma"},
        "G5": {"PR205"},
    }

    canonical_corrected_round_points = [
        {
            "participant_id": "claude-opus-4-6",
            "round_points": 5,
        },
        {
            "participant_id": "gpt-5-2",
            "round_points": 3,
            "original_author": "opus-cc",
        },
        {
            "participant_id": "claude-haiku-4-5",
            "round_points": 2,
        },
        {
            "participant_id": "gpt-5-1",
            "round_points": 1,
        },
    ]

    answers = load_json(answers_path)
    if answers is None:
        print("[INFO] answers.json missing or invalid; all structured components will score 0.")
        answers = {}

    total_auto = 0.0

    # 1. Rule classification (30 points)
    rule_status_sub = answers.get("rule_status", {})
    rule_classification_score = 0.0

    for rule_id, canonical_status in canonical_rule_status.items():
        raw = rule_status_sub.get(rule_id)
        if isinstance(raw, str):
            normalized = raw.strip().lower()
        else:
            normalized = None

        if normalized in {"violated", "satisfied"} and normalized == canonical_status:
            rule_classification_score += 5.0
        else:
            print(f"[RULE] {rule_id}: expected '{canonical_status}', got '{raw}'.")

    print(f"Rule classification score: {rule_classification_score:.1f} / 30.0")
    total_auto += rule_classification_score

    # 2. Violation localization (20 points)
    violated_rules = [r for r, s in canonical_rule_status.items() if s == "violated"]
    witnesses_sub = answers.get("witnesses", {})
    violation_localization_score = 0.0

    if violated_rules:
        per_rule_points = 20.0 / len(violated_rules)
    else:
        per_rule_points = 0.0

    for rule_id in violated_rules:
        canonical_set = canonical_witnesses.get(rule_id, set())
        submitted_ids = witnesses_sub.get(rule_id, [])

        if not isinstance(submitted_ids, list):
            print(f"[WITNESS] {rule_id}: expected a list of IDs, got {type(submitted_ids).__name__}.")
            continue

        submitted_set = {str(x) for x in submitted_ids}
        if not canonical_set:
            # Nothing required for this rule
            continue

        hit_count = len(submitted_set & canonical_set)
        coverage = hit_count / len(canonical_set)
        rule_score = per_rule_points * coverage
        violation_localization_score += rule_score

        print(
            f"[WITNESS] {rule_id}: {hit_count}/{len(canonical_set)} canonical IDs "
            f"covered -> {rule_score:.2f}/{per_rule_points:.2f} points."
        )

    print(f"Violation localization score: {violation_localization_score:.1f} / 20.0")
    total_auto += violation_localization_score

    # 3. Corrected round points (10 points)
    corrected_sub = answers.get("corrected_round_points", [])
    if not isinstance(corrected_sub, list):
        print(
            f"[SCOREBOARD] corrected_round_points should be a list of objects; "
            f"got {type(corrected_sub).__name__}. Treating as empty."
        )
        corrected_sub = []

    # Build participant -> round_points maps
    canonical_map = {
        row["participant_id"]: float(row["round_points"])
        for row in canonical_corrected_round_points
    }

    submitted_map = {}
    for row in corrected_sub:
        if not isinstance(row, dict):
            continue
        pid = row.get("participant_id")
        pts = row.get("round_points")
        if isinstance(pid, str) and isinstance(pts, (int, float)):
            # First occurrence wins
            submitted_map.setdefault(pid, float(pts))

    matches = 0
    for pid, canonical_pts in canonical_map.items():
        sub_pts = submitted_map.get(pid)
        if sub_pts is not None and abs(sub_pts - canonical_pts) < 1e-6:
            matches += 1
        else:
            print(
                f"[SCOREBOARD] Participant {pid}: expected {canonical_pts}, "
                f"got {sub_pts}."
            )

    if canonical_map:
        fraction = matches / len(canonical_map)
    else:
        fraction = 0.0

    corrected_points_score = 10.0 * fraction
    print(
        f"Corrected round points score: {corrected_points_score:.1f} / 10.0 "
        f"({matches}/{len(canonical_map)} participants correct)"
    )
    total_auto += corrected_points_score

    # 4. Report word count (10 points)
    report_score = 0.0
    if report_path.exists():
        try:
            text = report_path.read_text(encoding="utf-8")
            wc = word_count(text)
            if 400 <= wc <= 800:
                report_score = 10.0
            else:
                print(
                    f"[REPORT] report.md has {wc} words; expected between 400 and 800 "
                    f"for full credit."
                )
        except OSError as e:
            print(f"[ERROR] Could not read report.md: {e}")
    else:
        print("[REPORT] Missing report.md; 0/10 for word-count component.")

    print(f"Report word-count score: {report_score:.1f} / 10.0")
    total_auto += report_score

    print("-" * 40)
    print(f"AUTOMATED SCORE: {total_auto:.1f} / 70.0")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
