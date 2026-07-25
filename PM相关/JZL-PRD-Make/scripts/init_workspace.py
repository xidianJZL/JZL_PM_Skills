"""
JZL-PRD-Make 工作区初始化脚本

用法：
    python scripts/init_workspace.py --name "<产品名>" [--type "<产品类型>"] [--source "<输入源描述>"]

参数：
    --name     产品名（必填），用于命名工作区
    --type     产品类型（可选），如 SaaS、移动端、管理后台等
    --source   用户提供的输入源内容（可选），仅当用户明确说明根据"用户描述/文件路径"时才传入
              传入时表示需创建 inputs/source_note.md 并写入内容

功能：
1. 自动检测当前目录是否已在产品工作区内
2. 若在现有工作区内，仅补齐 inputs/ 和 prd/（不覆盖已有文件）
3. 若不在工作区内，在同级创建/复用 {name}-workspace/
4. prd/ 中创建 PRD.md、_module-plan.md、_append-log.md（仅当不存在时）
5. 仅当 --source 参数有值时，才创建 inputs/source_note.md 并写入输入源内容
6. 读取 PRD 复杂度等级（L1-L4），写入对应模板内容
7. 脚本本身不感知模板内容变更，模板修改后脚本无需任何改动
"""

import argparse
import os
from pathlib import Path
from datetime import datetime

# -------------------------------------------------------
# 工具函数
# -------------------------------------------------------

def log(msg: str):
    print(f"[init_workspace] {msg}")


def read_template(templates_dir: Path, level: str) -> str:
    """从 templates/ 目录动态读取指定等级的 PRD 模板内容"""
    tpl_path = templates_dir / f"PRD-{level.upper()}.md"
    if not tpl_path.exists():
        raise FileNotFoundError(
            f"模板文件不存在: {tpl_path}。"
            f"请确认 templates/ 目录下存在 PRD-{level.upper()}.md 文件。"
        )
    return tpl_path.read_text(encoding="utf-8")


def read_template_raw(templates_dir: Path, name: str) -> str:
    """读取参考模板文件（_module-plan.md, _append-log.md）"""
    tpl_path = templates_dir.parent / "reference" / name
    if not tpl_path.exists():
        raise FileNotFoundError(f"参考模板不存在: {tpl_path}")
    return tpl_path.read_text(encoding="utf-8")


def ensure_dir(path: Path):
    """确保目录存在，不存在则创建"""
    path.mkdir(parents=True, exist_ok=True)
    log(f"目录已创建/确认：{path}")


def is_workspace(cwd: Path) -> bool:
    """判断当前目录是否已是产品工作区"""
    return any((cwd / marker).exists() for marker in [
        "shaping", "prd", "prototype"
    ]) or (cwd / "00-intake.md").exists()


def resolve_workspace(cwd: Path, name: str) -> Path:
    """
    确定工作区根目录：
    1. 当前目录已是工作区 → 返回当前目录
    2. 检查同级是否存在 {name}-workspace/ → 复用
    3. 否则在同级创建新的 {name}-workspace/
    """
    if is_workspace(cwd):
        log(f"当前目录已是工作区：{cwd}")
        return cwd

    parent = cwd.parent
    candidate = parent / f"{name}-workspace"
    if candidate.exists():
        log(f"复用已有工作区：{candidate}")
        return candidate

    log(f"创建新工作区：{candidate}")
    return candidate


# -------------------------------------------------------
# 核心逻辑
# -------------------------------------------------------

def init_workspace(
    name: str,
    level: str = "L2",
    source_content: str = None,
    script_path: str = None,
):
    """
    主入口。

    参数：
        name            产品名
        level           PRD 复杂度等级（L1-L4）
        source_content  用户提供的输入源全文（str），仅当用户明确说明
                        根据"用户描述/文件路径"时才传入
        script_path     __file__，用于从脚本所在目录推算 skill 根目录
    """
    cwd = Path.cwd()
    script_dir = Path(script_path).parent if script_path else Path(__file__).parent
    skill_root = script_dir.parent.resolve()

    templates_dir = skill_root / "templates"
    reference_dir = skill_root / "reference"

    # 确认模板目录存在
    if not templates_dir.exists():
        raise FileNotFoundError(
            f"templates/ 目录不存在：{templates_dir}。"
            f"请确认 skill 目录结构完整。"
        )

    # 规范等级
    level = level.upper()
    if level not in ("L1", "L2", "L3", "L4"):
        raise ValueError(f"无效的复杂度等级：{level}，应为 L1/L2/L3/L4")

    # 确定工作区
    workspace = resolve_workspace(cwd, name)
    ensure_dir(workspace)

    # ---------- inputs/ ----------
    inputs_dir = workspace / "inputs"
    ensure_dir(inputs_dir)

    # 仅当 source_content 有效时才创建 source_note.md
    if source_content and source_content.strip():
        source_note = inputs_dir / "source_note.md"
        if source_note.exists():
            log(f"inputs/source_note.md 已存在，跳过写入")
        else:
            source_note.write_text(source_content.strip(), encoding="utf-8")
            log(f"已创建 inputs/source_note.md（来源：用户描述/文件路径）")
    else:
        log("本次未传入输入源内容，inputs/source_note.md 不创建")

    # ---------- prd/ ----------
    prd_dir = workspace / "prd"
    ensure_dir(prd_dir)

    # 1. PRD.md
    prd_file = prd_dir / "PRD.md"
    if prd_file.exists():
        log(f"prd/PRD.md 已存在，跳过创建")
    else:
        prd_content = read_template(templates_dir, level)
        prd_file.write_text(prd_content, encoding="utf-8")
        log(f"已创建 prd/PRD.md（模板：PRD-{level}）")

    # 2. _module-plan.md
    module_plan_file = prd_dir / "_module-plan.md"
    if module_plan_file.exists():
        log(f"prd/_module-plan.md 已存在，跳过创建")
    else:
        # 优先从 reference/ 读取，否则从 skill 根目录读取（旧路径兼容）
        if (reference_dir / "_module-plan.md").exists():
            tpl = (reference_dir / "_module-plan.md").read_text(encoding="utf-8")
        else:
            tpl = read_template_raw(templates_dir, "_module-plan.md")
        module_plan_file.write_text(tpl, encoding="utf-8")
        log(f"已创建 prd/_module-plan.md")

    # 3. _append-log.md
    append_log_file = prd_dir / "_append-log.md"
    if append_log_file.exists():
        log(f"prd/_append-log.md 已存在，跳过创建")
    else:
        if (reference_dir / "_append-log.md").exists():
            tpl = (reference_dir / "_append-log.md").read_text(encoding="utf-8")
        else:
            tpl = read_template_raw(templates_dir, "_append-log.md")
        append_log_file.write_text(tpl, encoding="utf-8")
        log(f"已创建 prd/_append-log.md")

    log(f"\n工作区初始化完成：{workspace}")
    log(f"  inputs/  -> {'source_note.md 已创建' if source_content and source_content.strip() else '空目录'}")
    log(f"  prd/     -> PRD.md（{level}）、_module-plan.md、_append-log.md")


# -------------------------------------------------------
# CLI 入口
# -------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="JZL-PRD-Make 工作区初始化"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="产品名（用于命名工作区）",
    )
    parser.add_argument(
        "--level",
        default="L2",
        help="PRD 复杂度等级（L1/L2/L3/L4，默认 L2）",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="用户提供的输入源内容（仅当用户明确说明根据'描述/路径'时才传入）",
    )
    parser.add_argument(
        "--script",
        default=None,
        help="脚本自身路径（自动传入，通常无需指定）",
    )

    args = parser.parse_args()

    try:
        init_workspace(
            name=args.name,
            level=args.level,
            source_content=args.source,
            script_path=args.script or __file__,
        )
    except FileNotFoundError as e:
        log(f"错误：{e}")
        exit(1)
    except ValueError as e:
        log(f"错误：{e}")
        exit(1)
