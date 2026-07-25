---
name: JZL-skill-LLM-check
description: |
  对 Skill 包进行 LLM 缺陷审查的工具。审查 Skill 包（SKILL.md + scripts/ + evals/ + references/），对照 22 条 LLM/Agent 缺陷逐项打分，输出"有没有问题、有的话在哪、怎么修"的审查报告。
  
  **触发条件（必须满足）：**
  - 用户明确表达"对某某 skill 做 LLM 缺陷检查/审查"
  - 触发关键词（必须包含其一）：`LLM 缺陷`、`LLM 缺陷检查`、`LLM 缺陷审查`
  - 用户 @ 了 skill 路径或目录
  
  **典型用户输入：**
  - "对这个 skill 做 LLM 缺陷检查" + @skill 路径
  - "@/path/to/skill，做 LLM 缺陷审查"
  
  **不触发的情况：**
  - "帮我看看这个 skill 写得怎么样"（缺少"LLM 缺陷"语义）
  - "对比一下这两个 skill"（缺少"LLM 缺陷"语义）
  - "优化这个 skill"（缺少"LLM 缺陷"语义）
---

# JZL-skill-LLM-check

> 对 Skill 包进行 LLM 缺陷审查的工具。审查 Skill 包，对照 22 条 LLM/Agent 缺陷逐项打分，输出"有没有问题、有的话在哪、怎么修"的审查报告。

## 核心资源（自包含）

- **检查清单**：`references/22-checks.md` — 22 条缺陷清单 + 判定要点
- **Markdown 报告模板**：`references/markdown-report-template.md`
- **JSON 报告模板**：`references/json-report-template.md`
- **初始化脚本**：`scripts/init-workspace.sh` — 工作空间初始化脚本（必须执行此脚本创建 `./LLM-check-workspace/` 目录）
- **测试用例**：`evals/test-cases.md` — 验证测试场景

## 工作流

7 步自动审查，无需人工干预：

```
1. 工作空间初始化
   → 执行 scripts/init-workspace.sh 脚本
   → 在当前路径创建 ./LLM-check-workspace/ 工作目录

2. 加载
   → 主动读取用户 @ 的 skill 文件/目录（SKILL.md + scripts/ + evals/ + references/）

3. 解析
   → 把 skill 内容结构化，提取关键字段（指令、示例、依赖、工具调用等）

4. 逐项审查（核心价值 + 高风险）
   → 对照 22 条缺陷清单逐项判定
   → 每个判定包含：通过状态 + 证据（引述待审查 skill 原文）+ 可执行解决方案

5. 汇总
   → 计算通过数/总数、生成分级（高/中/低风险）

6. 输出
   → 按模板生成 Markdown + JSON 双格式报告
   → Markdown 模板：references/markdown-report-template.md
   → JSON 模板：references/json-report-template.md

7. 落盘
   → 把双格式报告写入 ./LLM-check-workspace/ 目录
```

## 输入

**格式：** 用户 @ skill 文件路径或目录路径

**示例：**
```
@/path/to/my-skill/
```

**处理逻辑：**
- 路径存在 → 继续
- 路径不存在 → 直接返回失败原因
- 结构不完整（如缺少 SKILL.md）→ 返回失败原因

## 输出

### 报告格式

详见模板文件：
- **Markdown 报告**：`references/markdown-report-template.md`
- **JSON 报告**：`references/json-report-template.md`

### 落盘位置

- `LLM-check-workspace/`
  - `<skill-name>-report.md`
  - `<skill-name>-report.json`

## 22 条检查清单

详见 `references/22-checks.md`。核心检查项：

1. 容易自由发挥
2. 对私有知识不了解
3. 输出有概率性
4. 长链路容易漏步骤
5. 对高风险操作边界不稳定
6. 格式遵守不稳定
7. 工具调用顺序不确定
8. 判断标准容易漂移
9. 不知道该读哪些上下文
10. 多次输出风格不一致
11. 异常处理能力不稳定
12. 容易只生成不验证
13. 容易产生事实幻觉
14. 信息不足时易主观假设
15. 单一视角分析不足
16. 容易混淆术语口径
17. 批量任务稳定性差
18. 不掌握专家经验
19. 不熟悉工程约定
20. 容易过度解决问题
21. 不知道何时需要人工介入询问
22. 执行过程不可审计

## 审查方法

1. **读取** skill 的相关章节（SKILL.md / scripts/ / references/ / evals/）
2. **匹配** 缺陷项的"判定要点"
3. **判定**：通过 ✅ / 未通过 ❌
4. **若未通过**：
   - **理由**：引述 skill 中的具体段落（作为证据）
   - **解决方案**：给出可执行的修改建议（具体到章节/字段）

## 风险分级标准

| 风险等级 | 标准 |
|---|---|
| 🔴 高风险 | 直接导致 LLM 输出错误/有害内容，或完全无法完成任务 |
| 🟡 中风险 | 降低任务成功率，或需要用户大量返工 |
| 🟢 低风险 | 轻微影响用户体验，或可通过简单优化改善 |

## 失败处理

任何步骤失败时，直接返回失败原因，不做降级处理。

**常见失败场景：**
- 路径不存在
- Skill 包结构不完整（缺少 SKILL.md）
- 内容无法读取

## 安全边界

- **只读不改**：审查过程绝不修改待审查 skill 文件
- **不外传**：不向网络外传输 skill 内容
- **不执行**：不运行 skill 内的任何脚本或代码

## 验收

冷启动测试：用本 skill 自身作为被审对象，验证报告输出是否符合预期。

测试步骤：
1. 使用本 skill 审查 `JZL-skill-LLM-check` 自身
2. 验证生成的报告包含 22 条检查项
3. 验证报告格式符合 `references/markdown-report-template.md` 和 `references/json-report-template.md` 模板
4. 验证落盘位置正确（`LLM-check-workspace/`）
