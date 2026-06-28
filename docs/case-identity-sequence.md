# Case Identity Sequence

## Scope

This document describes the Phase 1.5 case identity path for wisdom login, frontend state hydration, chat request metadata, backend case resolution, prompt construction, response composition, and minimal blueprint writeback.

## Naming Priority

Highest to lowest:

1. `preferred_name` from request/session metadata
2. stored `preferred_name` in `CaseProfile`
3. `login_username`
4. `display_name`
5. workspace default name
6. generic fallback `"你"`

## Sequence

```mermaid
sequenceDiagram
    participant User
    participant WisdomLogin as wisdom login
    participant SessionJson as /__wisdom/session.json
    participant Frontend as OpenClaw UI state
    participant ChatBody as chat.send payload
    participant Backend as truth-api / gateway backend
    participant Resolver as CaseResolver
    participant Builder as PromptBuilder
    participant Compose as compose_response()
    participant Blueprint as blueprint updater
    participant Store as case store

    User->>WisdomLogin: authenticate
    WisdomLogin->>SessionJson: issue session payload
    SessionJson-->>Frontend: preferredName, loginUsername, displayName, sourceChannel, sessionKey
    Frontend->>ChatBody: send preferred_name + login_username + display_name + source_channel
    ChatBody->>Backend: request arrives
    Backend->>Resolver: resolve identity
    Resolver->>Store: load/create CaseProfile
    Store-->>Resolver: profile
    Resolver-->>Backend: CaseContext(address_as)
    Backend->>Builder: build case context prompt message
    Builder-->>Backend: case_context message with address_as
    Backend->>Compose: compose_response(question, puzzles, case_ctx)
    Compose-->>Backend: response addressed as resolved name
    Backend->>Blueprint: update_case_blueprint_from_conversation(...)
    Blueprint->>Store: persist last_session_insight, life_themes, blind_spots
    Backend-->>User: final response
```

## Hank Acceptance Path

When `session.json` returns `preferredName = "Hank"`:

- frontend state keeps `preferredName = "Hank"`
- chat metadata includes `preferred_name = "Hank"`
- backend request model accepts `preferred_name`
- `CaseResolver` resolves `address_as = "Hank"`
- `PromptBuilder` serialises `Address as: Hank`
- `compose_response()` addresses the user as `Hank`
- workspace default naming never overrides this path
