# agent-skills

A personal collection of **agent skills** — self-contained instruction packages that extend AI coding agents (Codex, Claude, and compatible runtimes) with focused capabilities: UI/UX design, verification, project governance, and reverse engineering.

Each skill is a directory containing a `SKILL.md` (front-matter metadata + instructions), plus optional `references/`, `scripts/`, `assets/`, and `agents/` folders.

## Skills

| Skill | Description |
| --- | --- |
| [`advisor-review`](./advisor-review) | Provide one independent, read-only second-model opinion when the user explicitly requests an advisor or second-model review. |
| [`awesome-design-md`](./awesome-design-md) | Apply a named brand's design language using the bundled `DESIGN.md` library. |
| [`beautify-github-readme`](./beautify-github-readme) | Redesign GitHub README homepages or create project-native pure SVG, hybrid SVG/PNG/WebP, and opt-in animated GIF assets. |
| [`create-verification-skill`](./create-verification-skill) | Generate a project-local verification skill that drives your app the way a user does. |
| [`css-native`](./css-native) | Build zero-dependency web motion and visual effects with modern CSS. |
| [`design-dna`](./design-dna) | Extract a reference design into structured Design DNA — tokens, qualitative style, and visual effects — or apply an existing DNA JSON to new content. |
| [`doc-steward`](./doc-steward) | 对齐新方案与已有决策及项目文档，审计或修复文档职责、冲突、重复和失效信息。 |
| [`draw-ui`](./draw-ui) | 设计 App、后台、游戏界面或完整落地页，并按需还原为 HTML/CSS、现有前端项目或微信小程序。 |
| [`maintain-verification-skill`](./maintain-verification-skill) | Audit and update a project's verification skill and feature map through source inspection and live feature verification. |
| [`oil-icon`](./oil-icon) | 通过宫格生图、切分和去背景制作风格统一的透明 PNG 图标集合。 |
| [`project-governance`](./project-governance) | Audit or minimally repair project instructions, agent coordination, ownership, handoffs, or verification mechanisms. |
| [`reverse-engineer-anything`](./reverse-engineer-anything) | Reverse engineer native, managed, Electron/JavaScript, packaged, firmware, and browser targets with REA. |
| [`root-cause-review`](./root-cause-review) | 诊断反复出现、已有修复失败、补丁持续累积或局部修复引发回归的问题。 |
| [`selector-UI-patch`](./selector-UI-patch) | 从 UI 组件市场（21st.dev 等）拿组件源码；支持组件页 URL、DevTools DOM 片段、组件名或截图。 |
| [`ui-design-guide`](./ui-design-guide) | 为 UI/UX 设计、视觉优化、截图还原和设计评审提供构图、层级、排版、交互与素材知识。 |
| [`ui-worker-gate`](./ui-worker-gate) | Coordinate shared UI constraints, component and data contracts, and file ownership when delegating one shared UI product to multiple workers. |

## Installation

Copy the skill folder you want into your agent's skills directory:

```bash
# Codex
cp -R <skill-name> ~/.codex/skills/

# Claude Code
cp -R <skill-name> ~/.claude/skills/
```

Restart or reload the agent so it picks up the new skill. A skill becomes active once its directory (with `SKILL.md`) is present and enabled in your agent's config.

## Notes

- **`design-dna`** ships optional Node scripts under `scripts/`. `node_modules/` is **not** included — run `npm ci` inside `design-dna/scripts/` if you want the deterministic color-measurement tooling.
- **`draw-ui`** and **`oil-icon`** call image-generation services. Their `credential-ui` helper stores API keys in the **OS keychain** (macOS Keychain / Windows Credential Manager / Linux Secret Service) or reads them from environment variables (`OPENAI_API_KEY`, `ZENMUX_API_KEY`, …). **No keys are stored in this repository.**
- Scripts that shell out may assume macOS; check each `SKILL.md` for platform-specific requirements.

## License

Licenses vary per skill — see the individual `LICENSE` / `README` files inside each skill directory where present. Skills without an explicit license are shared for reference use.
