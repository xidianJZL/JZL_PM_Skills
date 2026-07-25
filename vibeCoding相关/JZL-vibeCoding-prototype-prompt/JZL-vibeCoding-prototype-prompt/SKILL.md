---
name: JZL-vibeCoding-prototype-prompt
description: |
  接收产品想法，输出可直接用于生成高保真原型图的 prompt。

  **触发时机**：
  - 用户提到"原型图 prompt"、"UI 设计 prompt"、"生成原型 prompt"
  - 用户说"给个 [产品名] 的 UI 设计 prompt"、"帮我做个 [产品名] 的原型图的 prompt"
  - 用户提供产品想法或文件，希望生成用于AI绘图的设计prompt

  **本 skill 只生成 prompt，不做其他**：
  - 不生成图片
  - 不写代码
  - 不做交互稿
  - 不做部署上线

  **使用流程**：初始化工作空间 → 接收输入 → 生成功能描述 → 生成原型prompt → 自检 → 输出文件
---

# JZL-vibeCoding-prototype-prompt

接收产品想法，输出可用于生成高保真原型图的 prompt。

## 工作流程

### Step 1: 初始化工作空间

读取 `scripts/init_workspace.bat`（Windows）或 `scripts/init_workspace.sh`（Mac/Linux），在用户工作目录创建输出目录。

```bash
# Windows
scripts/init_workspace.bat "%USERPROFILE%\vibeCoding-prototype"

# Mac/Linux
bash scripts/init_workspace.sh ~/vibeCoding-prototype
```

执行后检查返回码：
- 成功 → 继续
- 失败 → 提示用户问题所在，停止后续流程

---

### Step 2: 接收用户输入

支持以下输入方式：

**方式A：用户直接描述产品想法**
要求包含：
- 产品是什么
- 面向什么用户
- 解决什么问题
- 需要哪些核心功能/页面

**方式B：用户提供文件路径**
读取 `templates/vibecodingFunction.md` 作为输入模板格式要求，解析用户提供的产品描述文件。

输入信息检查：
- 信息完整 → 继续
- 信息不全 → 提示用户补充具体信息，停止后续流程

---

### Step 3: 生成功能描述

检测 `JZL-vibeCoding-function-prompt` skill 是否已安装：

- 已安装 → 调用该skill生成功能描述
- 未安装 → 提示用户安装，停止后续流程

**安装提示**：
```
[INFO] 本skill依赖 JZL-vibeCoding-function-prompt skill
请先安装：设置 → Skills → 安装 JZL-vibeCoding-function-prompt
```

---

### Step 4: 生成原型图 prompt

基于功能描述，按 `templates/vibecodingPrototype.md` 的模板结构生成prompt。

**必须包含的8个板块**：
1. 产品背景
2. 原型目标
3. 页面清单
4. 每个页面的布局说明
5. 组件说明
6. 交互说明
7. 视觉风格说明

**风格选择**：生成prompt前，询问用户选择视觉风格。

可选风格（读取对应文件获取详细规范）：

| 风格 | 风格文件 | 来源 |
|-----|---------|------|
| Cursor | `styles/cursor.md` | https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/cursor/DESIGN.md |
| Cohere | `styles/cohere.md` | https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/cohere/DESIGN.md |
| Figma | `styles/figma.md` | https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/figma/DESIGN.md |

**选择方式**：
- 用户指定具体风格 → 直接引用对应风格文件
- 用户未指定 → 展示三个选项供用户选择
- 用户提供自定义风格文件 → 读取用户指定的本地文件或网络链接

**风格文件来源**：
- 默认风格文件已捆绑在 `styles/` 目录下
- 用户也可以提供自定义风格文件路径或网络链接
- 支持从GitHub raw链接获取：`https://raw.githubusercontent.com/.../DESIGN.md`

8. 交付要求

**约束规则**：

描述"交互关系"，不要只列功能：
- ❌ 有搜索、有列表、有筛选
- ✅ 页面顶部是固定导航栏，左侧为产品名称，右侧为用户头像与通知入口

描述"交互结果"，不要只写"支持"：
- ❌ 支持登录、支持删除、支持切换
- ✅ 用户点击"删除"后，先弹出二次确认弹窗；确认后该条目从列表中消失，并出现可撤销 toast，持续 3 秒

避免模糊风格词：
- ❌ 高级感、简洁、科技感、年轻化
- ✅ 使用浅色背景、大留白、低饱和中性色、单主色强调

此步骤完成后，向用户展示生成结果，等待确认（human-in-the-loop）。

---

### Step 5: 自检

按 `templates/vibecodingPrototype.md` 的审查清单逐项检查：

1. 是否写清了产品目标与用户
2. 是否列出了页面清单和页面关系
3. 是否描述了每个页面的布局结构
4. 是否写清了关键组件与其状态
5. 是否写清了关键交互流程
6. 是否补充了空状态、加载状态、错误状态
7. 是否写清了关键业务规则
8. 是否有"简洁点""高级点""优化一下"等模糊表达

检查结果展示给用户，由用户最终确认。

---

### Step 6: 输出文件

将生成的prompt写入Markdown文件：

- 文件名：`{产品名}-prototype-prompt.md`
- 位置：Step 1 初始化的工作空间目录
- 格式：Markdown

---

## 错误处理

任何步骤出错，统一处理：**给用户明确提示，说明问题所在，然后停止后续流程**。

常见错误场景：
- 初始化脚本执行失败
- `JZL-vibeCoding-function-prompt` skill 未安装
- 用户输入信息不全
- 写文件失败（路径问题/磁盘满）

---

## 捆绑资源

| 资源 | 路径 | 用途 |
|-----|------|------|
| 输出模板 | `templates/vibecodingPrototype.md` | 原型prompt输出结构 |
| 输入模板 | `templates/vibecodingFunction.md` | 功能描述输入参考 |
| Cursor风格 | `styles/cursor.md` | Cursor品牌视觉风格 |
| Cohere风格 | `styles/cohere.md` | Cohere品牌视觉风格 |
| Figma风格 | `styles/figma.md` | Figma品牌视觉风格 |
| 初始化脚本 | `scripts/init_workspace.bat` / `scripts/init_workspace.sh` | 工作空间初始化 |
