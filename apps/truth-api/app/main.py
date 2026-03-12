from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Query

from app.case_models import CaseResolutionInput
from app.case_insight_service import CaseInsightService
from app.case_resolver import get_case_resolver
from app.case_resolver import load_case_profile
from app.db import connect_db
from app.dimension_classifier import classify_dimensions
from app.embedding_pipeline import get_embedding_mode
from app.gateway_check import check_embedding_gateway
from app.models import CorePrincipleItem
from app.models import CorePrinciplesResponse
from app.models import SessionMemoryItem
from app.models import SessionMemoryResponse
from app.models import TruthDimensionItem
from app.models import TruthDimensionsResponse
from app.models import TruthQueryRequest
from app.models import TruthQueryResponse
from app.prompt_builder import PromptBuilder
from app.reasoning import compose_response
from app.retriever import get_retrieval_mode, retrieve_puzzles
from app.vector_index import vector_index_exists

logger = logging.getLogger(__name__)
case_insight_service = CaseInsightService()
prompt_builder = PromptBuilder()

app = FastAPI(title="TruthOS API", version="0.3.0")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolved_session_id(payload: TruthQueryRequest) -> str:
    return payload.session_id or f"default:{payload.user_id}"


def _write_session_memory(
    *,
    user_id: str,
    session_id: str,
    dimension_code: str,
    principle_code: str | None,
    message: str,
) -> None:
    snippet = message.strip()[:80] or None
    with connect_db() as connection:
        connection.execute(
            """
            INSERT INTO session_memory (
              id, user_id, session_id, dimension_code, principle_code, message_snippet, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                uuid4().hex,
                user_id,
                session_id,
                dimension_code,
                principle_code,
                snippet,
                _utc_now(),
            ),
        )
        connection.commit()


def _dimensions_rows() -> list[TruthDimensionItem]:
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT code, name_zh, name_en, description
            FROM truth_dimensions
            ORDER BY order_index ASC, code ASC
            """
        ).fetchall()
    return [
        TruthDimensionItem(
            code=row["code"],
            name_zh=row["name_zh"],
            name_en=row["name_en"],
            description=row["description"],
        )
        for row in rows
    ]


def _principle_rows(dimension: str | None) -> list[CorePrincipleItem]:
    sql = """
        SELECT dimension_code, code, title, axiom, explanation
        FROM core_principles
    """
    params: tuple[str, ...] = ()
    if dimension:
        sql += " WHERE dimension_code = ?"
        params = (dimension,)
    sql += " ORDER BY dimension_code ASC, code ASC"

    with connect_db() as connection:
        rows = connection.execute(sql, params).fetchall()
    return [
        CorePrincipleItem(
            dimension_code=row["dimension_code"],
            code=row["code"],
            title=row["title"],
            axiom=row["axiom"],
            explanation=row["explanation"],
        )
        for row in rows
    ]


def _session_history_rows(user_id: str) -> list[SessionMemoryItem]:
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT dimension_code, principle_code, message_snippet, created_at
            FROM session_memory
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (user_id,),
        ).fetchall()
    return [
        SessionMemoryItem(
            dimension=row["dimension_code"],
            principle=row["principle_code"],
            snippet=row["message_snippet"],
            at=row["created_at"],
        )
        for row in rows
    ]


# --------------------------------------------------------------------------
# Health
# --------------------------------------------------------------------------

@app.get("/healthz")
def healthz() -> dict[str, str | bool]:
    gateway = check_embedding_gateway()
    return {
        "status": "ok",
        "embedding_gateway": bool(gateway["gateway"]),
        "vector_index": vector_index_exists(),
        "embedding_mode": get_embedding_mode(),
        "retrieval_mode": get_retrieval_mode(),
    }


@app.get("/api/truth/dimensions", response_model=TruthDimensionsResponse)
def list_dimensions() -> TruthDimensionsResponse:
    return TruthDimensionsResponse(dimensions=_dimensions_rows())


@app.get("/api/truth/principles", response_model=CorePrinciplesResponse)
def list_principles(dimension: str | None = Query(default=None)) -> CorePrinciplesResponse:
    return CorePrinciplesResponse(principles=_principle_rows(dimension))


@app.get("/api/truth/session/{user_id}", response_model=SessionMemoryResponse)
def get_session_history(user_id: str) -> SessionMemoryResponse:
    return SessionMemoryResponse(user_id=user_id, history=_session_history_rows(user_id))


# --------------------------------------------------------------------------
# Main truth query (backwards-compatible — case context is optional)
# --------------------------------------------------------------------------

@app.post("/api/truth/query", response_model=TruthQueryResponse)
def truth_query(payload: TruthQueryRequest) -> TruthQueryResponse:
    embedding_mode = get_embedding_mode()

    # --- Resolve case context if any identity signals are present ---
    case_ctx = None
    has_identity = any([
        payload.login_username,
        payload.preferred_name,
        payload.display_name,
        payload.user_id and payload.user_id != "anonymous",
    ])
    if has_identity:
        try:
            inp = CaseResolutionInput(
                login_username=payload.login_username or (
                    payload.user_id if payload.user_id != "anonymous" else None
                ),
                preferred_name=payload.preferred_name,
                display_name=payload.display_name,
                source_channel=payload.source_channel or "api",
                external_user_id=payload.user_id,
                session_id=payload.session_id,
            )
            case_ctx, _ = get_case_resolver().resolve(inp)
            logger.info(
                "/api/truth/query: case resolved -> %s (address_as=%r)",
                case_ctx.case_id, case_ctx.address_as,
            )
        except Exception as exc:
            logger.warning("Case resolution failed (non-fatal): %s", exc)
    if case_ctx:
        try:
            prompt_builder.build_case_context_message(case_ctx)
        except Exception as exc:
            logger.warning("PromptBuilder failed to serialize case context (non-fatal): %s", exc)

    # --- DB health check ---
    try:
        with connect_db() as connection:
            connection.execute("SELECT 1")
    except sqlite3.DatabaseError:
        response = compose_response(payload.message, [], case_ctx=case_ctx)
        return TruthQueryResponse(
            mirror=response["mirror"],
            truth_view="資料庫目前不可用，系統已退回最小回應模式。",
            coach_question=response["coach_question"],
            action="先確認 SQLite 狀態，之後再重試查詢。",
            dimension="discernment",
            principles=[],
            retrieval_mode="sqlite",
            case_id=case_ctx.case_id if case_ctx else None,
            session_id=payload.session_id,
            dimensions_triggered=["discernment"],
            matched_puzzles_count=0,
            embedding_mode=embedding_mode,
        )

    dimensions = classify_dimensions(payload.message)

    try:
        retrieval = retrieve_puzzles(payload.message, dimensions=dimensions, limit=12)
        puzzles = retrieval["puzzles"]
        retrieval_mode = retrieval["retrieval_mode"]
    except Exception as exc:
        logger.warning("Puzzle retrieval failed, falling back to sqlite response mode: %s", exc)
        puzzles = []
        retrieval_mode = "sqlite"

    leading_dimension = dimensions[0] if dimensions else (puzzles[0]["dimension_code"] if puzzles else "unknown")
    principles = [code for code in dict.fromkeys(puzzle["principle_code"] for puzzle in puzzles) if code]
    response = compose_response(payload.message, puzzles, case_ctx=case_ctx)

    if case_ctx:
        try:
            profile = load_case_profile(case_ctx.case_id)
            if profile is not None:
                case_insight_service.update_case_blueprint_from_conversation(
                    profile,
                    conversation_messages=[{"role": "user", "content": payload.message}],
                    model_response=response,
                    metadata={
                        "session_id": payload.session_id,
                        "source_channel": payload.source_channel or "api",
                    },
                )
        except Exception as exc:
            logger.warning("Case blueprint writeback failed (non-fatal): %s", exc)

    try:
        _write_session_memory(
            user_id=payload.user_id,
            session_id=_resolved_session_id(payload),
            dimension_code=leading_dimension,
            principle_code=principles[0] if principles else None,
            message=payload.message,
        )
    except Exception as exc:
        logger.warning("Session memory write failed (non-fatal): %s", exc)

    return TruthQueryResponse(
        mirror=response["mirror"],
        truth_view=response["truth_view"],
        coach_question=response["coach_question"],
        action=response["action"],
        dimension=leading_dimension,
        principles=principles[:12],
        retrieval_mode=retrieval_mode,
        case_id=case_ctx.case_id if case_ctx else None,
        session_id=payload.session_id,
        dimensions_triggered=dimensions[:3],
        matched_puzzles_count=len(puzzles),
        embedding_mode=embedding_mode,
    )


# --------------------------------------------------------------------------
# Internal: Case resolution debug endpoint
# --------------------------------------------------------------------------

@app.post("/internal/case/resolve")
def internal_case_resolve(inp: CaseResolutionInput) -> dict:
    """
    Debug / integration endpoint: resolve a CaseResolutionInput and return
    the resulting CaseContext as JSON.

    Only accessible from internal callers (caller should enforce network policy).
    Useful for:
      - Integration testing
      - Verifying name resolution priority
      - Debugging "why is the AI calling me X instead of Y"
    """
    try:
        ctx, is_new = get_case_resolver().resolve(inp)
        return {
            "ok": True,
            "is_new_case": is_new,
            "case_context": ctx.model_dump(),
        }
    except Exception as exc:
        logger.error("internal/case/resolve error: %s", exc)
        return {"ok": False, "error": str(exc)}
