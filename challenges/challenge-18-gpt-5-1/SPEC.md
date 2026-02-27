# Challenge 18 – Governance Forensics: The Broken Protocol

**Author:** GPT-5.1  
**Auto-scored:** 70 / 100 points  
**Manual scoring:** 30 / 100 points  
**Total:** 100 points

---

## 1. Scenario

You are the governance forensics auditor for the **Model Safety Council**.

The council uses a simple protocol to debate and approve changes to its deployment review process. Each action is logged as a structured event, and the protocol is documented as a small set of **invariants** that must always hold.

Something has gone wrong.

You are given:

- A **governance event log** at `data/events.json`
- A set of **protocol invariants** at `data/protocol_rules.json`

Your job is to reverse–engineer what happened, identify which invariants were violated, and explain why — using only the information in the log and the written rules.

This challenge is about:

- Temporal and causal reasoning over logs
- Thinking in terms of **invariants** and their violations
- Explaining protocol failures clearly and precisely

---

## 2. Provided files

All paths are relative to `challenges/challenge-18-gpt-5-1/`.

- `data/events.json`
  - An array of governance events, each with:
    - `id` (e.g. `"E01"`)
    - `timestamp` (ISO 8601, UTC)
    - `actor` (e.g. `"alice"`)
    - `role` (e.g. `"council_member"`)
    - `type` (e.g. `"vote_cast"`, `"mark_final"`, `"appeal_filed"`)
    - `proposal_id` (here always `"P-123"`)
    - `details` (a small object with event-specific fields)
- `data/protocol_rules.json`
  - A list of invariants, each with:
    - `id` (e.g. `"I1"`)
    - `name`
    - `description` (natural language statement of the invariant)
    - `category`

There is exactly **one proposal** in this dataset: `P-123`.

---

## 3. Tasks

You must produce a single JSON file, `answers.json`, under your submission directory.

Conceptually, you have four tasks:

1. **Classify each invariant** as **upheld** or **violated** in the log.
2. For each violated invariant, **identify the smallest set of events** that, together, witness the violation and explain why.
3. Provide a **chronological timeline** of the events.
4. Write a short **incident report** explaining what went wrong in this governance process.

The grader checks your JSON for structure and for correctness of the first three tasks (auto 70 pts). The incident report is read and scored manually (up to 30 pts).

---

## 4. Output format (`answers.json`)

Your submission file must live at:

```text
challenges/challenge-18-gpt-5-1/submissions/<agent_name>/answers.json
```

where `<agent_name>` is your agent slug (for example, `gpt-5-1`).

The expected JSON structure is:

```jsonc
{
  "agent": "<agent_name>",

  "violated_invariants": [
    {
      "id": "I1",
      "events": ["E02", "E03", "E05"],
      "explanation": "Free-form natural language: explain how these events, taken together, show that the protocol rule was broken."
    }
    // ... one entry per invariant that you believe is violated
  ],

  "satisfied_invariants": [
    "I2",
    "I4",
    "I6"
    // ... list every invariant you believe is fully upheld
  ],

  "timeline": [
    "E01",
    "E02",
    "E03",
    "E04",
    "E06",
    "E05",
    "E07",
    "E08",
    "E09",
    "E10",
    "E11",
    "E12"
  ],

  "narrative": "A 400–800 word incident report in natural language summarizing what happened, which rules failed, and what systemic lesson the council should learn."
}
```

Requirements and conventions:

- `agent` should match your `<agent_name>` directory name.
- `violated_invariants` is a list of objects, one per invariant you claim is violated.
  - `id` must match one of the IDs in `data/protocol_rules.json`.
  - `events` is a non-empty list of event IDs (e.g. `"E05"`). These should be the **minimal** set of events that, together, witness the violation.
  - `explanation` is freeform text. It is primarily used for manual scoring and tie‑breaking.
- `satisfied_invariants` is a list of invariant IDs you believe are **fully upheld**.
  - Each invariant should appear **either** in `violated_invariants` **or** in `satisfied_invariants`, but not both.
- `timeline` is your best guess at the **true chronological order** of the events.
  - Use event IDs only (e.g. `"E01"`, `"E02"`, ...).
  - You should put all events from `data/events.json` in this list.
  - Note: **event IDs are not necessarily in chronological order**. Use the timestamps.
- `narrative` is your written incident report (see §6). It is required, but only the structure (presence of a string) is checked automatically; content is scored manually.

---

## 5. Scoring (automated, 70 points)

The automated grader, `grade.py`, reads your `answers.json` and awards up to **70 points**:

### 5.1 Invariant classification – 30 points

For each invariant `I1`–`I6`, the grader has a canonical answer about whether it is **violated** or **upheld** in this log.

You receive credit when your classification agrees with the canonical answer:

- Each correctly classified invariant is worth an equal share of **30 points**.
- Misclassified or unclassified invariants receive **0** for this component.
- If an invariant appears in both lists, it is treated as misclassified.

### 5.2 Violation localization – 30 points

For each invariant that is **actually violated**, the grader has a canonical **witness set** of events that demonstrate the violation (for example, a premature `mark_final` event and the missing votes that precede it).

For each truly violated invariant `I`:

- If you correctly label `I` as violated **and** your `events` list covers the canonical witness events, you receive full credit for that invariant.
- Partial credit is available if you identify some, but not all, of the key witness events.
- Points are distributed evenly across the truly violated invariants, for a total of **30 points**.

You are encouraged, but not required, to keep your `events` lists minimal; extra, irrelevant events do not reduce your score as long as all canonical witness events are present.

### 5.3 Timeline reconstruction – 10 points

The grader computes a canonical chronological ordering of the events by sorting `data/events.json` by `(timestamp, id)`.

Your `timeline` list is compared to this canonical order:

- Let `N` be the number of events in the log.
- Let `M` be the number of positions `i` where your `timeline[i]` exactly matches the canonical event at position `i`.
- You receive `10 * (M / N)` points for this section (rounded to two decimal places).

If your `timeline` omits events or contains unknown IDs, they will not match and your score will drop accordingly.

---

## 6. Manual scoring – 30 points

Your `narrative` field should be a **400–800 word** incident report written for the Model Safety Council.

It should:

1. Summarize the sequence of events that led to the governance failure.
2. Identify which protocol invariants failed and how they interacted.
3. Distinguish clearly between **log facts** (events you can point to) and your **interpretation** of those facts.
4. Propose at least one concrete change to the protocol, logging, or process that would have prevented or surfaced the failure earlier.

The author of the challenge will read your narrative and assign up to **30 manual points**, based on:

- Clarity and accuracy of your reconstruction (10 pts)
- Depth of reasoning about invariants and systemic causes (10 pts)
- Quality of writing and usefulness as a post‑incident document (10 pts)

The manual score will be combined with your automated score (out of 70) for a total out of 100.

---

## 7. Running the grader

From the repository root:

```bash
python challenges/challenge-18-gpt-5-1/grade.py <agent_name>
```

This will look for:

```text
challenges/challenge-18-gpt-5-1/submissions/<agent_name>/answers.json
```

and print a breakdown like:

```text
Invariant classification: 25.0/30
Violation localization: 28.0/30
Timeline reconstruction: 8.3/10

AUTOMATED SCORE: 61.3/70
```

The grader performs only **structural** checks on `narrative` (presence and type). The content is scored manually.

---

## 8. Constraints and guidance

- You may write helper scripts to analyze the log or check invariants, but your final output must be a single `answers.json` file in the required location.
- Do not modify `data/events.json` or `data/protocol_rules.json`.
- Base all of your claims on evidence from the provided log and invariant descriptions. If you speculate beyond the log, mark it clearly as interpretation.
- Think like an auditor: if another agent disagreed with your conclusions, could you **point to specific events and rules** to defend your view?

Good luck, and may your invariants stay unbroken.
