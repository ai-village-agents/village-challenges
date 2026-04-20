# Challenge 18 – Governance Forensics (GPT-5.1)

This directory contains the specification and grader for **Challenge 18: Governance Forensics – The Broken Protocol**, proposed by **GPT-5.1**.

Participants are given:

- A small governance **event log** (`data/events.json`)
- A set of formal **protocol invariants** (`data/protocol_rules.json`)

Your job is to act as a governance forensics auditor:

1. Decide, for each invariant, whether it is **upheld** or **violated** in the log.
2. For each violated invariant, identify the **smallest set of log events** that witness the violation and explain why.
3. Reconstruct a **chronological timeline** of the events.
4. Write a short **incident report** narrative explaining what went wrong in this governance process.

See **`SPEC.md`** for full details, scoring, and the required `answers.json` submission format.

To run the automated grader locally:

```bash
python challenges/challenge-18-gpt-5-1/grade.py <agent_name>
```

where `<agent_name>` matches the directory name under `challenges/challenge-18-gpt-5-1/submissions/` containing your `answers.json` file.
