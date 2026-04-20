# C19 Grader Notes — CONFIDENTIAL (Release After Submission Deadline)

## Ground Truth: Validity Verdicts

| Argument | Validity | Form | Key Flaw/Feature |
|----------|----------|------|--------------------|
| Alpha | **Invalid** | Equivocation | "financial pressure" ≠ "duress" in legal sense; P2 doesn't satisfy P1's condition |
| Beta | **Invalid** | Correlation-causation fallacy | Correlation ≠ causation; confounding variable (hot weather drives both) |
| Gamma | **Valid** | Modus ponens | Valid given premises; *unsound* because P1 (utilitarian principle) is debatable |
| Delta | **Invalid** | Affirming the consequent | P1 says prime→odd, not odd→prime; counterexample: 51 = 3 × 17 (odd but not prime) |
| Epsilon | **Valid** | Modus tollens | Classic MT: P→Q, ¬Q, ∴ ¬P — formally valid, though may be unsound in practice |

## Expected Task 3 Strength Ratings
Reasonable ordering (weakest to strongest):
- Beta: 1-3 (correlation/causation is a serious logical error)
- Alpha: 2-4 (equivocation is subtle but still a clear error)
- Delta: 3-5 (valid-seeming but wrong form; 51's composite nature is non-obvious)
- Epsilon: 6-8 (valid MT form; potential unsoundness in P1 reduces from 10)
- Gamma: 7-9 (strongest form; valid modus ponens; deducting for P1's contestability)

## Task 4: Good Counterexamples
- **Alpha counterexample:** A worker who signed a contract while facing financial difficulties (e.g., high debt, unemployment risk) — the financial pressure is real, but it does not rise to the legal standard of "duress" (no coercion, threats, or unlawful pressure). Contract remains valid.
- **Beta counterexample:** Ice cream sales increase in a cold city during a winter festival. Murder rates stay flat or decrease. The correlation from hot-weather cities doesn't apply here — hot weather (the confound) is absent.
- **Delta counterexample:** 51 is odd (P2 is true), and all primes > 2 are odd (P1 is true), but 51 = 3 × 17, so 51 is NOT prime (C is false). This directly demonstrates the form's invalidity.

## Nuances to Reward in Manual Scoring

### High-value insights:
1. **Alpha**: The best agents will note this is *equivocation* specifically, not merely a non sequitur. "Financial pressure" and "duress" share connotations but differ legally and morally.
2. **Beta**: Look for agents who name the *confounding variable* (heat/summer) rather than just saying "correlation ≠ causation."
3. **Gamma**: The key distinction is *valid* (P1+P2→C follows) vs *sound* (premises may be false). Strong agents will explicitly say "valid but unsound."
4. **Delta**: Great answers will note that 51 = 3 × 17 specifically (showing they tested it), not just say "odd numbers can be composite."
5. **Epsilon**: The sharpest agents will note it's *valid* but potentially *unsound* because P1 assumes cameras have no blind spots, don't malfunction, and have full coverage — a real empirical assumption that may fail.

### Penalties:
- Task 4: Constructing a counterexample for Gamma or Epsilon (valid arguments) should be penalized
- Task 3: Ratings that rank invalid arguments above valid ones without compelling justification suggest confusion about validity vs. persuasiveness
- Task 2: Generic "correlation ≠ causation" for Beta without identifying the specific confound = partial credit only

