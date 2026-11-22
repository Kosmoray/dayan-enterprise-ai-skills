#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ev_station_tco_calc.py — 电动重卡超充/换电站投建与国网两部制电价精算器 (Zero-Dependency CLI)
输入变压器容量(kVA)、最大并发需量(kW)、日均充电量(kWh)、国网容量电价与需量电价、
尖峰平谷度电价差与度电服务费、总投资额；自动对比「按容量计费 vs 按最大需量计费」每年节省电费临界点，
输出静态回收月数、盈亏平衡日均度电与红黄绿投决建议。

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/ev_station_tco_calc.py --demo
  python3 scripts/industry/ev_station_tco_calc.py --demo --json
  python3 scripts/industry/ev_station_tco_calc.py --kva 2500 --max-kw 1450 --daily-kwh 11500 --capex 4200000
"""

import argparse
import json
import math
import pathlib
import sys
from typing import Any, Dict

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"

DEMO_SCENARIO: Dict[str, Any] = {
    "project_name": "川渝砂石干线 2×1250kVA 电动重卡群充超充站（示范测算）",
    "transformer_kva": 2500.0,
    "max_concurrent_kw": 1450.0,
    "contracted_demand_kw": 1500.0,
    "daily_kwh": 16000.0,
    "operating_days_per_year": 350,
    "capacity_tariff_per_kva_month": 28.0,
    "demand_tariff_per_kw_month": 38.0,
    "grid_spread_per_kwh": 0.06,
    "service_fee_per_kwh": 0.38,
    "line_loss_cost_per_kwh": 0.02,
    "annual_opex_yuan": 180000.0,
    "capex_yuan": 4200000.0,
}


def calculate_ev_station_tco(params: Dict[str, Any]) -> Dict[str, Any]:
    """核心精算函数：计算国网两部制电价临界点、静态回收期与盈亏平衡日均度电。"""
    project_name = str(params.get("project_name", "电动重卡超充/换电站投建测算"))
    transformer_kva = float(params["transformer_kva"])
    max_concurrent_kw = float(params["max_concurrent_kw"])
    contracted_demand_kw = float(params.get("contracted_demand_kw", max_concurrent_kw))
    daily_kwh = float(params["daily_kwh"])
    operating_days = int(params.get("operating_days_per_year", 350))
    cap_tariff = float(params.get("capacity_tariff_per_kva_month", 28.0))
    dem_tariff = float(params.get("demand_tariff_per_kw_month", 38.0))
    grid_spread = float(params.get("grid_spread_per_kwh", 0.0))
    service_fee = float(params["service_fee_per_kwh"])
    line_loss_cost = float(params.get("line_loss_cost_per_kwh", 0.0))
    annual_opex = float(params.get("annual_opex_yuan", 0.0))
    capex_yuan = float(params["capex_yuan"])

    if transformer_kva <= 0 or dem_tariff <= 0 or capex_yuan <= 0 or operating_days <= 0:
        raise ValueError("变压器容量、需量电价、总投资额与年运营天数必须大于 0")

    # 1. 国网两部制基本电费：按容量计费 vs 按需量计费（含超合同需量 105% 加倍惩罚核查）
    monthly_capacity_fee = transformer_kva * cap_tariff
    annual_capacity_fee = monthly_capacity_fee * 12.0

    overrun_limit_kw = contracted_demand_kw * 1.05
    overrun_penalty_kw = max(0.0, max_concurrent_kw - overrun_limit_kw)
    # 超过核定值 105% 的部分，基本电费加倍收取（即额外再收 1 倍）
    monthly_demand_fee = (max_concurrent_kw + overrun_penalty_kw) * dem_tariff
    annual_demand_fee = monthly_demand_fee * 12.0

    # 无超限罚款前提下的理论临界并发需量 (kW)
    critical_demand_kw = (transformer_kva * cap_tariff) / dem_tariff
    critical_load_ratio = critical_demand_kw / transformer_kva

    if annual_demand_fee < annual_capacity_fee:
        recommended_billing = "按实际最大需量计费"
        optimal_annual_basic_fee = annual_demand_fee
    elif annual_capacity_fee < annual_demand_fee:
        recommended_billing = "按变压器容量计费"
        optimal_annual_basic_fee = annual_capacity_fee
    else:
        recommended_billing = "容量与需量持平（处于临界平衡点）"
        optimal_annual_basic_fee = annual_capacity_fee

    annual_basic_fee_saving = abs(annual_capacity_fee - annual_demand_fee)

    # 2. 度电边际贡献与年度现金流
    unit_margin_per_kwh = service_fee + grid_spread - line_loss_cost
    if unit_margin_per_kwh <= 0:
        raise ValueError("度电净毛利（服务费+价差-线损）必须大于 0，否则每充一度电都在倒贴")

    annual_kwh = daily_kwh * operating_days
    annual_gross_margin = annual_kwh * unit_margin_per_kwh
    annual_net_cashflow = annual_gross_margin - optimal_annual_basic_fee - annual_opex
    monthly_net_cashflow = annual_net_cashflow / 12.0

    # 3. 盈亏平衡日均度电 & 36个月目标回本日均度电
    annual_fixed_burden = optimal_annual_basic_fee + annual_opex
    breakeven_daily_kwh = annual_fixed_burden / (unit_margin_per_kwh * operating_days)
    target_36m_daily_kwh = (annual_fixed_burden + capex_yuan / 3.0) / (
        unit_margin_per_kwh * operating_days
    )

    if monthly_net_cashflow > 0:
        static_payback_months = capex_yuan / monthly_net_cashflow
    else:
        static_payback_months = math.inf

    # 4. 风险预警与红黄绿投决建议
    alerts = []
    if overrun_penalty_kw > 0:
        alerts.append(
            f"需量刺客红灯预警：最大并发功率 {max_concurrent_kw:.1f}kW 超过合同核定需量 105% 上限 ({overrun_limit_kw:.1f}kW)，"
            f"超出部分 {overrun_penalty_kw:.1f}kW 触发国网加倍计收基本电费！"
        )
    if max_concurrent_kw > transformer_kva * 0.90:
        alerts.append(
            f"变压器过载风险：最大并发 {max_concurrent_kw:.1f}kW 已逼近箱变视在容量 {transformer_kva:.0f}kVA 安全裕度，建议加装 EMS 柔性群充限功率或配储削峰。"
        )

    if math.isinf(static_payback_months) or static_payback_months > 54.0:
        risk_level = "RED"
        verdict = "🔴 红灯暂缓投建（静态回收期 > 54 个月或现金流为负，严禁盲目进场施工）"
        action = "必须重谈车队保底充电量协议、压降外线箱变 EPC 造价，或调整两部制电价申报模式后再上会。"
    elif static_payback_months > 36.0:
        risk_level = "YELLOW"
        verdict = "🟡 黄灯带条件立项（静态回收期 36–54 个月，抗车队流失垫子较薄）"
        action = "投建前务必与核心砂石/专线车队锁定阶梯保底度电条款，并通过错峰调度将谷电消纳占比推高。"
    else:
        risk_level = "GREEN"
        verdict = "🟢 绿灯优质立项（静态回收期 <= 36 个月，安全边际充足）"
        action = f"建议立即按「{recommended_billing}」向供电局申报基本电费，并锁定变压器增容点位。"

    return {
        "project_name": project_name,
        "inputs": {
            "transformer_kva": round(transformer_kva, 2),
            "max_concurrent_kw": round(max_concurrent_kw, 2),
            "contracted_demand_kw": round(contracted_demand_kw, 2),
            "daily_kwh": round(daily_kwh, 2),
            "operating_days_per_year": operating_days,
            "capacity_tariff_per_kva_month": round(cap_tariff, 2),
            "demand_tariff_per_kw_month": round(dem_tariff, 2),
            "grid_spread_per_kwh": round(grid_spread, 4),
            "service_fee_per_kwh": round(service_fee, 4),
            "line_loss_cost_per_kwh": round(line_loss_cost, 4),
            "annual_opex_yuan": round(annual_opex, 2),
            "capex_yuan": round(capex_yuan, 2),
        },
        "grid_two_part_comparison": {
            "monthly_capacity_fee_yuan": round(monthly_capacity_fee, 2),
            "annual_capacity_fee_yuan": round(annual_capacity_fee, 2),
            "monthly_demand_fee_yuan": round(monthly_demand_fee, 2),
            "annual_demand_fee_yuan": round(annual_demand_fee, 2),
            "critical_demand_kw": round(critical_demand_kw, 2),
            "critical_load_ratio_pct": round(critical_load_ratio * 100.0, 2),
            "overrun_penalty_kw": round(overrun_penalty_kw, 2),
            "recommended_billing": recommended_billing,
            "annual_basic_fee_saving_yuan": round(annual_basic_fee_saving, 2),
        },
        "economics": {
            "unit_margin_per_kwh": round(unit_margin_per_kwh, 4),
            "annual_kwh": round(annual_kwh, 2),
            "annual_gross_margin_yuan": round(annual_gross_margin, 2),
            "optimal_annual_basic_fee_yuan": round(optimal_annual_basic_fee, 2),
            "annual_net_cashflow_yuan": round(annual_net_cashflow, 2),
            "monthly_net_cashflow_yuan": round(monthly_net_cashflow, 2),
            "static_payback_months": None if math.isinf(static_payback_months) else round(static_payback_months, 1),
            "breakeven_daily_kwh": round(breakeven_daily_kwh, 1),
            "target_36m_daily_kwh": round(target_36m_daily_kwh, 1),
        },
        "decision": {
            "risk_level": risk_level,
            "verdict": verdict,
            "recommended_action": action,
            "alerts": alerts,
        },
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(res: Dict[str, Any]) -> str:
    inp = res["inputs"]
    grid = res["grid_two_part_comparison"]
    eco = res["economics"]
    dec = res["decision"]
    payback_str = (
        f"{eco['static_payback_months']:.1f} 个月 ({eco['static_payback_months']/12.0:.2f} 年)"
        if eco["static_payback_months"] is not None
        else "无法回本（净现金流 <= 0）"
    )

    lines = [
        "=" * 80,
        f"⚡ 大衍千机 · 电动重卡超充/换电站投建与两部制电价精算表",
        f"   项目名称 : {res['project_name']}",
        "=" * 80,
        f"• 投决综合定级 : {dec['verdict']}",
        f"• 首选报装策略 : {grid['recommended_billing']}（相比另一档每年净省电费 ¥{grid['annual_basic_fee_saving_yuan']:,.2f}）",
        f"• 静态回收周期 : {payback_str}  |  总投资额: ¥{inp['capex_yuan']:,.0f}",
        "-" * 80,
        "【一、国网两部制基本电费「容量 vs 需量」临界对撞】",
        f"  1. 变压器容量计费 : {inp['transformer_kva']:,.0f} kVA × ¥{inp['capacity_tariff_per_kva_month']:.2f}/月 = ¥{grid['monthly_capacity_fee_yuan']:,.2f}/月 (年缴 ¥{grid['annual_capacity_fee_yuan']:,.2f})",
        f"  2. 最大需量计费   : {inp['max_concurrent_kw']:,.0f} kW  × ¥{inp['demand_tariff_per_kw_month']:.2f}/月 = ¥{grid['monthly_demand_fee_yuan']:,.2f}/月 (年缴 ¥{grid['annual_demand_fee_yuan']:,.2f})",
        f"  3. 省钱切换临界点 : 当月最大并发需量 = {grid['critical_demand_kw']:,.1f} kW（约为变压器容量的 {grid['critical_load_ratio_pct']:.1f}%）",
        f"     └─ 低于 {grid['critical_demand_kw']:,.1f} kW 选「按需量」划算；高于该阈值果断切回「按容量」封顶！",
        "-" * 80,
        "【二、度电毛利、盈亏平衡点与年度净现金流】",
        f"  • 度电净边际毛利  : ¥{eco['unit_margin_per_kwh']:.4f}/kWh (服务费 ¥{inp['service_fee_per_kwh']:.2f} + 峰谷价差 ¥{inp['grid_spread_per_kwh']:.2f} - 线损 ¥{inp['line_loss_cost_per_kwh']:.2f})",
        f"  • 测算日均充电量  : {inp['daily_kwh']:,.0f} kWh/天 × {inp['operating_days_per_year']} 天 = 年充 {eco['annual_kwh']:,.0f} kWh",
        f"  • 年度经营净现金流: ¥{eco['annual_net_cashflow_yuan']:,.2f}/年 (毛利 ¥{eco['annual_gross_margin_yuan']:,.0f} - 最优基本电费 ¥{eco['optimal_annual_basic_fee_yuan']:,.0f} - 运维租金 ¥{inp['annual_opex_yuan']:,.0f})",
        f"  • 保本生死线日充电: {eco['breakeven_daily_kwh']:,.1f} kWh/天（低于此电量连基本电费与场租都包不住）",
        f"  • 36个月回本目标量: {eco['target_36m_daily_kwh']:,.1f} kWh/天",
    ]
    if dec["alerts"]:
        lines.append("-" * 80)
        lines.append("【三、工程与电费刺客预警】")
        for idx, al in enumerate(dec["alerts"], 1):
            lines.append(f"  [{idx}] {al}")
    lines.extend(
        [
            "-" * 80,
            f"📌 拍板动作建议 : {dec['recommended_action']}",
            "   （注：正式电力报装及并网投决请由电气总工结合当地电网最新代理购电工商业分时电价表复核签字）",
            FOOTER_SIGN,
            "=" * 80,
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · 电动重卡超充/换电站投建与两部制电价精算器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行川渝砂石干线电动重卡超充站内置示范样例")
    parser.add_argument("--input", type=str, help="读取外部 JSON 测算参数文件")
    parser.add_argument("--name", type=str, help="项目名称")
    parser.add_argument("--kva", type=float, help="变压器总容量 (kVA)")
    parser.add_argument("--max-kw", type=float, help="月最大并发需量功率 (kW)")
    parser.add_argument("--contract-kw", type=float, help="向电网申报核定的合同最大需量 (kW)")
    parser.add_argument("--daily-kwh", type=float, help="日均充电量 (kWh)")
    parser.add_argument("--days", type=int, help="年有效运营天数 (默认 350)")
    parser.add_argument("--cap-tariff", type=float, help="国网容量电价 (元/kVA·月)")
    parser.add_argument("--dem-tariff", type=float, help="国网需量电价 (元/kW·月)")
    parser.add_argument("--spread", type=float, help="尖峰平谷购售度电套利净价差 (元/kWh)")
    parser.add_argument("--service-fee", type=float, help="度电充电服务费 (元/kWh)")
    parser.add_argument("--line-loss", type=float, help="度电线损成本 (元/kWh)")
    parser.add_argument("--opex", type=float, help="年固定场租与运维人工成本 (元/年)")
    parser.add_argument("--capex", type=float, help="场站总投资额 CapEx (元)")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    params = dict(DEMO_SCENARIO)
    if args.input:
        in_path = pathlib.Path(args.input)
        if not in_path.is_file():
            print(f"参数文件不存在: {in_path}", file=sys.stderr)
            sys.exit(1)
        loaded = json.loads(in_path.read_text(encoding="utf-8"))
        params.update(loaded)

    cli_overrides = {
        "project_name": args.name,
        "transformer_kva": args.kva,
        "max_concurrent_kw": args.max_kw,
        "contracted_demand_kw": args.contract_kw,
        "daily_kwh": args.daily_kwh,
        "operating_days_per_year": args.days,
        "capacity_tariff_per_kva_month": args.cap_tariff,
        "demand_tariff_per_kw_month": args.dem_tariff,
        "grid_spread_per_kwh": args.spread,
        "service_fee_per_kwh": args.service_fee,
        "line_loss_cost_per_kwh": args.line_loss,
        "annual_opex_yuan": args.opex,
        "capex_yuan": args.capex,
    }
    for k, v in cli_overrides.items():
        if v is not None:
            params[k] = v
    if args.max_kw is not None and args.contract_kw is None and not args.input:
        params["contracted_demand_kw"] = args.max_kw

    result = calculate_ev_station_tco(params)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(result))


if __name__ == "__main__":
    main()
