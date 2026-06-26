# SEED_AUTHORING_GUIDE.md
# TruthOS Seed Authoring Guide

## 1. Purpose

This document defines how to author, review, expand, and maintain TruthOS seed data for `inspirit-truthos`.

It formalizes:

- dimensions
- core principles
- truth puzzles
- seed expansion strategy
- de-duplication rules
- semantic density rules
- source extraction from WordPress, life teachings, transcripts, and case material

This guide exists so that:

- seed growth remains governable
- retrieval quality remains stable
- new authors do not inflate content volume while degrading semantic precision
- agents can extend the corpus without blurring the truth model

TruthOS grows by sharpening truth atoms, not by inflating content volume.

---

## 2. Seed Philosophy

TruthOS seeds are not filler content.
They are the founding semantic substrate of the reasoning engine.

Every seed row should help the system do at least one of these better:

- classify a human pattern
- retrieve a principle edge
- recognize a distortion
- name a truth reframe
- open a grounded coaching angle

Core rules:

- one puzzle = one main pattern
- keep siblings, delete clones
- grow sharper, not merely larger
- prefer semantic precision over literary flourish
- preserve source meaning while transforming it into retrievable structure

---

## 3. Canonical Seed Families

TruthOS seed growth should organize around these families:

### 3.1 Dimensions

The stable top-level truth domains used for classification and routing.

### 3.2 Core principles

Reusable axioms that describe enduring truth laws, not one-off stories.

### 3.3 Truth puzzles

The smallest retrievable units for semantic search and reasoning composition.

### 3.4 Future seed families

These may be added later, but must remain structurally separate:

- blind-spot signatures
- reflection prompts
- puzzle relations
- case summaries
- coach review notes

Do not mix these into `truth_puzzles` without an explicit schema reason.

---

## 4. The 12-Dimension Canon

TruthOS currently uses this canonical 12-dimension set:

1. `motive`
2. `cognition`
3. `emotion`
4. `relationship`
5. `belief`
6. `evolution`
7. `causality`
8. `manifestation`
9. `suffering`
10. `freedom`
11. `compassion`
12. `discernment`

Dimension rules:

- keep the set intentionally small and stable
- do not add synonym dimensions casually
- do not rename dimension codes without migration planning
- use dimensions to narrow retrieval, not to replace reasoning

When a source seems to touch many dimensions, choose:

- the primary dimension for the main row
- neighboring dimensions later through sibling principles or related puzzles

---

## 5. Principle Authoring Rules

A principle is a reusable truth law.
It should be broader than a single anecdote, but concrete enough to guide retrieval and coaching.

Every principle should:

- have a stable code
- have a short memorable title
- contain one clear axiom
- define a recognizable shadow form
- define a recognizable truth form

Good principle characteristics:

- concise
- pattern-oriented
- reusable across many cases
- semantically distinct from nearby principles

Avoid:

- slogans with no operational meaning
- duplicated ideas with surface-level wording changes
- mystical phrasing that cannot guide retrieval or coaching
- titles too long for indexing or UI

Principle growth rule:

When a principle feels too broad, do not split it immediately.
First test whether the variation belongs in additional puzzles under the same principle.

---

## 6. Puzzle Authoring Rules

A truth puzzle is the primary retrieval atom in TruthOS.

Every puzzle should contain:

- one main pattern
- one distortion or misbelief
- one truth reframe
- one coaching angle
- one semantic fingerprint for retrieval

Required authoring standard:

- one puzzle = one main pattern

Good puzzle variations come from:

- a different distortion
- a different use case
- a different principle edge
- a different blind-spot signature

Bad puzzle variations usually are:

- clones with slightly different wording
- story fragments that are too specific to generalize
- poetic reflections with no retrieval value
- rows missing either `misbelief` or `truth_reframe`

If a draft puzzle contains three patterns, split it.
If it contains one pattern and three contexts, keep one row and move contexts into `use_cases`.

---

## 7. Semantic Density Rules

Seed quality depends on semantic density, not text length.

Semantic density means a row carries enough aligned meaning to retrieve well without becoming keyword spam.

### 7.1 What dense seeds contain

A good row tends to combine:

- dimension language
- principle language
- distortion language
- reframe language
- use-case signals

### 7.2 `embedding_text` rules

`embedding_text` should usually include:

- dimension code
- principle title or core concept
- puzzle title keywords
- statement essence
- misbelief language
- truth reframe language
- use case keywords

### 7.3 What to avoid

- text too short to retrieve robustly
- unrelated keywords stuffed for reach
- vague spiritual phrasing with no pattern markers
- duplicate rows with near-identical `embedding_text`

Rule:

Grow semantic density by sharpening the same truth atom, not by padding it.

---

## 8. De-duplication Rules

TruthOS should keep siblings and delete clones.

### 8.1 A sibling is valid when it changes:

- the main distortion
- the main reframe
- the main context
- the practical failure mode
- the blind-spot signature

### 8.2 A clone should be merged or deleted when it only changes:

- adjectives
- sentence rhythm
- poetic phrasing
- minor wording with identical semantic load

### 8.3 Duplicate review questions

When comparing two candidate rows, ask:

- do they retrieve for meaningfully different user situations?
- do they protect different principle edges?
- do they expose different distortions?
- would a coach keep both?

If the answer is mostly no, merge them.

---

## 9. Expansion Strategy: 100 Principles -> 1200+ Puzzles -> Beyond

TruthOS should expand by controlled branching, not uncontrolled accumulation.

### 9.1 Stage 1: Stabilize the principle layer

Target:

- around 100 core principles

Goal:

- broad conceptual coverage across the 12 dimensions

### 9.2 Stage 2: Expand puzzle coverage

Target:

- 1200+ truth puzzles

Expansion paths:

- new use cases
- new distortions
- new principle edges
- new blind-spot signatures

### 9.3 Stage 3: Beyond 1200

Beyond the initial puzzle layer, growth should favor:

- better retrieval separation
- richer blind-spot detection
- stronger coach-facing search
- clearer case mapping

Do not grow by turning every paragraph of source material into a row.
Grow by extracting truth atoms that improve reasoning coverage.

---

## 10. Source Extraction Workflow

TruthOS sources may include:

- WordPress articles
- long-form life teachings
- transcripts
- reflection notes
- case material

Recommended extraction workflow:

1. Read the source for the main truth movement.
2. Identify the dominant dimension.
3. Extract reusable principles before writing puzzles.
4. Convert recurring lived patterns into puzzle candidates.
5. Write `misbelief`, `truth_reframe`, and `coach_prompt`.
6. Build `embedding_text` around retrieval meaning, not prose beauty.
7. remove duplicates before committing seed rows.

Source conversion guidance:

- WordPress articles often yield principle and puzzle candidates.
- transcripts often yield practical phrasing and use-case language.
- life teachings often yield principle titles, shadow forms, and reframes.
- case material often yields blind-spot signatures and real-world trigger language.

Do not paste raw source paragraphs into seed files.
Transform source material into structured truth units.

---

## 11. Seed Review Workflow

Recommended seed review sequence:

1. Dimension review
2. Principle review
3. Puzzle review
4. Retrieval review
5. Duplicate review
6. Source provenance review

For each new batch, reviewers should confirm:

- the correct dimension was chosen
- principles are distinct
- puzzles are not clones
- `embedding_text` is retrieval-strong
- source references remain meaningful

If a row is beautiful but weak for retrieval, revise it.

---

## 12. Quality Heuristics

Use these heuristics when evaluating seeds:

### 12.1 Good principle heuristic

Could this principle guide more than one case?

### 12.2 Good puzzle heuristic

Can a user recognize themselves in the pattern quickly?

### 12.3 Good reframe heuristic

Does the reframe liberate without becoming vague?

### 12.4 Good coaching heuristic

Does the prompt open reflection instead of forcing a conclusion?

### 12.5 Good retrieval heuristic

Would this row likely be found by the phrases a real person uses?

If not, the row is not ready.

---

## 13. Seed File Management

Canonical seed files should live under `seeds/` and remain UTF-8 JSONL.

Current baseline:

- `seeds/dimensions.seed.jsonl`
- `seeds/core_principles.seed.jsonl`
- `seeds/truth_puzzles.seed.jsonl`

Management rules:

- keep one JSON object per line
- keep field names stable
- version material rewrites
- review retrieval-relevant changes carefully
- rebuild vectors when `embedding_text` or retrieval-relevant fields change materially

Do not mix environment config, runtime logs, or ad hoc notes into seed files.

---

## 14. Seed Authoring Examples

### 14.1 Principle example

```json
{
  "id": "p_rel_001",
  "dimension_code": "relationship",
  "code": "REL_001",
  "title": "愛不等於接管",
  "axiom": "支援不等於替對方活。",
  "shadow_form": "把控制包裝成關心",
  "truth_form": "帶著界線的支援"
}
```

### 14.2 Puzzle example

```json
{
  "id": "seed_relationship_001",
  "dimension_code": "relationship",
  "principle_code": "REL_001",
  "title": "拯救者焦慮會偽裝成愛",
  "statement": "你以為自己在幫人，實際上可能是在逃避自己的無力感。",
  "pattern_type": "control",
  "misbelief": "如果我不救他，我就不夠有愛。",
  "truth_reframe": "支援不等於接管他人的命運。",
  "coach_prompt": "你是在陪伴，還是在替他活？",
  "tags": ["拯救者", "界線", "關係"],
  "use_cases": ["家庭", "伴侶", "助人關係"],
  "source_doc": "核心機制：in spirit AI 神經系統",
  "embedding_text": "relationship 愛不等於接管 拯救者焦慮 界線 支援不是控制 家庭衝突 罪惡感"
}
```

### 14.3 Expansion example

Starting point:

- one principle: `REL_001`
- one puzzle: rescuing as disguised control

Valid next expansions:

- family-specific over-responsibility
- partner-specific emotional takeover
- helper identity tied to guilt
- spiritualized self-sacrifice as control

Invalid expansion:

- rewriting the same rescuing pattern five times with cosmetic wording changes

---

## 15. Final Rule

TruthOS seed growth is successful when the corpus becomes sharper, not merely bigger.

If you must choose between:

- more rows
- better rows

choose better rows.

If you must choose between:

- literary beauty
- retrievable truth structure

choose retrievable truth structure.

Keep siblings.
Delete clones.
Grow sharper, not merely larger.
