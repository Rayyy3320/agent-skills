---
name: selector-UI-patch
description: >-
  从 UI 组件市场（21st.dev 等）拿组件源码。用户给了组件页 URL、DevTools DOM
  片段、组件名或截图时用。不购买任何服务。触发词：抓源码、拿组件代码、
  extract component source、扒组件、21st 怎么拿代码。
agent_created: true
---

# selector-UI-patch

市场页是**索引**，组件数据在**预览渲染链路**里。
一条路：**页面能渲染预览 ⇒ 浏览器必然匿名下载过渲染产物 ⇒ 直接 GET 它。**

## 公理

- 预览 iframe 跨域嵌入 ⇒ 渲染产物必须是 CDN 上无鉴权的公开静态文件（否则匿名
  访客看不到预览）。**只要能看预览就能取 bundle**，与组件有没有开源出处无关。
- 压缩产物 ≠ 不可读：JSX 树、className 原文、props 属性名、displayName、handler、
  动效参数、演示数据全在。丢的只有注释、空行、内部变量名、import 路径。
- **拿不到原件 ≠ 拿不到源码**：产物信息足够时，重建等效源码是正规产出（分级见下）。

## 通道（按优先级）

| # | 通道 | 工具 | 产出 |
|---|---|---|---|
| 1 | 详情页 SSR | extract.py | demo（锚点）+ bundle URL + 对照图 |
| 2 | 预览 bundle 直取 | bundle.py | B 级或 C 级 |
| 3 | 浏览器渲染预览 DOM | 浏览器 | D 级兜底 |
| 4 | 上游开源站 / GitHub | 手动 | A 级（仅当页面明示 Source 或组件本是开源库原语） |

通道 4 垫底且非默认：社区独占组件走这步是纯损耗——实测翻 3981 文件仓库、
查 534 组件 registry、打 /r/ 端点，三路全空手。bundle 通道确实不通时再考虑。

## 产出分级（先定级，按级验收，按级声明）

| 级 | 是什么 | 验收 |
|---|---|---|
| A | 原始源码直取 | 无需 |
| B | 结构 1:1（编译树反推） | `--check compiled-tree.js 重建.tsx --demo demo.tsx`：className 全集 + props 三方对齐 + 动效 token |
| C | 等效实现（编译产物信息充分，逐字重建数据/逻辑/样式） | `--check inventory.json 重建.tsx`：class 词汇全出自 bundle + 数据/逻辑/依赖清单一致 |
| D | UI 等效（渲染 DOM 反推） | 目视对照 preview.png |

C 级声明句式（交付时原样给出）：「原始 .tsx 不可逐字还原（无 sourcemap）；
本件为等效实现，数据/逻辑/样式与原组件一致，变量名自起，依赖清单来自 bundle。」

## Runbook

1. **extract** — `extract.py <详情页URL> -o demo.tsx`。demo 薄壳是锚点，不是废料。
2. **bundle** — `bundle.py <详情页URL> -o out/`：自动发现 bundle URL → 下载 →
   displayName 锚（slug 转 PascalCase）→ 编译树。三种走向：
   - 树命中 → B 级。锚点是 `(VAR,"Name")` 转发引用时会自动追 `function VAR(){…}` 真身。
   - 名字不对 → 看 stderr「命名组件」清单找真名（社区组件命名常带前缀），
     `--name 真名` 重试。
   - 树提不出来 → 自动落全 bundle 清单 inventory.json（命名组件 / shadcn 原语
     依赖 / className 直方图 / 演示数据线索）→ C 级重建。
   SSR 没有 bundle URL 时上浏览器列 iframe 拿 src 喂给 bundle.py。
3. **reconstruct** — 按 compiled-tree.js 反推 JSX；compiled-subs.js 三类混居
   （兄弟子组件要重建｜shadcn 原语当依赖装｜radix/motion 内部忽略）；
   inventory.json 给 className 全集 / props / 动效 / 依赖 manifest。规则表见下。
4. **verify** — 按级跑 --check；B 级再加 `npx -y -p typescript tsc --noEmit
   --noResolve …`（必须 `-p typescript`，裸 `npx tsc` 拉到 npm 同名占位废包）；
   有 preview.png 时目视对照。
5. **report** — 报级别。B 级说明「结构 1:1，注释/内部变量名不可恢复」；
   C 级给声明句式；D 级说明丢了 handler/动效/props API。

## 反推规则表（编译产物 → 源码）

| 编译产物里长这样 | 源码里是什么 |
|---|---|
| `…},"InsuranceCard")` | 组件边界与名字（displayName 锚） |
| `u(dA,"ContributorsTable");` | 转发引用：真身在 `function dA(){…}`，追过去 |
| `({clientName:a,…})=>` | props 接口；属性名是原文，冒号后单字母是压缩局部名 |
| `function dA(){const[a,i]=x.useState(…)}` | 有状态函数组件；useState 解构名要自起 |
| `$.jsx(N2.div,{initial:{…}})` | framer-motion 的 `<motion.div>` |
| `$.jsx(w0,{…})` 且 w0 定义含 forwardRef/cva | shadcn 原语；displayName 清单 = 依赖 manifest |
| `children:["(",p,")"]` | JSX 子节点里的字面括号文本 |
| 图标全是短别名 | 对照预览渲染 DOM 的 lucide-xxx class（浏览器打开 bundle URL） |

## 防呆

- demo 薄壳 ≠ 组件实现（import 自己的块按定义是示例），别当源码交付，但别扔。
- 列表页不含源码，先进详情页。
- 死路不重试：SSR 没下发实现是架构事实；换锚点（--name / --props / --text），
  不是换 UA。
- 走通道 4 之前，先确认 bundle 通道真的不通（含浏览器列 iframe 这一手段）。

## 边界（如实告知用户）

- 只 GET 无鉴权的公开静态文件——浏览器渲染预览本来就要下载的东西；不碰 403
  的 registry 端点、不模拟登录、不重放 cookie。带鉴权的端点没有额外必要信息：
  B/C 级产出已满足重建需要。
- B 级丢注释、空行、内部变量名；C 级另丢变量名对应关系（自起名）；D 级丢
  handler、动效、props API。按级如实声明。
- bundle 被签名 URL 保护或强混淆到不可读时退 D 级，如实说明。

`scripts/`：`bundle.py`（通道 2 全流程 + 分级校验）、`extract.py`（通道 1）。
退出码语义见各脚本头部注释。
