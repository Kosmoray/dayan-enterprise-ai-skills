#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gb7718_oem_quote_guard.py — 川调复合调味品与食品 OEM GB 7718-2025 防职业打假扫描 + 炒制损耗三档核价器
静态扫描标签文本中的极限违禁词（如“特供/极品/零添加违规暗示/疾病预防治疗词”）、八大致敏原漏标、
净含量字符高度合规提醒，并根据原料成本、油脂炒制挥发收率（如 82%）、包材与人工算出
500kg / 2T / 10T 三档保本含税出厂价。

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/gb7718_oem_quote_guard.py --demo
  python3 scripts/industry/gb7718_oem_quote_guard.py --demo --json
  python3 scripts/industry/gb7718_oem_quote_guard.py --input oem_spec.json [--json]
"""

import argparse
import json
import pathlib
import re
import sys
from typing import Any, Dict, List

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"

# 1. GB 7718-2025 & 食品安全法/广告法 高频职业打假索赔词库
PROHIBITED_LABEL_RULES = [
    {
        "code": "GB7718_2025_ZERO_ADDITIVE_BAN",
        "level": "RED",
        "category": "GB 7718-2025 禁用声称",
        "pattern": r"(零添加|0添加|不添加.{0,8}(防腐剂|香精|色素|味精|添加剂)|无添加)",
        "fix": "删除『零添加/不添加』字样！GB 7718-2025 明确禁止使用『不添加』『不使用』及其同义语对配料或食品添加剂进行强调。",
    },
    {
        "code": "EXTREME_OR_SPECIAL_SUPPLY_CLAIM",
        "level": "RED",
        "category": "特供/极限绝对化违禁词",
        "pattern": r"(特供|专供|内供|国宴|极品|国家级|全网第一|第一品牌|最正宗|顶级秘方)",
        "fix": "立即删除『特供/专供/极品/最正宗』等涉政及《广告法》第九条绝对化用语，防范市场监管重罚与十倍索赔。",
    },
    {
        "code": "MEDICAL_EFFICACY_CLAIM",
        "level": "RED",
        "category": "普通食品暗示疾病预防治疗功效",
        "pattern": r"(预防.{0,6}(疾病|感冒|三高)|治疗|降血压|降血脂|降血糖|养胃护肝|清热解毒|增强免疫力|排毒抗癌)",
        "fix": "普通预包装食品严禁涉及疾病预防、治疗功能或保健功能声称（违反《食品安全法》第七十一条、第七十三条）。",
    },
]

# 2. GB 7718 八大类强制致敏物质映射表
EIGHT_ALLERGENS = [
    ("含麸质的谷物及其制品", ["小麦", "面粉", "小麦粉", "大麦", "黑麦", "燕麦", "谷朊粉"]),
    ("甲壳纲类动物及其制品", ["虾", "蟹", "小龙虾", "虾仁", "虾皮", "蟹黄"]),
    ("鱼类及其制品", ["鱼", "鳀鱼", "鱼露", "三文鱼", "金枪鱼"]),
    ("蛋类及其制品", ["鸡蛋", "蛋黄", "蛋白液", "全蛋粉", "鸭蛋"]),
    ("花生及其制品", ["花生", "花生油", "花生酱", "花生碎"]),
    ("大豆及其制品", ["大豆", "黄豆", "豆豉", "大豆油", "大豆磷脂", "豆瓣"]),
    ("乳及乳制品（含乳糖）", ["牛奶", "乳粉", "全脂乳粉", "黄油", "奶酪", "干酪", "乳清粉"]),
    ("坚果及其果仁类制品", ["核桃", "巴旦木", "扁桃仁", "腰果", "榛子", "开心果", "夏威夷果"]),
]

DEMO_OEM_PAYLOAD: Dict[str, Any] = {
    "product_name": "老成都零添加极品牛油火锅底料（餐饮贴牌送审样稿 500g/袋）",
    "label_check": {
        "marketing_copy": "古法慢熬·零添加防腐剂·极品特供老火锅·冬天吃养胃护肝不上火",
        "ingredients_text": "牛油、辣椒、郫县豆瓣（红辣椒、蚕豆、小麦粉、食用盐）、黄豆酱、花生酱、冰糖、花椒、姜、蒜、食用盐、5'-呈味核苷酸二钠",
        "allergen_notice": "本品含有大豆制品。",
        "net_weight_g": 500.0,
        "net_weight_font_height_mm": 3.0,
    },
    "costing": {
        "raw_material_cost_per_kg": 18.80,
        "cooking_yield_rate": 0.82,
        "base_packaging_cost_per_kg": 2.40,
        "labor_energy_per_kg": 1.90,
        "kettle_dead_loss_kg": 25.0,
        "batch_setup_fee_yuan": 1800.0,
        "target_gross_margin": 0.20,
        "vat_rate": 0.13,
    },
}


def required_net_weight_font_mm(net_weight_g_or_ml: float) -> float:
    """依据 GB 7718 净含量字符最小高度强制规定返回最小毫米数。"""
    if net_weight_g_or_ml <= 0:
        raise ValueError("净含量必须大于 0")
    if net_weight_g_or_ml <= 50.0:
        return 2.0
    if net_weight_g_or_ml <= 200.0:
        return 3.0
    if net_weight_g_or_ml <= 1000.0:
        return 4.0
    return 6.0


def scan_gb7718_label(label_data: Dict[str, Any]) -> Dict[str, Any]:
    """扫描标签文案违禁词、八大致敏原漏标与净含量字高。"""
    marketing_copy = str(label_data.get("marketing_copy", ""))
    ingredients_text = str(label_data.get("ingredients_text", ""))
    allergen_notice = str(label_data.get("allergen_notice", ""))
    net_weight_g = float(label_data.get("net_weight_g", 500.0))
    font_height_mm = float(label_data.get("net_weight_font_height_mm", 4.0))

    full_text = f"{marketing_copy}\n{ingredients_text}"
    red_flags: List[Dict[str, str]] = []

    # 1. 违禁词扫描
    for rule in PROHIBITED_LABEL_RULES:
        m = re.search(rule["pattern"], full_text)
        if m:
            red_flags.append(
                {
                    "code": rule["code"],
                    "category": rule["category"],
                    "matched": m.group(0),
                    "fix": rule["fix"],
                }
            )

    # 2. 八大致敏原交叉扫描
    missing_allergens = []
    detected_allergens = []
    for allergen_group, triggers in EIGHT_ALLERGENS:
        hit_words = [w for w in triggers if w in ingredients_text]
        if hit_words:
            detected_allergens.append({"group": allergen_group, "triggers": hit_words})
            # 检查致敏提示语中是否包含该类关键词或核心触发词
            group_short = allergen_group.split("及")[0].replace("含", "")
            covered = (group_short in allergen_notice) or any(w in allergen_notice for w in hit_words)
            if "麸质" in allergen_group:
                covered = covered or ("麸质" in allergen_notice) or ("小麦" in allergen_notice)
            if not covered:
                missing_allergens.append(f"{allergen_group}（配料含：{'/'.join(hit_words)}）")

    if missing_allergens:
        red_flags.append(
            {
                "code": "ALLERGEN_OMISSION_RED_CARD",
                "category": "GB 7718-2025 致敏物质强制标示漏标",
                "matched": "；".join(missing_allergens),
                "fix": "在配料表邻近位置以加粗/下划线明确补齐全部致敏物质提示（如：『致敏原提示：本品含有含麸质的谷物制品、大豆制品、花生制品』）。",
            }
        )

    # 3. 净含量最小字符高度合规核查
    min_font_mm = required_net_weight_font_mm(net_weight_g)
    font_compliant = font_height_mm >= min_font_mm
    if not font_compliant:
        red_flags.append(
            {
                "code": "NET_WEIGHT_FONT_HEIGHT_VIOLATION",
                "category": "GB 7718 净含量字符最小高度不达标",
                "matched": f"净含量 {net_weight_g:g}g 实测字高 {font_height_mm:.1f}mm < 国标最低要求 {min_font_mm:.1f}mm",
                "fix": f"立即通知平面设计师将包装正面净含量数字及法定计量单位字符高度放大至 >= {min_font_mm:.1f}mm（建议留 0.5mm 印刷缩水余量）。",
            }
        )

    return {
        "net_weight_g": net_weight_g,
        "font_height_mm": font_height_mm,
        "min_required_font_mm": min_font_mm,
        "font_height_compliant": font_compliant,
        "detected_allergens": detected_allergens,
        "missing_allergens": missing_allergens,
        "red_flags": red_flags,
        "is_label_clean": len(red_flags) == 0,
    }


def calculate_oem_tier_quotes(costing: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算复合调味品炒制挥发损耗放大后的 500kg / 2T / 10T 三档保本与目标毛利含税出厂价。
    """
    raw_cost = float(costing["raw_material_cost_per_kg"])
    yield_rate = float(costing["cooking_yield_rate"])
    base_pkg = float(costing["base_packaging_cost_per_kg"])
    labor_energy = float(costing["labor_energy_per_kg"])
    dead_loss_kg = float(costing.get("kettle_dead_loss_kg", 25.0))
    setup_fee = float(costing.get("batch_setup_fee_yuan", 1800.0))
    target_margin = float(costing.get("target_gross_margin", 0.20))
    vat_rate = float(costing.get("vat_rate", 0.13))

    if not (0.30 <= yield_rate <= 1.0):
        raise ValueError("炒制收率 cooking_yield_rate 必须在 0.30 ~ 1.00 之间（如 0.82 代表 82% 收率）")
    if not (0.0 <= target_margin < 0.85):
        raise ValueError("目标毛利率必须在 0 ~ 0.85 之间")

    cooked_paste_cost_per_kg = raw_cost / yield_rate
    hidden_yield_loss_per_kg = cooked_paste_cost_per_kg - raw_cost

    # 三档起订量与包材小单溢价系数（500kg 小单数码袋/制版损耗高，10T 规模集采折让）
    tier_defs = [
        ("500kg", 500.0, 1.25),
        ("2T", 2000.0, 1.05),
        ("10T", 10000.0, 0.95),
    ]

    tiers: Dict[str, Dict[str, float]] = {}
    for label, qty_kg, pkg_mult in tier_defs:
        effective_paste_kg = qty_kg + dead_loss_kg
        paste_total = effective_paste_kg * cooked_paste_cost_per_kg
        pkg_total = qty_kg * (base_pkg * pkg_mult)
        mfg_total = qty_kg * labor_energy + setup_fee

        untaxed_breakeven_per_kg = (paste_total + pkg_total + mfg_total) / qty_kg
        taxed_breakeven_per_kg = untaxed_breakeven_per_kg * (1.0 + vat_rate)
        taxed_target_quote_per_kg = (untaxed_breakeven_per_kg / (1.0 - target_margin)) * (1.0 + vat_rate)

        tiers[label] = {
            "order_kg": qty_kg,
            "untaxed_breakeven_yuan_per_kg": round(untaxed_breakeven_per_kg, 2),
            "taxed_breakeven_yuan_per_kg": round(taxed_breakeven_per_kg, 2),
            "taxed_target_quote_yuan_per_kg": round(taxed_target_quote_per_kg, 2),
        }

    return {
        "raw_material_cost_per_kg": round(raw_cost, 2),
        "cooking_yield_rate": round(yield_rate, 4),
        "cooked_paste_cost_per_kg": round(cooked_paste_cost_per_kg, 2),
        "hidden_yield_loss_per_kg": round(hidden_yield_loss_per_kg, 2),
        "vat_rate": vat_rate,
        "target_gross_margin": target_margin,
        "tiers": tiers,
    }


def evaluate_oem_guard(payload: Dict[str, Any]) -> Dict[str, Any]:
    product_name = str(payload.get("product_name", "复合调味品 OEM 审标与阶梯核价单"))
    label_report = scan_gb7718_label(payload["label_check"])
    quote_report = calculate_oem_tier_quotes(payload["costing"])

    if not label_report["is_label_clean"]:
        status = "RED"
        verdict = f"🔴 红牌阻断印制（检出 {len(label_report['red_flags'])} 处职业打假十倍索赔雷点，改稿前严禁开机印袋！）"
    else:
        status = "GREEN"
        verdict = "🟢 标签初筛通过（未命中高频打假雷区，可按三档含税阶梯底线对外报价）"

    return {
        "product_name": product_name,
        "status": status,
        "verdict": verdict,
        "label_audit": label_report,
        "oem_tier_pricing": quote_report,
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(report: Dict[str, Any]) -> str:
    la = report["label_audit"]
    pr = report["oem_tier_pricing"]
    lines = [
        "=" * 84,
        "🌶️  大衍千机 · 川调食品 OEM《GB 7718-2025》防打假扫描 & 炒制损耗三档核价表",
        f"   送审品名 : {report['product_name']}",
        "=" * 84,
        f"• 综合放行建议 : {report['verdict']}",
        f"• 净含量字高核验: 规格 {la['net_weight_g']:g}g | 排版字高 {la['font_height_mm']:.1f}mm vs 国标下限 {la['min_required_font_mm']:.1f}mm -> {'✅ 合规' if la['font_height_compliant'] else '❌ 不达标'}",
        "-" * 84,
        "【一、GB 7718-2025 标签防职业打假逐项清零清单】",
    ]
    if la["red_flags"]:
        for idx, rf in enumerate(la["red_flags"], 1):
            lines.append(f"  ❌ [{idx}] ({rf['category']}) 命中: 「{rf['matched']}」")
            lines.append(f"       └─ 整改动作: {rf['fix']}")
    else:
        lines.append("  ✅ 未检出极限词、『零添加』违规声称、致敏原漏标或净含量字高缺陷。")

    lines.extend(
        [
            "-" * 84,
            "【二、油脂炒制挥发损耗还原 & 500kg / 2T / 10T 三档出厂报价底线】",
            f"  • 生料配方成本 : ¥{pr['raw_material_cost_per_kg']:.2f}/kg  |  炒制挥发收率: {pr['cooking_yield_rate']*100:.1f}%",
            f"  • 熟料真实成本 : ¥{pr['cooked_paste_cost_per_kg']:.2f}/kg  （每公斤隐性蒸发损耗 ¥{pr['hidden_yield_loss_per_kg']:.2f}，漏算即白干！）",
            f"  • 阶梯核价结果（含 {pr['vat_rate']*100:.0f}% 增值税，目标毛利率 {pr['target_gross_margin']*100:.0f}%）：",
        ]
    )
    for tier_key in ("500kg", "2T", "10T"):
        t = pr["tiers"][tier_key]
        lines.append(
            f"      ▪ [{tier_key:<5s} 档] 车间裸保本(不含税): ¥{t['untaxed_breakeven_yuan_per_kg']:>6.2f}/kg"
            f"  |  保本含税生死线: ¥{t['taxed_breakeven_yuan_per_kg']:>6.2f}/kg"
            f"  |  建议含税出厂报价: ¥{t['taxed_target_quote_yuan_per_kg']:>6.2f}/kg"
        )

    lines.extend(
        [
            "-" * 84,
            "⚖️  合规底线 : 正式印刷菲林定稿前须经工厂品控主管（食品安全总监）对照最新产品执行标准及营养成分检测报告复核签字。",
            FOOTER_SIGN,
            "=" * 84,
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · 川调食品 OEM GB 7718-2025 防职业打假与三档核价器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行火锅底料贴牌标签排雷与三档损耗核价演示")
    parser.add_argument("--input", type=str, help="读取外部标签与成本参数 JSON 文件")
    parser.add_argument("--yield-rate", type=float, help="覆盖炒制收率 (0.30~1.0)")
    parser.add_argument("--raw-cost", type=float, help="覆盖生料配方加权单价 (元/kg)")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    payload = json.loads(json.dumps(DEMO_OEM_PAYLOAD))
    if args.input:
        in_path = pathlib.Path(args.input)
        if not in_path.is_file():
            print(f"参数文件不存在: {in_path}", file=sys.stderr)
            sys.exit(1)
        payload = json.loads(in_path.read_text(encoding="utf-8"))

    if args.yield_rate is not None:
        payload["costing"]["cooking_yield_rate"] = args.yield_rate
    if args.raw_cost is not None:
        payload["costing"]["raw_material_cost_per_kg"] = args.raw_cost

    report = evaluate_oem_guard(payload)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(report))


if __name__ == "__main__":
    main()
