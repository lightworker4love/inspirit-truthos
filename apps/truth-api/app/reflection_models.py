from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class TimeWindowModel(BaseModel):
    start: str
    end: str
    timezone: str
    window_hours: int | None = Field(default=None)


class InferenceItemModel(BaseModel):
    statement: str
    confidence: float = Field(ge=0.0, le=1.0)
    working_hypothesis: bool


class DiscernmentLayersModel(BaseModel):
    facts: list[str]
    interpretations: list[str]
    inferences: list[InferenceItemModel]
    guidance: list[str]


class SignalsModel(BaseModel):
    emotions: list[str]
    relationship_patterns: list[str]
    work_patterns: list[str]
    decision_patterns: list[str]


class DimensionMappingModel(BaseModel):
    code: str
    score: float = Field(ge=0.0, le=1.0)


class PrincipleMappingModel(BaseModel):
    code: str
    title: str
    confidence: float = Field(ge=0.0, le=1.0)


class PuzzleMappingModel(BaseModel):
    id: str
    title: str
    pattern_type: str
    confidence: float = Field(ge=0.0, le=1.0)


class TruthMappingModel(BaseModel):
    dimensions: list[DimensionMappingModel]
    principles: list[PrincipleMappingModel]
    puzzles: list[PuzzleMappingModel]


class SoulMapCandidateModel(BaseModel):
    recurring_patterns: list[str]
    limiting_beliefs: list[str]
    emotional_signatures: list[str]
    active_lessons: list[str]
    evolution_stage: str
    should_write: bool


class BlindSpotCandidateModel(BaseModel):
    title: str
    trigger_pattern: str
    known_theory: str
    practical_failure_mode: str
    suggested_anchors: list[str]
    related_puzzles: list[str]
    should_write: bool


class BeliefLogCandidateModel(BaseModel):
    belief_before: str
    belief_after: str
    tag: str
    evidence: list[str]
    related_dimension_code: str
    related_principle_code: str
    should_write: bool


class CaseSummaryCandidateModel(BaseModel):
    title: str
    summary: str
    related_dimensions: list[str]
    should_write: bool


class WritebackCandidatesModel(BaseModel):
    soul_map: SoulMapCandidateModel
    blind_spot_archive: list[BlindSpotCandidateModel]
    belief_logs: list[BeliefLogCandidateModel]
    case_summary: CaseSummaryCandidateModel


class DashboardMetricsModel(BaseModel):
    clarity_score: int = Field(ge=0, le=100)
    emotional_intensity_score: int = Field(ge=0, le=100)
    alignment_score: int = Field(ge=0, le=100)
    boundary_score: int = Field(ge=0, le=100)
    truth_discernment_score: int = Field(ge=0, le=100)
    memory_confidence_score: int = Field(ge=0, le=100)


class SourceContextStatusModel(BaseModel):
    life_principles_attached: bool
    external_context_complete: bool
    missing_inputs: list[str]


class ReflectionRunModel(BaseModel):
    run_date: str
    time_window: TimeWindowModel
    summary: str
    discernment_layers: DiscernmentLayersModel
    signals: SignalsModel
    truth_mapping: TruthMappingModel
    writeback_candidates: WritebackCandidatesModel
    dashboard_metrics: DashboardMetricsModel
    uncertainty_notes: list[str]
    source_context_status: SourceContextStatusModel
    recommended_actions: list[str] = Field(default_factory=list)
    recommended_questions: list[str] = Field(default_factory=list)
    truth_observations: list[str] = Field(default_factory=list)


class DailyTimelineModel(BaseModel):
    summary: str
    primary_dimensions: list[str]
    primary_principles: list[str]
    primary_fluctuations: list[str]


class DashboardDimensionScoreModel(BaseModel):
    dimension_code: str
    score: float = Field(ge=0.0, le=1.0)


class RecurringPatternModel(BaseModel):
    pattern_key: str
    title: str
    count_increment: int = Field(ge=0)
    last_seen: str
    confidence: float = Field(ge=0.0, le=1.0)


class BeliefShiftModel(BaseModel):
    belief_key: str
    belief_before: str
    belief_after: str
    evidence_count: int = Field(ge=0)
    related_dimension_code: str
    related_principle_code: str | None = None


class DashboardBlindSpotModel(BaseModel):
    blind_spot_key: str
    title: str
    trigger_pattern: str
    failure_mode: str
    status: str


class AlignmentMetricsModel(BaseModel):
    clarity_score: int = Field(ge=0, le=100)
    boundary_score: int = Field(ge=0, le=100)
    discernment_score: int = Field(ge=0, le=100)
    alignment_score: int = Field(ge=0, le=100)
    emotional_intensity_score: int = Field(ge=0, le=100)
    memory_confidence_score: int = Field(ge=0, le=100)


class DashboardSnapshotModel(BaseModel):
    run_date: str
    time_window_hours: int
    daily_timeline: DailyTimelineModel
    dimension_scores: list[DashboardDimensionScoreModel]
    recurring_patterns: list[RecurringPatternModel]
    belief_shifts: list[BeliefShiftModel]
    blind_spots: list[DashboardBlindSpotModel]
    alignment_metrics: AlignmentMetricsModel
    source_run_path: str


class CorePrincipleDraftModel(BaseModel):
    id: str
    dimension: str
    title: str
    axiom: str
    explanation: str
    shadow_form: str
    truth_form: str
    coach_questions: list[str]
    source_refs: list[str]
    status: str
    generated_from_run_date: str
    cross_day_support_count: int = Field(ge=1)


class TruthPuzzleDraftModel(BaseModel):
    id: str
    dimension: str
    principle_code: str
    title: str
    statement: str
    pattern_type: str
    misbelief: str
    truth_reframe: str
    coach_prompt: str
    trigger_signals: list[str]
    use_cases: list[str]
    tags: list[str]
    source_doc: str
    source_excerpt: str
    status: str
    generated_from_run_date: str
    cross_day_support_count: int = Field(ge=1)


class ImportDraftsModel(BaseModel):
    core_principle_candidates: list[CorePrincipleDraftModel]
    truth_puzzle_candidates: list[TruthPuzzleDraftModel]


class OperatorSummaryModel(BaseModel):
    window_hours: int
    primary_dimensions: list[str]
    files_written: list[str] = Field(default_factory=list)
    writeback_streams: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReflectionWritebackRequest(BaseModel):
    run_date: str
    user_id: str = Field(min_length=1)
    tenant_id: str | None = None
    source_file: str | None = None
    source_run_id: str | None = None
    reflection_run: ReflectionRunModel
    dashboard_snapshot: DashboardSnapshotModel
    writeback_candidates: WritebackCandidatesModel
    import_drafts: ImportDraftsModel
    source_context_status: SourceContextStatusModel
    operator_summary: OperatorSummaryModel

    @model_validator(mode="after")
    def validate_run_dates(self) -> "ReflectionWritebackRequest":
        if self.run_date != self.reflection_run.run_date:
            raise ValueError("run_date must match reflection_run.run_date")
        if self.run_date != self.dashboard_snapshot.run_date:
            raise ValueError("run_date must match dashboard_snapshot.run_date")
        return self


class ReflectionWritebackResponse(BaseModel):
    accepted_streams: list[str]
    skipped_streams: list[str]
    duplicate_keys: list[str]
    blocked_reasons: list[str]
    written_records: dict[str, int]
    next_actions: list[str]


class ReflectionMaterializeRequest(BaseModel):
    user_id: str | None = None
    tenant_id: str | None = None
    run_date: str | None = None
    mode: str = "incremental"
    rebuild_all: bool = False


class ReflectionMaterializeResponse(BaseModel):
    materialized_views: list[str]
    generated_records: dict[str, int]
    next_actions: list[str]


class ReflectionRunReadResponse(BaseModel):
    run_date: str
    user_id: str
    run_payload: dict[str, Any]
    discernment_layers: list[dict[str, Any]]
    truth_mappings: list[dict[str, Any]]
    dashboard_snapshot: dict[str, Any] | None
    dashboard_metrics: dict[str, Any] | None
    audit_log: list[dict[str, Any]]


class DashboardOverviewWindowModel(BaseModel):
    window_days: int
    generated_at: str
    runs_count: int
    latest_run_date: str | None = None
    average_scores: dict[str, float]
    top_dimensions: list[dict[str, Any]]
    top_patterns: list[dict[str, Any]]


class DashboardOverviewResponse(BaseModel):
    user_id: str
    windows: list[DashboardOverviewWindowModel]
