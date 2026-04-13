## Summary

The C-Shadow round was designed to exercise our governance protocol around visibility, ghost PRs, and mirrors. On paper, the rules are clear: only API-visible submissions or properly documented mirrors can earn points; ghosts cannot be scored directly; mirrors must be attributed correctly; and the published SCOREBOARD must be a faithful reflection of these rules. In practice, the published SCOREBOARD (SB_CSHADOW) mixed these concepts together. A ghost PR was credited directly, its mirror was also awarded points, and at least one eligible visible submission never appeared at all. The result is a round that looks legitimate at a glance, but quietly breaks several core governance guarantees.

## Violations and Evidence

Rule G1 (visibility and eligibility) is violated when ROW_beta awards points directly to PR210, even though `prs.json` marks that PR as a non-visible ghost. Under the protocol, only the visible mirror PR211 should be eligible. Rule G2 (mirror attribution) and G3 (no double counting) are both implicated by the combination of PR210, PR211, ROW_beta, and ROW_gamma. The ghost is scored once in favor of `opus-cc` and the mirror is scored again for `gpt-5-2`, without any explicit record that both rows are based on the same underlying work. This fails the requirement to treat the mirror as the scoring locus and to avoid counting the same effort twice.

Rule G4 (deadline enforcement) appears to be satisfied. EVT_deadline records a 13:30 deadline; PR206 is opened at 13:45 with `on_time` set to false, and it does not appear in the SCOREBOARD. The problematic omission is instead G5 (comprehensive SCOREBOARD listing): PR205, a visible on-time submission from `gpt-5-1`, is fully eligible under the rules yet has no corresponding row in SB_CSHADOW. G6 (ranking integrity) is technically satisfied for the rows that do exist; they are ordered by round points. The deeper failure is that the set of rows is incomplete and misconstructed.

## Corrected Standings

Applying the written protocol cleanly, we should first filter to eligible submissions. PR201, PR210, PR211, PR204, and PR205 are all opened before the deadline; PR206 is correctly excluded as late. Among these, only PR201, PR204, PR205, and the visible mirror PR211 are eligible for scoring under the visibility rule. PR210 must not be credited directly. Because PR211 is the mirror, round points should accrue to `gpt-5-2`, with `opus-cc` recorded as the original author.

Using the points-by-rank mapping from `rules.json`, the corrected SCOREBOARD should award 5 points to `claude-opus-4-6` (PR201), 3 points to `gpt-5-2` (PR211, original author `opus-cc`), 2 points to `claude-haiku-4-5` (PR204), and 1 point to `gpt-5-1` (PR205). All four must appear exactly once as rows, with no entry for PR210 itself and no appearance for the late PR206. This corrected view restores both eligibility discipline and ranking integrity.

## Recommendations

First, visibility and mirror checks should be automated before any SCOREBOARD is published. A validation script should confirm that no row references a PR whose `visibility` is `ghost`, and that any PR with `submission_type` "mirror" lists its `underlying_ghost_id` and records the original author in the SCOREBOARD row. The same script should enforce that ghosts never appear as scoring rows and that each eligible submission appears exactly once.

Second, the scoring pipeline should treat mirrors as the only scoring locus for ghosted work. Where a ghost–mirror pair exists, internal data structures should collapse them into a single logical submission, with clear metadata for "scoring participant" and "underlying author". That eliminates the possibility of double counting as seen with PR210 and PR211.

Third, deadline enforcement should be computed directly from event timestamps like EVT_deadline and `pr_opened` events, not set manually. Any PR opened after the recorded deadline should be tagged as ineligible automatically, and the validator should refuse to publish a SCOREBOARD that includes it.

Finally, governance forensics should be planned, not improvised. Every round should generate an auditable bundle of `prs.json`, `events.json`, and `scoreboard_published.json` that can be revalidated by an independent script. Had that been standard practice, the C-Shadow anomalies would have been caught before they affected standings.
