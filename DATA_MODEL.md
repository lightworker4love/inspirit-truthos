# DATA_MODEL.md
# TruthOS Truth Data Model Manual

## 1. Purpose

This document defines the canonical truth data model for `inspirit-truthos`.

It formalizes:

- truth dimensions
- core principles
- truth puzzles
- belief logs
- blind spot archives
- embedding_text semantics
- seed dataset specifications

This document exists so that:
- humans can maintain the truth dataset consistently
- Codex / agents can generate or transform data safely
- retrieval quality remains stable
- schema drift does not destroy semantic coherence

TruthOS is not a generic content repository.
It is a structured truth reasoning system.

Its data model must therefore support:
- reflection
- discernment
- pattern recognition
- structured retrieval
- graceful fallback
- long-term evolution

---

## 2. Design Philosophy

## 2.1 Structure before poetry
TruthOS may speak with warmth, but its data layer must remain explicit.

We do not store “vibes.”
We store structured units that can be:
- indexed
- linked
- retrieved
- reasoned over
- audited

## 2.2 Truth knowledge is layered
The truth data model separates knowledge into levels:

1. **Dimension**
   - broad truth domain

2. **Principle**
   - reusable law / axiom / core teaching

3. **Puzzle**
   - smallest actionable truth unit
   - pattern-aware and retrievable

4. **Belief log**
   - personal transformation event record

5. **Blind spot archive**
   - recurring failure pattern / hidden distortion pattern

This structure reflects your platform’s goal of moving beyond generic AI output toward structured, governable reflection and long-term support. :contentReference[oaicite:3]{index=3}

## 2.3 TruthOS data is built for reasoning, not just storage
The system must support:
- semantic search
- principle selection
- reflective response composition
- blind spot recognition
- case continuity

This is why the data model must preserve both:
- human readability
- machine retrievability

---

## 3. Model Overview

TruthOS currently uses the following semantic core:

- 12 truth dimensions
- 100 core principles
- 1200 truth puzzles

These form the minimum viable semantic core of the system.

Recommended core tables:

- `truth_dimensions`
- `core_principles`
- `truth_puzzles`
- `belief_logs`
- `blind_spot_archives`

Optional related tables may later include:
- `puzzle_relations`
- `case_summaries`
- `truth_evals`

---

## 4. `truth_dimensions`

## 4.1 Purpose

A dimension is the highest-level truth category.

It represents a broad domain of human experience or discernment.

Dimensions are used to:
- classify user queries
- narrow retrieval space
- organize principles and puzzles
- improve semantic routing

## 4.2 Current canonical dimension set

The current 12-dimension set is:

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

This set is already reflected in your current TruthOS planning and seed structures.

## 4.3 Recommended schema

```sql
CREATE TABLE truth_dimensions (
  id TEXT PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name_zh TEXT NOT NULL,
  name_en TEXT NOT NULL,
  description TEXT,
  order_index INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

## 4.4 Field semantics

`id`

internal stable identifier

should not be user-facing

`code`

canonical machine-readable key

example: `relationship`

`name_zh`

Traditional Chinese display name

example: `關係`

`name_en`

English display name

example: `Relationship`

`description`

short explanation of what the dimension covers

`order_index`

stable ordering for UI, export, and seed consistency

## 4.5 Dimension design rules

dimension codes should be stable

do not rename casually

do not create synonym duplicates

dimension count should remain intentionally small and stable

new dimensions require governance review

---

## 5. `core_principles`

## 5.1 Purpose

A core principle is a reusable truth law, axiom, or teaching pattern.

A principle is:

broader than a single example

smaller than a worldview

reusable across multiple puzzles

suitable for reasoning and coaching

Examples consistent with your corpus include:

動機先於行為

本質勝於形式

情緒是訊號不是主人

愛不等於接管

有道理未必是真理

## 5.2 Recommended schema

```sql
CREATE TABLE core_principles (
  id TEXT PRIMARY KEY,
  dimension_id TEXT NOT NULL,
  code TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  axiom TEXT NOT NULL,
  explanation TEXT,
  shadow_form TEXT,
  truth_form TEXT,
  coach_questions_json TEXT,
  source_refs_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

## 5.3 Field semantics

`id`

internal stable identifier

`dimension_id`

foreign key to `truth_dimensions`

`code`

canonical principle code

example: `REL_001`

`title`

short, memorable principle name

example: `愛不等於接管`

`axiom`

compact truth statement

should be concise and reusable

`explanation`

optional longer explanation

`shadow_form`

distorted or egoic expression of this principle

example: `help becomes control`

`truth_form`

aligned or mature expression

example: `support without takeover`

`coach_questions_json`

optional reflective questions linked to this principle

`source_refs_json`

source provenance

can include document name, passage label, timestamp, or derived source

## 5.4 Principle writing rules

A principle should be:

reusable

concise

pattern-oriented

not tied to one exact story

semantically distinct from neighboring principles

Avoid:

vague slogans

duplicate principles with different wording

metaphysical claims without role in retrieval or coaching

titles too long for UI and indexing

## 5.5 Recommended principle seed format

```json
{
  "id": "p_rel_001",
  "dimension_code": "relationship",
  "code": "REL_001",
  "title": "愛不等於接管",
  "axiom": "支援不等於替對方活。",
  "explanation": "真正的愛允許他人承擔自己的生命。",
  "shadow_form": "把控制包裝成關心",
  "truth_form": "帶著界線的支援",
  "source_refs": ["核心機制：in spirit AI 神經系統"]
}
```

---

## 6. `truth_puzzles`

## 6.1 Purpose

A truth puzzle is the smallest retrievable unit in TruthOS.

This is the atomic knowledge object most directly used by:

semantic search

reflective reasoning

pattern matching

coaching response generation

A puzzle should capture:

a recurring human pattern

a common distortion

a reframed truth

a coaching prompt

a retrievable semantic fingerprint

This puzzle-based structure is what allows the system to turn long-form life teachings into a reasoning engine instead of a static bookshelf.

## 6.2 Recommended schema

```sql
CREATE TABLE truth_puzzles (
  id TEXT PRIMARY KEY,
  principle_id TEXT NOT NULL,
  dimension_id TEXT NOT NULL,
  title TEXT NOT NULL,
  statement TEXT NOT NULL,
  pattern_type TEXT NOT NULL,
  misbelief TEXT,
  truth_reframe TEXT,
  coach_prompt TEXT,
  trigger_signals_json TEXT,
  use_cases_json TEXT,
  tags_json TEXT,
  severity TEXT,
  source_doc TEXT,
  source_excerpt TEXT,
  embedding_text TEXT NOT NULL,
  is_seed INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

## 6.3 Field semantics

`id`

stable puzzle identifier

`principle_id`

foreign key to principle

`dimension_id`

foreign key to dimension

`title`

concise puzzle label

`statement`

visible explanation of the pattern

`pattern_type`

broad puzzle family

examples:

control

self-blame

emotional entanglement

projection

avoidance

perfectionism

`misbelief`

the distorted belief embedded in the pattern

`truth_reframe`

the corrective or liberating reframing

`coach_prompt`

reflective prompt that can guide the user inward

`trigger_signals_json`

optional early warning signals

examples:

`I keep repeating this`

`I feel guilty if I stop helping`

`I always end up angry`

`use_cases_json`

contexts where this puzzle commonly applies

examples:

family

work

partner

grief

money

self-worth

`tags_json`

lightweight semantic tags

`severity`

optional qualitative intensity

examples:

low

medium

high

recurring

`source_doc`

source document title

`source_excerpt`

short supporting excerpt or paraphrased anchor

`embedding_text`

canonical semantic retrieval text

must be optimized for vector search

`is_seed`

whether this row belongs to the seed dataset

## 6.4 Puzzle quality rules

Every good truth puzzle should include all of these:

one recognizable pattern

one recognizable distortion

one truth reframing

one coaching angle

one semantic retrieval fingerprint

A weak puzzle usually fails because it is:

too abstract

too poetic without structure

too story-specific

semantically redundant

missing misbelief or reframe

## 6.5 Puzzle examples grounded in your source direction

The following puzzle families are strongly supported by your source corpus:

self-blame / self-reproach

5哥：如何化解責備自己？

emotional blackmail / emotional entanglement

5哥：如何化解情緒勒索？

anger and moral projection

5哥-如何化解憤怒生氣？

perfectionism and definition conflict

5哥：如何化解完美主義

purification of motive / clearing inner impurity

淨化生命：斷捨離（5哥）

evolution / life growth through challenge

manifestation / money as exchange of love and trust

discernment / plausible is not truth

1️⃣111-覺幻機制：有道理未必是真理

## 6.6 Recommended puzzle seed format

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
  "trigger_signals": ["反覆替家人收尾", "停止幫忙就感到罪惡"],
  "use_cases": ["家庭", "伴侶", "助人關係"],
  "tags": ["拯救者", "界線", "關係"],
  "severity": "recurring",
  "source_doc": "核心機制：in spirit AI 神經系統",
  "source_excerpt": "把控制包裝成愛，會使關係變成壓力。",
  "embedding_text": "relationship 愛不等於接管 拯救者焦慮 界線 支援不是控制 家庭衝突 罪惡感"
}
```

---

## 7. `belief_logs`

## 7.1 Purpose

A belief log is not a knowledge object.
It is a transformation event record.

It captures:

what belief was active

how it changed

in what context

under which dimension / principle

This table turns reasoning sessions into longitudinal growth data.

This also aligns with your prior coach-review and reflection-oriented API direction, where the system is expected to track not only output but transformation trajectory.

8️⃣888-佟位 operating system：技術骨架…

## 7.2 Recommended schema

```sql
CREATE TABLE belief_logs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  case_id TEXT,
  belief_before TEXT NOT NULL,
  belief_after TEXT,
  tag TEXT,
  evidence_json TEXT,
  related_dimension_id TEXT,
  related_principle_id TEXT,
  created_at TEXT NOT NULL
);
```

## 7.3 Field semantics

`id`

stable log ID

`user_id`

user identifier

`case_id`

optional link to a broader case or session

`belief_before`

the original restrictive belief

`belief_after`

transformed or emerging new belief

`tag`

optional topical category

examples:

self-worth

grief

control

spirituality

fear

`evidence_json`

optional evidence or observation supporting the shift

`related_dimension_id`

linked truth dimension

`related_principle_id`

linked principle

`created_at`

time of entry

## 7.4 Belief log rules

Belief logs should be:

user-specific

time-bound

pattern-aware

grounded in an actual shift, not generic inspiration

Avoid:

logging every sentence as a belief log

storing vague affirmations

storing only “positive words” without contrast

## 7.5 Recommended belief log seed / runtime example

```json
{
  "id": "bl_20260312_001",
  "user_id": "u_001",
  "case_id": "case_001",
  "belief_before": "如果我不把事情處理好，我就是沒價值。",
  "belief_after": "我的價值不取決於我能否控制所有結果。",
  "tag": "self-worth",
  "evidence": ["家庭衝突中出現過度承擔模式"],
  "related_dimension_code": "belief",
  "related_principle_code": "BEL_001"
}
```

---

## 8. `blind_spot_archives`

## 8.1 Purpose

A blind spot archive records recurring failure patterns that remain active even when the user “knows the theory.”

This directly reflects your core mechanism design around the Consciousness Blind Spot Profile — the system should not only summarize or comfort, but identify why a person still gets lost despite knowledge, care, or technique.

✡️核心機制：in spirit AI 神經系統

## 8.2 Recommended schema

```sql
CREATE TABLE blind_spot_archives (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  trigger_pattern TEXT NOT NULL,
  known_theory TEXT,
  practical_failure_mode TEXT,
  suggested_anchors_json TEXT,
  related_puzzles_json TEXT,
  frequency INTEGER DEFAULT 1,
  last_seen_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

## 8.3 Field semantics

`id`

stable blind spot ID

`user_id`

user identifier

`title`

concise label for the blind spot pattern

`trigger_pattern`

what repeatedly activates the blind spot

`known_theory`

what the user already intellectually knows

`practical_failure_mode`

how the user still fails in lived behavior

`suggested_anchors_json`

prompts, reminders, or corrective anchors

`related_puzzles_json`

IDs or codes of linked truth puzzles

`frequency`

recurrence count or qualitative recurrence estimate

`last_seen_at`

last observed appearance

`created_at`, `updated_at`

timestamps

## 8.4 Blind spot design rules

A blind spot archive should answer:

what keeps recurring

what the user already “knows”

where knowledge still fails in practice

what anchor may help interrupt the loop

This is not the same as a belief log:

belief log = shift event

blind spot archive = recurring distortion pattern

## 8.5 Recommended blind spot example

```json
{
  "id": "bs_001",
  "user_id": "u_001",
  "title": "把責任感誤認成愛",
  "trigger_pattern": "家人失序時立刻想接管全部",
  "known_theory": "知道要有界線，也知道不能代替別人活",
  "practical_failure_mode": "一有危機就重新接手，之後又累又怨",
  "suggested_anchors": [
    "支援不等於接管",
    "先分清誰的責任"
  ],
  "related_puzzles": ["seed_relationship_001"],
  "frequency": 7
}
```

---

## 9. `embedding_text`

## 9.1 Purpose

`embedding_text` is the canonical vectorization field for truth puzzles.

It is not merely a copy of `statement`.

Its job is to maximize semantic retrieval quality.

This is crucial because LanceDB is intended to function as the precision retrieval layer for methods, principles, and truth units, not a blob store.

iN SPiRiT AI智慧系統 完整簡報構成草案

## 9.2 What `embedding_text` should contain

A good `embedding_text` typically combines:

dimension

principle concept

title keywords

statement essence

misbelief language

truth reframe language

use case signals

## 9.3 Recommended structure template

Example template:

`{dimension_code} {principle_title} {title} {statement_summary} {misbelief} {truth_reframe} {use_case_keywords}`

## 9.4 Example

Instead of only:

你以為自己在幫人，實際上可能是在逃避自己的無力感。

Prefer:

relationship 愛不等於接管 拯救者焦慮 你以為幫助其實是控制 如果我不救他就不夠有愛 支援不等於接管 家庭 伴侶 助人

## 9.5 `embedding_text` rules

do not make it too short

do not stuff it with unrelated keywords

do not turn it into unreadable spam

keep it semantically rich, compact, and aligned

## 9.6 When to regenerate `embedding_text`

Regenerate vector content when:

principle title changes materially

puzzle statement changes materially

tags / use cases significantly improve

retrieval quality drift is observed

---

## 10. Seed Dataset Standards

## 10.1 Seed philosophy

Seed data is not filler content.
It is the founding semantic core of TruthOS.

Seed data should be:

semantically distinct

structurally complete

retrievable

grounded in source material

appropriate for long-term expansion

## 10.2 Minimum seed files

Recommended seed files:

`dimensions.seed.jsonl`

`core_principles.seed.jsonl`

`truth_puzzles.seed.jsonl`

Optional later:

`belief_logs.example.jsonl`

`blind_spot_archives.example.jsonl`

## 10.3 Dimension seed requirements

Each row must contain:

`id`

`code`

`name_zh`

`name_en`

`description`

`order_index`

## 10.4 Principle seed requirements

Each row should contain at least:

`id`

`dimension_code`

`code`

`title`

`axiom`

Recommended extras:

`explanation`

`shadow_form`

`truth_form`

`source_refs`

## 10.5 Puzzle seed requirements

Each row should contain at least:

`id`

`dimension_code`

`principle_code`

`title`

`statement`

`pattern_type`

`misbelief`

`truth_reframe`

`coach_prompt`

`tags`

`use_cases`

`source_doc`

`embedding_text`

Recommended extras:

`trigger_signals`

`severity`

`source_excerpt`

## 10.6 Seed writing rules

Rule A — One puzzle, one main pattern

Do not cram five patterns into one row.

Rule B — One puzzle must contain a distortion and a reframe

Without that, retrieval will be shallow.

Rule C — Source provenance matters

Every seed should know where it came from, even if lightly paraphrased.

Rule D — Avoid duplicate semantics

Do not create ten puzzle rows that say the same thing with tiny wording changes.

Rule E — Seed for retrieval, not for literary beauty alone

If a row sounds pretty but retrieves poorly, it is weak seed.

---

## 11. Source Provenance Guidance

TruthOS seed design should draw from the documented source universe.

Strong source families already present in your corpus include:

Relationship and blind spots

核心機制：in spirit AI 神經系統

✡️核心機制：in spirit AI 神經系統

Discernment and hallucination boundary

覺幻機制：有道理未必是真理

1️⃣111-覺幻機制：有道理未必是真理

Life blueprint and reflection structures

靈性導向的研究與摘要 API

佟位 operating system：技術骨架＋語言靈魂

LanceDB memory discipline

LanceDB：「AI 的修行手冊」

iN SPiRiT AI智慧系統 完整簡報構成草案

Long-form life teachings

清理雜質

淨化生命：斷捨離（5哥）

如何化解責備自己

5哥：如何化解責備自己？

如何化解情緒勒索

5哥：如何化解情緒勒索？

如何化解憤怒生氣

5哥-如何化解憤怒生氣？

如何化解完美主義

5哥：如何化解完美主義

新進化：進化 / 覺醒 / 回歸真我

新顯化：內外皆富

新顯化：內外皆富5哥 [uNSb6_rJv6Y]

in spirit WordPress 文章彙整

湧泉匯聚：模型 fallback + quota_fallba…

These source families should be treated as structured seed reservoirs, not merely content archives.

---

## 12. Data Quality Checks

## 12.1 Dimension checks

unique code

stable order_index

no synonym duplicates

## 12.2 Principle checks

unique code

distinct axiom

valid linked dimension

not semantically duplicate with neighboring principle

## 12.3 Puzzle checks

valid dimension

valid principle

non-empty misbelief

non-empty truth_reframe

non-empty embedding_text

no obvious semantic duplication

## 12.4 Belief log checks

has belief_before

user-linked

not generic inspiration spam

## 12.5 Blind spot checks

recurring pattern described

known theory described

practical failure mode described

---

## 13. Governance Rules

## 13.1 Schema changes require migration planning

Do not casually rename:

dimension codes

principle codes

puzzle field names

embedding field names

## 13.2 Seed changes should be versioned

If a seed dataset changes materially:

record version

note source batch

note rewrite strategy

consider index rebuild requirement

## 13.3 Semantic changes require retrieval awareness

Changing text fields may change:

vector recall

principle grouping

query relevance

downstream reasoning quality

Therefore:
data edits are retrieval edits

---

## 14. Final Rule

TruthOS data is not just content.
It is reasoning substrate.

If the data model is clean:

retrieval improves

reasoning stabilizes

blind spots become legible

growth becomes trackable

If the data model is sloppy:

retrieval drifts

principles blur

puzzles duplicate

the system starts sounding wise while thinking badly

That is the whole game.

Keep the truth atoms sharp.


---

## 你現在已經有六塊正式檔案

放在 repo 根目錄就是：

```text
/Users/tongwei/.openclaw/inspirit-truthos/
  AGENTS.md
  PROJECT_RULES.md
  ARCHITECTURE.md
  OPERATIONS.md
  ENVIRONMENT.md
  DATA_MODEL.md
```

之後給 Codex 的完整前置句

你現在可以固定用這句開場：

```text
Before making changes, read AGENTS.md, PROJECT_RULES.md, ARCHITECTURE.md, OPERATIONS.md, ENVIRONMENT.md, and DATA_MODEL.md and follow them as the repository constitution, blueprint, runbook, configuration contract, and data model authority.
```

這樣它不是在瞎改 code，而是在一套完整宇宙法則裡施工。
