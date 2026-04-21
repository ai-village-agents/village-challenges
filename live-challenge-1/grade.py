#!/usr/bin/env python3
"""Grader for 'The Perfect Sequence' challenge."""
import sys
import math

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def is_perfect_square(n):
    s = int(math.sqrt(n))
    return s * s == n

def grade(filepath):
    try:
        with open(filepath) as f:
            lines = [line.strip() for line in f if line.strip()]
        seq = [int(x) for x in lines]
    except Exception as e:
        print(f"ERROR: Could not parse file: {e}")
        return 0

    score = 0
    results = []

    # C1: Exactly 20 integers (5 pts)
    c1 = len(seq) == 20
    results.append(("C1: Exactly 20 integers", 5, c1))
    if c1:
        score += 5

    if len(seq) != 20:
        print("FATAL: Sequence must have exactly 20 integers. Remaining constraints not checked.")
        print(f"TOTAL SCORE: {score}/100")
        return score

    # C2: All between 1 and 100 (5 pts)
    c2 = all(1 <= x <= 100 for x in seq)
    results.append(("C2: All integers 1-100", 5, c2))
    if c2:
        score += 5

    # C3: No two adjacent differ by more than 20 (5 pts)
    c3 = all(abs(seq[i] - seq[i+1]) <= 20 for i in range(19))
    results.append(("C3: Adjacent diff <= 20", 5, c3))
    if c3:
        score += 5

    # C4: Sum = 1000 (8 pts)
    total = sum(seq)
    c4 = total == 1000
    results.append(("C4: Sum = 1000", 8, c4, f"(actual sum: {total})"))
    if c4:
        score += 8

    # C5: Exactly 5 primes (8 pts)
    prime_count = sum(1 for x in seq if is_prime(x))
    c5 = prime_count == 5
    results.append(("C5: Exactly 5 primes", 8, c5, f"(found {prime_count} primes)"))
    if c5:
        score += 8

    # C6: Not fully sorted (8 pts)
    asc = all(seq[i] <= seq[i+1] for i in range(19))
    desc = all(seq[i] >= seq[i+1] for i in range(19))
    c6 = not asc and not desc
    results.append(("C6: Not fully sorted", 8, c6))
    if c6:
        score += 8

    # C7: First = Last (5 pts)
    c7 = seq[0] == seq[-1]
    results.append(("C7: First = Last", 5, c7, f"(first={seq[0]}, last={seq[-1]})"))
    if c7:
        score += 5

    # C8: No integer appears > 3 times (5 pts)
    from collections import Counter
    counts = Counter(seq)
    c8 = all(v <= 3 for v in counts.values())
    results.append(("C8: No integer > 3 times", 5, c8))
    if c8:
        score += 5

    # C9: Even-index sum = Odd-index sum = 500 (8 pts)
    even_sum = sum(seq[i] for i in range(0, 20, 2))
    odd_sum = sum(seq[i] for i in range(1, 20, 2))
    c9 = even_sum == 500 and odd_sum == 500
    results.append(("C9: Even-idx sum = Odd-idx sum = 500", 8, c9, f"(even={even_sum}, odd={odd_sum})"))
    if c9:
        score += 8

    # C10: Exactly 4 perfect squares (8 pts)
    sq_count = sum(1 for x in seq if is_perfect_square(x))
    c10 = sq_count == 4
    results.append(("C10: Exactly 4 perfect squares", 8, c10, f"(found {sq_count})"))
    if c10:
        score += 8

    # C11: max - min in [30, 60] (7 pts)
    rng = max(seq) - min(seq)
    c11 = 30 <= rng <= 60
    results.append(("C11: Range 30-60", 7, c11, f"(range={rng})"))
    if c11:
        score += 7

    # C12: At least 3 consecutive integer values present (7 pts)
    # Check if any 3 consecutive integers (like n, n+1, n+2) all appear in the sequence
    vals = set(seq)
    c12 = False
    for v in vals:
        if (v + 1) in vals and (v + 2) in vals:
            c12 = True
            break
    results.append(("C12: 3 consecutive integer values present", 7, c12))
    if c12:
        score += 7

    # C13: Each group of 5 sums to 250 (7 pts)
    g1 = sum(seq[0:5])
    g2 = sum(seq[5:10])
    g3 = sum(seq[10:15])
    g4 = sum(seq[15:20])
    c13 = g1 == 250 and g2 == 250 and g3 == 250 and g4 == 250
    results.append(("C13: Groups of 5 sum to 250", 7, c13, f"(groups: {g1},{g2},{g3},{g4})"))
    if c13:
        score += 7

    # C14: 10 even, 10 odd (7 pts)
    even_count = sum(1 for x in seq if x % 2 == 0)
    odd_count = 20 - even_count
    c14 = even_count == 10 and odd_count == 10
    results.append(("C14: 10 even, 10 odd", 7, c14, f"(even={even_count}, odd={odd_count})"))
    if c14:
        score += 7

    # C15: Zigzag - no 3 consecutive all-increasing or all-decreasing (7 pts)
    c15 = True
    for i in range(18):
        if seq[i] < seq[i+1] < seq[i+2]:
            c15 = False
            break
        if seq[i] > seq[i+1] > seq[i+2]:
            c15 = False
            break
    results.append(("C15: Zigzag pattern", 7, c15))
    if c15:
        score += 7

    # Print results
    print("=" * 60)
    print("THE PERFECT SEQUENCE — GRADING RESULTS")
    print("=" * 60)
    print(f"Sequence: {seq}")
    print("-" * 60)
    for r in results:
        name, pts, passed = r[0], r[1], r[2]
        extra = r[3] if len(r) > 3 else ""
        status = f"PASS (+{pts})" if passed else f"FAIL (+0)"
        print(f"  {name}: {status} {extra}")
    print("-" * 60)
    print(f"TOTAL SCORE: {score}/100")
    return score

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 grade.py <answer.txt>")
        sys.exit(1)
    grade(sys.argv[1])
