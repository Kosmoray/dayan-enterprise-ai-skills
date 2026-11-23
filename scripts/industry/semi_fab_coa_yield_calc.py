#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
semi_fab_coa_yield_calc.py — 12寸晶圆厂耗材批次 CoA 痕量金属(ppb)拦截 & 脆硬材料崩边良率核价器 (Zero-Dependency CLI)
校核 12 寸晶圆厂耗材批次 CoA 痕量金属杂质 (Fe/Na/K/Cu/Ni/Cr 等 ppb 限值卡位，超标直接红牌拦截防整炉晶圆污染索赔)，
并精算高纯石英/碳化硅陶瓷超声深孔与薄壁 CNC 加工崩边良率损耗后的真实单件保本出厂价。

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/semi_fab_coa_yield_calc.py --demo
  python3 scripts/industry/semi_fab_coa_yield_calc.py --demo --json
  python3 scripts/industry/semi_fab_coa_yield_calc.py --blank-usd 1450 --drill-yield 0.84
"""

import argparse
import json
import math
import pathlib
import sys
from typing import Any, Dict, List

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"

# 演示用客户规格（ppb = ng/g）。实际比对使用采购合同或客户签字规格。
DEFAULT_300MM_FAB_PPB_LIMITS: Dict[str, float] = {
    "Fe": 50.0,
    "Cu": 10.0,
    "Ni": 15.0,
    "Na": 25.0,
    "K": 25.0,
    "Cr": 15.0,
}

DEMO_SEMI_LOT: Dict[str, Any] = {
    "part_name": "300mm 等离子刻蚀腔 CVD-SiC 高纯碳化硅聚焦环/喷淋头 (Lot #SIC-20261123)",
    "coa_trace_metals_ppb": {
        "spec_limits_ppb": DEFAULT_300MM_FAB_PPB_LIMITS,
        "measured_ppb": {
            "Fe": 32.0,
            "Cu": 14.5,
            "Ni": 8.2,
            "Na": 28.6,
            "K": 11.0,
            "Cr": 6.4,
        },
    },
    "machining_cost_and_yield": {
        "blank_cvd_sic_usd": 1480.0,
        "step1_rough_grind_cost_usd": 190.0,
        "step1_rough_grind_yield": 0.96,
        "step2_ultrasonic_microhole_cost_usd": 520.0,
        "step2_ultrasonic_microhole_yield": 0.82,
        "step3_lapping_upw_clean_cost_usd": 240.0,
        "step3_lapping_upw_clean_yield": 0.94,
        "target_gross_margin": 0.38,
    },
}


def evaluate_semi_coa_and_yield(payload: Dict[str, Any]) -> Dict[str, Any]:
    """核查 12 寸晶圆厂 CoA ppb 金属污染红线并按工序递推崩边良率精算保本单价。"""
    part_name = str(payload.get("part_name", "12寸半导体腔室高纯耗材 CoA 与良率核价"))
    coa = payload["coa_trace_metals_ppb"]
    mfg = payload["machining_cost_and_yield"]

    limits: Dict[str, float] = {k: float(v) for k, v in coa["spec_limits_ppb"].items()}
    if not limits or any(not math.isfinite(v) or v <= 0 for v in limits.values()):
        raise ValueError("请填写客户确认的有效元素上限（正数，单位 ppb）")

    measured: Dict[str, float] = {k: float(v) for k, v in coa["measured_ppb"].items()}

    red_cards: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    element_rows: List[Dict[str, Any]] = []

    for elem, limit_val in limits.items():
        meas_val = measured.get(elem)
        if meas_val is None or not math.isfinite(meas_val) or meas_val < 0:
            red_cards.append({
                "code": "COA_MEASUREMENT_UNVERIFIED",
                "title": f"{elem} 检测值缺失或无效",
                "message": f"请补充 {elem} 实验室结果及检出限，交质量负责人复核。",
            })
            element_rows.append({
                "element": elem, "measured_ppb": None, "limit_ppb": limit_val,
                "utilization_pct": None, "status": "UNVERIFIED",
            })
            continue
        ratio = meas_val / limit_val
        if meas_val > limit_val:
            st = "EXCEEDED_RED"
            red_cards.append(
                {
                    "code": f"COA_METAL_{elem.upper()}_EXCEEDED",
                    "title": f"痕量金属 [{elem}] 超出 12 寸 Fab 规格上限红牌",
                    "message": (
                        f"{elem} 实测 {meas_val:.1f} ppb > 准入上限 {limit_val:.1f} ppb！"
                        "请质量负责人复核测试结果和批次处置。"
                    ),
                }
            )
        elif ratio >= 0.85:
            st = "BORDERLINE_YELLOW"
            warnings.append(
                {
                    "code": f"COA_METAL_{elem.upper()}_NEAR_LIMIT",
                    "title": f"痕量金属 [{elem}] 逼近规格警戒线 ({ratio*100:.1f}%)",
                    "message": f"{elem} 实测 {meas_val:.1f} ppb 接近上限 {limit_val:.1f} ppb，请质量负责人决定是否复测。",
                }
            )
        else:
            st = "PASS_GREEN"

        element_rows.append(
            {
                "element": elem,
                "measured_ppb": round(meas_val, 2),
                "limit_ppb": round(limit_val, 2),
                "utilization_pct": round(ratio * 100.0, 1),
                "status": st,
            }
        )

    # 2. 高脆硬材料多道工序累积在制品报废成本递推 (WIP Scrap Escalation)
    blank_usd = float(mfg["blank_cvd_sic_usd"])
    c1, y1 = float(mfg["step1_rough_grind_cost_usd"]), float(mfg["step1_rough_grind_yield"])
    c2, y2 = float(mfg["step2_ultrasonic_microhole_cost_usd"]), float(mfg["step2_ultrasonic_microhole_yield"])
    c3, y3 = float(mfg["step3_lapping_upw_clean_cost_usd"]), float(mfg["step3_lapping_upw_clean_yield"])
    target_margin = float(mfg.get("target_gross_margin", 0.38))

    for y in (y1, y2, y3):
        if not (0.20 <= y <= 1.0):
            raise ValueError("工序良率必须在 0.20 ~ 1.00 之间")
    if not (0.0 <= target_margin < 0.85):
        raise ValueError("目标毛利率须在 0 ~ 0.85 之间")

    rolled_throughput_yield = y1 * y2 * y3
    naive_zero_scrap_cost_usd = blank_usd + c1 + c2 + c3

    # 精确递推：后道崩边报废会连带损失前道已投入的高价 CVD-SiC 毛坯与前序工时！
    after_step1_usd = (blank_usd + c1) / y1
    after_step2_usd = (after_step1_usd + c2) / y2
    true_good_breakeven_usd = (after_step2_usd + c3) / y3

    hidden_chipping_scrap_usd = true_good_breakeven_usd - naive_zero_scrap_cost_usd
    target_fob_quote_usd = true_good_breakeven_usd / (1.0 - target_margin)

    if rolled_throughput_yield < 0.70:
        warnings.append(
            {
                "code": "CHIPPING_YIELD_EROSION_HIGH",
                "title": "超声微孔/薄壁加工崩边综合直通良率偏低 (<70%)",
                "message": (
                    f"全流程直通良率 RTY={rolled_throughput_yield*100:.1f}%，单件隐性报废摊销高达 ${hidden_chipping_scrap_usd:,.2f}，"
                    "须优化超声主轴振幅与金刚石砂轮修整频次！"
                ),
            }
        )

    if red_cards:
        status = "RED"
        verdict = f"🔴 红牌锁批冻结（CoA 有 {len(red_cards)} 项超限或未核实，待质量负责人处理）"
    elif warnings:
        status = "YELLOW"
        verdict = "🟡 黄灯内控预警（CoA 满足限值但存在擦边项或崩边报废偏高，须按真实递推成本锁死报价）"
    else:
        status = "GREEN"
        verdict = f"🟢 已录入结果满足所填限值（待质量签字，RTY={rolled_throughput_yield*100:.1f}% 良率受控）"

    return {
        "part_name": part_name,
        "status": status,
        "verdict": verdict,
        "coa_audit": {
            "is_coa_clean": len(red_cards) == 0,
            "elements": element_rows,
        },
        "yield_costing": {
            "rolled_throughput_yield_pct": round(rolled_throughput_yield * 100.0, 2),
            "naive_zero_scrap_cost_usd": round(naive_zero_scrap_cost_usd, 2),
            "true_good_breakeven_usd": round(true_good_breakeven_usd, 2),
            "hidden_chipping_scrap_usd": round(hidden_chipping_scrap_usd, 2),
            "target_gross_margin": target_margin,
            "target_fob_quote_usd": round(target_fob_quote_usd, 2),
        },
        "red_cards": red_cards,
        "warnings": warnings,
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(res: Dict[str, Any]) -> str:
    yc = res["yield_costing"]
    lines = [
        "=" * 86,
        "🔬 大衍千机 · 12寸晶圆厂高纯耗材 CoA 痕量金属(ppb)拦截 & 崩边良率核价单",
        f"   送检批次 : {res['part_name']}",
        "=" * 86,
        f"• 品质核价结论 : {res['verdict']}",
        "-" * 86,
        "【一、300mm Fab 腔室级 ICP-MS 痕量金属杂质 (ppb) 极值门禁】",
    ]
    elem_chunks = []
    badges = {
        "EXCEEDED_RED": "❌超限", "BORDERLINE_YELLOW": "⚠️接近限值",
        "PASS_GREEN": "✅满足所填限值", "UNVERIFIED": "❌待核",
    }
    for element in res["coa_audit"]["elements"]:
        value = element["measured_ppb"]
        value_label = str(value) if value is not None else "未核验"
        badge = badges[element["status"]]
        elem_chunks.append(f"{element['element']}: {value_label}/{element['limit_ppb']}ppb({badge})")
    lines.append("  • " + "  |  ".join(elem_chunks[:3]))
    if len(elem_chunks) > 3:
        lines.append("  • " + "  |  ".join(elem_chunks[3:]))

    lines.extend(
        [
            "-" * 86,
            "【二、高纯石英/CVD-SiC 超声深孔崩边直通良率(RTY)与保本报价还原】",
            f"  • 全工序直通良率(RTY) : {yc['rolled_throughput_yield_pct']:.2f}%",
            f"  • 零报废假象裸成本    : ${yc['naive_zero_scrap_cost_usd']:,.2f}/件 （新手业务员漏算后道崩边连带报废毛坯的亏损价）",
            f"  • 真实良品保本底线价  : ${yc['true_good_breakeven_usd']:,.2f}/件 （含每件隐性崩边废品摊销 ${yc['hidden_chipping_scrap_usd']:,.2f}）",
            f"  • 建议含毛利出厂报价  : ${yc['target_fob_quote_usd']:,.2f}/件 （目标毛利率 {yc['target_gross_margin']*100:.0f}%）",
        ]
    )

    if res["red_cards"] or res["warnings"]:
        lines.append("-" * 86)
        lines.append("【三、晶圆厂污染拒收与工艺良率预警】")
        for rc in res["red_cards"]:
            lines.append(f"  ❌ [{rc['code']}] {rc['title']}: {rc['message']}")
        for wn in res["warnings"]:
            lines.append(f"  ⚠️  [{wn['code']}] {wn['title']}: {wn['message']}")

    lines.extend(
        [
            "-" * 86,
            "⚖️  合规底线 : 发往 12 寸 Fab 产线的高纯部件双层百级真空塑封前，须由品质总监核签原厂炉批号与 ICP-MS 检测原件。",
            FOOTER_SIGN,
            "=" * 86,
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · 半导体高纯耗材 CoA 金属拦截与脆硬加工良率核价器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行 300mm 刻蚀腔 CVD-SiC 部件 CoA 拦截与核价演示")
    parser.add_argument("--input", type=str, help="读取外部 JSON 批次参数文件")
    parser.add_argument("--blank-usd", type=float, help="高纯毛坯单价 (USD)")
    parser.add_argument("--drill-yield", type=float, help="超声微深孔工序良率 (0.20~1.0)")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    payload = json.loads(json.dumps(DEMO_SEMI_LOT))
    if args.input:
        p = pathlib.Path(args.input)
        if not p.is_file():
            print(f"参数文件不存在: {p}", file=sys.stderr)
            sys.exit(1)
        payload = json.loads(p.read_text(encoding="utf-8"))

    if args.blank_usd is not None:
        payload["machining_cost_and_yield"]["blank_cvd_sic_usd"] = args.blank_usd
    if args.drill_yield is not None:
        payload["machining_cost_and_yield"]["step2_ultrasonic_microhole_yield"] = args.drill_yield

    res = evaluate_semi_coa_and_yield(payload)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(res))


if __name__ == "__main__":
    main()
