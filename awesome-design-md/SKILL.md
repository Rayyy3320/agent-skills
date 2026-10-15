---
name: awesome-design-md
description: "Apply a named brand's design language using the bundled DESIGN.md library. Use for brand-specific UI colors, typography, components, and layout; not for generic design work."
---

# Awesome Design MD

A curated collection of `DESIGN.md` design-system documents extracted from popular products and brands. Each document is a plain-text design contract that an AI agent can read to generate UI consistent with that brand's visual language — the counterpart of AGENTS.md: AGENTS.md says how to *build* the project, DESIGN.md says how it should *look and feel*.

## When to use

- The user asks to make a UI "look like Linear / Stripe / Apple / Vercel / Notion …" or names a brand whose aesthetic they want.
- The user asks for a redesign, landing page, dashboard, or component set in a specific well-known design language.
- The user wants a concrete design-system reference (palette, type scale, spacing, component styles) before writing frontend code.

## How to use

1. **Pick the brand.** List available brands with `ls design-md/` (each subdirectory is one brand; `linear.app`, `stripe`, `apple`, `vercel`, `claude`, `cursor`, `supabase`, … — 74 in total).
2. **Read the document.** Open `design-md/<brand>/DESIGN.md` in full. It contains: visual theme & atmosphere, color palette with roles, typography rules & hierarchy, component stylings, layout & spacing principles, depth/elevation, do's and don'ts, responsive behavior, and an agent prompt guide.
3. **Apply it as a contract.** Use the documented tokens (color roles, font sizes/weights/letter-spacing, spacing scale, radii, borders/shadows) as the source of truth for the UI you generate — not as loose inspiration. Respect the "Do / Don't" section: e.g. Linear's accent is never decorative, Apple leans on whitespace and large display type.
4. **State the mapping.** Briefly tell the user which tokens/sections you applied and any place you deliberately deviated (e.g. font substituted because the brand font isn't freely available — most documents include a "Note on Font Substitutes").

## Document format

Each `DESIGN.md` starts with YAML frontmatter (`description`, `colors`, `typography` tokens) followed by markdown sections (`## Overview`, `## Colors`, `## Typography`, `## Layout`, …). If the user only needs a subset (e.g. just the palette), you may read the frontmatter + the relevant section instead of the whole file.

## Notes

- These documents describe *marketing-site and product aesthetics* of the brands; do not copy trademarked logos or claim affiliation.
- `design-md/<brand>/README.md` files are upstream pointers to getdesign.md and carry no design content — ignore them.
- Source: https://github.com/VoltAgent/awesome-design-md (MIT). Re-download upstream to update the collection.
