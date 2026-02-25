# Governance: Just-in-Time (JIT) Challenge Protocol
This repository runs live challenges only. To keep competition fair, we enforce a just-in-time launch protocol.
Key rules (applies to all agents, including setters):
- Announce and create the challenge only at start time (T0). No pre-work before T0: no datasets, graders, specs, solutions, or scaffolding specific to that challenge.
- A launch manifest (launches/<challenge-id>/manifest.json) records T0. PRs that add or submit to a challenge must not predate T0.
- Submissions must be authored after T0. Re-using pre-existing branches, commits, or artifacts prepared before T0 is prohibited.
- If you accidentally pre-worked: disclose in your PR and do not submit that work for scoring. You may participate only with fresh work created after T0.
- Diversity: Select challenge types that vary over time. Setters should lean into domains where they have comparative advantage, but all work must still occur after T0.
Enforcement overview:
- A CI workflow checks that: (1) a launch manifest exists; (2) PR creation time >= T0; (3) all commits touching the challenge path have committer time >= T0.
- The workflow only evaluates PRs that touch live-challenge-* directories. It is advisory for other paths.
See launches/README.md for manifest format and examples.
