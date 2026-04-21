#!/usr/bin/env python3
"""Automated grader for Challenge 19: The Audit Alchemist.

Score is 0-100 based on average F1 match between extracted events and ground truth.

Notes:
- Deterministic: uses a fixed RNG seed.
- Robust to invocation location: resolves submission paths relative to this file.
"""

from __future__ import annotations

import importlib.util
import os
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone

ACTIONS = ["READ", "WRITE", "DELETE", "LOGIN", "LOGOUT", "EXPORT"]
RESULTS = ["OK", "DENY"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass(frozen=True)
class Event:
    ts: str
    actor: str
    action: str
    resource: str
    result: str
    req: str


ISO = "%Y-%m-%dT%H:%M:%SZ"


def norm_ts(raw: str) -> str:
    s = str(raw).strip().strip("[](){}")

    # already canonical
    try:
        dt = datetime.strptime(s, ISO).replace(tzinfo=timezone.utc)
        return dt.strftime(ISO)
    except Exception:
        pass

    fmts = [
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",  # treated as UTC
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
            return dt.strftime(ISO)
        except Exception:
            continue

    # bracketed human: [2026-02-27 20:01:00 UTC]
    m = re.search(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})", s)
    if m:
        dt = datetime.strptime(
            m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)
        return dt.strftime(ISO)

    raise ValueError(f"Unrecognized timestamp: {raw!r}")


def render_event(rng: random.Random, ev: Event) -> str:
    fmt = rng.choice(["json", "kv", "human", "csv"])
    if fmt == "json":
        # manual to keep it simple (no json import needed)
        return (
            '{"ts":"%s","actor":"%s","action":"%s","resource":"%s","result":"%s","req":"%s"}'
            % (
                ev.ts,
                ev.actor,
                ev.action,
                ev.resource.replace('"', '\\"'),
                ev.result,
                ev.req,
            )
        )
    if fmt == "kv":
        parts = [
            f"actor={ev.actor}",
            f"result={ev.result}",
            f"action={ev.action}",
            f"req={ev.req}",
            f"ts={rng.choice([ev.ts, ev.ts.replace('T',' ').replace('Z',''), ev.ts.replace('-','/').replace('T',' ').replace('Z','')])}",
            f"resource=\"{ev.resource}\"",
        ]
        rng.shuffle(parts)
        return " ".join(parts)
    if fmt == "human":
        ts_h = rng.choice(
            [
                f"[{ev.ts}]",
                f"[{ev.ts.replace('T',' ').replace('Z','')} UTC]",
            ]
        )
        return (
            f"{ts_h} actor={ev.actor} performed {ev.action} on {ev.resource}"
            f" -> {ev.result} (req: {ev.req})"
        )
    # csv
    ts_c = rng.choice(
        [
            ev.ts,
            ev.ts.replace("T", " ").replace("Z", ""),
        ]
    )
    return f"{ts_c},{ev.actor},{ev.action},{ev.resource},{ev.result},{ev.req}"


def make_case(rng: random.Random, n_events: int) -> tuple[str, set[Event]]:
    base = datetime(2026, 2, 27, 20, 0, 0, tzinfo=timezone.utc)
    actors = [
        "alice@example.com",
        "bob@example.com",
        "carol",
        "dave.sre",
        "erin@hospital.org",
    ]
    resources = [
        "patient/123/labs",
        "patient/999 imaging",
        "billing/export 2026-02",
        "auth/session",
        "records/archive/A",
    ]

    truth: set[Event] = set()
    lines: list[str] = []
    for i in range(n_events):
        dt = base.replace(second=(i % 60), minute=(i // 60))
        ts = dt.strftime(ISO)
        ev = Event(
            ts=ts,
            actor=rng.choice(actors),
            action=rng.choice(ACTIONS),
            resource=rng.choice(resources),
            result=rng.choice(RESULTS),
            req=f"r-{rng.randint(1000,9999)}",
        )
        truth.add(ev)
        lines.append(render_event(rng, ev))

        # noise lines
        if rng.random() < 0.35:
            lines.append(
                rng.choice(
                    [
                        "--- rotate log ---",
                        "# heartbeat ok",
                        "WARNING: transient network error",
                        "{}",
                        "garbage line without fields",
                    ]
                )
            )

    rng.shuffle(lines)
    return "\n".join(lines) + "\n", truth


def load_submission(agent_name: str):
    path = os.path.join(SCRIPT_DIR, "submissions", agent_name, "submission.py")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location("submission", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load submission")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "parse_audit_log"):
        raise AttributeError(
            "submission.py must define parse_audit_log(text: str) -> list[dict]"
        )
    return mod.parse_audit_log


def canon_from_dict(d: dict) -> Event:
    # tolerate extra keys by ignoring them; but require required keys
    for k in ["ts", "actor", "action", "resource", "result", "req"]:
        if k not in d:
            raise KeyError(k)
    return Event(
        ts=norm_ts(d["ts"]),
        actor=str(d["actor"]),
        action=str(d["action"]),
        resource=str(d["resource"]),
        result=str(d["result"]),
        req=str(d["req"]),
    )


def f1_score(pred: set[Event], truth: set[Event]) -> float:
    if not pred and not truth:
        return 1.0
    if not pred or not truth:
        return 0.0
    tp = len(pred & truth)
    prec = tp / max(1, len(pred))
    rec = tp / max(1, len(truth))
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python grade.py <agent_name>")
        return 2
    agent = sys.argv[1]
    parse = load_submission(agent)

    rng = random.Random(19)
    f1s: list[float] = []

    for case_idx in range(30):
        text, truth = make_case(rng, n_events=rng.randint(12, 22))
        try:
            out = parse(text)
            if not isinstance(out, list):
                raise TypeError("parse_audit_log must return a list[dict]")
            pred = set(canon_from_dict(x) for x in out)
            f1s.append(f1_score(pred, truth))
        except Exception as e:
            # Partial credit: a single crash shouldn't necessarily zero out the whole run.
            print(f"Case {case_idx}: ERROR: {e}")
            f1s.append(0.0)

    avg_f1 = sum(f1s) / len(f1s)
    score = int(round(100 * avg_f1))
    print(f"Average F1: {avg_f1:.4f}")
    print(f"AUTOMATED SCORE: {score}/100")
    return score


if __name__ == "__main__":
    raise SystemExit(main())
