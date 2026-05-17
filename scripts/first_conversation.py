from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any

import httpx


HERMES_URL = os.getenv("HERMES_URL", "http://localhost:8001").rstrip("/")
TRUTHOS_URL = os.getenv("TRUTHOS_URL", "http://localhost:18000").rstrip("/")
USER_ID = os.getenv("FIRST_CONVERSATION_USER", "user-first-light")
SESSION_ID = os.getenv(
    "FIRST_CONVERSATION_SESSION",
    f"session-first-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
)

CONVERSATION = [
    {
        "turn": 1,
        "message": (
            "I keep starting new projects with a lot of excitement, but I always "
            "abandon them halfway through. I've done this my whole life and I "
            "don't know why I can't finish anything."
        ),
        "expected_pattern": "abandonment_cycle",
    },
    {
        "turn": 2,
        "message": (
            "Every time I get close to finishing something meaningful, I find a "
            "reason to stop. Last month it was my book. Before that, my business. "
            "I think I'm afraid of actually succeeding."
        ),
        "expected_pattern": "fear_of_completion",
    },
    {
        "turn": 3,
        "message": (
            "My father always told me I was a dreamer and would never finish what "
            "I started. I'm starting to think he was right."
        ),
        "expected_pattern": "inherited_belief_virus",
    },
    {
        "turn": 4,
        "message": (
            "What if this is just who I am? What if I'm fundamentally broken and "
            "no amount of coaching will change that?"
        ),
        "expected_pattern": "identity_collapse",
    },
    {
        "turn": 5,
        "message": (
            "I want to understand the truth about why I do this. Not to feel "
            "better about it - I want to actually see it clearly."
        ),
        "expected_pattern": "truth_seeking_awakening",
    },
]


def send_message(turn_data: dict[str, Any]) -> dict[str, Any]:
    print(f"\n[Turn {turn_data['turn']}] {turn_data['message'][:72]}...")
    try:
        response = httpx.post(
            f"{HERMES_URL}/chat",
            json={
                "user_id": USER_ID,
                "session_id": SESSION_ID,
                "message": turn_data["message"],
            },
            timeout=15,
        )
        if response.status_code != 200:
            print(f"  ERROR {response.status_code}: {response.text[:160]}")
            return {}
    except Exception as exc:
        print(f"  FAILED: {exc}")
        return {}

    data = response.json()
    truth_layer = data.get("truth_layer") or {}
    print("  OK response received")
    print(f"  Truth Score: {truth_layer.get('score', 'N/A')}")
    print(f"  Verified: {truth_layer.get('verified', 'N/A')}")
    print(f"  Soul Map Updated: {data.get('soul_map_updated', False)}")
    print(f"  Hard Case: {data.get('is_hard_case', False)}")
    if data.get("guidance_overlay"):
        print(f"  Guidance: {data['guidance_overlay'][:100]}...")
    return data


def check_soul_map() -> dict[str, Any]:
    print(f"\n[Soul Map Check] user={USER_ID}")
    try:
        response = httpx.get(f"{TRUTHOS_URL}/api/soul-map/{USER_ID}", timeout=10)
    except Exception as exc:
        print(f"  FAILED: {exc}")
        return {}

    if response.status_code != 200:
        print(f"  ERROR {response.status_code}: {response.text[:160]}")
        return {}

    soul_map = response.json()
    print(f"  Status: {soul_map.get('status', 'unknown')}")
    print(f"  Evolution Stage: {soul_map.get('evolution_stage', 'N/A')}")
    print(f"  Updated At: {soul_map.get('updated_at', 'N/A')}")

    weights = soul_map.get("pattern_weights") or {}
    patterns = soul_map.get("recurring_patterns") or []
    print(f"  Recurring Patterns: {len(patterns)}")
    for pattern in patterns[:5]:
        pattern_id = pattern.get("id") or pattern.get("pattern") or "unknown"
        weight = weights.get(pattern_id, {}).get("weight", pattern.get("weight", 0))
        frequency = weights.get(pattern_id, {}).get("frequency", pattern.get("frequency", 0))
        print(f"    - {pattern_id} (weight: {weight}, freq: {frequency})")

    blind_spots = soul_map.get("blind_spots") or soul_map.get("top_blind_spots") or []
    print(f"  Blind Spots: {len(blind_spots)}")
    print(f"  Active Lessons: {len(soul_map.get('active_lessons') or [])}")
    return soul_map


def check_hard_cases() -> list[dict[str, Any]]:
    print("\n[Hard Case Check]")
    try:
        response = httpx.get(
            f"{TRUTHOS_URL}/api/designer/hard-cases?status=pending",
            timeout=10,
        )
    except Exception as exc:
        print(f"  FAILED: {exc}")
        return []

    if response.status_code != 200:
        print(f"  ERROR {response.status_code}: {response.text[:160]}")
        return []

    cases = response.json().get("hard_cases", [])
    print(f"  Pending hard cases: {len(cases)}")
    for case in cases:
        case_user = case.get("user_id") or case.get("userid")
        if case_user == USER_ID:
            print(f"  FOUND hard case for {USER_ID}: {case_user}")
            print(f"    Reasons: {case.get('reasons', [])}")
    return cases


def check_live_stats() -> dict[str, Any]:
    print("\n[Live Stats Check]")
    try:
        response = httpx.get(f"{TRUTHOS_URL}/api/sessions/stats/summary", timeout=10)
    except Exception as exc:
        print(f"  FAILED: {exc}")
        return {}

    if response.status_code != 200:
        print(f"  ERROR {response.status_code}: {response.text[:160]}")
        return {}

    stats = response.json()
    print(f"  Sessions (1h): {stats.get('sessions_last_1h', 0)}")
    print(f"  Queries (1h): {stats.get('queries_last_1h', 0)}")
    print(f"  Avg Truth Score: {stats.get('avg_truth_score_1h', 0)}")
    print(f"  Pending Hard Cases: {stats.get('hard_cases_pending', 0)}")
    return stats


def require_service(url: str, label: str) -> bool:
    try:
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
    except Exception:
        print(f"ERROR {label} not reachable at {url}. Run: docker compose up -d")
        return False
    print(f"OK {label}: online")
    return True


def main() -> int:
    print("=" * 60)
    print("TruthOS Sprint 011 - First Real Conversation")
    print(f"User: {USER_ID}")
    print(f"Session: {SESSION_ID}")
    print(f"Hermes: {HERMES_URL}")
    print(f"TruthOS: {TRUTHOS_URL}")
    print("=" * 60)

    if not require_service(f"{HERMES_URL}/health", "Hermes Agent"):
        return 1
    if not require_service(f"{TRUTHOS_URL}/health", "TruthOS API"):
        return 1

    print("\n" + "-" * 60)
    print("SENDING CONVERSATION (5 turns)...")
    print("-" * 60)

    results = []
    for turn in CONVERSATION:
        results.append(send_message(turn))
        time.sleep(1.5)

    print("\n" + "-" * 60)
    print("POST-CONVERSATION CHECKS")
    print("-" * 60)
    time.sleep(3)

    soul_map = check_soul_map()
    hard_cases = check_hard_cases()
    live_stats = check_live_stats()

    hard_cases_for_user = sum(
        1
        for case in hard_cases
        if (case.get("user_id") or case.get("userid")) == USER_ID
    )

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Turns sent: {len(results)}")
    print(f"Soul Map created: {bool(soul_map and soul_map.get('status') == 'active')}")
    print(f"Hard cases triggered: {hard_cases_for_user}")
    print(f"Live queries in last hour: {live_stats.get('queries_last_1h', 0)}")
    print(f"\nOpen: {TRUTHOS_URL}/console")
    print(f"Look for user: {USER_ID}")
    print("Check: Soul Map, Blind Spots, Hard Cases, Live Monitor")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
