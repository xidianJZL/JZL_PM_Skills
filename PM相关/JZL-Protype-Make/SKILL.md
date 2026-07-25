---
name: JZL-Protype-Make
description: 把产品描述、PRD 模块或定型摘要转成可浏览、可评审、可迭代的 HTML 原型工作台与高保真原型。适用于：原型设计、线框图、高保真视觉演示、页面关系画布、页面清单梳理和交互流转确认。触发条件：用户提到"画原型"、"生成原型"、"做一个原型"、"design a prototype"、"make a prototype"，或提供了 PRD/产品描述/功能列表并要求生成界面原型时。特性：工作区初始化、PRD 结构化解析（P0）、PRD 覆盖度校验（P0）、分支路径覆盖度校验（P0）、逐步确认画原型（每步预览+用户确认）、设计系统沉淀、画布可视化、Mock 数据规范。P0 功能全量内置，P1 核心体验内置，P2/P3 功能按需引用 references。
---

# JZL-Protype-Make

把产品描述、PRD 模块或定型摘要，转成可浏览、可评审、可继续迭代的 HTML 原型工作台与高保真原型。

**核心原则**：先理解，再计划；先确认，再实现；每步有日志，每步有状态，上一步完成才进入下一步。

---

## 0. 准备工作区

### 0.1 检测当前目录

检查当前目录是否已经是产品工作区（存在 `prototype/`、`shaping/`、`prd/`、`00-intake.md` 其一即视为已有工作区`{name}-workspace/` ）。

### 0.2 初始化工作区

如果当前目录不是工作区，先检查同级是否存在 `{name}-workspace/`；优先复用，不新建嵌套路径。

```bash
python scripts/init_workspace.py --name "<产品名>" --type P3
```

**调用位置**：
- **形式 A（推荐）**：在 skill 根目录 `JZL-Protype-Make/` 下执行（cwd = JZL-Protype-Make/）
- **形式 B**：在已有 `{name}-workspace/` 根目录下执行，用 `python ../JZL-Protype-Make/scripts/init_workspace.py ...`

**参数说明**（**严禁**传中文给 `--type` / `--name`）：

| 参数 | 取值 | 必填 | 说明 |
|------|------|------|------|
| `--name` | 任意 ASCII 字符串 | ✅ | 产品名称，**禁止中文**（用于目录名，避免空格） |
| `--type` | `P1`–`P8` 大写字母+数字 | ❌ | 产品类型；不传默认 `P3`。`P1` 社交娱乐 / `P2` 消费电商 / `P3` 企业工具 / `P4` 内容媒体 / `P5` 工具效率 / `P6` 金融支付 / `P7` 教育学习 / `P8` 健康运动 |
| `--force` | flag | ❌ | 强制重新生成所有模板文件（**会覆盖** `prototype/` 下已有文件） |
| `--workspace` | 绝对路径 | ❌ | 显式指定工作区根目录（多候选时用；见 §0.1） |

> **⚠️ 不要**写 `--type "<产品类型>"` 这种中文占位——argparse 会直接 `unrecognized arguments` 报错。正确：`--type P3`，**不带引号占位**。

### 0.3 确认工作区路径

初始化完成后，**调用 AskQuestion** 确认 `prototype/` 目录路径作为后续所有产物的根路径（选项："使用此目录 / 改用其他路径"）。

⏸️ **停顿点 ① → 等待用户回答 AskQuestion 后才进入阶段 1。**

---

## 1. 读取输入源（优先级顺序）

1. 用户本轮明确要求的页面或模块
2. `prd/PRD.md` 中相关模块
3. `shaping/06-shaped-brief.md`、`shaping/04-pages-and-flows.md`
4. 旧版根目录 `06-shaped-brief.md`、`04-pages-and-flows.md`
5. 任何用户提供的 Markdown/TXT 文件

如果没有任何输入，提示用户提供产品描述或 PRD 内容。

---

## 2. PRD 结构化解析（P0）

**目标**：从 PRD 原文提取结构化数据，作为生成和校验的基础。

### 2.1 读取 visual-brief TL;DR

如果 `prototype/visual-brief.md` 已存在，先读取其 TL;DR 区（文件前 30 行），了解已有的设计决策（产品类型、用户画像、风格、密度等）。如果 TL;DR 区为空或文件不存在，跳过此步。

### 2.2 提取结构化数据

从 PRD 原文解析并生成以下四个结构化清单，写入 `prototype/prd-parse.md`（参照 `references/prd-parse.md` 模板）。**按下面的章节定位精确抽取**，找不到对应章节时按"备选方法"降级。

#### F1 功能点清单

**主路径**（P0 主取来源，优先生效）：从 PRD 的 `## 功能需求总览` 章节读取 `### 功能模块划分` 表和 `### 功能清单` 各模块子表（编号、功能名、描述、优先级、依赖）。

**备选方法**（仅在主路径失效时使用）：如果 PRD 中没有 `## 功能需求总览` 章节，则改为遍历 `## 核心功能模块详述` 下各模块的 `#### 目标` 与 `#### 页面与交互` 两节，从描述中提取功能点（粒度比主路径粗，仅做兜底）。

> **判别标准**：标题严格匹配 `## 功能需求总览`（H2）。如果只有 H3 的"功能清单"而缺 H2 包裹，仍按"找不到"处理，降级到备选方法。

#### B1 分支路径清单

**主路径**（P0 主取来源，优先生效）：
1. 从 PRD 的 `### 主流程`（在 `## 产品方案概述` 之下）部分，提取所有 ```` ```mermaid flowchart TD ` ```` 代码块中的逻辑作为全局的路径
2. 从 `## 核心功能模块详述` 下各模块的 `#### 流程` 节，提取所有 ```` ```mermaid flowchart TD ` ```` 代码块中的逻辑作为各个模块的具体路径

**备选方法**（仅在主路径失效时使用）：如果上述来源中均未找到 mermaid 流程图，则改用文本搜索以下模式自行总结：
- "如果…则…" / "若…则…" / "成功 →" / "失败 →" / "{X}" 决策描述
- 模块详述中的 `#### 业务规则` 表的"触发条件"列
- `### 验收标准` 中的每个验收 Given/When/Then 对应 1 条分支

**抽取完成后**：把 mermaid 里的中文分支概括归纳（如"注册时选择手机号 / 选择邮箱"），保留原图作为补充引用。

#### S1 状态机清单

**主路径**（P0 主取来源，优先生效）：从以下三个位置抽取状态节点（去重合并）：
1. PRD 的 `### 状态机` 章节（在 `## 产品方案概述` 之下），提取所有 ```` ```mermaid stateDiagram-v2 ` ```` 代码块里的状态机
2. `## 核心功能模块详述` 下各模块的 `#### 状态说明` 表，提取所有条目
3. `### 状态流转汇总` 表（在 `## 异常处理与业务规则汇总` 之下）—— 提取每一条信息："实体"+"状态"+"允许的流转"+"触发规则"。**`状态流转汇总` 不存在则忽略**该来源，仅用 1 + 2 两个来源，不报错。

**备选方法**（仅在主路径三个来源均失效时使用）：识别所有状态名（待XX/已XX/进行中/草稿等）作为状态机节点。

**抽取要求**（主路径与备选方法共用）：
- 每个实体的状态节点列出（不限数量，按 PRD 实际描述来）
- 每个状态节点标注触发条件（什么操作导致进入该状态）
- 标注状态间流转关系（有向边），包括正向/分支/异常路径

**状态覆盖校验规则**（两层分开校验，不混用）：

> **第一层：业务状态完整性**（校验业务实体状态是否齐全）
> - 提取 PRD 中所有业务状态名
> - 检查每个业务实体是否覆盖了"正向路径上的所有状态"
> - 缺漏时在 prd-parse.md 中标注 `[GAP: 实体 <X> 缺状态 "<状态名>"]`，进入 AskQuestion 询问用户是否接受或补充

> **第二层：UI 态覆盖**（校验每个 Frame 的视图层状态，与 S1 业务状态独立）
> - 每个 Frame 至少覆盖 3 个 UI 态：
>   - 空态（无数据/默认状态）
>   - 正常态（有数据/加载完成）
>   - 异常态（加载失败/网络错误/无权限）
> - 3 态覆盖针对 Frame，不针对业务实体状态机
> - 缺态时在 page-map.md 的"Frame 状态覆盖要求"表中标注 `[GAP: <Frame ID> 缺 <空态/正常态/异常态>]`，进入 AskQuestion 询问用户是否补充

#### R1 业务规则清单

**主路径**（P0 主取来源，优先生效）：
1. 从 `## 核心功能模块详述` 下各模块的 `#### 业务规则` 表，提取所有"编号 / 规则 / 触发条件"行
2. 从 `### 业务规则汇总` 表（在 `## 异常处理与业务规则汇总` 之下）提取所有"编号 / 规则 / 来源模块"行。**`业务规则汇总` 不存在则忽略**该来源，仅用 1 这一来源，不报错。

**备选方法**（仅在主路径失效时使用）：提取所有枚举值、最大长度、权限关键词、字段校验规则作为来源，结合项目功能，生成业务规则。

**抽取规则**（主路径与备选方法共用）：
- 每条规则保留"编号 + 规则文本 + 触发条件 + 模块归属"四列
- 规则中的"待确认"列如有值，在 prd-parse.md 中同步保留 `Q-N` 引用，便于后续在 §open-questions 阶段追溯

### 2.3 输出并确认

将解析结果以 Markdown 表格展示给用户，说明：
- 共提取了 N 个功能点、F 个分支路径、S 个状态机节点、R 条业务规则
- 各清单的实际来源（主路径 / 备选方法 / 降级到了哪一步）
- 如有 `[GAP: 缺 X 态]` 或"备选方法被触发"的情况，必须显式标注
- 请用户确认是否有遗漏

⏸️ **§2 完成 → 调用 AskQuestion 询问"PRD 解析结果是否通过 / 补充遗漏项 / 重新解析"，等待确认后才进入 §3 。**

**与 §4 硬约束一致**：本步必须执行四件套——① 更新 `prototype/.step-log.json` 顶层 `current_step = 'Step-prd'` 与 `current_status = 'USER_REVIEW'`、② 同步更新 `steps[]` 中 `Step-prd` 元素的 `status = 'USER_REVIEW'`、③ 输出 sentinel `⏸️ PRD 解析完成，等待确认`、④ 调用 `AskQuestion`。**不得用"用户确认后"等软叙述替代**。

---

## 3. 生成计划（Step-by-Step Plan）

在开始任何视觉实现之前，先根据 F1/B1/S1/R1 清单和已确认的设计决策，生成一份逐步实现计划。

> **Step ID 命名约定**：所有 step_id 在 `prototype/.step-log.json` 中为字符串型。
> - 数字型（`Step-0`、`Step-1` ... `Step-14`）表示按顺序执行的步骤
> - 字母型（`Step-prd`）表示非数字序位的特殊步骤
> - 检查"上一步是否完成"时，**按 `steps` 数组中的顺序找前一条**，不依赖数字推算（详见 §4）

计划格式：

```
## 原型实现计划 — {产品名}
### 步骤 0（系统初始化）
- [ ] Step-0: 工作区初始化（由 init_workspace.py 完成）

### PRD解析（输入源处理）
- [ ] Step-prd: PRD 结构化解析

### 阶段一：视觉规范确认
- [ ] Step-1: 视觉风格选择（从 Step-1 权威风格表选择 1–6 号风格或混合 X+Y）
- [ ] Step-2: 更新 visual-brief.md TL;DR 区（沉淀决策）
- [ ] Step-3: 生成/确认 page-map.md（页面清单 + 状态覆盖 + 响应式策略）
- [ ] Step-4: 生成/确认 interaction-flow.md（主流程 + 分支路径 + 交互矩阵）
- [ ] Step-5: 生成/确认 terminology.md（术语表）
- [ ] 阶段一待确认点：风格选择、页面清单、流转路径、术语表

### 阶段二：线框图生成
- [ ] Step-6: 生成 canvas.html（页面画布，frames + links）
- [ ] Step-7: 生成 wireframe.html（线框图，覆盖所有 Frame）
- [ ] 阶段二待确认点：画布布局、线框图结构

### 阶段三：高保真原型
- [ ] Step-8: 更新 design-system/theme.css（基于选定风格的 tokens）
- [ ] Step-9: 生成高保真页面（按 page-map.md 顺序，每次一个页面）
- [ ] Step-10: 更新 canvas.html 中 frames 状态（全部置为 done）
- [ ] 阶段三待确认点：每个页面的预览确认

### 阶段四：完成与校验
- [ ] Step-11: PRD 覆盖度校验（对照 F1 清单检查每个功能点是否有对应 UI）
- [ ] Step-12: 分支路径覆盖度校验（对照 B1 清单检查每个分支是否有对应页面/状态）
- [ ] Step-13: Mock 数据规范检查（数据真实性、多样性）
- [ ] Step-14: 更新 decision-log.md（记录最终设计决策）
- [ ] 阶段四待确认点：覆盖度报告、校验结论
```

**每次只执行计划中的当前步骤**，不跳跃。每次步骤完成后：
1. 生成预览或更新对应文件
2. 说明本步骤的变更内容
3. 提出待确认点请用户提建议
4. 用户确认后，才进入下一步
5. 记录步骤状态到 `prototype/.step-log.json`

---

## 4. 每步执行与确认流程

**核心原则**：每步完成后**必须暂停**，调用 `AskQuestion` 等待用户明确确认，才进入下一步。下文"⏸️"标记 = 强制暂停点。

### 步骤状态机

每步遵循以下状态机：

```
TODO → IN_PROGRESS → USER_REVIEW → DONE（或 BACK_TO_IN_PROGRESS）
```

状态语义：
- **TODO**：未开始（步骤创建时的初始状态）
- **IN_PROGRESS**：AI 正在执行该步骤（生成文件、读模板、写代码）——**必须**在开始工作前一刻设置
- **USER_REVIEW**：AI 已完成该步骤的产物，**正在等待用户确认**——同时输出 sentinel + AskQuestion
- **DONE**：用户已确认通过

`.step-log.json` 顶层字段（与 `scripts/init_workspace.py` 的 `INITIAL_STEP_LOG` 严格对齐）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `current_step` | string | 当前正在执行的 `step_id`（如 `Step-0` / `Step-prd` / `Step-3`） |
| `current_status` | string | 当前步骤的 status（必须与 `current_step` 指向的步骤的 `status` 字段保持一致） |
| `selected_style` | object \| null | Step-1 完成后填入 `{id, name, is_hybrid, mix_components}`；初始化时为 `null` |
| `steps[]` | array | 步骤列表，元素 schema 见下 |

`steps[]` 元素 schema：

| 字段 | 类型 | 说明 |
|------|------|------|
| `step_id` | string | 如 `Step-0` / `Step-prd` / `Step-3`（**带连字符**） |
| `step_name` | string | 步骤中文名 |
| `status` | string | `TODO` / `IN_PROGRESS` / `USER_REVIEW` / `DONE` |
| `started_at` | string | ISO8601 时间戳（`TODO` 时为空串，进入 `IN_PROGRESS` 时填写） |
| `completed_at` | string | ISO8601 时间戳（`USER_REVIEW` 及之前为空串，进入 `DONE` 时填写） |
| `notes` | string | 步骤备注 |
| `feedback` | string \| undefined | 用户反馈意见（仅在 `USER_REVIEW` 退回 `IN_PROGRESS` 时填写；初始为空） |
| `substeps` | array \| undefined | 仅 `Step-9` 有，子步骤列表（见 §7 Step-9） |

### 进入 Step N 之前必须执行的检查（硬约束）

1. Read `prototype/.step-log.json`
2. 检查 `current_step` 与 `current_status` 一致性：若 `current_status === 'DONE'`，说明上一步已完成，可进入下一步；若 `current_status === 'USER_REVIEW'`，说明上一步尚未获用户确认，**必须先解决上一步的 AskQuestion**
3. 在 `steps` 数组中按顺序定位当前 `current_step`，找到**前一条** step（数组中前一个元素）
4. 断言前一条 step 的 `status === 'DONE'`
5. 若不满足，**不要继续**，先用 AskQuestion 询问用户是否要跳过/回退上一步

### 记录日志（每步三件套）

每次状态变更时，**同时**更新三个地方：

**A. 顶层字段**（`current_step` / `current_status` / `started_at`）：

```json
{
  "current_step": "Step-3",
  "current_status": "IN_PROGRESS",
  "current_step_name": "生成 page-map.md"
}
```

**B. `steps[]` 中对应步骤的字段**（`status` / `started_at` / `completed_at` / `notes`）：

```json
{
  "step_id": "Step-3",
  "step_name": "生成 page-map.md",
  "status": "IN_PROGRESS",
  "started_at": "2026-06-12T00:30:00",
  "completed_at": "",
  "notes": "根据 PRD 解析结果生成页面清单"
}
```

**C. 顶层 `current_step` 与 `steps[]` 中对应元素的 `step_id` 必须相同**（一致性硬约束）。

### 预览生成

视觉类步骤（线框图、高保真页面）必须先生成 HTML 预览，用 Read 工具读取后在对话中呈现代码关键片段，说明如何预览（"可保存为 HTML 直接打开"）。

### ⏸️ 每步硬性暂停协议

**每个 Step 完成后，必须在当轮消息末尾执行以下三件事，然后停止：**

1. 更新 `.step-log.json` 中当前步骤 `status = 'USER_REVIEW'`
2. 在对话中输出一行 sentinel：`⏸️ Step N 完成，等待确认：[本步骤产物]`
3. 调用 `AskQuestion` 工具发起确认问题（提供"通过 / 需要修改 / 跳过本步"等选项，详见 §9 表）

**绝对禁止**：
- 不要在用户确认前生成下一份文件
- 不要"顺手"把后续步骤一起做完
- 不要把 AskQuestion 当成可选项省略

### 用户反馈处理

用户提出修改意见时：
- 记录意见到 `prototype/.step-log.json` 的当前步骤 `feedback` 字段
- 把当前步骤状态从 `USER_REVIEW` 退回 `IN_PROGRESS`（即 §4 状态机中的 `BACK_TO_IN_PROGRESS` 转移）
- 理解修改需求，在当前步骤中修正
- 重新生成预览，再次提交 AskQuestion 确认
- 循环直到用户明确选择"通过"

> **自洽提示**：每次 BACK_TO_IN_PROGRESS 都必须从 §12.1 的 5 项自检重做一遍——避免"修了一半顺手往下做"。

---

## 5. 阶段一：视觉规范确认

### Step-1: 视觉风格选择

**风格表来源**（硬约束）：Step-1 展示的候选风格必须从下方"权威风格表"中选取。**严禁**凭空生成未在该表中定义的新风格名。

打开 `prototype/workbench.html`，向用户展示六个风格候选：

| 编号 | 风格名 | 适用场景 | 密度 | 参考设计 |
|------|--------|---------|------|---------|
| 1 | AI 平台风（Cohere） | AI/LLM 平台、企业工具、命令控制台 | D1–D2 | `design-md/cohere/DESIGN.md` |
| 2 | 开发工具风（Cursor） | IDE、开发者工具、代码编辑器周边 | D2–D3 | `design-md/cursor/DESIGN.md` |
| 3 | 数据库/DevOps 风（Supabase） | 后端平台、数据库、基础设施工具 | D2–D3 | `design-md/supabase/DESIGN.md` |
| 4 | 生产力/SaaS 风（Notion） | SaaS 产品、协作工具、All-in-one 工作台 | D2 | `design-md/notion/DESIGN.md` |
| 5 | 创意设计风（Figma） | 设计工具、创意平台、Creative SaaS | D1–D2 | `design-md/figma/DESIGN.md` |
| 6 | 媒体科技风（Wired） | 媒体、消费科技、内容平台、杂志风 | D1–D2 | `design-md/wired/DESIGN.md` |

**风格表的绑定关系**（防止编号漂移）：
- 风格表是本 Skill 内**唯一**的"风格编号 → 风格名"权威映射源
- 任何 AskQuestion 选项、决策日志、visual-brief.md 引用风格时，必须使用"编号 + 风格名"双标（如 `1 号 (AI 平台风/Cohere)`），**不得**只用编号
- 任何与上表冲突的"风格编号"描述，一律以上表为准
- 若需要新增/调整风格，必须先修改本表并更新所有引用位置

**用户选择动作**（输入域规则）：
- 选 X 号：单一风格
- 选 X+Y 号：混合风格，**必须**说明混合维度（"X 号的色彩 + Y 号的间距"）
- 选"自定义"：必须描述具体参考产品/截图/色卡/字体偏好，AI 不可凭空命名新风格

**确认后三件套**（与 §4 硬约束一致）：
1. 在 `prototype/.step-log.json` 中记录 `selected_style: { id: "X", name: "<风格名>", is_hybrid: false, mix_components: [] }`
2. 更新 `prototype/visual-brief.md` TL;DR 的"风格基线"行
3. 调用 AskQuestion 确认

⏸️ **Step-1 完成 → 调用 AskQuestion 询问"选定 X 号 (风格名) / 调整为混合 X+Y / 改用其他"，等待确认后才进入 Step-2。**

### Step-2: 更新 visual-brief.md TL;DR

在 `prototype/visual-brief.md` 顶部追加或更新 TL;DR 区（30 行以内）：

```markdown
> **TL;DR**
> - ProductType: P3-企业工具
> - Persona: U-C（中年，效率优先）/ U-S（熟练用户）
> - Style: 4 - 生产力/SaaS 风（Notion）
> - BrandColor: #5645d4
> - Density: D2
> - Layout: L-Dashboard / L-Split
> - Date: 2026-06-13
```

⏸️ **Step-2 完成 → 调用 AskQuestion 询问"TL;DR 是否通过"，等待确认后才进入 Step-3。**

### Step-3: 生成/确认 page-map.md

根据 F1 功能点清单，生成完整的页面清单（参考 `references/page-map.md` 模板）：

- Frame ID、页面名、类型、路径
- 每个 Frame 的**状态覆盖**（空/有数据/加载中/错误，至少 3 态）
- 响应式策略（桌面/平板/手机）
- 对应 PRD 中的来源章节

**漂移检测**：生成 page-map.md 后，检查 canvas.html 中的 frame 数量是否与 page-map.md 中的 Frame 数量一致。不一致时报错并暂停。

⏸️ **Step-3 完成 → 调用 AskQuestion 询问"page-map.md 是否通过"，等待确认后才进入 Step-4。**

### Step-4: 生成/确认 interaction-flow.md

根据 B1 分支路径清单，生成交互流转（参考 `references/interaction-flow.md` 模板）：
- 主流程（Mermaid flowchart）
- 分支路径表（触发条件、路径、对应 Frame）
- 交互一致性矩阵（删除需确认对话框、保存实时/手动、加载骨架屏等）

⏸️ **Step-4 完成 → 调用 AskQuestion 询问"interaction-flow.md 是否通过"，等待确认后才进入 Step-5。**

### Step-5: 生成/确认 terminology.md

从 PRD 和页面内容中提取术语表（参考 `references/terminology.md` 模板），确保所有标签、按钮文字、提示语在 prototype 中与术语表一致。

⏸️ **Step-5 完成 → 调用 AskQuestion 询问"terminology.md 是否通过"，等待确认后才进入 Step-6。**

---

## 6. 阶段二：线框图生成

### Step-6: 生成 canvas.html

将 page-map.md 中的每个 Frame 渲染为可拖拽的画布节点，links 渲染为 SVG 连接线。参考现有的 `canvas.html` 模板，将 `frames` 和 `links` 配置替换为实际数据。

⏸️ **Step-6 完成 → 调用 AskQuestion 询问"canvas.html 布局/连线是否通过"，等待确认后才进入 Step-7。**

### Step-7: 生成 wireframe.html

根据 page-map.md，生成线框图 HTML（参考 `starter-wireframe.html` 模板）。每个 Frame 生成对应的线框区域，覆盖其所有声明的状态（初始态/成功态/异常态）。

线框图要求：
- 结构完整，不依赖后端
- 数据用真实感 Mock 数据（参考 mock 数据规范）
- 桌面端和移动端均可用

⏸️ **Step-7 完成 → 调用 AskQuestion 询问"wireframe.html 结构是否通过"，等待确认后才进入 Step-8。**

---

## 7. 阶段三：高保真原型

### Step-8: 更新 design-system/theme.css

根据选定的视觉风格，更新 `prototype/design-system/theme.css` 中的 `:root` 变量：
- 主品牌色（--brand-* 系列）
- 背景/表面色（--bg, --surface）
- 文本/边框色（--text, --border）
- 间距与圆角基数
- 密度相关变量（行高、字号）

⏸️ **Step-8 完成 → 调用 AskQuestion 询问"theme.css tokens 是否通过"，等待确认后才进入 Step-9。**

### Step-9: 生成高保真页面（逐页进行）

**每次只生成一个页面**（按 page-map.md 的 Frame 顺序）。

**子步骤记录机制**（硬约束）：
- `Step-9` 在 `.step-log.json` 中有一个 `substeps` 数组（schema 见下）
- 每生成一页 → **必须**往 `substeps` 追加一条子步骤记录
- 每个子步骤的 `substep_id` 格式：`Step-9.{N}`，N 从 1 开始递增
- 子步骤也走 §4 状态机（`TODO → IN_PROGRESS → USER_REVIEW → DONE`）
- 进入 `Step-9.{N+1}` 之前必须断言 `Step-9.{N}.status === 'DONE'`

子步骤 schema（`substeps[]` 中每个元素）：

```json
{
  "substep_id": "Step-9.1",
  "frame_id": "login-page",
  "frame_name": "登录页",
  "status": "TODO",
  "started_at": "",
  "completed_at": "",
  "notes": ""
}
```

每页执行流程（每页都走一遍）：
1. **检查前一条子步骤**（如 `Step-9.2` 进入前查 `Step-9.1`）：读 `substeps` 数组最后一条，断言 `status === 'DONE'`；若是 `Step-9.{N}` 第一页（`substeps` 为空数组），跳过此检查
2. 追加新子步骤记录到 `substeps`，`status: 'IN_PROGRESS'`
3. 生成该页 HTML 文件（文件名建议 `frame-{frame_id}.html`）
4. Read 一次确认结构
5. 更新子步骤 `status: 'USER_REVIEW'`，输出 sentinel：`⏸️ Step-9.{N} [{frame_id}] 完成，等待确认`
6. 调用 AskQuestion 询问"通过 / 修改 / 跳过本页"
7. 用户选"通过" → 子步骤 `status: 'DONE'`；选"修改" → 回退到 `IN_PROGRESS`，回到第 3 步

**`Step-9` 父步骤推进规则**：
- 仅当 `substeps` 中所有子步骤 `status === 'DONE'` 时，父步骤才能进入 `DONE`
- 子步骤全部 `DONE` → 父步骤 `status: 'DONE'`，进入 `Step-10`

**绝对禁止**：一次性生成 N 个页面后才询问；不写子步骤记录直接生成页面；用"全部完成后统一写日志"。

高保真页面要求（参考 `starter-index.html` 模板）：
- 引用 `design-system/theme.css` 和 `design-system/prototype.js`
- 页面必须可点击演示主流程
- 覆盖 Frame 声明的所有状态
- Mock 数据真实：真实姓名、真实地名、合理价格、随机但合理的日期
- 移动端无重叠、无严重溢出

⏸️ **每生成一个高保真页面 → 必须调用 AskQuestion 确认后才生成下一个。**

### Step-10: 更新 canvas.html

确认所有页面生成完成后，将 `canvas.html` 中的 `frames` 状态（`status` 字段）全部更新为 `done`。

⏸️ **Step-10 完成 → 调用 AskQuestion 询问"canvas 状态更新是否通过"，等待确认后才进入阶段四。**

---

## 8. 阶段四：完成与校验

### Step-11: PRD 覆盖度校验（P0）

对照 F1 功能点清单，逐一检查每个功能点是否有对应 UI：

```
功能覆盖度: X/Y (Z%)
未覆盖: F1.x 功能名, ...
```

缺失功能点 → 记录为 Gap。

⏸️ **Step-11 完成 → 调用 AskQuestion 列出 Gap 项，每项询问"补充 / 接受 Gap / 标记为后续"，等待确认后才进入 Step-12。**

### Step-12: 分支路径覆盖度校验（P0）

对照 B1 分支路径清单，检查每个分支是否有对应页面/状态：

```
分支路径覆盖度: X/Y (Z%)
未覆盖: BR-x 分支名, ...
```

⏸️ **Step-12 完成 → 调用 AskQuestion 列出未覆盖分支，询问"补充 / 接受 Gap"，等待确认后才进入 Step-13。**

### Step-13: Mock 数据规范检查

检查所有页面 Mock 数据：
- 命名真实（禁止"测试1/测试2"）
- 价格合理（不用整数）
- 时间戳分布在合理范围内
- 边界值覆盖（正常 80%/边界 15%/极端 5%）

⏸️ **Step-13 完成 → 调用 AskQuestion 询问"Mock 数据是否通过"，等待确认后才进入 Step-14。**

### Step-14: 更新 decision-log.md

将所有最终设计决策记录到 `prototype/decision-log.md`（参考 `references/decision-log.md` 模板），包括风格选择、密度决策、关键设计变更。

⏸️ **Step-14 完成 → 调用 AskQuestion 询问"decision-log 是否通过 / 补记某条决策"，等待确认后才进入交付阶段。**

---

## 9. 停顿点（必须等待用户确认）

**下表中的每一个停顿点都是硬约束：必须调用 `AskQuestion` 工具发起问题，等待用户回答后才能进入下一步。**

| 停顿点 | 位置 | 确认内容 | AskQuestion 选项模板 |
|--------|------|---------|---------------------|
| ① 工作区初始化 | §0.3 完成后 | 目录路径正确 | "使用此目录 / 改用其他路径" |
| ② PRD 解析结果 | §2.3 完成后 | 功能点/分支/状态机/业务规则清单 | "通过 / 补充遗漏项 / 重新解析" |
| ③ 视觉风格 | Step-1 完成后 | 选定 1–6 号风格或混合 | "选 1 (AI 平台风) / 选 2 (开发工具风) / 选 3 (数据库 DevOps) / 选 4 (生产力 SaaS) / 选 5 (创意设计) / 选 6 (媒体科技) / 混合 X+Y" |
| ③.5 TL;DR | Step-2 完成后 | visual-brief.md TL;DR 区 | "通过 / 修改字段 / 改风格" |
| ④ 页面清单 | Step-3 完成后 | page-map.md 中所有 Frame | "通过 / 增删 Frame / 调整状态覆盖" |
| ⑤ 交互流转 | Step-4 完成后 | 流程图、分支路径、交互矩阵 | "通过 / 调整分支 / 补交互规则" |
| ⑥ 术语表 | Step-5 完成后 | 所有术语一致性 | "通过 / 增删术语 / 改译法" |
| ⑦ 页面画布 | Step-6 完成后 | canvas.html 中所有 frame 位置 | "通过 / 调整 frame 位置 / 调整连线" |
| ⑧ 线框图 | Step-7 完成后 | wireframe.html 结构 | "通过 / 调整结构 / 调整 Mock" |
| ⑧.5 theme.css | Step-8 完成后 | design-system/theme.css tokens | "通过 / 调整 token / 换风格" |
| ⑨ 每个高保真页面 | Step-9 每页完成后 | 当前页面预览 | "通过 / 修改本页 / 跳过本页" |
| ⑩ canvas 状态 | Step-10 完成后 | frames.status 全为 done | "通过 / 回到 Step-9 补页" |
| ⑪ PRD 覆盖度 | Step-11 完成后 | Gap 列表 | "逐项：补充 / 接受 Gap / 标记后续" |
| ⑫ 分支覆盖度 | Step-12 完成后 | 未覆盖分支 | "补充 / 接受 Gap" |
| ⑬ Mock 数据 | Step-13 完成后 | 命名/价格/边界值 | "通过 / 指定页面需重写" |
| ⑭ decision-log | Step-14 完成后 | 最终决策记录 | "通过 / 补记某条决策" |

**自检规则**：每轮消息结束时，AI 必须能在心里回答"我现在停在了哪一行的停顿点？"——如果答不出来，就说明跳步了，必须回退。

---

## 10. 交付检查清单

交付前检查：
- [ ] `prototype/workbench.html` 能展示风格候选并正确切换
- [ ] `prototype/canvas.html` 能展示所有 Frame 和跳转连线
- [ ] `prototype/wireframe.html` 能直接打开
- [ ] `prototype/index.html` 能直接打开，核心页面齐全
- [ ] 所有页面主导航、跳转、弹窗/抽屉/表单提交可用
- [ ] 移动端（375px 宽度）无重叠、无溢出
- [ ] PRD 功能覆盖度 ≥ 80%（Gap 已记录或已补充）
- [ ] 分支路径覆盖度 ≥ 80%（Gap 已记录或已补充）
- [ ] Mock 数据真实且多样
- [ ] `prototype/.step-log.json` 记录完整（所有步骤 DONE）
- [ ] 新增设计假设写入 `prototype/open-questions.md`
- [ ] 所有规范引用写入代码注释（如 `/* §2.1 btn-lg */`）

---

## 11. 附录：参考模板索引

使用参考模板时，按需读取：

| 文件 | 用途 |
|------|------|
| `references/visual-brief.md` | 视觉规范完整模板（TL;DR + 组件规范） |
| `references/page-map.md` | 页面清单标准模板（Frame + 状态覆盖 + 响应式） |
| `references/interaction-flow.md` | 交互流转标准模板（主流程 + 分支 + 矩阵） |
| `references/open-questions.md` | 设计假设跟踪模板 |
| `references/prd-parse.md` | PRD 结构化解析模板（F1/B1/S1/R1 清单） |
| `references/terminology.md` | 术语表模板 |
| `references/decision-log.md` | 设计变更日志模板 |
| `references/prd-coverage.md` | PRD 覆盖度报告模板 |
| `references/component-inventory.md` | 组件清单模板 |
| `starter-canvas.html` | 页面画布模板（含 frames + SVG links） |
| `starter-wireframe.html` | 线框图模板（Step-7 输出 wireframe.html 的样式参考） |
| `starter-index.html` | 高保真页面模板（Step-9 输出 frame-{frame_id}.html 的样式参考） |

---

## 12. 逐步确认原则

1. **计划先行**：在开始任何视觉工作之前先生成完整计划，用户了解全貌。
2. **每步独立**：每个 Step 聚焦一个目标，不混合多个任务。
3. **预览驱动**：视觉类步骤必须先生成预览，用 Read 工具读取后在对话中说明预览方式。
4. **确认解锁**（硬约束）：进入 Step N 之前必须 Read `prototype/.step-log.json`，断言 Step N-1 的 `status === 'DONE'`。若不满足，禁止继续，先 AskQuestion。
5. **日志记录**：每步都有状态记录，可追溯。
6. **校验闭环**：最后有覆盖度检查，发现问题与用户确认后修复。

### 12.1 跳步自检（每轮消息发送前执行）

在发送当轮消息前，AI 必须完成以下自检：

- [ ] 本轮只完成了一个 Step（或一个 Step-9 子步骤）
- [ ] `.step-log.json` 中当前步骤（或子步骤）的 `status` 已走过完整路径：`TODO → IN_PROGRESS → USER_REVIEW`（不是直接跳到 `USER_REVIEW`）
- [ ] 顶层 `current_step` / `current_status` 与 `steps[]` 中对应元素已同步（一致性硬约束）
- [ ] 对话中输出了 `⏸️` sentinel
- [ ] 调用了 `AskQuestion` 工具
- [ ] **没有**继续生成下一份文件
- [ ] **Step-9 子步骤额外检查**：
  - 若当前是 `Step-9.{N}` 第一页（`substeps` 为空数组）：无需检查前一条子步骤
  - 若 `substeps` 非空：进入前一条子步骤 `Step-9.{N-1}.status === 'DONE'`
  - 每完成一页就追加一条子步骤记录，不允许"全部完成后统一写日志"

任意一项未满足 = 跳步，必须修正后再发。
