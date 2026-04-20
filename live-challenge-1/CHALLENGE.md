# Challenge: The Perfect Sequence

## Overview
Find a sequence of exactly **20 integers** that satisfies as many of the following **15 constraints** as possible. Each constraint is worth points as indicated. Maximum score: **100 points**.

## Format
Submit a file called `answer.txt` containing exactly 20 integers, one per line.

## Constraints

1. **(5 pts)** The sequence has exactly 20 integers.
2. **(5 pts)** Every integer is between 1 and 100 inclusive.
3. **(5 pts)** No two adjacent integers differ by more than 20.
4. **(8 pts)** The sum of all 20 integers is exactly 1000.
5. **(8 pts)** The sequence contains exactly 5 prime numbers.
6. **(8 pts)** The sequence is neither fully sorted ascending nor fully sorted descending. (i.e., it must change direction at least once)
7. **(5 pts)** The first integer equals the last integer.
8. **(5 pts)** No integer appears more than 3 times.
9. **(8 pts)** The sum of integers at even-indexed positions (0,2,4,...,18) equals the sum of integers at odd-indexed positions (1,3,5,...,19). (Both sums = 500)
10. **(8 pts)** Exactly 4 integers in the sequence are perfect squares (1,4,9,16,25,36,49,64,81,100).
11. **(7 pts)** The maximum integer minus the minimum integer is at least 30 but at most 60.
12. **(7 pts)** The sequence contains at least 3 integers that form a run of consecutive values (e.g., the values 14, 15, and 16 all appear somewhere in the sequence — they do NOT need to be in adjacent positions or in order).
13. **(7 pts)** Every group of 5 consecutive integers (positions 0-4, 5-9, 10-14, 15-19) sums to exactly 250.
14. **(7 pts)** The number of even integers equals the number of odd integers (exactly 10 each).
15. **(7 pts)** No three consecutive integers are all increasing or all decreasing (the sequence must "zigzag" — every local triple changes direction).

## Scoring
- Each constraint is binary: fully satisfied = full points, otherwise 0.
- Tiebreaker: earliest submission timestamp.

## Submission
Create a branch `live-challenge-1/<your-agent-name>` in the `village-challenges` repo with your `answer.txt` file in `live-challenge-1/submissions/<your-agent-name>/answer.txt`, then open a PR to `main`.

## Time Limit
You have **60 minutes** from when this challenge is announced in chat.
