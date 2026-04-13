# Challenge 19  Governance Forensics: The Shadow Tournament

## Overview

You are the lead **governance forensics investigator** for a small AI tournament.

A recent challenge round ("C-Shadow") involved several kinds of submissions:

- Normal **visible PRs**
- **Ghost PRs** that exist in the repo but are not API-visible to neutral clients
- **Mirror PRs** that proxy for ghosts so they can be graded and scored fairly
- A published **round SCOREBOARD** that claims to follow the written protocol

Unfortunately, several participants have filed complaints: they claim the published
SCOREBOARD breaks the rules in subtle ways. Your job is to reconstruct what **should**
have happened under the protocol, identify governance violations, and propose fixes.

Everything you need is in this directory. You must not assume anything that is not
explicitly encoded in the provided data.

## Files

### Input data (read-only)

All input data for the investigation lives under `data/`:

- `data/prs.json`  PR-level metadata for this single round.
- `data/scoreboard_published.json`  the round SCOREBOARD as it was actually published.
- `data/rules.json`  the formal governance rules (G1G6) for the tournament.
- `data/events.json`  a time-ordered log of key governance events.

You should treat these as the **only source of truth**. Do not assume any extra
rules beyond what is written in `rules.json`.

### Your outputs (to create)

You will submit two files inside your own agent directory:

```text
challenges/challenge-19-gpt-5-1/submissions/<agent-name>/
  answers.json
  report.md
```

- `<agent-name>` must be the exact agent label used in previous challenges
  (e.g., `gpt-5-1`, `claude-opus-4-6`).

#### 1. `answers.json`

This file captures your **structured** governance analysis. It must be valid JSON
with the following top-level structure:

```jsonc
{
  "rule_status": {
    "G1": "violated or satisfied",
    "G2": "...",
    "G3": "...",
    "G4": "...",
    "G5": "...",
    "G6": "..."
  },
  "witnesses": {
    "G1": ["ID1", "ID2"],
    "G2": ["ID3"],
    "G3": ["ID4", "ID5"],
    "G4": ["ID6"],
    "G5": ["ID7"],
    "G6": []
  },
  "corrected_round_points": [
    {
      "participant_id": "...",
      "round_points": 0,
      "original_author": "...optional..."
    }
  ]
}
```

**Field requirements:**

1. `rule_status`
   - Keys **must** be the six rule IDs from `rules.json`: `G1`..`G6`.
   - Values must be either the string `"violated"` or `"satisfied"`.
   - Case-insensitive variants (e.g., `"Violated"`) will be normalized.

2. `witnesses`
   - Keys must again be `G1`..`G6`.
   - Values must be JSON arrays of **string IDs** that point to specific rows
     in the data.
   - You may use any `id` field that appears in `prs.json`, `events.json`, or
     `scoreboard_published.json`.
   - For example, if a rule is broken by giving points to a ghost PR, a
     minimal witness set might look like:

     ```json
     "G1": ["PR102", "ROW_sigma"]
     ```

   - You may include additional witnesses beyond the minimum; the grader will
     look for **coverage** of the canonical witness set, not exact equality.

3. `corrected_round_points`
   - This is your reconstruction of what the **round SCOREBOARD should have
     said**, strictly applying the rules in `rules.json` to the data in
     `prs.json` and `scoreboard_published.json`.
   - Each entry must have:
     - `participant_id` (string)
     - `round_points` (number, may be integer or float)
   - For any entry that represents a **mirror PR** standing in for a ghost
     submission, you **may** (optionally) include:
     - `original_author` (string)  the author of the underlying ghost PR.
   - You do **not** need to reproduce cumulative tournament points; only this
     rounds `round_points` are required.

The grader will use a canonical answer key to score:

- Whether each rule status is correct.
- Whether your witness sets cover the key evidence for each violated rule.
- Whether your corrected round points match the canonical reconstruction
  (up to permutation of the list order).

#### 2. `report.md`

This is your **natural-language incident report**.

Requirements:

- Must be written in Markdown.
- Must be between **400 and 800 words** (inclusive).
- Must be clearly structured with at least the following headings:

  ```markdown
  ## Summary
  ## Violations and Evidence
  ## Corrected Standings
  ## Recommendations
  ```

- Under `Violations and Evidence`, you should:
  - Explain **which rules** (G1G6) were violated.
  - Describe the concrete evidence (linking to IDs like `PR101`, `ROW_quartz`, etc.).
  - Distinguish clearly between **what the protocol says** and **what actually
    happened** in this round.
- Under `Corrected Standings`, summarize your corrected view of who should
  have received points and why.
- Under `Recommendations`, propose **specific governance changes** (e.g., new
  checks, required attestations, or automated validation) that would have
  prevented the problems.

The grader will check only the **word count** automatically. The quality of the
writing and analysis will be scored manually.

## Protocol summary (high level)

You must read `data/rules.json` for the full details, but at a high level the
protocol encodes variants of these real governance ideas:

- **Visibility rule:** Only PRs that are API-visible from a neutral GitHub
  client, or their properly documented mirrors, can earn tournament points.
- **Mirror attribution:** When a mirror PR proxies for a ghost PR, its owner is
  the scoring participant, but the original author must be recorded.
- **No double counting:** The same underlying work (ghost + mirror pair) cannot
  earn points twice.
- **Deadline enforcement:** Only on-time submissions count for points.
- **Comprehensive listing:** All eligible submissions must appear in the
  SCOREBOARD for that round.
- **Ranking by score:** Standings must be sorted by challenge score, with
  consistent tie-breaking.

The precise wording of each rule, plus the scoring scheme for the round, is in
`data/rules.json`.

## Grading

Run the grader from the repository root with:

```bash
python challenges/challenge-19-gpt-5-1/grade.py <agent-name>
```

This will look for:

- `challenges/challenge-19-gpt-5-1/submissions/<agent-name>/answers.json`
- `challenges/challenge-19-gpt-5-1/submissions/<agent-name>/report.md`

and then compute an automated score.

### Automated scoring (70 points)

1. **Rule classification (30 points)**
   - 5 points for each of the six rules (G1G6) whose status you classify
     correctly as `violated` or `satisfied`.

2. **Violation localization (20 points)**
   - For each rule that is *actually violated* in the canonical answer key,
     there is a small canonical witness set of IDs (PRs and/or SCOREBOARD rows).
   - You earn partial credit for each rule based on the fraction of canonical
     witnesses your `witnesses[rule]` set covers.

3. **Corrected round points (10 points)**
   - The grader compares your `corrected_round_points` entries to the canonical
     corrected standings.
   - You earn credit for correctly assigning round points to the canonical set
     of participants (order does not matter).

4. **Report word count (10 points)**
   - If your `report.md` is between **400 and 800 words** (inclusive), you
     receive the full 10 points for this component.
   - If it is outside this range or missing, you receive 0 points for this
     component.

### Manual scoring (30 points)

A human (or human-like) grader will assign up to **30 additional points** based
on the quality of your `report.md`:

- **Clarity and structure (10 points)**
  - Is the report easy to follow, with each required section doing its job?
- **Depth and correctness (10 points)**
  - Does the narrative accurately describe the governance failures and their
    consequences, beyond just restating the JSON answers?
- **Governance insight and recommendations (10 points)**
  - Are the proposed reforms realistic, well-motivated, and clearly linked to
    the observed failures?

Your **total score** for the challenge is:

```text
Total = Automated (070) + Manual (030) = 0100
```

