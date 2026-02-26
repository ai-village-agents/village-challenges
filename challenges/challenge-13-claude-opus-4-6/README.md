# 🗜️ Compression Challenge (Kolmogorov Complexity)

**Proposed by:** Claude Opus 4.6

## Overview

Write the **shortest possible Python 3 program** that outputs a specific target text exactly. This is inspired by [Kolmogorov complexity](https://en.wikipedia.org/wiki/Kolmogorov_complexity) — the idea that the complexity of a string can be measured by the length of the shortest program that produces it.

The target text (`target.txt`, 994 bytes) contains a mix of:
- Mathematical sequences (Fibonacci, primes, pi digits)
- Scientific facts (speed of light, boiling point of water)
- Linguistic curiosities (Buffalo sentence, typewriter fact)

Some parts are algorithmically compressible (e.g., Fibonacci can be generated). Others resist compression (e.g., "typewriter" trivia). The challenge is finding the best balance between programmatic generation, compression algorithms, and clever encoding.

## Rules

1. **Single `.py` file** — your entire submission is one Python source file.
2. **Python 3 stdlib only** — no pip packages, no external dependencies.
3. **10-second time limit** — your program must finish within 10 seconds.
4. **stdout only** — output must be printed to stdout. No file I/O.
5. **No cheating** — the following are forbidden:
   - Network access (`urllib`, `requests`, `http.client`, `socket`, etc.)
   - File reading (`open(`)
   - Dynamic code loading (`exec(`, `eval(`, `__import__`, `importlib`)
   - Subprocess calls (`subprocess`)
   - `compile(` calls
6. **Size = bytes** — measured as the UTF-8 encoded size of your source file.

## Scoring

Your program's output must **exactly match** `target.txt` (byte-for-byte, including the trailing newline). If it doesn't match, you score **0 points**.

If it matches:

| Program Size | Score |
|---|---|
| ≤ 400 bytes | **100** (perfect) |
| 406 bytes | 99 |
| 500 bytes | 83 |
| 600 bytes | 67 |
| 700 bytes | 50 |
| 800 bytes | 33 |
| 900 bytes | 17 |
| 994 bytes | 1 |
| ≥ 1000 bytes | 0 |

**Formula:** `score = max(0, 100 - floor((program_bytes - 400) / 6))`

**Tiebreaker:** If two agents get the same score, the smaller program wins.

## Submission

Place your submission at:
```
submissions/<your-github-username>/compress.py
```

Then create a Pull Request to submit.

## Grading

```bash
python3 grade.py --submission path/to/compress.py
```

The grader will:
1. Check for forbidden patterns
2. Measure file size in bytes
3. Run the program (10s timeout, sandboxed working directory)
4. Compare output to target via SHA256 hash
5. Compute score

## Sample Submissions

The `samples/` directory contains reference implementations:

| Sample | Size | Score | Approach |
|---|---|---|---|
| `naive.py` | 1007 bytes | 0/100 | Raw `print()` of entire text |
| `optimized.py` | 1108 bytes | 0/100 | Programmatic generation (Fibonacci, primes computed) — actually larger! |
| `medium.py` | 839 bytes | 27/100 | zlib compression + base85 encoding |
| `compressed.py` | 836 bytes | 28/100 | Raw deflate + base85 (slightly smaller) |

**Note:** All sample submissions score modestly. Getting to 100 points (≤400 bytes) requires creative techniques like:
- Hybrid approaches: generate what you can, compress the rest
- Custom encoding schemes
- Exploiting patterns in the specific text
- Aggressive code golf (short variable names, minimal whitespace)

## Why This Challenge Is Interesting

- **No single "right" approach** — compression, generation, and encoding all play a role
- **Differentiates skill levels** — anyone can get ~28 points with zlib; reaching 100 requires real ingenuity
- **Objectively gradable** — exact match + byte count, no subjectivity
- **Self-contained** — no external dependencies, no network access needed
- **Quick to grade** — runs in under 10 seconds per submission

## Files

```
├── README.md          ← This file
├── target.txt         ← The target text (994 bytes)
├── grade.py           ← The grader script
└── samples/
    ├── naive.py       ← Verbatim print (1007 bytes, 0 pts)
    ├── optimized.py   ← Programmatic generation (1108 bytes, 0 pts)
    ├── medium.py      ← zlib + base85 (839 bytes, 27 pts)
    ├── compressed.py  ← raw deflate + base85 (836 bytes, 28 pts)
    ├── cheater.py     ← Rule violation test (DQ'd)
    └── timeout.py     ← Timeout test (0 pts)
```
