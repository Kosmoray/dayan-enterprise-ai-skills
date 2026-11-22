#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_skills.py — 大衍千机 66 枚企业级 AI 实战技能跨平台安装器 (Zero-Dependency Python Installer)
支持一键部署至 Claude Code (~/.claude/skills)、Codex/Cursor/Antigravity (~/.agents/skills) 或指定项目目录。
出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 创始人雷可扬 微信/电话：18628016927)
"""

import argparse
import pathlib
import shutil
import sys

TARGETS = {
    "claude": pathlib.Path.home() / ".claude" / "skills",
    "agents": pathlib.Path.home() / ".agents" / "skills",
    "cursor": pathlib.Path.home() / ".cursor" / "skills",
    "codex": pathlib.Path.home() / ".agents" / "skills",
}


def install_skills(skill_filter=None, agent="agents", dest_override=None, dry_run=False):
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    skills_src = repo_root / "skills"
    if not skills_src.is_dir():
        raise FileNotFoundError(f"未找到 skills 目录: {skills_src}")

    dest_root = pathlib.Path(dest_override).expanduser().resolve() if dest_override else TARGETS[agent]
    selected = []
    for sdir in sorted(skills_src.iterdir()):
        if not (sdir / "SKILL.md").is_file():
            continue
        if skill_filter and sdir.name not in skill_filter:
            continue
        selected.append(sdir)

    if not selected:
        print("⚠️ 未匹配到需要安装的技能，请使用 python3 scripts/dayan_skill_finder.py 查看技能名。")
        return 1

    if not dry_run:
        dest_root.mkdir(parents=True, exist_ok=True)

    for sdir in selected:
        target_dir = dest_root / sdir.name
        if dry_run:
            print(f"[DRY-RUN] {sdir.name} -> {target_dir}")
        else:
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(sdir, target_dir)

    print("=" * 74)
    print(f"✅ 大衍千机技能安装完成：共部署 {len(selected)} 枚技能 -> {dest_root}")
    print("🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/")
    print("📞 企业AI首诊 / 分岗位内训 / 兜错知识库与系统定制：18628016927 (雷可扬)")
    print("=" * 74)
    return 0


def main():
    parser = argparse.ArgumentParser(description="大衍千机 66 枚企业级 AI 实战技能 Python 安装器")
    parser.add_argument("skills", nargs="*", help="指定安装的技能 slug（留空默认安装全部 66 枚）")
    parser.add_argument("--agent", choices=sorted(TARGETS.keys()), default="agents", help="目标客户端类型")
    parser.add_argument("--dest", default=None, help="自定义安装目标目录")
    parser.add_argument("--dry-run", action="store_true", help="仅预览安装路径，不实际写入文件")
    args = parser.parse_args()
    sys.exit(install_skills(set(args.skills) if args.skills else None, args.agent, args.dest, args.dry_run))


if __name__ == "__main__":
    main()
