---
name: ui-worker-gate
description: "Coordinate shared UI constraints, component and data contracts, and file ownership when delegating one shared UI product to multiple workers. Do not use for ordinary single-worker UI work or independent design alternatives."
---

# UI Worker Gate

Coordinate only the constraints needed for workers to contribute to one shared UI product.

1. Identify shared constraints from approved decisions, the existing implementation, and valid visual references. Distinguish current behavior from approved targets, and clarify stale or conflicting references that affect the work. Do not create a new authority document by default.
2. Before dispatch, distinguish visual exploration from implementation. Exploration fixes product goals, necessary data semantics, and non-negotiable constraints; implementation agrees on the necessary shared visual language, design tokens, component interfaces, and data contracts. Leave local design choices to workers within those constraints.
3. Assign clear ownership for shared components, tokens, and files. Avoid unnecessary shared edits; in a shared checkout, give each shared file one writer and keep page-specific work within existing page or component boundaries. When parallel edits to the same files are necessary, use isolated branches or worktrees and plan integration. Isolation separates writes but does not resolve semantic conflicts.
4. Pause only tasks whose unresolved conflicts affect shared contracts, cause write collisions, or create clear rework; state the specific dependency and let independent tasks proceed. Give each worker an observable goal, modification scope, relevant shared constraints, and a delivery interface.
5. Assign one integrator, which may be the coordinating agent. Verify the changed critical paths in a real browser and inspect screenshots for visual and interaction consistency. Check observable behavior; assert wording or DOM structure only when it is itself a requirement.

Use existing project structure and tools; do not add locks, state files, or a coordination framework without a demonstrated need.
