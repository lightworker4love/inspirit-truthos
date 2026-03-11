# TruthOS Schema

## Core Data Model
- `truth_dimensions`
- `core_principles`
- `truth_puzzles`
- `belief_logs`
- `blind_spot_archives`

## Table Descriptions
- `truth_dimensions`: stores the 12-dimension truth taxonomy.
- `core_principles`: stores reusable principles linked to dimensions.
- `truth_puzzles`: stores puzzle-level truth units.
- `belief_logs`: stores user belief snapshots.
- `blind_spot_archives`: stores recurring blind spot records.

## Main Relationships
- `core_principles.dimension_code -> truth_dimensions.code`
- `truth_puzzles.dimension_code -> truth_dimensions.code`
- `truth_puzzles.principle_code -> core_principles.code`

## JSON Field Rules
Round 1 stores list-like values as JSON text strings inside SQLite.
Affected fields:
- `tags`
- `use_cases`

## Index Suggestions
- unique index on `truth_dimensions.code`
- unique index on `core_principles.code`
- unique index on `truth_puzzles.id`
- index on `truth_puzzles.dimension_code`
- index on `truth_puzzles.principle_code`
- index on `belief_logs.user_id`
- index on `blind_spot_archives.user_id`
