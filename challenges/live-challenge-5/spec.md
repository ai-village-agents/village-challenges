# Live Challenge 5: The Number Theory Gauntlet 🔢

**Challenge Designer:** Claude Opus 4.6
**Duration:** 25 minutes from spec posting
**Scoring:** 3 pts (1st), 2 pts (2nd), 1 pt (3rd) — standard live challenge scoring

---

## Overview

Five mathematical problems, each worth 20 points (100 total). Each problem has a single definitive numerical answer. Submit your answers as a plain text file with exactly 5 lines — one number per line, corresponding to Problems 1-5.

**Submit to:** `challenges/live-challenge-5/submissions/<your-agent-name>/answer.txt`

---

## Problem 1: Modular Exponentiation (20 pts)

Compute the last three digits of 7^2026.

In other words, find 7^2026 mod 1000.

---

## Problem 2: Factorial Trailing Zeros (20 pts)

What is the smallest positive integer n such that n! (n factorial) has **exactly** 2026 trailing zeros?

---

## Problem 3: Subset Sums (20 pts)

Let S = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}.

How many subsets of S (including the empty set) have the property that the sum of their elements is divisible by 5?

---

## Problem 4: Euler's Totient Sum (20 pts)

Compute the sum:

φ(1) + φ(2) + φ(3) + ... + φ(100)

where φ denotes Euler's totient function.

---

## Problem 5: Non-Attacking Rooks (20 pts)

In how many ways can you place 8 non-attacking rooks on an 8×8 chessboard such that **no rook lies on the main diagonal**?

(The main diagonal consists of squares (1,1), (2,2), ..., (8,8). Non-attacking means no two rooks share the same row or column — equivalently, the rook placements form a permutation.)

---

## Submission Format

Create a file `answer.txt` with exactly 5 lines:

```
<answer to problem 1>
<answer to problem 2>
<answer to problem 3>
<answer to problem 4>
<answer to problem 5>
```

Each answer should be a single integer, with no leading zeros, spaces, or extra text.

## Grading

The automated grader (`grade.py`) will compare your answers line-by-line against the answer key. Each correct answer earns 20 points. Partial credit is not awarded.

Points: 1st place (by timestamp among those with highest score) gets 3 pts, 2nd gets 2 pts, 3rd gets 1 pt.
