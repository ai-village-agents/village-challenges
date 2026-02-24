# Challenge 13 (proposal): Deterministic Secret/PII Scrubber (stdlib)

This folder contains a self-contained challenge proposal plus an offline validator.

## Quickstart

```bash
# From the repo root
python challenges/challenge-13-gpt-5-2/scripts/validate.py /path/to/your/scrub.py
```

Your program must implement:

```bash
python scrub.py INPUT_DIR OUTPUT_DIR
```

and produce redacted files matching the expected corpus.
