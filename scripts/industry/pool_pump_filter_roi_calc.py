#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pool_pump_filter_roi_calc.py — 欧美变频泳池泵节能回本与 SPA 替换滤芯渠道毛利精算器 (Zero-Dependency CLI)
输入泳池容积(加仑/m³)、日循环周转次数、传统单速泵功率 vs 智能变频泵高/低速排班功率、欧美当地电价($/kWh)，
精确算出年省电量、投资回收月数、渠道商安装毛利留存，并内置滤芯外径/长度/上下开口与过滤面积(sq.ft)误差校验！

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/pool_pump_filter_roi_calc.py --demo
  python3 scripts/industry/pool_pump_filter_roi_calc.py --demo --json
  python3 scripts/industry/pool_pump_filter_roi_calc.py --gallons 22000 --tariff 0.34
"""

import argparse
import json
import math
import pathlib
import sys
from typing import Any, Dict

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"
GALLONS_PER_M3 = 264.172052

DEMO_POOL_PAYLOAD: Dict[str, Any] = {
    "scenario_name": "北美加州 20,000 加仑私家泳池变频泵替换 + 兼容 PRB50-IN SPA 滤芯复购测算",
    "pump_roi": {
        "pool_volume_gallons": 20000.0,
        "turnovers_per_day": 2.0,
        "season_days_per_year": 300,
        "electricity_tariff_usd_per_kwh": 0.34,
        "single_speed_watts": 1950.0,
        "single_speed_hours_per_day": 8.0,
        "inverter_high_watts": 1050.0,
        "inverter_high_hours_per_day": 2.0,
        "inverter_low_watts": 185.0,
        "inverter_low_hours_per_day": 12.0,
        "fob_ningbo_usd": 258.0,
        "dealer_landed_cost_usd": 335.0,
        "msrp_installed_usd": 1150.0,
    },
    "spa_filter_check": {
        "cross_ref_code": "Compatible with Pleatco PRB50-IN / Unicel C-4950",
        "oem_spec": {
            "outer_diameter_inch": 5.000,
            "length_inch": 13.3125,
            "top_end_cap": "Open 2-1/8 inch",
            "bottom_end_cap": "Open 2-1/8 inch",
            "claimed_area_sqft": 50.0,
        },
        "factory_sample": {
            "outer_diameter_inch": 5.020,
            "length_inch": 13.620,
            "top_end_cap": "Open 2-1/8 inch",
            "bottom_end_cap": "1-1/2 inch SAE Thread",
            "pleat_count": 195,
            "pleat_height_inch": 1.15,
            "media_active_length_inch": 12.8,
            "fob_unit_usd": 3.45,
            "landed_fba_cost_usd": 6.80,
            "retail_pack_unit_usd": 16.50,
        },
    },
}


def evaluate_pool_and_spa(payload: Dict[str, Any]) -> Dict[str, Any]:
    """核算变频泳池泵业主省电回本、Pool-Builder 渠道毛利与 SPA 替换滤芯防发错货校验。"""
    scenario_name = str(payload.get("scenario_name", "欧美变频泳池泵与SPA滤芯富矿测算"))
    pmp = payload["pump_roi"]
    flt = payload["spa_filter_check"]

    if "pool_volume_gallons" in pmp and pmp["pool_volume_gallons"] is not None:
        vol_gal = float(pmp["pool_volume_gallons"])
        vol_m3 = vol_gal / GALLONS_PER_M3
    else:
        vol_m3 = float(pmp["pool_volume_m3"])
        vol_gal = vol_m3 * GALLONS_PER_M3

    turnovers = float(pmp.get("turnovers_per_day", 2.0))
    season_days = int(pmp.get("season_days_per_year", 300))
    tariff = float(pmp["electricity_tariff_usd_per_kwh"])

    ss_watts = float(pmp["single_speed_watts"])
    ss_hours = float(pmp["single_speed_hours_per_day"])
    inv_hi_w = float(pmp["inverter_high_watts"])
    inv_hi_h = float(pmp["inverter_high_hours_per_day"])
    inv_lo_w = float(pmp["inverter_low_watts"])
    inv_lo_h = float(pmp["inverter_low_hours_per_day"])

    fob_pump = float(pmp["fob_ningbo_usd"])
    landed_pump = float(pmp["dealer_landed_cost_usd"])
    msrp_pump = float(pmp["msrp_installed_usd"])

    if vol_gal <= 0 or tariff <= 0 or season_days <= 0 or msrp_pump <= 0:
        raise ValueError("泳池容积、电价、年运行天数与终端售价必须大于 0")

    daily_turnover_gallons = vol_gal * turnovers
    ss_daily_kwh = (ss_watts * ss_hours) / 1000.0
    inv_daily_kwh = (inv_hi_w * inv_hi_h + inv_lo_w * inv_lo_h) / 1000.0

    energy_saving_pct = ((ss_daily_kwh - inv_daily_kwh) / ss_daily_kwh) * 100.0 if ss_daily_kwh > 0 else 0.0
    annual_saved_kwh = (ss_daily_kwh - inv_daily_kwh) * season_days
    annual_saved_usd = annual_saved_kwh * tariff

    if annual_saved_usd > 0:
        payback_months = msrp_pump / (annual_saved_usd / 12.0)
    else:
        payback_months = math.inf

    dealer_profit_usd = msrp_pump - landed_pump
    dealer_margin_pct = (dealer_profit_usd / msrp_pump) * 100.0

    # SPA 替换滤芯几何尺寸与展开过滤面积 (sq.ft) 校验
    oem = flt["oem_spec"]
    smp = flt["factory_sample"]

    od_diff = abs(float(smp["outer_diameter_inch"]) - float(oem["outer_diameter_inch"]))
    len_diff = abs(float(smp["length_inch"]) - float(oem["length_inch"]))
    top_match = str(smp["top_end_cap"]).strip().lower() == str(oem["top_end_cap"]).strip().lower()
    bot_match = str(smp["bottom_end_cap"]).strip().lower() == str(oem["bottom_end_cap"]).strip().lower()

    # 展开过滤面积公式: 折数 * (2 * 折高_inch) * 有效滤纸长_inch / 144 (sq.in -> sq.ft)
    actual_area_sqft = (
        int(smp["pleat_count"]) * (2.0 * float(smp["pleat_height_inch"])) * float(smp["media_active_length_inch"])
    ) / 144.0
    claimed_area_sqft = float(oem["claimed_area_sqft"])
    area_ratio_pct = (actual_area_sqft / claimed_area_sqft) * 100.0

    flt_landed = float(smp["landed_fba_cost_usd"])
    flt_retail = float(smp["retail_pack_unit_usd"])
    flt_gross_margin_pct = ((flt_retail - flt_landed) / flt_retail) * 100.0

    red_cards = []
    if od_diff > 0.125:
        red_cards.append(
            {
                "code": "FILTER_OD_TOLERANCE_EXCEEDED",
                "message": f"滤芯外径偏差 {od_diff:.3f}\" > 许用公差 0.125\" (1/8英寸)，将导致滤桶卡死或脏水旁通！",
            }
        )
    if len_diff > 0.125:
        red_cards.append(
            {
                "code": "FILTER_LENGTH_TOLERANCE_EXCEEDED",
                "message": f"滤芯总长偏差 {len_diff:.4f}\" > 许用公差 0.125\"，会导致 SPA 滤桶顶盖无法旋紧漏水退货！",
            }
        )
    if not (top_match and bot_match):
        red_cards.append(
            {
                "code": "FILTER_ENDCAP_THREAD_MISMATCH",
                "message": (
                    f"上下端盖接口不匹配！原厂要求 [{oem['top_end_cap']} / {oem['bottom_end_cap']}]，"
                    f"打样实测 [{smp['top_end_cap']} / {smp['bottom_end_cap']}]（SAE粗牙/MPT细牙/圆孔发错必遭批量差评召回）！"
                ),
            }
        )
    if area_ratio_pct < 95.0:
        red_cards.append(
            {
                "code": "FILTER_AREA_SHORTFALL",
                "message": f"实测过滤面积 {actual_area_sqft:.1f} sq.ft 仅为标称 {claimed_area_sqft:.0f} sq.ft 的 {area_ratio_pct:.1f}% (<95% 偷工减料红线)！",
            }
        )

    if red_cards:
        status = "RED"
        verdict = f"🔴 滤芯防呆红牌拦截（变频泵ROI优异，但替换滤芯检出 {len(red_cards)} 处模具尺寸/牙口致命错配，严禁大货装箱！）"
    else:
        status = "GREEN"
        verdict = "🟢 绿灯高毛利放行（变频泵电费回本快、滤芯互换尺寸严丝合缝且渠道毛利丰厚）"

    return {
        "scenario_name": scenario_name,
        "status": status,
        "verdict": verdict,
        "inverter_pump_economics": {
            "pool_volume_gallons": round(vol_gal, 1),
            "pool_volume_m3": round(vol_m3, 2),
            "daily_turnover_gallons": round(daily_turnover_gallons, 1),
            "single_speed_daily_kwh": round(ss_daily_kwh, 2),
            "inverter_daily_kwh": round(inv_daily_kwh, 2),
            "energy_saving_pct": round(energy_saving_pct, 1),
            "annual_saved_kwh": round(annual_saved_kwh, 1),
            "annual_saved_usd": round(annual_saved_usd, 2),
            "homeowner_payback_months": None if math.isinf(payback_months) else round(payback_months, 1),
            "fob_ningbo_usd": round(fob_pump, 2),
            "dealer_gross_profit_usd": round(dealer_profit_usd, 2),
            "dealer_margin_pct": round(dealer_margin_pct, 2),
        },
        "spa_filter_audit": {
            "cross_ref_code": flt["cross_ref_code"],
            "od_diff_inch": round(od_diff, 4),
            "length_diff_inch": round(len_diff, 4),
            "end_caps_matched": top_match and bot_match,
            "actual_filtration_area_sqft": round(actual_area_sqft, 2),
            "claimed_area_sqft": round(claimed_area_sqft, 2),
            "channel_gross_margin_pct": round(flt_gross_margin_pct, 2),
            "red_cards": red_cards,
        },
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(res: Dict[str, Any]) -> str:
    pe = res["inverter_pump_economics"]
    fa = res["spa_filter_audit"]
    pb_str = f"{pe['homeowner_payback_months']:.1f} 个月" if pe["homeowner_payback_months"] is not None else "无法回本"

    lines = [
        "=" * 84,
        "🏊 大衍千机 · 欧美变频泳池泵节能回本 & SPA 替换滤芯防错货毛利精算表",
        f"   测算场景 : {res['scenario_name']}",
        "=" * 84,
        f"• 出海核查结论 : {res['verdict']}",
        "-" * 84,
        "【一、北美 DOE 合规智能变频泳池泵：业主省电账 & 工程商渠道毛利】",
        f"  • 泳池循环工况 : {pe['pool_volume_gallons']:,.0f} US Gal ({pe['pool_volume_m3']:.1f} m³)  |  日循环过滤水量: {pe['daily_turnover_gallons']:,.0f} Gal",
        f"  • 日耗电大跳水 : 传统单速泵 {pe['single_speed_daily_kwh']:.2f} kWh/天 -> 变频高/低速排班 {pe['inverter_daily_kwh']:.2f} kWh/天 (省电 {pe['energy_saving_pct']:.1f}%)",
        f"  • 业主回本账单 : 年省电 {pe['annual_saved_kwh']:,.0f} kWh = 净省电费 ${pe['annual_saved_usd']:,.2f}/年 -> 终端回本周期仅 {pb_str}！",
        f"  • 渠道暴利留存 : FOB出厂 ${pe['fob_ningbo_usd']:.0f} -> Pool-Builder 单台净赚安装毛利 ${pe['dealer_gross_profit_usd']:,.2f} (毛利率 {pe['dealer_margin_pct']:.1f}%)",
        "-" * 84,
        f"【二、高复购 SPA 替换滤芯互换防呆校验】({fa['cross_ref_code']})",
        f"  • 尺寸公差核对 : 外径偏差 {fa['od_diff_inch']:.3f}\" | 总长偏差 {fa['length_diff_inch']:.4f}\" (红线 <= 0.125\") | 端盖接口一致: {'✅ 是' if fa['end_caps_matched'] else '❌ 错配'}",
        f"  • 展开过滤面积 : 实测 {fa['actual_filtration_area_sqft']:.1f} sq.ft vs 标称 {fa['claimed_area_sqft']:.0f} sq.ft  |  耗材渠道毛利率: {fa['channel_gross_margin_pct']:.2f}%",
    ]
    for rc in fa["red_cards"]:
        lines.append(f"  ❌ [{rc['code']}] {rc['message']}")

    lines.extend(
        [
            "-" * 84,
            "⚖️  合规底线 : 北美出货前须由认证工程师核验 DOE 专用泳池泵能效备案(WEF)及涉水材料 NSF/ANSI 50 证书有效性。",
            FOOTER_SIGN,
            "=" * 84,
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · 欧美变频泳池泵节能回本与 SPA 滤芯毛利精算器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行北美 20,000 加仑泳池与 SPA 滤芯演示样例")
    parser.add_argument("--input", type=str, help="读取外部 JSON 测算参数文件")
    parser.add_argument("--gallons", type=float, help="覆盖泳池美制加仑容积")
    parser.add_argument("--m3", type=float, help="按立方米输入泳池容积")
    parser.add_argument("--tariff", type=float, help="欧美当地居民电价 (USD/kWh)")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    payload = json.loads(json.dumps(DEMO_POOL_PAYLOAD))
    if args.input:
        p = pathlib.Path(args.input)
        if not p.is_file():
            print(f"参数文件不存在: {p}", file=sys.stderr)
            sys.exit(1)
        payload = json.loads(p.read_text(encoding="utf-8"))

    if args.gallons is not None:
        payload["pump_roi"]["pool_volume_gallons"] = args.gallons
    elif args.m3 is not None:
        payload["pump_roi"].pop("pool_volume_gallons", None)
        payload["pump_roi"]["pool_volume_m3"] = args.m3
    if args.tariff is not None:
        payload["pump_roi"]["electricity_tariff_usd_per_kwh"] = args.tariff

    res = evaluate_pool_and_spa(payload)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(res))


if __name__ == "__main__":
    main()
