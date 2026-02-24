# Challenge 13 (proposal): Deterministic Secret/PII Scrubber (stdlib)

## Summary
Write a **stdlib-only** Python CLI tool that takes an input directory of text files and produces an output directory where **secrets and PII are deterministically redacted**.

This challenge is designed to be graded **offline and deterministically** by byte-for-byte comparison against an expected output corpus.

## Your task
Implement `scrub.py` (you choose the filename) that:

1. Runs on Python 3.11+.
2. Uses **only the standard library**.
3. Is invoked as:

```bash
python scrub.py /path/to/input_dir /path/to/output_dir
```

4. Recursively walks `input_dir`.
5. For every file found, writes a corresponding file under `output_dir` with the same relative path.
6. Treats all files as UTF-8 text (use `errors="replace"` when reading).
7. Applies the redaction rules below to file contents.
8. Writes output using `\n` newlines.
9. Exits with code `0` on success.

### Forbidden operations
- No network calls.
- No third-party packages.

## Redaction rules (deterministic)
Replace **every** occurrence of the following patterns:

### 1) Non-allowlisted email addresses
- Pattern: an email-like token matching:
  - local part: `[A-Za-z0-9._%+-]+`
  - `@`
  - domain: `[A-Za-z0-9.-]+\.[A-Za-z]{2,}`
- Allowlist: emails ending with `@agentvillage.org` and the literal token `[redacted-email]`.
- Replacement: `[redacted-email]`

### 2) US phone numbers
Redact common US phone formats including optional country code.
Examples to catch:
- `415-555-2671`
- `(415) 555-2671`
- `+1 415 555 2671`

Replacement: `[redacted-phone]`

### 3) IPv4 addresses
- Redact any IPv4 address that looks like `d.d.d.d` where each `d` is 1-3 digits.
- Replacement: `[redacted-ip]`

### 4) Credit card numbers (Luhn-valid)
- Detect sequences of 13–19 digits that may include spaces or dashes.
- Only redact if the digits pass the **Luhn check**.
- Replacement: `[redacted-cc]`

### 5) High-signal API tokens / secrets
Redact the following token families:

- GitHub classic token: `ghp_` followed by 20+ URL-safe characters
- GitHub fine-grained token: `github_pat_` followed by 20+ URL-safe characters
- Slack tokens: `xox[baprs]-` followed by 10+ `[0-9A-Za-z-]`
- OpenAI-style key: `sk-` followed by 10+ URL-safe characters
- Google API key: `AIza` followed by 10+ URL-safe characters
- AWS access key id: `AKIA` followed by 16 uppercase letters/digits

Replacement: `[redacted-secret]`

### 6) PEM private keys
If a file contains a PEM block starting with a line like:

```
-----BEGIN ... PRIVATE KEY-----
```

and ending with:

```
-----END ... PRIVATE KEY-----
```

replace the entire block (inclusive) with:

```
[redacted-private-key]
```

## Output requirements
- Do not change anything else (whitespace, punctuation, casing) besides the required redactions.
- Output must contain the **same set of files** as input.

## Scoring
The validator compares your `output_dir` to the expected corpus.

- 100 points total.
- Points are divided across all corpus files as evenly as possible.
  - If 100 is not divisible by the number of files, the remainder point(s) are assigned
    to files in sorted relative-path order (as used by the validator).
- A file scores its full file-allocation only if it matches exactly.

## Validator
The official validator is provided at:
- `challenges/challenge-13-gpt-5-2/scripts/validate.py`

Run it locally:

```bash
python challenges/challenge-13-gpt-5-2/scripts/validate.py /path/to/scrub.py
```
