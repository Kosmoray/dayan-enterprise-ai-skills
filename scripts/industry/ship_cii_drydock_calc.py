#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ship_cii_drydock_calc.py — 船舶 IMO CII 碳强度评级预警 & 坞修换钢板/追加工程单(VO)防漏核算器 (Zero-Dependency CLI)
精算 IMO CII 年度营运碳强度指标 AER = 燃油消耗CO2克数 / (载重吨DWT × 年航行海里) 与 A-E 评级边界预警，
以及船厂坞修换钢板(Steel Renewal)理论计费重量(长m × 宽m × 厚mm × 7.85 ÷ 1000 × 切割损耗系数)与
船东临时追加工程单(VO / Variation Order)阶梯加价防漏算模型。

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/ship_cii_drydock_calc.py --demo
  python3 scripts/industry/ship_cii_drydock_calc.py --demo --json
  python3 scripts/industry/ship_cii_drydock_calc.py --dwt 82000 --distance-nm 56000 --vlsfo-tons 6900
"""

import argparse
import json
import math
import pathlib
import sys
from typing import Any, Dict, List

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"

# IMO MEPC.364(79) 标准船用燃料碳转换因子 C_F (吨 CO2 / 吨燃油)
IMO_FUEL_CF: Dict[str, float] = {
    "HFO": 3.114,
    "VLSFO": 3.151,
    "MGO": 3.206,
    "LNG": 2.750,
    "METHANOL": 1.375,
}

# IMO 散货船 CII 评级四分位边界比值 (d1, d2, d3, d4)
BULK_CARRIER_DD_VECTORS = (0.86, 0.94, 1.06, 1.18)

# IMO MEPC.400(83), G3 年度因子。超出这些年份需要提供经核实的因子。
CII_REDUCTION_BY_YEAR = {
    2023: 5.0, 2024: 7.0, 2025: 9.0, 2026: 11.0,
    2027: 13.625, 2028: 16.250, 2029: 18.875, 2030: 21.500,
}

DEMO_SHIP_DRYDOCK: Dict[str, Any] = {
    "vessel_name": "M/V PACIFIC HORIZON (82,000 DWT 卡姆萨尔型散货船五周年特检坞修 & CII 核查)",
    "cii_input": {
        "dwt_tonnes": 82000.0,
        "annual_distance_nm": 54000.0,
        "eval_year": 2026,
        "reduction_factor_pct": 11.0,
        "fuel_consumption_tonnes": {
            "VLSFO": 5850.0,
            "MGO": 420.0,
        },
    },
    "drydock_steel_and_vo": {
        "cutting_scrap_factor": 1.22,
        "min_billed_piece_kg": 50.0,
        "base_steel_rate_usd_per_kg": 4.10,
        "steel_plates": [
            {
                "item_no": "SR-01",
                "location": "No.3 压载边舱底纵骨与外板双曲度换新 (AH36)",
                "length_m": 6.2,
                "width_m": 2.1,
                "thickness_mm": 18.0,
                "curvature_location_mult": 1.35,
                "is_urgent_vo": False,
            },
            {
                "item_no": "VO-14",
                "location": "出坞前48h船检UT抽查追加：机舱海底门阀箱烂穿换板 (AH36)",
                "length_m": 2.4,
                "width_m": 1.5,
                "thickness_mm": 22.0,
                "curvature_location_mult": 1.50,
                "is_urgent_vo": True,
            },
        ],
        "urgent_vo_surcharge_mult": 1.40,
        "staging_gasfree_ndt_extra_usd": 6800.0,
    },
}


def calc_bulk_carrier_required_aer(dwt_tonnes: float, reduction_pct: float = 11.0) -> float:
    """按 IMO MEPC.337(76) 计算散货船基准 CII_ref 及折减后 Required AER (g CO2 / DWT·nm)。"""
    capped_dwt = min(dwt_tonnes, 279000.0)
    cii_ref = 4745.0 * (capped_dwt ** -0.622)
    return cii_ref * (1.0 - reduction_pct / 100.0)


def assign_cii_rating(ratio: float) -> str:
    d1, d2, d3, d4 = BULK_CARRIER_DD_VECTORS
    if ratio <= d1:
        return "A"
    if ratio <= d2:
        return "B"
    if ratio <= d3:
        return "C"
    if ratio <= d4:
        return "D"
    return "E"


def evaluate_ship_cii_and_drydock(payload: Dict[str, Any]) -> Dict[str, Any]:
    """精算 IMO CII 碳强度评级与坞修换板计费钢重/临时 VO 追加工程总价。"""
    vessel_name = str(payload.get("vessel_name", "远洋商船 CII 评级与特检坞修核算"))
    cii_in = payload["cii_input"]
    dd_in = payload["drydock_steel_and_vo"]

    dwt = float(cii_in["dwt_tonnes"])
    dist_nm = float(cii_in["annual_distance_nm"])
    eval_year = int(cii_in.get("eval_year", 2026))
    red_pct = cii_in.get("reduction_factor_pct", CII_REDUCTION_BY_YEAR.get(eval_year))
    if red_pct is None or not 0 <= float(red_pct) < 100:
        raise ValueError("请填写已核实的年度 CII 折减因子")
    red_pct = float(red_pct)
    fuels = cii_in["fuel_consumption_tonnes"]

    if dwt <= 0 or dist_nm <= 0:
        raise ValueError("船舶载重吨 DWT 与年航行海里数必须大于 0")

    if not fuels:
        raise ValueError("请提供至少一项燃油用量")

    total_co2_tonnes = 0.0
    for f_type, tons in fuels.items():
        key = str(f_type).strip().upper()
        if key not in IMO_FUEL_CF:
            raise ValueError(f"不支持的船用燃油代码 '{f_type}'，可选 {list(IMO_FUEL_CF)}")
        consumed = float(tons)
        if not math.isfinite(consumed) or consumed < 0:
            raise ValueError("燃油用量须为非负有限数")
        total_co2_tonnes += consumed * IMO_FUEL_CF[key]

    total_co2_grams = total_co2_tonnes * 1_000_000.0
    attained_aer = total_co2_grams / (dwt * dist_nm)
    required_aer = (
        float(cii_in["required_aer_override"])
        if cii_in.get("required_aer_override") is not None
        else calc_bulk_carrier_required_aer(dwt, red_pct)
    )
    if not math.isfinite(required_aer) or required_aer <= 0:
        raise ValueError("Required CII 须为正有限数")
    cii_ratio = attained_aer / required_aer
    rating = assign_cii_rating(cii_ratio)
    c_upper_limit_aer = required_aer * BULK_CARRIER_DD_VECTORS[2]

    # 坞修换钢板与临时追加工程单 (VO) 计价
    scrap_factor = float(dd_in.get("cutting_scrap_factor", 1.22))
    min_piece_kg = float(dd_in.get("min_billed_piece_kg", 50.0))
    base_rate_kg = float(dd_in.get("base_steel_rate_usd_per_kg", 4.10))
    vo_mult = float(dd_in.get("urgent_vo_surcharge_mult", 1.40))
    extra_aux_usd = float(dd_in.get("staging_gasfree_ndt_extra_usd", 0.0))

    plate_rows: List[Dict[str, Any]] = []
    total_net_tonnes = 0.0
    total_billed_tonnes = 0.0
    total_steel_vo_usd = 0.0
    naive_unadjusted_usd = 0.0

    for pl in dd_in.get("steel_plates", []):
        l_m = float(pl["length_m"])
        w_m = float(pl["width_m"])
        t_mm = float(pl["thickness_mm"])
        loc_mult = float(pl.get("curvature_location_mult", 1.0))
        is_vo = bool(pl.get("is_urgent_vo", False))

        # 长m × 宽m × 厚mm × 7.85 ÷ 1000 = 净吨数
        net_tonnes = (l_m * w_m * t_mm * 7.85) / 1000.0
        net_kg = net_tonnes * 1000.0
        billed_kg = max(min_piece_kg, net_kg * scrap_factor)
        billed_tonnes = billed_kg / 1000.0

        applied_vo_mult = vo_mult if is_vo else 1.0
        effective_rate_kg = base_rate_kg * loc_mult * applied_vo_mult
        line_amount_usd = billed_kg * effective_rate_kg

        # 新手报价员漏算损耗系数、曲度难度与紧急VO加价的裸价
        naive_usd = net_kg * base_rate_kg

        total_net_tonnes += net_tonnes
        total_billed_tonnes += billed_tonnes
        total_steel_vo_usd += line_amount_usd
        naive_unadjusted_usd += naive_usd

        plate_rows.append(
            {
                "item_no": pl.get("item_no", "SR"),
                "location": pl.get("location", ""),
                "is_urgent_vo": is_vo,
                "net_weight_tonnes": round(net_tonnes, 4),
                "billed_weight_tonnes": round(billed_tonnes, 4),
                "effective_rate_usd_per_kg": round(effective_rate_kg, 2),
                "line_total_usd": round(line_amount_usd, 2),
            }
        )

    grand_drydock_section_usd = total_steel_vo_usd + extra_aux_usd
    prevented_underquote_loss_usd = grand_drydock_section_usd - naive_unadjusted_usd

    red_cards = []
    warnings = []
    if rating == "E":
        red_cards.append(
            {
                "code": "IMO_CII_RATING_E_PENALTY",
                "title": "散货船 CII 测算落入 E 级区间",
                "message": (
                    f"实测 AER={attained_aer:.2f} > D/E 红线 {required_aer*BULK_CARRIER_DD_VECTORS[3]:.2f} g CO2/(DWT·nm)！"
                    "请机务核对正式数据及经核验的 SEEMP 整改要求。"
                ),
            }
        )
    elif rating == "D":
        warnings.append(
            {
                "code": "IMO_CII_RATING_D_WARNING",
                "title": "IMO CII 落入 D 级黄灯预警（连续 3 年 D 级将强制整改）",
                "message": f"实测 AER={attained_aer:.2f} 高于 C 级上限 {c_upper_limit_aer:.2f}，请机务核对年度结果与历史等级。",
            }
        )

    if any(p["is_urgent_vo"] for p in plate_rows):
        warnings.append(
            {
                "code": "URGENT_VO_DOCK_DELAY_GUARD",
                "title": "出坞前紧急追加工程单(VO)船坞占坞期顺延提醒",
                "message": "存在水线以下临时追加换板 VO，商务报价单须同步由船东机务签认『坞期顺延免除船期延误罚金(LD)』！",
            }
        )

    if red_cards:
        status = "RED"
        verdict = "🔴 红牌合规预警（散货船 CII 预估进入 E 级区间，待专业复核）"
    elif warnings:
        status = "YELLOW"
        verdict = "🟡 黄灯商务管控（CII 处于 D 级边缘或含紧急追加 VO，须锁死切割损耗与免责顺延签字）"
    else:
        status = "GREEN"
        verdict = f"🟢 散货船 CII 预估为 {rating} 级，可核对坞修费用明细"

    return {
        "vessel_name": vessel_name,
        "status": status,
        "verdict": verdict,
        "imo_cii_audit": {
            "scope": "散货船初估，未纳入航次修正，供机务与核验方复核",
            "eval_year": eval_year,
            "dwt_tonnes": dwt,
            "annual_distance_nm": dist_nm,
            "total_co2_tonnes": round(total_co2_tonnes, 2),
            "attained_aer": round(attained_aer, 3),
            "required_aer": round(required_aer, 3),
            "c_grade_upper_aer": round(c_upper_limit_aer, 3),
            "cii_ratio": round(cii_ratio, 3),
            "cii_rating": rating,
        },
        "drydock_vo_settlement": {
            "cutting_scrap_factor": scrap_factor,
            "total_net_steel_tonnes": round(total_net_tonnes, 3),
            "total_billed_steel_tonnes": round(total_billed_tonnes, 3),
            "plates": plate_rows,
            "staging_gasfree_ndt_extra_usd": round(extra_aux_usd, 2),
            "grand_total_usd": round(grand_drydock_section_usd, 2),
            "prevented_underquote_loss_usd": round(prevented_underquote_loss_usd, 2),
        },
        "red_cards": red_cards,
        "warnings": warnings,
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(res: Dict[str, Any]) -> str:
    cii = res["imo_cii_audit"]
    dd = res["drydock_vo_settlement"]

    lines = [
        "=" * 86,
        "🚢 大衍千机 · 远洋船舶 IMO CII 碳强度评级 & 坞修换板/追加工程单(VO)核算表",
        f"   目标船舶 : {res['vessel_name']}",
        "=" * 86,
        f"• 海事总工结论 : {res['verdict']}",
        "-" * 86,
        "【一、IMO MARPOL Annex VI 年度营运碳强度指标 (CII / AER) 核验】",
        f"  • 营运排放底数 : 载重吨 {cii['dwt_tonnes']:,.0f} DWT  |  年航程 {cii['annual_distance_nm']:,.0f} 海里  |  年排 CO2 {cii['total_co2_tonnes']:,.1f} 吨",
        f"  • 碳强度比对   : 实测 AER = {cii['attained_aer']:.3f} vs 折减基准 {cii['required_aer']:.3f} (C级安全上限 {cii['c_grade_upper_aer']:.3f})",
        f"  • 测算范围     : {cii['scope']}",
        f"  • 散货船 CII 预估评级 : 【 {cii['cii_rating']} 级 】 (AER 比值 = {cii['cii_ratio']:.3f})",
        "-" * 86,
        "【二、船厂坞修换钢板(Steel Renewal)计费钢重 & 紧急 VO 阶梯结算单】",
        f"  • 钢重损耗放大 : 几何净钢重 {dd['total_net_steel_tonnes']:.3f} 吨 × 切割余量系数 {dd['cutting_scrap_factor']:.2f} -> 结算计费钢重 {dd['total_billed_steel_tonnes']:.3f} 吨",
    ]
    for p in dd["plates"]:
        vo_tag = "[紧急VO加价]" if p["is_urgent_vo"] else "[常规合同项]"
        lines.append(
            f"    ▪ {p['item_no']} {vo_tag} {p['location']} | 计费重 {p['billed_weight_tonnes']:.3f}t × ${p['effective_rate_usd_per_kg']:.2f}/kg = ${p['line_total_usd']:,.2f}"
        )
    lines.append(
        f"  • 脚手架/测爆/NDT辅费 : ${dd['staging_gasfree_ndt_extra_usd']:,.2f}  |  本分项应收总计: ${dd['grand_total_usd']:,.2f}"
    )
    lines.append(
        f"  • 防漏算挽回毛利额    : 相比按净尺寸平铺直算多挽回隐性损耗与抢工费 ${dd['prevented_underquote_loss_usd']:,.2f}！"
    )

    if res["red_cards"] or res["warnings"]:
        lines.append("-" * 86)
        lines.append("【三、船级社合规与修船商务风控提示】")
        for rc in res["red_cards"]:
            lines.append(f"  ❌ [{rc['code']}] {rc['title']}: {rc['message']}")
        for wn in res["warnings"]:
            lines.append(f"  ⚠️  [{wn['code']}] {wn['title']}: {wn['message']}")

    lines.extend(
        [
            "-" * 86,
            "⚖️  合规底线 : 船体换板材料船检证书(3.1/3.2)与 VO 坞期顺延协议须经验船师及机务代表现场双签确认。",
            FOOTER_SIGN,
            "=" * 86,
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · 船舶 IMO CII 评级与坞修换板 VO 计价核算器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行 82,000 DWT 散货船 CII 与特检换板 VO 演示")
    parser.add_argument("--input", type=str, help="读取外部 JSON 测算参数文件")
    parser.add_argument("--dwt", type=float, help="船舶载重吨 (DWT)")
    parser.add_argument("--distance-nm", type=float, help="年累计航行海里数 (nm)")
    parser.add_argument("--vlsfo-tons", type=float, help="年消耗 VLSFO 低硫重油吨数")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    payload = json.loads(json.dumps(DEMO_SHIP_DRYDOCK))
    if args.input:
        p = pathlib.Path(args.input)
        if not p.is_file():
            print(f"参数文件不存在: {p}", file=sys.stderr)
            sys.exit(1)
        payload = json.loads(p.read_text(encoding="utf-8"))

    if args.dwt is not None:
        payload["cii_input"]["dwt_tonnes"] = args.dwt
    if args.distance_nm is not None:
        payload["cii_input"]["annual_distance_nm"] = args.distance_nm
    if args.vlsfo_tons is not None:
        payload["cii_input"]["fuel_consumption_tonnes"] = {"VLSFO": args.vlsfo_tons}

    res = evaluate_ship_cii_and_drydock(payload)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(res))


if __name__ == "__main__":
    main()
