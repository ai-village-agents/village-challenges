# The Inference Engine — Reference Submission

*This is a reference submission demonstrating the expected quality and format for full marks. Written by Claude Sonnet 4.6 (challenge author) after the proposal was finalized.*

---

## Task 1: Formal Structure Analysis

Classify each argument's logical form, deliver a validity verdict, and explain the core reasoning flaw or feature.

### Alpha

**Form:** Equivocation (invalid syllogism via semantic ambiguity)

**Verdict:** Invalid

**Reason:** The argument exploits an equivocation on the term "financial pressure." Premise 1 states that contracts signed under *duress* are void — a legal term requiring coercion, threats, or wrongful pressure that overcomes free will. Premise 2 states that Alex signed under "financial pressure" — a psychological and economic state that may influence but does not legally constitute duress. The middle term shifts meaning between premises, so the conclusion does not follow. Financial desperation is not the same as legal duress; the argument's apparent validity collapses the moment the equivocation is exposed.

---

### Beta

**Form:** Correlation-causation fallacy (post hoc, ergo propter hoc variant)

**Verdict:** Invalid

**Reason:** The argument infers a causal relationship from a statistical correlation. Even if ice cream sales and murder rates genuinely co-vary, correlation alone does not establish causation. The argument ignores the possibility of a confounding variable — specifically, hot weather. High temperatures independently increase both ice cream consumption and outdoor activity (raising homicide opportunity and heat-related aggression). The observed correlation is a statistical artifact of this shared cause, not evidence of a causal mechanism between dessert and violence.

---

### Gamma

**Form:** Modus ponens

**Verdict:** Valid

**Reason:** The argument has the form: If P1 (the principle that saving more lives is always right) and P2 (one organ can save five lives), then C (we ought to harvest). This is a textbook modus ponens — the conclusion follows necessarily from the premises. The argument is *valid* (the logical form is impeccable), though it is likely *unsound* in the real world: Premise 1 is a strong utilitarian claim that many ethical frameworks reject, and the conclusion violates deontological constraints on treating persons as mere means. Validity and soundness are distinct — an argument can be one without the other.

---

### Delta

**Form:** Affirming the consequent (formal fallacy)

**Verdict:** Invalid

**Reason:** Premise 1 states that all primes greater than 2 are odd (P → Q). Premise 2 affirms the consequent: 51 is odd (Q). The conclusion claims 51 is prime (P). This is the classic fallacy of affirming the consequent: Q does not entail P, because Q may be true for other reasons. A decisive counterexample: 51 = 3 × 17. The number 51 satisfies the consequent (it is odd) but falsifies the conclusion (it is composite). The form P→Q, Q, ∴ P is always invalid regardless of content.

---

### Epsilon

**Form:** Modus tollens

**Verdict:** Valid

**Reason:** Premise 1 states that if the suspect was at the scene, the cameras would have recorded them (P → Q). Premise 2 denies the consequent: cameras did not record the suspect (¬Q). Conclusion: the suspect was not at the scene (¬P). This is a valid modus tollens: P→Q, ¬Q ∴ ¬P. The argument form is logically impeccable. However, it may be *unsound* in practice: Premise 1 assumes cameras had full coverage, no blind spots, and were functioning correctly — empirical assumptions that may not hold.

---

## Task 2: Hidden Assumption Excavation

Identify the most critical hidden assumption in each of Alpha, Beta, and Delta.

### Alpha

**Assumption:** That "financial pressure" and legal "duress" are sufficiently similar concepts to be treated as interchangeable in the same legal argument.

**Why it matters:** The entire argument depends on this semantic bridge. If we distinguish the terms — as courts do — the conclusion evaporates immediately. The contract remains legally binding even if economically coercive, because duress requires a specific wrongful threat, not merely a difficult bargain. The hidden assumption is doing all the logical work while remaining invisible in the stated premises.

**Failure case:** A worker accepts a terrible job offer because rent is due and savings are depleted. Financial pressure is real and severe. But no employer threatened unlawful action; the choice, however constrained, was still freely made in the legal sense. The assumption fails, and the argument collapses.

### Beta

**Assumption:** That ice cream sales and murder rates are causally connected rather than jointly caused by a third variable — specifically, that no common external factor drives both phenomena simultaneously.

**Why it matters:** If we accept this hidden causal premise, the conclusion about banning ice cream appears to follow from the data. Reject it, and the entire empirical basis of the argument disappears. The assumption is invisible in the statistical claim "ice cream sales correlate with murders" — correlation statements do not assert causation, but the argument treats them as if they do.

**Failure case:** Imagine a cold northern city in December where ice cream sales spike (winter festival) but murder rates remain flat or decline. Hot weather — the actual confounding driver — is absent, and the assumed correlation vanishes entirely in a different context.

### Delta

**Assumption:** That the property of being odd is *sufficient* to identify primes, not merely *necessary* — in other words, that the set of odd numbers and the set of primes (>2) are the same set, rather than the primes being a strict subset of the odds.

**Why it matters:** The conditional "all primes > 2 are odd" establishes that oddness is a necessary condition for primality. The argument's hidden premise is that this relationship is bidirectional — that odd numbers are therefore prime. This converts a one-way implication into an equivalence without justification.

**Failure case:** 51 is odd, 9 is odd, 25 is odd, 35 is odd, 49 is odd — none are prime. Composite odd numbers are plentiful. The assumption treats a one-directional gate (prime → odd) as a two-directional equivalence (odd ↔ prime), which is straightforwardly false.

---

## Task 3: Strength Calibration

Rate each argument's logical strength (1–10) and rank from weakest to strongest.

**Alpha: 3/10**
A subtle but unambiguous equivocation. The argument *feels* compelling — financial pressure really does constrain choice — but collapses immediately on any rigorous terminological examination. The flaw is detectable by anyone who notices the semantic shift.

**Beta: 2/10**
Perhaps the most classically invalid argument in popular reasoning: correlation-causation. The argument provides no mechanism, no experimental evidence, and overlooks an obvious confounding variable (seasonal temperature). It is weak because its fallacy is widely recognized and easily exposed.

**Gamma: 9/10**
A textbook modus ponens. The logical form is flawless; no reasoning error exists. Strength is reduced slightly because Premise 1 (the utilitarian axiom) is a contestable philosophical claim — many frameworks reject it — so the argument may be unsound even though it is formally valid.

**Delta: 4/10**
Affirming the consequent is a formal fallacy, not merely a rhetorical sleight-of-hand. Unlike Alpha's semantic trick, Delta's flaw is visible in the logical structure alone without examining the content. Rating above Beta because the premises are true and the error is subtler to non-logicians.

**Epsilon: 8/10**
Valid modus tollens. The form is correct, the reasoning is tight, and the conclusion follows necessarily. Minor deductions because Premise 1 smuggles in an empirical assumption (cameras are complete and functional) that could fail in practice, potentially rendering the argument unsound despite its validity.

**Ranking (weakest to strongest):**

Beta: 2/10 < Alpha: 3/10 < Delta: 4/10 < Epsilon: 8/10 < Gamma: 9/10

**Strongest justification:** Gamma — formal validity with modus ponens is logically unimpeachable; strength is limited only by the debatability of the utilitarian premise, not by any error in reasoning.

**Weakest justification:** Beta — correlation-causation fallacy with an obvious confounding variable (seasonal temperature) and no causal mechanism proposed; universally recognized as among the most fundamental errors in empirical reasoning.

---

## Task 4: Counterexample Construction

Construct minimal counterexamples that directly refute the invalid arguments: Alpha, Beta, and Delta.

### Counterexample: Alpha

A skilled tradesperson signs a below-market contract because their savings have run out and a mortgage payment is due in two weeks. The financial pressure is genuine and acute — they had no good alternatives. However, the employer made no threats, issued no ultimatums beyond a take-it-or-leave-it offer, and broke no laws. No court would void this contract: financial hardship, however severe, does not constitute legal duress without an element of wrongful coercion. The contract stands, falsifying the argument's conclusion directly.

### Counterexample: Beta

A Scandinavian city runs a winter ice cream festival in January, dramatically increasing sales across two cold weeks. During the same period, murder rates decline seasonally as people spend less time outdoors. High ice cream sales coexist with low homicides. The proposed causal link — more ice cream → more murders — makes the wrong prediction. Without the confounding driver (heat), the correlation disappears entirely, exposing it as a seasonal artifact rather than a causal relationship.

### Counterexample: Delta

51 is odd (satisfying Premise 2 — the consequent). All prime numbers greater than 2 are indeed odd (Premise 1 is true). Yet 51 = 3 × 17: it factors into two smaller integers and is therefore composite, not prime. The conclusion "51 is prime" is false while both premises are true. A single true-premise, false-conclusion instance is sufficient to demonstrate invalidity. The argument's form — affirming the consequent — is refuted by this elementary arithmetic fact.

---

## Task 5: Synthesis

**Champion:** Gamma — the utilitarian organ harvesting argument.

Gamma stands as the strongest argument because it commits no logical error. Its modus ponens form — If P₁ and P₂, then C — is the gold standard of deductive validity, and the conclusion follows with the same necessity as mathematical proof. The argument does not equivocate, does not confuse correlation with causation, and does not affirm the consequent. Its only vulnerability is that Premise 1 asserts a contested utilitarian axiom that deontological frameworks reject. But this is an issue of soundness, not validity — and validity is the harder, purer achievement. An argument can be valid while unsound, as Gamma demonstrates.

**Deceiver:** Alpha — the duress contract argument.

Alpha is the most treacherous argument because it sounds immediately compelling. Financial pressure really does constrain choice; desperate circumstances really do limit freedom. The equivocation on "duress" is not invented — it exploits a genuine conceptual blurriness between economic coercion and legal coercion. A non-specialist reader may never detect the semantic slide from "financial pressure" to "duress" because the terms inhabit similar moral territory. Yet the legal distinction is precise: duress requires specific wrongful acts, not merely bad options.

**Principle:** Validity and soundness are distinct, and conflating them is the source of most reasoning errors in this collection.

An argument can be valid (its conclusion follows necessarily from its premises) while unsound (its premises are contestable). Gamma is valid but possibly unsound. Epsilon is valid but potentially unsound in practice. Alpha, Beta, and Delta are invalid — their conclusions do not follow from their premises regardless of whether those premises are true. Strong reasoning requires diagnosing both dimensions: first checking whether the form holds, then separately questioning whether the premises deserve acceptance.