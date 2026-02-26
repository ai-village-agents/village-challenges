#!/usr/bin/env python3
import importlib.util
import os
import sys
from typing import Any, Callable, List, Tuple


FUNCTION_NAMES = [
    "binary_search",
    "count_vowels",
    "rotate_list",
    "is_prime",
    "longest_common_subsequence",
    "valid_parentheses",
    "merge_sorted_lists",
    "fibonacci",
    "matrix_transpose",
    "run_length_encode",
]


def load_submission(path: str):
    submission_path = os.path.abspath(path)
    submission_dir = os.path.dirname(submission_path)
    sys.path.insert(0, submission_dir)

    spec = importlib.util.spec_from_file_location("submission", submission_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec from {submission_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_test_cases(
    fn: Callable[..., Any],
    cases: List[Tuple[Tuple[Any, ...], Any]],
) -> Tuple[bool, str]:
    for args, expected in cases:
        try:
            result = fn(*args)
        except Exception as exc:
            return False, f"exception on args={args}: {exc}"
        if result != expected:
            return False, f"args={args} expected={expected} got={result}"
    return True, ""


def main():
    submission_arg = sys.argv[1] if len(sys.argv) > 1 else "submission.py"

    try:
        submission = load_submission(submission_arg)
    except Exception as exc:
        print(f"IMPORT FAIL: {exc}")
        print("Final score: 0/100")
        return

    tests = {
        "binary_search": [
            (([1, 3, 5, 7, 9], 5), 2),
            (([1, 3, 5, 7, 9], 9), 4),
            (([1, 3, 5, 7, 9], 1), 0),
            (([], 1), -1),
            (([1], 1), 0),
            (([1, 3, 5], 4), -1),
        ],
        "count_vowels": [
            (("Hello World",), 3),
            (("AEIOU",), 5),
            (("xyz",), 0),
            (("aAbBcC",), 2),
            (("",), 0),
        ],
        "rotate_list": [
            (([1, 2, 3, 4, 5], 2), [4, 5, 1, 2, 3]),
            (([1, 2, 3], 1), [3, 1, 2]),
            (([1, 2, 3, 4], 4), [1, 2, 3, 4]),
            (([1], 5), [1]),
            (([], 3), []),
        ],
        "is_prime": [
            ((0,), False),
            ((1,), False),
            ((2,), True),
            ((17,), True),
            ((4,), False),
            ((97,), True),
        ],
        "longest_common_subsequence": [
            (("abcde", "ace"), 3),
            (("abc", "abc"), 3),
            (("abc", "def"), 0),
            (("", "abc"), 0),
            (("abcbdab", "bdcaba"), 4),
            (("aaaa", "aa"), 2),
        ],
        "valid_parentheses": [
            (("()[]{}",), True),
            (("([)]",), False),
            (("{[]}",), True),
            (("]",), False),
            (("",), True),
            (("(((",), False),
        ],
        "merge_sorted_lists": [
            (([1, 3, 5], [2, 4, 6]), [1, 2, 3, 4, 5, 6]),
            (([1], [2]), [1, 2]),
            (([], [1, 2, 3]), [1, 2, 3]),
            (([1, 2, 3], []), [1, 2, 3]),
            (([0, 2, 2], [1, 3]), [0, 1, 2, 2, 3]),
        ],
        "fibonacci": [
            ((0,), 0),
            ((1,), 1),
            ((2,), 1),
            ((5,), 5),
            ((6,), 8),
            ((10,), 55),
        ],
        "matrix_transpose": [
            (([[1, 2, 3], [4, 5, 6]],), [[1, 4], [2, 5], [3, 6]]),
            (([[1, 2], [3, 4]],), [[1, 3], [2, 4]]),
            (([[1, 2, 3]],), [[1], [2], [3]]),
            (([],), []),
            (([[1]],), [[1]]),
        ],
        "run_length_encode": [
            (("aaabb",), "a3b2"),
            (("abc",), "a1b1c1"),
            (("",), ""),
            (("aaa",), "a3"),
            (("a",), "a1"),
        ],
    }

    score = 0
    for name in FUNCTION_NAMES:
        fn = getattr(submission, name, None)
        if fn is None:
            print(f"{name}: FAIL (missing function)")
            continue
        passed, detail = run_test_cases(fn, tests[name])
        if passed:
            print(f"{name}: PASS")
            score += 10
        else:
            print(f"{name}: FAIL ({detail})")

    print(f"Final score: {score}/100")


if __name__ == "__main__":
    main()
