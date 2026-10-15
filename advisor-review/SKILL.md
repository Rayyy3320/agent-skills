---
name: advisor-review
description: "Provide one independent, read-only second-model opinion when the user explicitly requests an advisor or second-model review. Do not invoke implicitly or modify repository state."
---

# Advisor Review

Use a second model to reduce a specific uncertainty, not to create another workflow layer.

## Scope

- This skill applies only to the current explicit request. Do not claim that an advisor mode persists across turns or projects.
- Keep the question narrow. Do not expand into a repository-wide review, routine stage gate, or recurring checkpoint unless the user explicitly asks for that scope.
- A second opinion is most useful for a high-impact decision, a diagnosis that remains uncertain, or a bug that resisted reasonable attempts. It is not required merely because shared code changed.

## Boundaries

- The user and primary executor retain all decisions and write authority.
- The advisor must not edit files, commit, send messages, mutate external systems, or create repository artifacts.
- The advisor may inspect files and diffs and run clearly non-mutating checks when they materially improve the answer. If useful evidence requires mutation, stop and recommend the check to the primary executor.
- Do not delegate to further reviewers or review the review.

## Request the opinion

Give the advisor only:

```text
Goal or decision: <one sentence>
Evidence scope: <specific files, diff, or reproduction>
Constraints: <only constraints that affect the answer>
Question: <one concrete question, up to three only when inseparable>
```

For an independent design or architecture opinion, avoid supplying the primary executor's preferred answer before the first pass. For debugging, include the minimal reproduction, expected versus actual behavior, and verified facts; include prior attempts only when they prevent repetition.

## Required output

- Lead with a verdict that answers the question.
- Return at most three material findings, each with evidence, impact, and the smallest useful recommendation.
- State meaningful uncertainty or missing evidence plainly.
- Omit nits and speculative improvements unless the user requests exhaustive review.
- If nothing would change the decision, say **no material issue** and stop.

## Integration

The primary executor evaluates the advice and continues through the project's normal implementation and verification path. Surface only decision-changing findings to the user; do not create a triage document, rejection log, task mirror, or persistent advisor state. One pass is the default; follow up only for a specific unresolved question.
