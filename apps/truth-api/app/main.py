from __future__ import annotations

import sqlite3
from fastapi import FastAPI

from app.dimension_classifier import classify_dimensions
from app.db import connect_db
from app.embedding_pipeline import get_embedding_mode
from app.gateway_check import check_embedding_gateway
from app.models import TruthQueryRequest
from app.reasoning import compose_response
from app.retriever import retrieve_puzzles
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
    except sqlite3.DatabaseError as exc:
        response = compose_response(payload.message, [])
        return {
            "mirror": response["mirror"],
            "truth_view": "資料庫目前不可用，系統已退回最小回應模式。",
            "coach_question": response["coach_question"],
            "action": "先確認 SQLite 狀態，之後再重試查詢。",
            "dimension": "discernment",
            "principles": [],
        }

    dimensions = classify_dimensions(payload.message)

    try:
        puzzles = retrieve_puzzles(payload.message, dimensions=dimensions, limit=12)
    except Exception as exc:
        puzzles = []

    leading_dimension = dimensions[0] if dimensions else puzzles[0]["dimension_code"]
    principles = list(dict.fromkeys(puzzle["principle_code"] for puzzle in puzzles))
    response = compose_response(payload.message, puzzles)

    return {
        "mirror": response["mirror"],
        "truth_view": response["truth_view"],
        "coach_question": response["coach_question"],
        "action": response["action"],
        "dimension": leading_dimension,
        "principles": principles[:12],
    }
