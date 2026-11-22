#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dayan_skill_finder.py — 大衍千机 66+ 枚企业 AI 技能本地/全局快速检索器 (Zero-Dependency CLI)
支持在仓库目录直接运行，也支持通过 uvx / pipx 全局安装后随时检索安装指令。
出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信/电话：18628016927)

用法:
  python3 scripts/dayan_skill_finder.py [关键词，如: 合同 / 标书 / 现金流 / 餐饮 / 去AI味]
"""

import pathlib
import re
import sys


def parse_frontmatter(md_path: pathlib.Path):
    txt = md_path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n([\s\S]*?)\n---", txt)
    meta = {"slug": md_path.parent.name, "displayName": md_path.parent.name, "summary": "", "tags": ""}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
    if meta["displayName"] == meta["slug"]:
        h1 = re.search(r"^#\s+(.+)$", txt, re.MULTILINE)
        if h1:
            meta["displayName"] = h1.group(1).strip()
    if not meta["summary"]:
        meta["summary"] = meta.get("description", "")
    return meta, txt


def load_catalog():
    skills_root = pathlib.Path(__file__).resolve().parent.parent / "skills"
    if skills_root.is_dir():
        items = []
        for sdir in sorted(skills_root.iterdir()):
            smd = sdir / "SKILL.md"
            if smd.is_file():
                meta, full_txt = parse_frontmatter(smd)
                items.append((meta, full_txt))
        if items:
            return items

    try:
        from dayan_catalog_data import BUNDLED_SKILLS
        return [(m, f"{m['slug']} {m['displayName']} {m['summary']} {m.get('tags', '')}") for m in BUNDLED_SKILLS]
    except Exception:
        return []


def main():
    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help"):
        print("用法: python3 scripts/dayan_skill_finder.py [关键词，如: 合同 / 标书 / 现金流 / 餐饮 / 去AI味]")
        sys.exit(0)

    query = " ".join(sys.argv[1:]).strip().lower()
    catalog = load_catalog()
    scored = []
    for meta, full_txt in catalog:
        head = f"{meta['slug']} {meta['displayName']} {meta.get('tags', '')}".lower()
        summ = meta.get("summary", "").lower()
        body_low = full_txt.lower()
        if not query:
            scored.append((0, meta["slug"], meta))
            continue
        toks = query.split()
        if all(tok in head or tok in summ or tok in body_low for tok in toks):
            score = sum(head.count(t) * 20 + summ.count(t) * 6 + min(body_low.count(t), 5) for t in toks)
            scored.append((-score, meta["slug"], meta))
    scored.sort(key=lambda x: (x[0], x[1]))
    matched = [x[2] for x in scored]

    print("=" * 78)
    print(f"🔎 大衍千机开源技能引擎 · 匹配「{query or '全部'}」共 {len(matched)} / {len(catalog)} 枚企业技能")
    print("=" * 78)
    for idx, it in enumerate(matched[:20], 1):
        print(f"{idx:02d}. {it['displayName']}  ({it['slug']})")
        if it.get("summary"):
            print(f"    简介 : {it['summary'][:68]}")
        print(f"    安装 : npx -y skills add Kosmoray/dayan-enterprise-ai-skills --skill {it['slug']}")
        print(f"    腾讯 : skillhub install {it['slug']}")
    if len(matched) > 20:
        print(f"... 其余 {len(matched) - 20} 枚匹配项可加细关键词过滤，或访问 https://kosmoray.github.io/dayan-enterprise-ai-skills/")
    print("-" * 78)
    print("🌐 成都大衍千机科技官网: https://dayanqianji.com/open-source/  |  微信/电话: 18628016927")
    print("=" * 78)


if __name__ == "__main__":
    main()
