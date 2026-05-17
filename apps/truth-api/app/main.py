from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.designer import router as designer_router
from api.sessions import router as sessions_router
from api.soul_map import router as soul_map_router
from app.dimension_classifier import classify_dimensions
from app.db import connect_db
from app.designer_agent import DesignerAgent
from app.embedding_pipeline import get_embedding_mode
from app.gateway_check import check_embedding_gateway
from app.models import TruthQueryRequest
from app.reasoning import compose_response
from app.retriever import get_core_principle, retrieve_puzzles
from app.truth_clients import SQLiteBeliefLogClient, SQLiteSoulMapClient
from app.truth_eval import write_truth_eval
from app.truth_map import build_truth_map
from app.truth_verification import TruthVerificationLayer
from app.soul_map_engine import SoulMapEngine
from app.vector_index import vector_index_exists

app = FastAPI(title="TruthOS API", version="0.1.0")
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(designer_router)
app.include_router(sessions_router)
app.include_router(soul_map_router)


@app.get("/console", include_in_schema=False)
async def truth_console():
    return FileResponse(STATIC_DIR / "truth-console.html")


@app.get("/healthz")
def healthz() -> dict[str, str | bool]:
    gateway = check_embedding_gateway()
    return {
        "status": "ok",
        "embedding_gateway": bool(gateway["gateway"]),
        "vector_index": vector_index_exists(),
        "embedding_mode": get_embedding_mode(),
    }


@app.get("/health")
def health() -> dict[str, str | bool]:
    return healthz()


@app.post("/api/truth/query")
def truth_query(payload: TruthQueryRequest) -> dict:
    try:
        with connect_db() as connection:
            connection.execute("SELECT 1")
    except sqlite3.DatabaseError:
        response = compose_response(payload.message, [])
        return {
            "mirror": response["mirror"],
            "truth_view": "資料庫目前不可用，系統已退回最小回應模式。",
            "coach_question": response["coach_question"],
            "action": "先確認 SQLite 狀態，之後再重試查詢。",
            "dimension": "discernment",
            "dimensions": ["discernment"],
            "principles": [],
            "puzzles": [],
            "response": response,
            "truth_map": build_truth_map(
                user_message=payload.message,
                top_puzzle=None,
                matched_principle=None,
                soul_map_patterns=[],
                action="先確認 SQLite 狀態，之後再重試查詢。",
            ),
        }

    dimensions = classify_dimensions(payload.message)

    try:
        puzzles = retrieve_puzzles(payload.message, dimensions=dimensions, limit=12)
    except Exception:
        puzzles = []

    top_puzzle = puzzles[0] if puzzles else None
    leading_dimension = (
        dimensions[0]
        if dimensions
        else top_puzzle["dimension_code"]
        if top_puzzle
        else "discernment"
    )
    principles = list(dict.fromkeys(puzzle["principle_code"] for puzzle in puzzles))
    matched_principle = get_core_principle(top_puzzle["principle_code"]) if top_puzzle else None

    try:
        with connect_db() as connection:
            soul_map_engine = SoulMapEngine(db_client=connection)
            soul_map = soul_map_engine.get_soul_map(payload.user_id)
            user_context = {
                "soul_map_summary": soul_map_engine.get_summary_for_injection(payload.user_id),
                "primary_recurring_pattern": soul_map_engine.get_primary_pattern(payload.user_id),
                "evolution_stage": (soul_map or {}).get("evolution_stage", "awakening"),
            }
    except sqlite3.DatabaseError:
        user_context = {
            "soul_map_summary": "",
            "primary_recurring_pattern": "Soul Map not yet built for this user.",
            "evolution_stage": "awakening",
        }

    verifier = TruthVerificationLayer(
        belief_log_client=SQLiteBeliefLogClient(),
        soul_map_client=SQLiteSoulMapClient(),
    )
    discernment_score = _discernment_score(top_puzzle, leading_dimension)
    track = verifier.select_track(
        puzzle_verification_mode=(top_puzzle or {}).get("verification_mode") or "dialogue",
        discernment_score=discernment_score,
        user_id=payload.user_id,
        related_principle_id=(matched_principle or {}).get("code"),
    )
    life_evidence = verifier.get_life_evidence_for_principle(
        user_id=payload.user_id,
        principle_id=(matched_principle or {}).get("code"),
    )
    soul_map_patterns = verifier.get_soul_map_patterns(payload.user_id)

    response = compose_response(payload.message, puzzles)
    verification_context = verifier.build_verification_context(
        track=track,
        truth_view=response["truth_view"],
        life_evidence=life_evidence,
        soul_map_patterns=soul_map_patterns,
    )
    eval_id = write_truth_eval(
        user_id=payload.user_id,
        session_id=payload.session_id,
        question=payload.message,
        verification_track=track.value,
        life_evidence_confirmed=bool(life_evidence),
        discovery_triggered=False,
    )
    writeback = {
        "belieflogcandidate": bool(life_evidence),
        "blindspotcandidate": _detect_blindspot_candidate(payload.message, top_puzzle),
        "user_context": user_context,
    }
    soul_map_changes = {"updated": [], "new_patterns": [], "stage_change": None}
    hard_case = {"is_hard_case": False}
    designer_review = None
    try:
        with connect_db() as connection:
            soul_map_engine = SoulMapEngine(db_client=connection)
            detected_patterns = _detected_patterns(payload.message, top_puzzle, leading_dimension)
            soul_map_changes = soul_map_engine.update_from_query_result(
                user_id=payload.user_id,
                detected_patterns=detected_patterns,
                matched_dimension=leading_dimension,
                matched_principle_id=(matched_principle or {}).get("code", ""),
                belief_shift_detected=writeback["belieflogcandidate"],
                discovery_triggered=False,
                session_id=payload.session_id or "",
            )
            if writeback["blindspotcandidate"]:
                soul_map_engine.update_blind_spot(
                    user_id=payload.user_id,
                    trigger_pattern=detected_patterns[0] if detected_patterns else leading_dimension,
                    known_theory=response["truth_view"],
                    practical_failure_mode=(top_puzzle or {}).get("misbelief") or "",
                    domains=[leading_dimension],
                    related_puzzle_ids=[puzzle["id"] for puzzle in puzzles if puzzle.get("id")],
                )
            hard_case = soul_map_engine.detect_hard_case(payload.user_id)
            if hard_case.get("is_hard_case"):
                created_at = datetime.now(timezone.utc).isoformat()
                if _table_has_column(connection, "hardcasebuffer", "status"):
                    connection.execute(
                        """
                        INSERT OR REPLACE INTO hardcasebuffer
                          (userid, reasons, sessionid, createdat, status)
                        VALUES (?, ?, ?, ?, 'pending')
                        """,
                        (
                            payload.user_id,
                            json.dumps(hard_case["reasons"], ensure_ascii=False),
                            payload.session_id,
                            created_at,
                        ),
                    )
                    designer_review = DesignerAgent(db_client=connection).review_hard_case(
                        payload.user_id
                    )
                else:
                    connection.execute(
                        """
                        INSERT OR REPLACE INTO hardcasebuffer
                          (userid, reasons, sessionid, createdat)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            payload.user_id,
                            json.dumps(hard_case["reasons"], ensure_ascii=False),
                            payload.session_id,
                            created_at,
                        ),
                    )
                connection.commit()
    except sqlite3.DatabaseError:
        soul_map_changes = {"updated": [], "new_patterns": [], "stage_change": None}

    writeback["soul_map_changes"] = soul_map_changes

    result = {
        "mirror": response["mirror"],
        "truth_view": response["truth_view"],
        "coach_question": response["coach_question"],
        "action": response["action"],
        "dimension": leading_dimension,
        "dimensions": dimensions,
        "principles": principles[:12],
        "puzzles": puzzles,
        "response": response,
        "verification_track": track.value,
        "verification_context": verification_context,
        "truth_eval_id": eval_id,
        "writeback": writeback,
        "truth_map": build_truth_map(
            user_message=payload.message,
            top_puzzle=top_puzzle,
            matched_principle=matched_principle,
            soul_map_patterns=soul_map_patterns,
            action=response["action"],
        ),
    }
    if hard_case.get("is_hard_case"):
        result["hard_case_flag"] = True
        result["coach_review_recommended"] = True
        result["hard_case_reasons"] = hard_case.get("reasons", [])
    if designer_review:
        result["designer_review"] = designer_review
        result["knowledge_evolution_written"] = bool(
            designer_review.get("knowledge_evolution")
        )
    return result


def _discernment_score(top_puzzle: dict | None, leading_dimension: str) -> float:
    if not top_puzzle:
        return 0.0
    raw_score = top_puzzle.get("score")
    if isinstance(raw_score, int | float):
        return max(0.0, min(1.0, 1.0 - float(raw_score)))
    if leading_dimension == "discernment":
        return 0.9
    return 0.7


def _detected_patterns(
    message: str,
    top_puzzle: dict | None,
    leading_dimension: str,
) -> list[str]:
    if top_puzzle:
        principle_code = top_puzzle.get("principle_code")
        title = top_puzzle.get("title")
        if principle_code:
            return [f"{leading_dimension}:{principle_code}"]
        if title:
            return [f"{leading_dimension}:{title}"]
    normalized = " ".join(message.split())[:80]
    return [f"{leading_dimension}:{normalized}"] if normalized else [leading_dimension]


def _detect_blindspot_candidate(message: str, top_puzzle: dict | None) -> bool:
    if not top_puzzle:
        return False
    text = f"{message} {top_puzzle.get('misbelief', '')}".lower()
    markers = (
        "i know",
        "but i",
        "can't",
        "cannot",
        "我知道",
        "可是",
        "但是",
        "做不到",
        "還是",
    )
    return bool(top_puzzle.get("misbelief")) and any(marker in text for marker in markers)


def _table_has_column(connection: sqlite3.Connection, table: str, column: str) -> bool:
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return column in {row[1] for row in rows}
