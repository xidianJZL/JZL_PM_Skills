---
name: JZL-PM-Make
description: |
  快速帮助产品经理把粗略产品想法定型成清晰、可严谨表述的产品构思。适用于产品构思、需求澄清、MVP 定义、用户场景梳理、JTBD 分析、信息架构和产品方案定型；可独立使用，也可作为 PRD 或原型制作前置步骤。

  当用户提到「帮我做一个产品」「我要做一个 XX 系统/应用/工具」「帮我梳理一下需求」「把想法定型」「PRD 前置」「产品构思」「产品定位」「用户场景」「JTBD」「产品定型」时使用本 skill。自动检测当前目录是否有现成工作区，自动补齐或新建 shaping/ 目录。
---

# JZL-PM-Make

目标：把用户的松散想法推进到「能写 PRD、能画原型、能向团队讲清楚」的状态。

## 文件约定

- **模板目录**：`{skill_root}/references/moban/`（存放所有 `.md` 模板文件，AI 不得修改模板框架）
- **工作区目录**：`./shaping/`（由 `init_workspace.py` 初始化，存放用户的实际填充内容）
- **提问手册**：`{skill_root}/references/shaping-playbook.md`

## 阶段定义

| 阶段 | 触发 | 更新文件 |
|------|------|----------|
| Stage 1 | 首次对话（无工作区） | 初始化 + 00-intake, 01-product-shaping , 05-open-questions.md, 06-shaped-brief|
| Stage 2 | 产品定位探索 | 01-product-shaping, 05-open-questions.md, 06-shaped-brief |
| Stage 3 | JTBD 挖掘 | 02-jtbd, 05-open-questions.md , 06-shaped-brief |
| Stage 4 | MVP 范围定义 | 03-scope, 05-open-questions.md, 06-shaped-brief|
| Stage 5 | 核心流程与页面 | 04-pages-and-flows, 05-open-questions.md, 06-shaped-brief |
| Stage 6 | 收尾确认 & 闭环校验 | 00-intake, 01-product-shaping, 02-jtbd, 03-scope, 04-pages-and-flows, 05-open-questions, 06-shaped-brief |
| Stage 7 | 定型稿输出 | 07-product-final-draft |

## 自动初始化（Stage 1 首次对话）

**Step 1：检测工作区**

检查当前目录是否存在 `shaping/` 目录或 `shaping/00-intake.md`：

```
os.path.exists("shaping/00-intake.md") or os.path.isdir("shaping")
```

**Step 2：若不存在，运行初始化脚本**

在当前终端目录下执行（当前工作区已确定）：

```bash
python3 {skill_root}/scripts/init_workspace.py
```

脚本会自动：
- 在当前目录创建 `shaping/`（不嵌套）
- 从 `{skill_root}/references/moban/` 读取所有模板文件
- 将模板内容复制到 `shaping/` 对应路径
- 解析 `产品名` 参数（若命令行未指定，则在首次对话时询问用户）

**Step 3：读取工作区文件**

初始化完成后，读取 `shaping/00-intake.md` 和 `shaping/01-product-shaping.md`，将用户已有输入填入文档，没有信息的地方保留【待确认】。

## 阶段推进逻辑

### 提问原则（严格遵守）

1. **严格按阶段顺序推进**：上一阶段未收敛，不得进入下一阶段。
2. **每次只问 4–5 个核心问题**：不一次性列出所有问题。
3. **追问真实动机**：多用"为什么不用现有方式？"逼出底层诉求。
4. **模糊回答必须追问澄清**：不得直接跳下一阶段。
5. **多选项必须排序**：出现多个用户/场景/问题时，要求用户按优先级排序，不允许同时推进。
6. **未经用户确认，禁止修改模板框架结构**。

### 阶段 2：产品定位探索

参考 `shaping-playbook.md` 中的【商业目标】【产品定位】【需求真实性验证】【目标用户分层】【产品形态】【北极星指标】章节，每次抛出 4–5 个问题，直到本阶段收敛，本轮对话才算结束。

### 阶段 3：JTBD 挖掘

参考 `shaping-playbook.md` 中的【JTBD】章节，进行 Job Story + 四力分析 + 任务分层提问，每次抛出 4–5 个问题，直到本阶段收敛，本轮对话才算结束。

### 阶段 4：MVP 范围定义

参考 `shaping-playbook.md` 中的【MVP范围】【成功标准】章节，明确必做、暂缓、不做，每次抛出 4–5 个问题，直到本阶段收敛，本轮对话才算结束。

### 阶段 5：核心流程与页面

参考 `shaping-playbook.md` 中的【产品细节】章节，梳理核心流程、页面架构、业务规则、数据指标，每次抛出 4–5 个问题，直到本阶段收敛，本轮对话才算结束。


## 每轮对话结束输出格式

每轮对话结束后，AI **必须**输出以下格式：

```md
【阶段结论】当前已确认内容

【仍待确认】当前仍存在的不确定项

【进入下一阶段理由】为什么当前信息足够继续推进
```

- **待确认问题**：本轮待确认问题，必须按照格式追加到 `shaping/05-open-questions.md`
- **本轮摘要**：本轮摘要，必须追加到 `shaping/06-shaped-brief.md`


## 每轮对话后的文档更新

每轮对话结束后，**必须**更新以下文件（读取模板 + 用户对话内容，填充到模板的对应区域）：

| 文件 | 更新内容 |
|------|----------|
| `shaping/00-intake.md` | 填入产品名、产品类型、用户原始想法、核心能力、已有材料 |
| `shaping/01-product-shaping.md` | 填入商业目标、一句话定位、目标用户、核心场景、核心价值、产品形态、北极星目标 |
| `shaping/02-jtbd.md` | 填入 Job Story、四力分析、功能/情感/社会性任务 |
| `shaping/03-scope.md` | 填入 MVP 做/暂缓/不做、成功指标、技术栈、约束条件 |
| `shaping/04-pages-and-flows.md` | 填入核心流程、页面清单、关键状态 |
| `shaping/05-open-questions.md` | 填如本轮需要澄清问题 |
| `shaping/06-shaped-brief.md` | 填入本轮的摘要 |



## 阶段 6：收尾确认与闭环校验

当 AI 认为关键信息已足够（满足定型通过标准）时：

1. 向用户输出【阶段结论】【仍待确认】【进入下一阶段理由】。
2. 提示用户确认产品定型摘要。
3. 用户确认后，将摘要追加到 `shaping/06-shaped-brief.md`（不覆盖历史）。
4. 进行**闭环校验**（参考 `shaping-playbook.md` 中的【闭环校验】章节），反向校验所有设计是否贴合核心定位与核心 JTBD。
5. 闭环校验完成后，对 `shaping/05-open-questions.md` 中所有遗留问题进行最终确认，更新状态。

定型通过标准（同时满足才进入 07）：

- 产品定位能用 1–2 句话准确表述
- 至少 1 个核心用户、1 个核心场景、1 条主流程明确
- MVP 范围有明确「做/不做/待确认」
- 关键业务规则、权限、数据对象没有含糊带过
- 未确认内容已集中写入 `shaping/05-open-questions.md`

## 阶段 7：输出产品定型稿

用户确认无误后：

1. 读取所有 `shaping/` 下的已填充文档。
2. 将内容全部填充到 `shaping/07-product-final-draft.md` 中对应的部分。
3. 输出最终定型稿供用户确认。

## 输出格式模板

在进入阶段 7 之前，需要向用户输出：

```md
## 产品定型摘要
- 产品定位:
- 目标用户:
- 核心场景:
- 核心价值:
- 产品形态：
- JTBD分析：
- MVP 范围:
- 技术栈：
- 约束条件：
- 核心数据模型：
- 页面与核心流程:
- 关键规则:
- 待确认问题:

请确认：以上是否可以作为后续 PRD/原型的基础版本?
```

## 模板修改规则

- **禁止**未经用户确认直接修改模板框架结构（指标题层级、表格列、章节顺序等）。
- 如需调整模板结构，必须先征得用户明确同意。
- 模板内容（填充内容）可在每轮对话后按需更新。
- `init_workspace.py` 会自动同步模板更新，无需修改脚本代码。
