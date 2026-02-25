# Challenge 12 Verification Notes

## Question 9: Commits modifying docs/events.json

- **Standard Count (`git log`):** 69
- **Follow Count (`git log --follow`):** 71
- **Discrepancy Cause:** File renames/moves.
- **Action:** If the question does not specify 'including renames', 69 is the literal answer for the file at its current path. If it asks for history of the *content*, 71 is correct.

## Question: Merge Commits
- **`git log --merges`:** 13 (Actual merge objects)
- **`git log --grep='Merge'`:** 19 (Includes squash/edit commits with 'Merge' in title)
5
