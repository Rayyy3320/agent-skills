---
name: ui-design-guide
description: "为 UI/UX 设计、视觉优化、截图还原和设计评审提供构图、层级、排版、交互与素材知识。需要这些设计判断时按问题选读参考；不用于纯业务逻辑、构建或无界面变化的代码整理。"
metadata:
  version: "0.22.1"
  upstream_skill: "oil-ui-pro"
  upstream_version: "0.22.1"
  compatibility: "设计参考与工具为宿主中立资源；截图和对比工具的依赖按需检查，独立评审需要已授权的隔离执行能力。"
---

# UI Design Guide

从产品任务、品牌和真实内容推导视觉方向，让构图、字体、色彩、素材和交互形成一致的表达。视觉品质与功能正确性分别判断，保留用户已确认的设计决定。

## 如何使用设计知识

识别当前最需要的设计判断，只读取下表对应资料中的相关部分，将知识应用到这次画面、交互或建议中。已有品牌、参考和已确认决定作为判断依据；不因加载 Skill 而重新探索整个产品。

参考中的方法、示例和检查点用于解决当前问题，不组成必须依次完成的开发流程。普通局部修改沿用当前线程的工作方式，不自动追加候选、设计卡、报告、全面走查或评审。

## 按需读取设计知识

| 当前问题 | 参考 |
| --- | --- |
| 新视觉方向或品牌表达 | [设计方向](references/design-direction.md)；说服型页面需要概念时读 [概念](references/direction-concept.md) |
| 已有页面精修 | [整理已有页面](references/existing-polish.md)；涉及共享组件或规范时读 [存量项目](references/existing-project.md) |
| 改流程或增加界面功能 | [存量流程](references/existing-project-workflow.md)、[交互与状态](references/interaction-and-state.md) |
| 截图还原、布局、滚动或浮层 | [布局与视口](references/layout-and-viewport.md)、[空间与浮层](references/layout-surfaces.md) |
| 字体、色彩、层级或细节 | [视觉语言](references/visual-language.md)、[视觉精修](references/visual-polish.md) |
| 单个组件设计 | [组件](references/component.md) |
| 摄影、插画、品牌素材或 3D | [素材](references/media.md) |
| 交互反馈或动效 | [动效](references/motion.md)；确需滚动叙事时读 [滚动叙事](references/scroll-narrative.md) |
| 用户要求并排比较 | [风格对比页](references/style-explorer.md) |
| 截图、录屏或对比工具的具体用法 | [工具](references/tools.md) |
| 用户要求独立评审 | [派发协议](references/visual-review.md)、[评审复核](references/review-loop.md) |

不预先加载全部参考，不为满足参考中的表现手法而增加任务外的素材、动效或依赖。优先复用项目和宿主已有工具。

## 工具与专项工作

验证由用户目标、实际改动风险和项目约定决定。画面证据用于判断当前设计问题，已有有效证据可复用；没有新风险、变化或失败依据时不追加检查。

- 多方向比较仅在用户要求或重要分歧确需画面判断时使用；不固定候选数量。
- 独立评审仅在用户要求或已授权且能解决重要不确定性时使用；评分不作为默认完成阈值。
- `--evidence` 全套取证仅在明确要求完整证据包时使用。局部修改、普通评审和交付无需自动录屏、遮字图、200% 图或全状态截图。
- 当前目标达到后交付，不把可选提升变成必做任务；只说明实际结果、必要验证和有实质影响的未验证项。

本 Skill 是基于 Oil UI Pro 的本地定制版。官方更新保留在独立的 `oil-ui-pro` 原版目录；需要同步上游知识时对比后定向合入，不使用原版更新器覆盖本目录。
