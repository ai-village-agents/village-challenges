import json
import re
from datetime import datetime, timezone

ACTIONS = {"READ", "WRITE", "DELETE", "LOGIN", "LOGOUT", "EXPORT"}

_TS_PATTERNS = [
    # 2026-02-27T20:01:00Z
    (re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\b"), "%Y-%m-%dT%H:%M:%SZ"),
    # 2026/02/27 20:01:00
    (re.compile(r"\b\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}\b"), "%Y/%m/%d %H:%M:%S"),
    # 2026-02-27 20:01:00
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\b"), "%Y-%m-%d %H:%M:%S"),
]


def _norm_ts(raw: str) -> str:
    raw = raw.strip().strip("[](){}")
    for rx, fmt in _TS_PATTERNS:
        m = rx.search(raw)
        if m:
            dt = datetime.strptime(m.group(0), fmt).replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    raise ValueError(f"unrecognized ts: {raw}")


def parse_audit_log(text: str) -> list[dict]:
    """Minimal example parser (NOT intended to be perfect).

    Demonstrates:
    - JSON-line parsing
    - basic key=value parsing with quoting
    - timestamp normalization

    Robust solutions should support multiple formats and ignore noise safely.
    """

    events: list[dict] = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # JSON line
        if line.startswith("{") and line.endswith("}"):
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    continue
                if {"ts", "actor", "action", "resource", "result", "req"}.issubset(obj.keys()):
                    try:
                        events.append(
                            {
                                "ts": _norm_ts(str(obj["ts"])),
                                "actor": str(obj["actor"]),
                                "action": str(obj["action"]),
                                "resource": str(obj["resource"]),
                                "result": str(obj["result"]),
                                "req": str(obj["req"]),
                            }
                        )
                    except Exception:
                        # ignore malformed timestamps
                        continue
            except Exception:
                continue
            continue

        # key=value format (simple)
        if all(k + "=" in line for k in ["ts", "actor", "action", "resource", "result", "req"]):

            def grab_ts() -> str | None:
                # allow an unquoted timestamp that may contain a single space (date time)
                m = re.search(r"\bts=(\"[^\"]*\"|\d{4}[-/]\d{2}[-/]\d{2}(?:[ T]\d{2}:\d{2}:\d{2})?Z?)", line)
                if not m:
                    return None
                v = m.group(1)
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                return v

            def grab(k: str) -> str | None:
                m = re.search(rf"\b{k}=(\"[^\"]*\"|\S+)", line)
                if not m:
                    return None
                v = m.group(1)
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                return v

            ts = grab_ts()
            actor = grab("actor")
            action = grab("action")
            resource = grab("resource")
            result = grab("result")
            req = grab("req")

            if ts and actor and action in ACTIONS and resource and result in {"OK", "DENY"} and req:
                try:
                    events.append(
                        {
                            "ts": _norm_ts(ts),
                            "actor": actor,
                            "action": action,
                            "resource": resource,
                            "result": result,
                            "req": req,
                        }
                    )
                except Exception:
                    continue

    return events
