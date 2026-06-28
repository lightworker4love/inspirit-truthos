from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "in-spirit-case-gateway"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8010
    app_base_url: str = "http://127.0.0.1:8010"

    session_secret: str = "replace-me"
    jwt_secret: str = "replace-me"
    jwt_expires_in: str = "7d"

    database_url: str = "sqlite:////Users/tongwei/.openclaw/data/in-spirit-case-auth.db"
    sqlite_busy_timeout_ms: int = 5000

    openclaw_gateway_base_url: str = "http://127.0.0.1:18789"
    openclaw_gateway_chat_path: str = "/v1/chat/completions"
    openclaw_gateway_models_path: str = "/v1/models"
    openclaw_gateway_token: str = "replace-with-gateway-token"

    mode_case_default: str = "spiritual_reflection"
    mode_case_alt: str = "scripture_reflection"
    mode_admin_default: str = "builder_workbench"
    mode_admin_alt: str = "deep_admin_analysis"

    prompt_version_case: str = "v1"
    prompt_version_admin: str = "v1"

    log_level: str = "info"
    audit_log_enabled: bool = True

    # -----------------------------------------------------------------
    # Phase 1/2: Long-term memory integration (default OFF).
    # All flags must remain false until Phase 1 infra is validated.
    # See docs/local-memory-phased-deployment-plan.md before enabling.
    # -----------------------------------------------------------------
    memory_longterm_enabled: bool = False
    memory_read_enabled: bool = False
    memory_write_enabled: bool = False
    memory_provider: str = "mem0"
    memory_strict_mode: bool = True
    memory_fail_open_read: bool = True
    memory_fail_open_write: bool = True

    # Retrieval policy
    memory_top_k: int = 5
    memory_max_context_chars: int = 2400
    memory_write_min_chars: int = 24

    # Scope governance
    memory_allowed_scopes: str = "default,none,session,experiment"
    memory_default_scope: str = "default"
    memory_experiment_scope_enabled: bool = False
    memory_session_scope_write_enabled: bool = False

    # Identity governance — always derive user_id from auth context unless
    # MEMORY_TRUST_PROXY_USER_ID is explicitly set true and a validated
    # internal token is present in the request.
    memory_user_id_source: str = "auth"  # auth | proxy
    memory_trust_proxy_user_id: bool = False

    # Audit
    memory_audit_enabled: bool = True
    memory_audit_redact_content: bool = True

    # Service endpoints
    mem0_base_url: str = ""
    mem0_api_key: str = ""
    qdrant_url: str = ""
    qdrant_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
