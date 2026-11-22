#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transformer_bom_quote_guard.py — 出海电力变压器硅钢铜重联动报价与 IEC/IEEE 损耗资本化罚金(TOC)防亏核算器
输入额定容量(kVA)、取向硅钢重量与单价、铜/铝绕组重量与 LME 铜价敞口、实测空载损耗(P0)与负载损耗(Pk)、
海外标书保证值及每千瓦超耗罚金单价($/kW，即 Loss Capitalization A/B 因子)，
秒算出总拥有成本 TOC、超耗拒收红牌与锁铜保本 FOB 报价！

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/transformer_bom_quote_guard.py --demo
  python3 scripts/industry/transformer_bom_quote_guard.py --demo --json
  python3 scripts/industry/transformer_bom_quote_guard.py --kva 2500 --spot-cu 10500 --measured-p0 2.85
"""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"

DEMO_TRANSFORMER_BID: Dict[str, Any] = {
    "bid_name": "北美光伏升压站 2500kVA 美式箱变(Pad-Mounted)出口投标与 TOC 超耗罚金测算",
    "rated_kva": 2500.0,
    "silicon_steel_kg": 3150.0,
    "silicon_steel_usd_per_kg": 2.85,
    "winding_material": "copper",
    "winding_weight_kg": 1420.0,
    "base_lme_metal_usd_per_ton": 9200.0,
    "spot_lme_metal_usd_per_ton": 10450.0,
    "wire_fabrication_usd_per_kg": 1.35,
    "tank_oil_accessories_mfg_usd": 14800.0,
    "target_gross_margin": 0.22,
    "guaranteed_p0_kw": 2.40,
    "measured_p0_kw": 2.82,
    "guaranteed_pk_kw": 18.50,
    "measured_pk_kw": 20.10,
    "factor_a_no_load_usd_per_kw": 8500.0,
    "factor_b_load_usd_per_kw": 2600.0,
    "zero_positive_tolerance_clause": True,
}


def evaluate_transformer_bid(params: Dict[str, Any]) -> Dict[str, Any]:
    """精算硅钢+铜铝绕组 BOM 实时锁价、IEC 60076 损耗拒收红线与 IEEE TOC 损耗资本化罚金。"""
    bid_name = str(params.get("bid_name", "出海电力变压器 BOM 联动与 TOC 罚金核算"))
    rated_kva = float(params["rated_kva"])
    steel_kg = float(params["silicon_steel_kg"])
    steel_price = float(params["silicon_steel_usd_per_kg"])
    winding_mat = str(params.get("winding_material", "copper")).lower()
    winding_kg = float(params["winding_weight_kg"])
    base_lme_ton = float(params["base_lme_metal_usd_per_ton"])
    spot_lme_ton = float(params["spot_lme_metal_usd_per_ton"])
    wire_fab_kg = float(params.get("wire_fabrication_usd_per_kg", 1.35))
    other_mfg_usd = float(params["tank_oil_accessories_mfg_usd"])
    target_margin = float(params.get("target_gross_margin", 0.22))

    guar_p0 = float(params["guaranteed_p0_kw"])
    meas_p0 = float(params["measured_p0_kw"])
    guar_pk = float(params["guaranteed_pk_kw"])
    meas_pk = float(params["measured_pk_kw"])
    factor_a = float(params["factor_a_no_load_usd_per_kw"])
    factor_b = float(params["factor_b_load_usd_per_kw"])
    zero_pos_tol = bool(params.get("zero_positive_tolerance_clause", True))

    if rated_kva <= 0 or guar_p0 <= 0 or guar_pk <= 0 or not (0.0 <= target_margin < 0.80):
        raise ValueError("额定容量、保证空载/负载损耗必须大于 0，且目标毛利率须在 0~0.80 之间")

    # 1. BOM 成本与 LME 铜/铝价格敞口计算
    steel_cost_usd = steel_kg * steel_price
    winding_cost_at_base_usd = winding_kg * ((base_lme_ton / 1000.0) + wire_fab_kg)
    winding_cost_at_spot_usd = winding_kg * ((spot_lme_ton / 1000.0) + wire_fab_kg)
    lme_unhedged_erosion_usd = winding_cost_at_spot_usd - winding_cost_at_base_usd

    total_cost_at_spot_usd = steel_cost_usd + winding_cost_at_spot_usd + other_mfg_usd
    fob_breakeven_locked_usd = total_cost_at_spot_usd
    fob_target_quote_usd = total_cost_at_spot_usd / (1.0 - target_margin)

    # 2. IEC 60076-1 损耗偏差率 & 拒收红线判定
    guar_total_kw = guar_p0 + guar_pk
    meas_total_kw = meas_p0 + meas_pk

    p0_over_pct = ((meas_p0 - guar_p0) / guar_p0) * 100.0
    pk_over_pct = ((meas_pk - guar_pk) / guar_pk) * 100.0
    total_over_pct = ((meas_total_kw - guar_total_kw) / guar_total_kw) * 100.0

    # 3. 损耗资本化罚金与总拥有成本 TOC = Bid_Price + A * P0 + B * Pk
    excess_p0_kw = max(0.0, meas_p0 - guar_p0)
    excess_pk_kw = max(0.0, meas_pk - guar_pk)

    if zero_pos_tol:
        penalty_p0_usd = excess_p0_kw * factor_a
        penalty_pk_usd = excess_pk_kw * factor_b
    else:
        # 若允许部分免罚容差，仍对超额部分计罚；此处对正偏差严格测算最大风险敞口
        penalty_p0_usd = excess_p0_kw * factor_a
        penalty_pk_usd = excess_pk_kw * factor_b

    total_loss_penalty_usd = penalty_p0_usd + penalty_pk_usd
    toc_evaluated_usd = fob_target_quote_usd + meas_p0 * factor_a + meas_pk * factor_b

    # 如果销售按未锁铜的旧报价且吃下超耗罚金，实际剩余净利：
    unhedged_old_quote_usd = (steel_cost_usd + winding_cost_at_base_usd + other_mfg_usd) / (1.0 - target_margin)
    realized_profit_after_penalty_usd = fob_target_quote_usd - total_cost_at_spot_usd - total_loss_penalty_usd

    red_cards = []
    warnings = []

    if total_over_pct > 10.0:
        red_cards.append(
            {
                "code": "IEC60076_TOTAL_LOSS_REJECT",
                "title": "总损耗超出保证值 +10% 触发 IEC 60076 整台拒收红牌",
                "message": f"实测总损耗 {meas_total_kw:.2f}kW 超出标书保证总损耗 {guar_total_kw:.2f}kW 达 +{total_over_pct:.1f}% (> +10% 拒收上限)！",
            }
        )
    if p0_over_pct > 15.0 or pk_over_pct > 15.0:
        red_cards.append(
            {
                "code": "IEC60076_COMPONENT_LOSS_REJECT",
                "title": "单项空载/负载损耗超出保证值 +15% 触发 IEC 60076 拒收红牌",
                "message": (
                    f"空载损耗偏差 {p0_over_pct:+.1f}% / 负载损耗偏差 {pk_over_pct:+.1f}%，突破 +15% 法定拒收红线！"
                    "必须改用更高等级激光刻痕硅钢片或加大电磁线截面积重做电磁设计！"
                ),
            }
        )
    if total_loss_penalty_usd > 0 and realized_profit_after_penalty_usd <= 0:
        red_cards.append(
            {
                "code": "TOC_PENALTY_WIPES_OUT_PROFIT",
                "title": "TOC 损耗资本化罚金击穿整单毛利红牌",
                "message": f"超耗罚金高达 ${total_loss_penalty_usd:,.2f}，扣罚后单台净利跌至 ${realized_profit_after_penalty_usd:,.2f}（倒贴赔本）！",
            }
        )
    elif total_loss_penalty_usd > 0:
        warnings.append(
            {
                "code": "LOSS_PENALTY_EXPOSURE",
                "title": "存在超耗扣款敞口黄灯预警",
                "message": f"预计触发 TOC 超耗罚金 ${total_loss_penalty_usd:,.2f}（其中铁损罚 ${penalty_p0_usd:,.0f} + 铜损罚 ${penalty_pk_usd:,.0f}），须将安全报价上调至覆盖罚金或重调铁芯设计。",
            }
        )

    if lme_unhedged_erosion_usd > 500.0:
        warnings.append(
            {
                "code": "LME_COPPER_UNHEDGED_SPIKE",
                "title": "LME 铜/铝原料涨价侵蚀预警",
                "message": f"现货金属价较基准价上涨导致单台绕组成本净增 ${lme_unhedged_erosion_usd:,.2f}，合同必须绑定 LME 调价公式！",
            }
        )

    fob_safe_quote_covering_penalty_usd = (total_cost_at_spot_usd + total_loss_penalty_usd) / (1.0 - target_margin)

    if red_cards:
        status = "RED"
        verdict = f"🔴 红牌阻断投产/报标（命中 {len(red_cards)} 项 IEC 拒收或罚金穿仓红线，严禁按原电磁方案签字！）"
    elif warnings:
        status = "YELLOW"
        verdict = "🟡 黄灯带条件报价（须在合同锁死 LME 铜价联动条款并计提超耗安全垫）"
    else:
        status = "GREEN"
        verdict = "🟢 绿灯稳健中标（损耗优于标书保证值零罚金，锁铜毛利扎实）"

    return {
        "bid_name": bid_name,
        "rated_kva": rated_kva,
        "status": status,
        "verdict": verdict,
        "bom_and_quote": {
            "winding_material": winding_mat,
            "silicon_steel_cost_usd": round(steel_cost_usd, 2),
            "winding_cost_at_spot_usd": round(winding_cost_at_spot_usd, 2),
            "lme_unhedged_erosion_usd": round(lme_unhedged_erosion_usd, 2),
            "fob_breakeven_locked_usd": round(fob_breakeven_locked_usd, 2),
            "unhedged_old_quote_usd": round(unhedged_old_quote_usd, 2),
            "fob_target_quote_usd": round(fob_target_quote_usd, 2),
            "fob_safe_quote_covering_penalty_usd": round(fob_safe_quote_covering_penalty_usd, 2),
        },
        "toc_and_iec_audit": {
            "guaranteed_p0_kw": guar_p0,
            "measured_p0_kw": meas_p0,
            "p0_over_pct": round(p0_over_pct, 2),
            "guaranteed_pk_kw": guar_pk,
            "measured_pk_kw": meas_pk,
            "pk_over_pct": round(pk_over_pct, 2),
            "total_over_pct": round(total_over_pct, 2),
            "loss_penalty_usd": round(total_loss_penalty_usd, 2),
            "toc_evaluated_usd": round(toc_evaluated_usd, 2),
            "realized_profit_after_penalty_usd": round(realized_profit_after_penalty_usd, 2),
        },
        "red_cards": red_cards,
        "warnings": warnings,
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(res: Dict[str, Any]) -> str:
    bq = res["bom_and_quote"]
    ta = res["toc_and_iec_audit"]

    lines = [
        "=" * 84,
        "⚡ 大衍千机 · 出海电力变压器硅钢铜重联动 & IEC/IEEE 损耗罚金(TOC)防亏核算单",
        f"   投标项目 : {res['bid_name']} ({res['rated_kva']:,.0f} kVA)",
        "=" * 84,
        f"• 商务总工结论 : {res['verdict']}",
        "-" * 84,
        "【一、取向硅钢 + LME 铜价敞口锁价核价】",
        f"  • 核心主材成本 : 取向硅钢 ${bq['silicon_steel_cost_usd']:,.2f}  |  现货铜/铝绕组 ${bq['winding_cost_at_spot_usd']:,.2f} (LME涨价蚀利 ${bq['lme_unhedged_erosion_usd']:+,.2f}/台)",
        f"  • 锁铜保本底线 : FOB ${bq['fob_breakeven_locked_usd']:,.2f}/台  |  标准目标毛利 FOB 报价: ${bq['fob_target_quote_usd']:,.2f}/台",
        f"  • 含罚金安全价 : FOB ${bq['fob_safe_quote_covering_penalty_usd']:,.2f}/台（若不改电磁设计硬扛超耗罚金所需的兜底报价）",
        "-" * 84,
        "【二、IEC 60076 损耗容差 & 海外电网 TOC 资本化罚金对撞】",
        f"  • 空载铁损(P0) : 保证 {ta['guaranteed_p0_kw']:.2f} kW vs 实测 {ta['measured_p0_kw']:.2f} kW ({ta['p0_over_pct']:+.1f}%，IEC单项红线 <= +15%)",
        f"  • 负载铜损(Pk) : 保证 {ta['guaranteed_pk_kw']:.2f} kW vs 实测 {ta['measured_pk_kw']:.2f} kW ({ta['pk_over_pct']:+.1f}%，IEC总耗偏差 {ta['total_over_pct']:+.1f}% 红线 <= +10%)",
        f"  • TOC 评标总价 : ${ta['toc_evaluated_usd']:,.2f}  |  超耗扣罚金额: ${ta['loss_penalty_usd']:,.2f}  |  扣罚后净利: ${ta['realized_profit_after_penalty_usd']:,.2f}",
    ]
    if res["red_cards"] or res["warnings"]:
        lines.append("-" * 84)
        lines.append("【三、海外电网拒收与蚀利红黄牌预警】")
        for rc in res["red_cards"]:
            lines.append(f"  ❌ [{rc['code']}] {rc['title']}: {rc['message']}")
        for wn in res["warnings"]:
            lines.append(f"  ⚠️  [{wn['code']}] {wn['title']}: {wn['message']}")

    lines.extend(
        [
            "-" * 84,
            "⚖️  合规底线 : 海外标书保证损耗填报及 LME 调价公式须经电磁总设计师与外贸商务总监双签字确认后方可递交。",
            FOOTER_SIGN,
            "=" * 84,
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · 出海电力变压器硅钢铜重联动与 TOC 损耗罚金核算器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行 2500kVA 美式箱变出海投标与超耗拦截演示")
    parser.add_argument("--input", type=str, help="读取外部投标参数 JSON 文件")
    parser.add_argument("--kva", type=float, help="额定容量 (kVA)")
    parser.add_argument("--spot-cu", type=float, help="交货期现货 LME 铜价 (USD/ton)")
    parser.add_argument("--measured-p0", type=float, help="设计/实测空载损耗 P0 (kW)")
    parser.add_argument("--measured-pk", type=float, help="设计/实测负载损耗 Pk (kW)")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    params = dict(DEMO_TRANSFORMER_BID)
    if args.input:
        p = pathlib.Path(args.input)
        if not p.is_file():
            print(f"参数文件不存在: {p}", file=sys.stderr)
            sys.exit(1)
        params.update(json.loads(p.read_text(encoding="utf-8")))

    overrides = {
        "rated_kva": args.kva,
        "spot_lme_metal_usd_per_ton": args.spot_cu,
        "measured_p0_kw": args.measured_p0,
        "measured_pk_kw": args.measured_pk,
    }
    for k, v in overrides.items():
        if v is not None:
            params[k] = v

    res = evaluate_transformer_bid(params)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(res))


if __name__ == "__main__":
    main()
