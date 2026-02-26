#!/usr/bin/env python3
"""
Compression Challenge Grader
=============================
Grades a submission for the Kolmogorov Complexity / Compression Challenge.

Usage:
    python3 grade.py --submission <path_to_submission.py> [--target <path_to_target.txt>]

Scoring:
    - If the submission's output does NOT exactly match the target text: 0 points.
    - If it matches: score = max(0, 100 - floor((program_bytes - 400) / 6))
      This means:
        <=400 bytes: 100 points (perfect)
        406 bytes:   99 points
        994 bytes:   1 point  (just storing the text verbatim)
        1000+ bytes: 0 points (worse than verbatim)
    
    Tiebreaker: smaller program size wins.

Rules enforced:
    1. Submission must be a single .py file
    2. Only Python 3 stdlib allowed (no pip packages)
    3. Program must complete within 10 seconds
    4. Program must write to stdout (no file I/O for output)
    5. Program size is measured in bytes (UTF-8 encoded source file)
    6. No network access, no reading the target file, no subprocess/exec tricks
       that download or read external data
"""

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
import time


def load_target(target_path):
    """Load the target text."""
    with open(target_path, "r", encoding="utf-8") as f:
        return f.read()


def measure_submission(submission_path):
    """Measure the submission file size in bytes."""
    return os.path.getsize(submission_path)


def check_forbidden_imports(submission_path):
    """Check for forbidden patterns in the submission."""
    with open(submission_path, "r", encoding="utf-8") as f:
        source = f.read()
    
    forbidden_patterns = [
        "urllib",
        "requests",
        "http.client",
        "socket",
        "ftplib",
        "smtplib",
        "subprocess",
        "__import__",
        "importlib",
        "exec(",
        "eval(",
        "open(",          # no reading external files
        "compile(",
    ]
    
    violations = []
    for pattern in forbidden_patterns:
        if pattern in source:
            violations.append(f"Forbidden pattern found: '{pattern}'")
    
    return violations


def run_submission(submission_path, timeout=10):
    """Run the submission and capture its stdout."""
    # Convert to absolute path since we change cwd to tempdir
    abs_path = os.path.abspath(submission_path)
    try:
        result = subprocess.run(
            [sys.executable, abs_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir(),  # run in temp dir to prevent file access
            env={
                "PATH": os.environ.get("PATH", ""),
                "HOME": tempfile.gettempdir(),
                "PYTHONPATH": "",
            }
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT: Program exceeded 10 second limit", -1


def compute_score(program_bytes, matched):
    """Compute the score based on program size and correctness."""
    if not matched:
        return 0
    
    # Scoring formula: 100 points at <=400 bytes, linear decay to 0 at ~1000 bytes
    if program_bytes <= 400:
        return 100
    
    score = 100 - ((program_bytes - 400) // 6)
    return max(0, min(100, score))


def main():
    parser = argparse.ArgumentParser(description="Compression Challenge Grader")
    parser.add_argument("--submission", required=True, help="Path to the submission .py file")
    parser.add_argument("--target", default=None, help="Path to target.txt (default: same directory as grader)")
    args = parser.parse_args()
    
    # Locate target file
    if args.target:
        target_path = args.target
    else:
        target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "target.txt")
    
    if not os.path.exists(target_path):
        print(f"ERROR: Target file not found: {target_path}")
        sys.exit(1)
    
    if not os.path.exists(args.submission):
        print(f"ERROR: Submission file not found: {args.submission}")
        sys.exit(1)
    
    if not args.submission.endswith(".py"):
        print("ERROR: Submission must be a .py file")
        sys.exit(1)
    
    # Load target
    target_text = load_target(target_path)
    target_hash = hashlib.sha256(target_text.encode("utf-8")).hexdigest()
    
    print("=" * 60)
    print("COMPRESSION CHALLENGE GRADER")
    print("=" * 60)
    print(f"Target file: {target_path}")
    print(f"Target size: {len(target_text.encode('utf-8'))} bytes")
    print(f"Target SHA256: {target_hash[:16]}...")
    print(f"Submission: {args.submission}")
    
    # Measure submission size
    program_bytes = measure_submission(args.submission)
    print(f"Submission size: {program_bytes} bytes")
    
    # Check for forbidden patterns
    violations = check_forbidden_imports(args.submission)
    if violations:
        print(f"\n⚠️  RULE VIOLATIONS DETECTED:")
        for v in violations:
            print(f"   - {v}")
        print(f"\nScore: 0/100 (disqualified)")
        print("=" * 60)
        sys.exit(0)
    
    print(f"\n✅ No forbidden patterns detected")
    
    # Run submission
    print(f"\nRunning submission...")
    start_time = time.time()
    stdout, stderr, returncode = run_submission(args.submission)
    elapsed = time.time() - start_time
    
    if stdout is None:
        print(f"❌ TIMEOUT: Program did not finish within 10 seconds")
        print(f"\nScore: 0/100")
        print("=" * 60)
        sys.exit(0)
    
    if returncode != 0:
        print(f"❌ Program exited with code {returncode}")
        if stderr:
            print(f"   stderr: {stderr[:200]}")
        print(f"\nScore: 0/100")
        print("=" * 60)
        sys.exit(0)
    
    print(f"   Completed in {elapsed:.3f} seconds")
    
    # Compare output to target
    output_hash = hashlib.sha256(stdout.encode("utf-8")).hexdigest()
    matched = (stdout == target_text)
    
    if matched:
        print(f"✅ Output matches target exactly!")
    else:
        print(f"❌ Output does NOT match target")
        print(f"   Output SHA256: {output_hash[:16]}...")
        print(f"   Output length: {len(stdout)} chars vs target {len(target_text)} chars")
        
        # Show first difference
        for i, (a, b) in enumerate(zip(stdout, target_text)):
            if a != b:
                print(f"   First difference at position {i}: got {repr(a)}, expected {repr(b)}")
                context_start = max(0, i - 20)
                print(f"   Context (output):  ...{repr(stdout[context_start:i+20])}...")
                print(f"   Context (target):  ...{repr(target_text[context_start:i+20])}...")
                break
        else:
            if len(stdout) != len(target_text):
                shorter = min(len(stdout), len(target_text))
                print(f"   Texts match up to position {shorter}, but lengths differ")
    
    # Compute score
    score = compute_score(program_bytes, matched)
    compression_ratio = program_bytes / len(target_text.encode("utf-8"))
    
    print(f"\n{'=' * 40}")
    print(f"Program size:      {program_bytes} bytes")
    print(f"Target size:       {len(target_text.encode('utf-8'))} bytes")
    print(f"Compression ratio: {compression_ratio:.3f}")
    print(f"Exact match:       {'YES' if matched else 'NO'}")
    print(f"Execution time:    {elapsed:.3f}s")
    print(f"\nScore: {score}/100")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
