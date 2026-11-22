#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
liquid_cooling_uqd_calc.py — AI算力机柜液冷热负荷、冷却液流量与 UQD 快接头压降 Cv 精算器 (Zero-Dependency CLI)
输入单机柜功率(kW)、冷板液冷占比(如 80%)、进出液温差 ΔT(℃)、丙二醇水溶液浓度(0%/25%/35%对应比热容与密度)、
串联 UQD 快接头对数与单对 Cv 值，自动算出所需体积流量(LPM)、快接头局部压降(kPa)、
风冷改液冷 PUE 节电年收益及防凝露露点温度红牌预警！

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/liquid_cooling_uqd_calc.py --demo
  python3 scripts/industry/liquid_cooling_uqd_calc.py --demo --json
  python3 scripts/industry/liquid_cooling_uqd_calc.py --rack-kw 120 --pg-pct 25 --delta-t 10 --cv 1.7
"""

import argparse
import json
import math
import pathlib
import sys
from typing import Any, Dict, Tuple

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"
LITERS_PER_US_GALLON = 3.785411784
KPA_PER_PSI = 6.894757

# 丙二醇水溶液 (Propylene Glycol, ~35℃ 二次侧工况) 标准物性表: {体积浓度%: (比热容 kJ/kg·K, 密度 kg/m³)}
PG_COOLANT_PROPS: Dict[int, Tuple[float, float]] = {
    0: (4.180, 994.0),   # 纯去离子水 DI Water
    25: (3.920, 1020.0), # OCP 冷板主流 PG25 抑菌防冻液
    35: (3.760, 1030.0), # PG35 增强型防冻冷却液
}

DEMO_LC_SCENARIO: Dict[str, Any] = {
    "project_name": "海外智算中心 120kW 8×GPU 高密液冷机柜二次侧选型核查（示范）",
    "rack_power_kw": 120.0,
    "rack_count": 20,
    "liquid_cooling_ratio": 0.80,
    "delta_t_c": 10.0,
    "pg_concentration_pct": 25,
    "parallel_nodes_per_rack": 8,
    "series_uqd_pairs_per_branch": 2,
    "uqd_cv_per_pair": 1.65,
    "max_allowed_uqd_dp_kpa": 45.0,
    "supply_inlet_temp_c": 22.0,
    "ambient_temp_c": 27.0,
    "ambient_rh_pct": 75.0,
    "old_air_pue": 1.52,
    "new_liquid_pue": 1.15,
    "electricity_price_yuan_per_kwh": 0.62,
}


def get_coolant_properties(pg_pct: int) -> Tuple[float, float]:
    """根据丙二醇浓度(0 / 25 / 35)返回 (比热容 Cp kJ/kg·K, 密度 rho kg/m³)。"""
    if pg_pct in PG_COOLANT_PROPS:
        return PG_COOLANT_PROPS[pg_pct]
    if not (0 <= pg_pct <= 55):
        raise ValueError("丙二醇浓度 pg_concentration_pct 须在 0% ~ 55% 之间（常用档：0 / 25 / 35）")
    # 线性近似插值
    cp = 4.180 - 0.0115 * pg_pct
    rho = 994.0 + 1.03 * pg_pct
    return round(cp, 4), round(rho, 2)


def calc_dew_point_c(ambient_temp_c: float, ambient_rh_pct: float) -> float:
    """使用 Magnus-Tetens 方程精确计算环境露点温度 (℃)。"""
    if not (1.0 <= ambient_rh_pct <= 100.0):
        raise ValueError("环境相对湿度 ambient_rh_pct 必须在 1% ~ 100% 之间")
    a = 17.27
    b = 237.7
    alpha = (a * ambient_temp_c) / (b + ambient_temp_c) + math.log(ambient_rh_pct / 100.0)
    return (b * alpha) / (a - alpha)


def calculate_liquid_cooling_uqd(params: Dict[str, Any]) -> Dict[str, Any]:
    """执行液冷机柜热负荷流量、UQD 快接头压降、露点防凝露与 PUE 节电收益精算。"""
    project_name = str(params.get("project_name", "AI算力机柜液冷与UQD快接头选型测算"))
    rack_kw = float(params["rack_power_kw"])
    rack_count = int(params.get("rack_count", 1))
    lc_ratio = float(params.get("liquid_cooling_ratio", 0.80))
    delta_t = float(params["delta_t_c"])
    pg_pct = int(params.get("pg_concentration_pct", 25))
    nodes = int(params.get("parallel_nodes_per_rack", 8))
    uqd_pairs = int(params.get("series_uqd_pairs_per_branch", 2))
    uqd_cv = float(params["uqd_cv_per_pair"])
    max_uqd_dp_kpa = float(params.get("max_allowed_uqd_dp_kpa", 45.0))

    inlet_temp_c = float(params.get("supply_inlet_temp_c", 25.0))
    amb_temp_c = float(params.get("ambient_temp_c", 26.0))
    amb_rh_pct = float(params.get("ambient_rh_pct", 60.0))

    old_pue = float(params.get("old_air_pue", 1.52))
    new_pue = float(params.get("new_liquid_pue", 1.15))
    elec_price = float(params.get("electricity_price_yuan_per_kwh", 0.62))

    if rack_kw <= 0 or delta_t <= 0 or nodes <= 0 or uqd_cv <= 0 or rack_count <= 0:
        raise ValueError("机柜功率、温差 ΔT、并联节点数、机柜数与快接头 Cv 值必须大于 0")
    if not (0.10 <= lc_ratio <= 1.0):
        raise ValueError("冷板液冷带走热量占比须在 0.10 ~ 1.00 之间")

    # 1. 物性与所需冷却液流量 (LPM)
    cp_kj_kgk, rho_kg_m3 = get_coolant_properties(pg_pct)
    specific_gravity = rho_kg_m3 / 1000.0

    rack_liquid_heat_kw = rack_kw * lc_ratio
    rack_air_residual_kw = rack_kw - rack_liquid_heat_kw

    mass_flow_kg_s = rack_liquid_heat_kw / (cp_kj_kgk * delta_t)
    rack_flow_lpm = (mass_flow_kg_s / rho_kg_m3) * 1000.0 * 60.0
    branch_flow_lpm = rack_flow_lpm / nodes

    # 2. UQD 盲插快接头局部压降 (ANSI/ISA Cv 公式: ΔP_psi = SG * (Q_gpm / Cv)^2)
    branch_flow_gpm = branch_flow_lpm / LITERS_PER_US_GALLON
    single_pair_dp_psi = specific_gravity * ((branch_flow_gpm / uqd_cv) ** 2)
    single_pair_dp_kpa = single_pair_dp_psi * KPA_PER_PSI
    branch_uqd_total_dp_kpa = single_pair_dp_kpa * uqd_pairs

    # 3. 机房露点温度与防凝露红牌判定
    dew_point_c = calc_dew_point_c(amb_temp_c, amb_rh_pct)
    dew_margin_c = inlet_temp_c - dew_point_c

    red_cards = []
    warnings = []

    if dew_margin_c <= 0.0:
        red_cards.append(
            {
                "code": "CONDENSATION_DEW_POINT_RED_CARD",
                "title": "二次侧进液温度低于机房露点温度（致命结露短路红牌）",
                "message": (
                    f"二次侧供液温度 {inlet_temp_c:.1f}℃ <= 机房当前露点 {dew_point_c:.2f}℃（环温 {amb_temp_c:.1f}℃/湿度 {amb_rh_pct:.0f}%）！"
                    "Manifold 与 GPU 冷板必结露滴水烧板，须立即将 CDU 供液温度调高至露点 +2℃ 以上或开启机房精密除湿！"
                ),
            }
        )
    elif dew_margin_c < 2.0:
        warnings.append(
            {
                "code": "NARROW_DEW_POINT_MARGIN",
                "title": "防凝露安全裕度不足 2.0℃ 黄灯预警",
                "message": f"供液温度 {inlet_temp_c:.1f}℃ 仅高于露点 {dew_point_c:.2f}℃ 约 {dew_margin_c:.2f}℃，不满足 OCP >= +2.0℃ 安全余量。",
            }
        )

    if branch_uqd_total_dp_kpa > max_uqd_dp_kpa:
        red_cards.append(
            {
                "code": "UQD_PRESSURE_DROP_EXCEEDED",
                "title": "UQD 快接头串联局部压降超标红牌",
                "message": (
                    f"单节点串联 {uqd_pairs} 对 UQD(Cv={uqd_cv}) 局部压降达 {branch_uqd_total_dp_kpa:.2f} kPa > 许用上限 {max_uqd_dp_kpa:.1f} kPa，"
                    "建议升级大通径 UQD06/UQD08 快接头或适当拉大进出液温差 ΔT。"
                ),
            }
        )

    # 4. 老旧风冷改液冷 PUE 节电年收益
    pue_reduction = max(0.0, old_pue - new_pue)
    total_it_kw = rack_kw * rack_count
    annual_saved_kwh = total_it_kw * 8760.0 * pue_reduction
    annual_saved_yuan = annual_saved_kwh * elec_price

    if red_cards:
        status = "RED"
        verdict = f"🔴 红牌拦截（检出 {len(red_cards)} 项凝露短路或流阻超标致命风险，严禁通液上电！）"
    elif warnings:
        status = "YELLOW"
        verdict = "🟡 黄灯带条件运行（水力满足要求，但防凝露温差安全垫偏薄需联动调温）"
    else:
        status = "GREEN"
        verdict = "🟢 绿灯工程放行（冷却液流量、UQD 压降与防凝露露点裕度均符合 OCP 规范）"

    return {
        "project_name": project_name,
        "status": status,
        "verdict": verdict,
        "hydraulics_and_thermal": {
            "rack_power_kw": round(rack_kw, 2),
            "rack_liquid_heat_kw": round(rack_liquid_heat_kw, 2),
            "rack_air_residual_kw": round(rack_air_residual_kw, 2),
            "pg_concentration_pct": pg_pct,
            "cp_kj_kgk": cp_kj_kgk,
            "density_kg_m3": rho_kg_m3,
            "delta_t_c": round(delta_t, 2),
            "rack_flow_lpm": round(rack_flow_lpm, 2),
            "branch_flow_lpm": round(branch_flow_lpm, 2),
            "branch_flow_gpm": round(branch_flow_gpm, 3),
            "single_uqd_dp_kpa": round(single_pair_dp_kpa, 2),
            "branch_uqd_total_dp_kpa": round(branch_uqd_total_dp_kpa, 2),
        },
        "condensation_guard": {
            "ambient_temp_c": round(amb_temp_c, 2),
            "ambient_rh_pct": round(amb_rh_pct, 2),
            "dew_point_c": round(dew_point_c, 2),
            "supply_inlet_temp_c": round(inlet_temp_c, 2),
            "dew_margin_c": round(dew_margin_c, 2),
        },
        "pue_energy_saving": {
            "rack_count": rack_count,
            "total_it_power_kw": round(total_it_kw, 2),
            "old_air_pue": round(old_pue, 3),
            "new_liquid_pue": round(new_pue, 3),
            "annual_saved_kwh": round(annual_saved_kwh, 1),
            "annual_saved_yuan": round(annual_saved_yuan, 2),
        },
        "red_cards": red_cards,
        "warnings": warnings,
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(res: Dict[str, Any]) -> str:
    ht = res["hydraulics_and_thermal"]
    cg = res["condensation_guard"]
    ps = res["pue_energy_saving"]

    lines = [
        "=" * 84,
        "💧 大衍千机 · AI算力机柜液冷热负荷、UQD快接头压降(Cv)与露点防凝露精算表",
        f"   项目名称 : {res['project_name']}",
        "=" * 84,
        f"• 工程审查结论 : {res['verdict']}",
        "-" * 84,
        "【一、冷却液流量与盲插快接头(UQD)流阻压降核算】",
        f"  • 机柜热负荷拆分 : 总功率 {ht['rack_power_kw']:.1f} kW -> 液冷带走 {ht['rack_liquid_heat_kw']:.1f} kW + 残余风冷 {ht['rack_air_residual_kw']:.1f} kW",
        f"  • 冷却液工质物性 : PG{ht['pg_concentration_pct']}% 丙二醇水溶液 (Cp={ht['cp_kj_kgk']:.3f} kJ/kg·K, 密度={ht['density_kg_m3']:.1f} kg/m³, ΔT={ht['delta_t_c']:.1f}℃)",
        f"  • 所需体积总流量 : 整柜 {ht['rack_flow_lpm']:.2f} LPM  |  单节点支路 {ht['branch_flow_lpm']:.2f} LPM ({ht['branch_flow_gpm']:.2f} GPM)",
        f"  • UQD 快接头压降 : 单对压降 {ht['single_uqd_dp_kpa']:.2f} kPa  -> 支路串联总压降 {ht['branch_uqd_total_dp_kpa']:.2f} kPa",
        "-" * 84,
        "【二、二次侧防凝露露点校核 & PUE 改造年度节电账单】",
        f"  • 机房露点核验   : 环温 {cg['ambient_temp_c']:.1f}℃ / 湿度 {cg['ambient_rh_pct']:.0f}% -> 露点温度 = {cg['dew_point_c']:.2f}℃",
        f"  • 供液防露安全垫 : 供液温度 {cg['supply_inlet_temp_c']:.1f}℃ vs 露点 {cg['dew_point_c']:.2f}℃ (裕度 {cg['dew_margin_c']:+.2f}℃，OCP要求 >= +2.0℃)",
        f"  • PUE 节电年收益 : {ps['rack_count']} 柜共 {ps['total_it_power_kw']:.0f} kW (PUE {ps['old_air_pue']:.2f}->{ps['new_liquid_pue']:.2f}) -> 年省电 {ps['annual_saved_kwh']:,.0f} kWh (约 ¥{ps['annual_saved_yuan']:,.2f}/年)",
    ]
    if res["red_cards"] or res["warnings"]:
        lines.append("-" * 84)
        lines.append("【三、热工水力与凝露短路拦截预警】")
        for rc in res["red_cards"]:
            lines.append(f"  ❌ [{rc['code']}] {rc['title']}: {rc['message']}")
        for wn in res["warnings"]:
            lines.append(f"  ⚠️  [{wn['code']}] {wn['title']}: {wn['message']}")

    lines.extend(
        [
            "-" * 84,
            "⚖️  合规底线 : 液冷二次侧保压检漏与供液温度曲线设定须经暖通/热设计总工签字确认后再带电投运。",
            FOOTER_SIGN,
            "=" * 84,
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · AI算力机柜液冷流量、UQD压降Cv与露点防凝露精算器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行 120kW AI 液冷机柜内置工程演示样例")
    parser.add_argument("--input", type=str, help="读取外部 JSON 测算文件")
    parser.add_argument("--rack-kw", type=float, help="单机柜总功率 (kW)")
    parser.add_argument("--lc-ratio", type=float, help="冷板液冷带走热负荷占比 (0.1~1.0)")
    parser.add_argument("--delta-t", type=float, help="进出液温差 ΔT (℃)")
    parser.add_argument("--pg-pct", type=int, help="丙二醇体积浓度百分比 (0 / 25 / 35)")
    parser.add_argument("--cv", type=float, help="单对 UQD 快接头流量系数 Cv")
    parser.add_argument("--inlet-temp", type=float, help="二次侧供液温度 (℃)")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    params = dict(DEMO_LC_SCENARIO)
    if args.input:
        p = pathlib.Path(args.input)
        if not p.is_file():
            print(f"参数文件不存在: {p}", file=sys.stderr)
            sys.exit(1)
        params.update(json.loads(p.read_text(encoding="utf-8")))

    overrides = {
        "rack_power_kw": args.rack_kw,
        "liquid_cooling_ratio": args.lc_ratio,
        "delta_t_c": args.delta_t,
        "pg_concentration_pct": args.pg_pct,
        "uqd_cv_per_pair": args.cv,
        "supply_inlet_temp_c": args.inlet_temp,
    }
    for k, v in overrides.items():
        if v is not None:
            params[k] = v

    res = calculate_liquid_cooling_uqd(params)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(res))


if __name__ == "__main__":
    main()
