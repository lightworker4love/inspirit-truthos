from __future__ import annotations

import sqlite3
from fastapi import FastAPI

from app.dimension_classifier import classify_dimensions
from app.db import connect_db
from app.embedding_pipeline import get_embedding_mode
from app.gateway_check import check_embedding_gateway
from app.models import TruthQueryRequest
from app.reasoning import compose_response
from app.retriever import get_core_principle, retrieve_puzzles
from app.truth_clients import SQLiteBeliefLogClient, SQLiteSoulMapClient
from app.truth_eval import write_truth_eval
from app.truth_map import build_truth_map
from app.truth_verification import TruthVerificationLayer
from app.vector_index import vector_index_exists

app = FastAPI(title="TruthOS API", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str | bool]:
    gateway = check_embedding_gateway()
    return {
        "status": "ok",
        "embedding_gateway": bool(gateway["gateway"]),
        "vector_index": vector_index_exists(),
        "embedding_mode": get_embedding_mode(),
    }


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
            "principles": [],
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

    return {
        "mirror": response["mirror"],
        "truth_view": response["truth_view"],
        "coach_question": response["coach_question"],
        "action": response["action"],
        "dimension": leading_dimension,
        "principles": principles[:12],
        "verification_track": track.value,
        "verification_context": verification_context,
        "truth_eval_id": eval_id,
        "truth_map": build_truth_map(
            user_message=payload.message,
            top_puzzle=top_puzzle,
            matched_principle=matched_principle,
            soul_map_patterns=soul_map_patterns,
            action=response["action"],
        ),
    }


def _discernment_score(top_puzzle: dict | None, leading_dimension: str) -> float:
    if not top_puzzle:
        return 0.0
    raw_score = top_puzzle.get("score")
    if isinstance(raw_score, (int, float)):
        return max(0.0, min(1.0, 1.0 - float(raw_score)))
    if leading_dimension == "discernment":
        return 0.9
    return 0.7
