#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dayan_humanize_lint.py — 大衍千机 · 中文 AI 腔与外发净稿静态扫描器 (Zero-Dependency CLI)
出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信/电话：18628016927)

用法:
  python3 scripts/dayan_humanize_lint.py <file.md|file.txt|file.html> [--json] [--fail-under 50]
"""

import argparse
import json
import pathlib
import re
import sys

BUZZWORDS = [
    "赋能", "抓手", "闭环", "颗粒度", "对齐", "拉通", "组合拳", "强强联合",
    "深度赋能", "全方位", "生态体系", "底层逻辑", "顶层设计", "心智占领", "势能", "全链路", "新范式",
]

HOLLOW_TRANSITIONS = [
    "随着人工智能技术的不断发展", "在数字化转型的大背景下", "值得注意的是",
    "综上所述", "总而言之", "众所周知", "不难发现", "由此可见",
]

CLICHE_ENDINGS = [
    "未来可期", "携手共创", "共赴未来", "迈向新台阶", "谱写新篇章", "让我们拭目以待",
]

WEAK_VERBS_NOMINAL = [
    r"进行.{1,6}(?:优化|升级|赋能|整合|梳理|重构)",
    r"实现.{1,6}(?:降本增效|全面提升|闭环|跃升)",
    r"打造.{1,8}(?:体系|平台|生态|矩阵|标杆)",
]

INTERNAL_META_LEAKS = [
    "PPT只记", "PPT 只记", "现场不需要讲", "讲述者注意", "演讲时注意",
    "待填", "待删", "待替换", "制作备注", "speaker notes",
]


def scan_text(text: str):
    findings = []
    lines = text.splitlines()
    em_dash_count = 0

    for idx, line in enumerate(lines, 1):
        for leak in INTERNAL_META_LEAKS:
            if leak.lower() in line.lower():
                findings.append(("CRITICAL", idx, f"疑似外发净稿泄露内部备注词「{leak}」", line.strip()[:70]))

        hit_buzz = [w for w in BUZZWORDS if w in line]
        if hit_buzz:
            findings.append(("WARN", idx, f"黑话/拔高词堆砌：{', '.join(hit_buzz)}", line.strip()[:70]))

        hit_trans = [w for w in HOLLOW_TRANSITIONS if w in line]
        if hit_trans:
            findings.append(("WARN", idx, f"空洞背景/过渡套话：{', '.join(hit_trans)}", line.strip()[:70]))

        hit_end = [w for w in CLICHE_ENDINGS if w in line]
        if hit_end:
            findings.append(("WARN", idx, f"万能鸡汤结尾：{', '.join(hit_end)}", line.strip()[:70]))

        for pat in WEAK_VERBS_NOMINAL:
            m = re.search(pat, line)
            if m:
                findings.append(("NOTE", idx, f"架空动词短语「{m.group(0)}」（建议换具体业务动作）", line.strip()[:70]))

        em_dash_count += line.count("——")

    if em_dash_count >= 3:
        findings.append(("WARN", 0, f"全文中文破折号「——」出现 {em_dash_count} 次（典型大模型标点习惯，建议改逗号/句号）", ""))

    char_len = max(len(text), 100)
    penalty = sum(25 if f[0] == "CRITICAL" else 8 if f[0] == "WARN" else 4 for f in findings)
    slop_score = min(100, int(round(penalty * (800 / max(char_len, 400)))))
    return slop_score, findings


def main():
    parser = argparse.ArgumentParser(
        description="大衍千机 · 中文 AI 腔与外发净稿静态扫描器 (https://dayanqianji.com/)"
    )
    parser.add_argument("file", help="待扫描的 .md / .txt / .html 文件路径")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    parser.add_argument("--fail-under", type=int, default=None, help="当 AI 塑料味指数 >= 该阈值时返回非零退出码（用于 CI）")
    args = parser.parse_args()

    target = pathlib.Path(args.file)
    if not target.is_file():
        print(f"文件不存在: {target}", file=sys.stderr)
        sys.exit(1)

    content = target.read_text(encoding="utf-8", errors="replace")
    score, findings = scan_text(content)
    verdict = (
        "🟢 真人质感清爽稿"
        if score < 15
        else ("🟡 轻度机器腔（建议顺手修）" if score < 45 else "🔴 重度 AI 塑料味（严禁直接发给老板/客户）")
    )

    if args.json:
        print(
            json.dumps(
                {
                    "file": str(target),
                    "ai_slop_score": score,
                    "verdict": verdict,
                    "findings": [
                        {"severity": s, "line": ln, "message": m, "snippet": sn}
                        for s, ln, m, sn in findings
                    ],
                    "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print("=" * 74)
        print(f"⚙️  大衍千机 · 中文去AI味与外发净稿扫描器  |  文件: {target.name}")
        print("=" * 74)
        print(f"• AI 塑料味指数 : {score} / 100   -->  {verdict}")
        print(f"• 命中病灶总数  : {len(findings)} 处")
        print("-" * 74)

        for sev, lineno, msg, snippet in findings[:25]:
            loc = f"L{lineno:<4d}" if lineno > 0 else "全文 "
            print(f"[{sev:<8s}] {loc} | {msg}")
            if snippet:
                print(f"                 └─ 原句: {snippet}...")

        if not findings:
            print("✨ 未检出典型中文 AI 黑话、空洞套话或内部制作备注残留！")

        print("-" * 74)
        print("💡 深度重写请调用技能: npx -y skills add Kosmoray/dayan-enterprise-ai-skills --skill dayan-humanize-pro")
        print("🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927")
        print("=" * 74)

    if args.fail_under is not None and score >= args.fail_under:
        sys.exit(2)


if __name__ == "__main__":
    main()
