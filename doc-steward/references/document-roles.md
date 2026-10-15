# 项目文档职责速查

这是**常见职责参考，不是 OpenAI 规定的文件清单**。先看项目已明确的分工和实际内容：文档名不能单独决定职责；合理的既有约定优先。只在职责或归属存在实际歧义时使用本表。

## 入口、指令与协作

| 文档 | 主要回答 | 边界／常见误用 |
| --- | --- | --- |
| `README.md` | 项目是什么、怎样开始、关键知识在哪。 | 项目入口，不复制全部需求、架构或进度。 |
| `AGENTS.md` | Agent 在**其生效范围内**遵守哪些长期项目约束，去哪查资料。 | Codex 指令文件；不放临时任务、流水账和冗长手册。 |
| `SKILL.md` | 哪类专项任务应如何使用工具、知识与资源。 | 可复用工作流，不当作项目百科或通用指令垃圾桶。 |
| `CONTRIBUTING.md` | 贡献者怎样搭建环境、提交变更和参与评审。 | 没有外部协作需求就未必需要。 |

## 产品、系统与决策

| 文档 | 主要回答 | 边界／常见误用 |
| --- | --- | --- |
| `PRD.md` / 产品说明 | 为谁解决什么问题，业务目标、场景、范围和约束是什么。 | 已定需求与待定假设要分开；不写函数级实现或开发日志。 |
| `spec.md` / `specs/` | **本次或某功能应满足什么**：行为、规则、边界、验收结果。 | Spec 也可指技术规格；按项目约定，避免与 PRD 重复。 |
| `architecture.md` | 模块、服务、数据或产品信息架构的边界与关系。 | 区分当前架构与目标架构；不积累逐次改动日志。 |
| `design.md` | 项目约定的视觉、交互、设计系统，**或**技术详细设计。 | `design` 含义高度依赖项目，不能按文件名推断。 |
| `RFC.md` / `proposal.md` | 尚未批准的方案、备选项和权衡。 | 不冒充正式决策、目标规范或当前实现。 |
| `ADR-*.md` / 决策记录 | 重要决策的背景、结论、理由及状态。 | 记录难以从代码还原的决策依据；不逐条记录日常修改。 |
| `API.md` / `schema.md` / Reference | 接口、数据结构、参数、错误与兼容约定是什么。 | 优先引用或生成自代码/Schema，避免人工维护两个事实源。 |
| `TESTING.md` / 测试策略 | 在确有必要时说明难以从代码与配置推断的测试约束、环境和策略。 | 不重复测试代码与 CI 配置，也不要求每个项目单设。 |

## 计划、操作与发布

| 文档 | 主要回答 | 边界／常见误用 |
| --- | --- | --- |
| `roadmap.md` | 后续阶段目标、优先级和未完成里程碑。 | 不是每次修改的进度日志。 |
| `plan.md` / 某次执行计划 | 某项复杂任务怎样实施、有哪些依赖与进展。 | 临时执行状态不自动变成永久规范。 |
| `PLANS.md` | **在 OpenAI ExecPlan Cookbook 示例中**，用于规定何时/怎样编写复杂执行计划。 | 不是某次 `plan.md`，也不是所有项目必须有。 |
| `RUNBOOK.md` / `OPERATIONS.md` | 如何重复执行发布、运维、排障和恢复动作。 | 一次性排查不需要永久 Runbook。 |
| `DEPLOYMENT.md` | 环境、部署、发布与回滚的具体操作。 | 简单项目的短命令可放 README。 |
| `CHANGELOG.md` | 面向使用者的版本发布变化。 | 不复制 Git 提交或内部每日记录。 |
| `SECURITY.md` | 对外漏洞报告、安全政策或特定安全边界。 | 没有实际需要不新建泛泛的安全口号文档。 |

## 容易混淆的关系

- **现状 vs 目标**：代码、配置和运行结果说明当前已实现行为；经确认的 PRD、Spec 与设计说明表达目标。实现偏离目标不自动证明目标过时。
- **决定 vs 提案**：已确认决策不能被尚未批准的新方案覆盖；ADR 记录重要选择的理由，RFC 讨论尚待决定的选项。
- **目标 vs 执行**：PRD/Spec 关注预期结果，Plan 关注落地步骤，Roadmap 关注阶段顺序；同一项目可以合并载体，但不要混淆信息状态。
- **重复 vs 必要概述**：为不同读者提供不同层级的摘要是合理的；反复独立维护同一可变事实而产生冲突时，保留主位置并用链接或可靠生成替代复制。
- **命名 vs 职责**：已有文档的明确约定优先于本表；缺少约定时才用上述默认含义判断内容归属。

## 依据

- [OpenAI：Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [OpenAI：Harness engineering](https://openai.com/index/harness-engineering/)
- [OpenAI：Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans)
- [OpenAI：Skills / SKILL.md 与 references](https://developers.openai.com/api/docs/guides/tools-skills)
