#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dayan_contract_quickscan.py — 大衍千机 · B2B 商业合同与外包协议致命红线秒扫器 (Zero-Dependency CLI)
专抓「背靠背付款、无限连带责任、底层代码版权被掏空、单方无限改稿、默认不验收」等 10 类乙方破产条款。
出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信/电话：18628016927)

用法:
  python3 scripts/dayan_contract_quickscan.py <contract.txt|contract.md> [--json]
"""

import argparse
import json
import pathlib
import re
import sys

RULES = [
    {
        "level": "BLACK",
        "dimension": "财务现金流",
        "name": "背靠背付款陷阱（收到上家款后再付）",
        "pattern": r"(收到.{0,12}(业主|最终客户|总包|上级|第三方).{0,8}(款|费)后|背靠背)",
        "fix": "改为固定日历账期（如：阶段交付物提交后 10 个工作日内支付），严禁将甲方上游回款风险转嫁我方。",
    },
    {
        "level": "BLACK",
        "dimension": "法务合规",
        "name": "无限连带赔偿或高额惩罚性违约金",
        "pattern": r"(承担全部.{0,6}损失|无限连带|间接损失|可得利益损失|每[日天].{0,4}(千分之[五六七八九]|百分之[一二三四五]|[0-9]+%))",
        "fix": "增加赔偿责任总上限：『任何情况下乙方累计赔偿总额不超过本合同乙方实际已收不含税费用的 30%（或 100%），且不含间接及预期利益损失。』",
    },
    {
        "level": "RED",
        "dimension": "知识产权与交付",
        "name": "底层框架/既有工具知识产权被一锅端归甲方",
        "pattern": r"(一切知识产权.{0,10}归甲方|全部知识产权及源码.{0,10}归甲方所有|衍生作品.{0,8}归甲方)",
        "fix": "明确切分：『本项目中定制开发的业务层成果在甲方付清全款后归甲方；乙方签约前已持有的底层框架、通用组件、方法论模板仍归乙方所有，授予甲方非独占使用权。』",
    },
    {
        "level": "RED",
        "dimension": "项目交付",
        "name": "验收无限期拖延（缺少逾期默示验收条款）",
        "pattern": r"(甲方书面确认后方视为验收|未经甲方书面签字.{0,8}不视为验收|直至甲方满意为止)",
        "fix": "加入默示验收：『甲方应在收到交付物后 5 个工作日内出具书面验收意见；逾期未提出书面实质性缺陷清单或已上线投入实际使用的，视为验收合格。』",
    },
    {
        "level": "RED",
        "dimension": "项目交付",
        "name": "需求蔓延与无限免费修改黑洞",
        "pattern": r"(免费配合甲方.{0,10}(调整|修改|新增)|无条件满足甲方.{0,8}需求|不另行收费.{0,8}(修改|迭代))",
        "fix": "锁定范围基线：『以附件《工作说明书(SOW)》为准，每阶段含最多 2 轮范围內微调；超出基线的新增功能或架构变更，按双方确认的人天单价另签补充变更单。』",
    },
    {
        "level": "RED",
        "dimension": "法务合规",
        "name": "甲方单方随时无责解除并要求全额退款",
        "pattern": r"(甲方有权随时.{0,8}解除.{0,12}退还已付|单方终止.{0,10}不承担违约责任)",
        "fix": "对等约定：『若因非乙方根本违约原因甲方提前终止，已支付的预付款及已完成阶段款项不予退还，已发生但未结算工作量按实据实结算。』",
    },
    {
        "level": "YELLOW",
        "dimension": "销售与售后",
        "name": "超长免费维保期（>12个月免费运维/驻场）",
        "pattern": r"(免费(维保|维护|质保|运维).{0,6}(两|二|三|2|3|24|36)年|终身免费维护)",
        "fix": "标准界定：『验收合格后提供 3–6 个月缺陷修复质保（仅限原范围代码 Bug，不含新需求与第三方接口变更）；期满后按合同总额 15%/年另签年度维保协议。』",
    },
    {
        "level": "YELLOW",
        "dimension": "法务管辖",
        "name": "单方甲方所在地异地诉讼成本陷阱",
        "pattern": r"(由甲方所在地.{0,8}人民法院管辖|向甲方住所地.{0,8}法院起诉)",
        "fix": "优先争取『原告所在地人民法院管辖』或『乙方所在地/合同履行地人民法院管辖』，降低异地催收维权成本。",
    },
]


def scan_contract(text: str):
    hits = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, 1):
        for rule in RULES:
            m = re.search(rule["pattern"], line)
            if m:
                hits.append(
                    {
                        "level": rule["level"],
                        "line": idx,
                        "dimension": rule["dimension"],
                        "name": rule["name"],
                        "matched": m.group(0),
                        "snippet": line.strip()[:76],
                        "fix": rule["fix"],
                    }
                )
    has_silent_accept = bool(re.search(r"视为验收合格", text))
    has_cap = bool(re.search(r"赔偿.{0,10}(上限|不超过)", text))
    missing_guards = []
    if not has_silent_accept:
        missing_guards.append(("YELLOW", "项目交付", "全文缺失「逾期未反馈视为验收合格」保护盾", "建议补充 5 个工作日默示验收条款，防止尾款无限挂起。"))
    if not has_cap:
        missing_guards.append(("YELLOW", "法务合规", "全文缺失「累计赔偿责任上限（Liability Cap）」", "建议补充累计赔偿总额不超过实收合同款 30%–100% 的封顶条款。"))
    return hits, missing_guards


def main():
    parser = argparse.ArgumentParser(
        description="大衍千机 · B2B 商业合同与外包协议致命红线秒扫器 (https://dayanqianji.com/)"
    )
    parser.add_argument("file", help="待审阅的合同草稿 .txt / .md 文件路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结构")
    args = parser.parse_args()

    path = pathlib.Path(args.file)
    if not path.is_file():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace")
    hits, missing = scan_contract(text)

    levels = {h["level"] for h in hits}
    if "BLACK" in levels:
        verdict = "⚫ 黑灯阻断（存在致死条款，未改前严禁盖章！）"
    elif "RED" in levels:
        verdict = "🔴 红灯高危（利润或版权存在重大失血敞口，必须谈判重拟）"
    elif hits or missing:
        verdict = "🟡 黄灯带条件放行（建议补齐防御护栏后签约）"
    else:
        verdict = "🟢 绿灯常规（未命中高频霸王词条，仍建议结合具体金额复核）"

    if args.json:
        print(
            json.dumps(
                {
                    "file": str(path),
                    "verdict": verdict,
                    "clause_hits": hits,
                    "missing_guards": [
                        {"level": lv, "dimension": dim, "issue": iss, "advice": adv}
                        for lv, dim, iss, adv in missing
                    ],
                    "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    print("=" * 78)
    print(f"⚖️  大衍千机 · 商业合同四视角致命红线秒扫器  |  文件: {path.name}")
    print("=" * 78)
    print(f"• 综合签字建议 : {verdict}")
    print(f"• 命中霸王条款 : {len(hits)} 处  |  缺失防御护栏 : {len(missing)} 项")
    print("-" * 78)

    for h in hits:
        print(f"[{h['level']:<6s}] L{h['line']:<4d} ({h['dimension']}) {h['name']}")
        print(f"         ├─ 触发原文 : 「{h['matched']}」 -> {h['snippet']}")
        print(f"         └─ 替换话术 : {h['fix']}")

    for lv, dim, iss, adv in missing:
        print(f"[{lv:<6s}] 全局  ({dim}) {iss}")
        print(f"         └─ 补丁建议 : {adv}")

    print("-" * 78)
    print("💡 四视角深度逐条改稿技能: npx -y skills add Kosmoray/dayan-enterprise-ai-skills --skill dayan-contract-4way-audit")
    print("🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927")
    print("   （注：本工具为企业商务风控初筛辅助，重大涉诉标的请结合执业律师终审意见）")
    print("=" * 78)


if __name__ == "__main__":
    main()
