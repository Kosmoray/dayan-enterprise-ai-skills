#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cis_export_doc_checker.py — 二手车与工程机械中亚/俄语出口单证交叉校对器 (Zero-Dependency CLI)
内置标准 17 位 VIN 车架号第 9 位模 11 校验位算法核验真伪，并交叉比对商业发票、装箱单、
出口许可证与 SMGS 国际铁路联运单证中的 VIN、件数、毛重(kg)、币种金额一致性。

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/cis_export_doc_checker.py --demo
  python3 scripts/industry/cis_export_doc_checker.py --demo --json
  python3 scripts/industry/cis_export_doc_checker.py --vin LGXC66C41R0125893
  python3 scripts/industry/cis_export_doc_checker.py --input shipment_docs.json [--json]
"""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"

VIN_TRANSLITERATION: Dict[str, int] = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4,
    "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "P": 7, "R": 9,
    "S": 2, "T": 3, "U": 4, "V": 5, "W": 6, "X": 7, "Y": 8, "Z": 9,
}

VIN_POSITION_WEIGHTS: List[int] = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
FORBIDDEN_VIN_CHARS = {"I", "O", "Q"}

# 内置青白江→霍尔果斯→阿拉木图二手新能源车与重卡联运单证错单演示包
DEMO_SHIPMENT_DOCS: Dict[str, Any] = {
    "shipment_id": "QBJ-KHORGOS-20261122-07",
    "route": "成都城厢(青白江) -> 霍尔果斯口岸 -> 哈萨克斯坦阿拉木图 (SMGS 笼车/集装箱联运)",
    "commercial_invoice": {
        "doc_no": "CI-DY-20261108",
        "currency": "USD",
        "total_amount": 56800.00,
        "units": 2,
        "vins": ["LGXC66C41R0125893", "LZZ5CLNBXRN208427"],
    },
    "packing_list": {
        "doc_no": "PL-DY-20261108",
        "units": 2,
        "gross_weight_kg": 11260.0,
        "vins": ["LGXC66C41R0125893", "LZZ5CLNBXRN208427"],
    },
    "export_license": {
        "license_no": "26-51-409982",
        "currency": "USD",
        "total_amount": 56800.00,
        "units": 2,
        "gross_weight_kg": 11260.0,
        "transfer_for_export_endorsed": True,
        "vins": ["LGXC66C41R0125893", "LZZ5CLNBXRN208427"],
    },
    "smgs_waybill": {
        "waybill_no": "SMGS-39081275",
        "units": 2,
        "gross_weight_kg": 11380.0,
        # 模拟货代录单员手滑把第二台车第 9 位校验位 'X' 误敲成数字 '0'，且第 24 栏毛重多填了 120kg
        "vins": ["LGXC66C41R0125893", "LZZ5CLNB0RN208427"],
    },
}


def verify_vin_mod11(vin: str) -> Dict[str, Any]:
    """
    依据 GB 16735 / ISO 3779 核验 17 位 VIN 车架号格式及第 9 位模 11 校验码。
    """
    normalized = str(vin or "").strip().upper()
    if len(normalized) != 17:
        return {
            "vin": normalized,
            "is_valid": False,
            "expected_check_digit": None,
            "actual_check_digit": normalized[8] if len(normalized) >= 9 else None,
            "error": f"长度错误：当前 {len(normalized)} 位，标准 VIN 必须严格为 17 位",
        }

    bad_chars = sorted({ch for ch in normalized if ch in FORBIDDEN_VIN_CHARS})
    if bad_chars:
        return {
            "vin": normalized,
            "is_valid": False,
            "expected_check_digit": None,
            "actual_check_digit": normalized[8],
            "error": f"含禁用混淆字符 {bad_chars}（标准 VIN 严禁包含字母 I、O、Q）",
        }

    illegal = sorted({ch for ch in normalized if ch not in VIN_TRANSLITERATION})
    if illegal:
        return {
            "vin": normalized,
            "is_valid": False,
            "expected_check_digit": None,
            "actual_check_digit": normalized[8],
            "error": f"含非法字符 {illegal}",
        }

    weighted_sum = sum(
        VIN_TRANSLITERATION[ch] * VIN_POSITION_WEIGHTS[idx]
        for idx, ch in enumerate(normalized)
    )
    remainder = weighted_sum % 11
    expected = "X" if remainder == 10 else str(remainder)
    actual = normalized[8]
    is_valid = actual == expected

    return {
        "vin": normalized,
        "is_valid": is_valid,
        "weighted_sum": weighted_sum,
        "expected_check_digit": expected,
        "actual_check_digit": actual,
        "error": None if is_valid else f"第 9 位模 11 校验位不匹配：实填 '{actual}'，算法应为 '{expected}'",
    }


def cross_check_cis_documents(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """交叉校对商业发票、装箱单、出口许可证与 SMGS 国际铁路联运运单。"""
    ci = bundle["commercial_invoice"]
    pl = bundle["packing_list"]
    el = bundle["export_license"]
    smgs = bundle["smgs_waybill"]

    doc_map = {
        "商业发票(CI)": ci,
        "装箱单(PL)": pl,
        "出口许可证(EL)": el,
        "国际铁路联运单(SMGS)": smgs,
    }

    # 1. 汇总全部出现的 VIN 并逐一过模 11 校验
    all_vins_ordered: List[str] = []
    for doc in doc_map.values():
        for v in doc.get("vins", []):
            vn = str(v).strip().upper()
            if vn not in all_vins_ordered:
                all_vins_ordered.append(vn)

    vin_audits = [verify_vin_mod11(v) for v in all_vins_ordered]
    red_discrepancies: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []

    for va in vin_audits:
        if not va["is_valid"]:
            holders = [
                name for name, d in doc_map.items()
                if va["vin"] in [str(x).strip().upper() for x in d.get("vins", [])]
            ]
            red_discrepancies.append(
                {
                    "code": "INVALID_VIN_CHECK_DIGIT",
                    "field": "VIN 第9位模11校验",
                    "detail": f"单证 [{', '.join(holders)}] 中的车架号 {va['vin']} 校验失败：{va['error']}",
                    "fix": "立即对照车辆铭牌拓印件与《机动车登记证书》原件更正错录字符，防止口岸海关布控退单。",
                }
            )

    # 2. 四单 VIN 列表一致性比对（以出口许可证为法定基准）
    base_vins = [str(x).strip().upper() for x in el.get("vins", [])]
    for doc_name, doc in doc_map.items():
        if doc_name == "出口许可证(EL)":
            continue
        curr_vins = [str(x).strip().upper() for x in doc.get("vins", [])]
        if curr_vins != base_vins:
            red_discrepancies.append(
                {
                    "code": "VIN_CROSS_DOC_MISMATCH",
                    "field": "跨单证 VIN 一致性",
                    "detail": f"{doc_name} VIN 列表 {curr_vins} 与出口许可证法定基准 {base_vins} 不一致！",
                    "fix": f"将 {doc_name} 中的 VIN 严格修正为与出口许可证及车管所转让待出口签注完全一致。",
                }
            )

    # 3. 件数/台数一致性比对
    unit_values = {name: int(d["units"]) for name, d in doc_map.items() if "units" in d}
    if len(set(unit_values.values())) > 1:
        red_discrepancies.append(
            {
                "code": "UNITS_COUNT_MISMATCH",
                "field": "车辆台数/件数",
                "detail": f"四单台数不一致：{unit_values}",
                "fix": "统一商业发票、装箱单、许可证及 SMGS 运单第 15 栏件数；若有随车备胎/充电桩分箱须单独列明包装件数。",
            }
        )

    # 4. 毛重(kg)一致性比对（装箱单 vs 出口许可证 vs SMGS 第24栏）
    weight_docs = {
        "装箱单(PL)": float(pl["gross_weight_kg"]),
        "出口许可证(EL)": float(el["gross_weight_kg"]),
        "国际铁路联运单(SMGS)": float(smgs["gross_weight_kg"]),
    }
    max_w = max(weight_docs.values())
    min_w = min(weight_docs.values())
    if abs(max_w - min_w) > 0.5:
        red_discrepancies.append(
            {
                "code": "GROSS_WEIGHT_MISMATCH",
                "field": "总毛重(kg)交叉核对",
                "detail": f"单证间毛重相差 {max_w - min_w:.1f} kg -> {weight_docs}",
                "fix": "SMGS 铁路口岸换装严查衡重与舱单一致，请立即拉齐装箱单、报关草单与 SMGS 第 24 栏毛重数据！",
            }
        )

    # 5. 币种与总金额比对（商业发票 vs 出口许可证）
    ci_curr = str(ci.get("currency", "")).strip().upper()
    el_curr = str(el.get("currency", "")).strip().upper()
    ci_amt = float(ci.get("total_amount", 0.0))
    el_amt = float(el.get("total_amount", 0.0))

    if ci_curr != el_curr:
        red_discrepancies.append(
            {
                "code": "CURRENCY_MISMATCH",
                "field": "结算币种",
                "detail": f"商业发票币种 ({ci_curr}) 与出口许可证币种 ({el_curr}) 不一致！",
                "fix": "按商务部二手车出口许可证申领口径统一结算币种，严禁 USD/CNY/RUB 混填报关。",
            }
        )
    elif abs(ci_amt - el_amt) > 0.01:
        red_discrepancies.append(
            {
                "code": "AMOUNT_MISMATCH",
                "field": "合同/发票总金额",
                "detail": f"商业发票金额 ({ci_curr} {ci_amt:,.2f}) 与出口许可证金额 ({el_curr} {el_amt:,.2f}) 不一致！",
                "fix": "核对贸易术语（FOB/CIP 霍尔果斯）运保费拆分明细，确保报关单与许可证证面金额吻合。",
            }
        )

    if not bool(el.get("transfer_for_export_endorsed", True)):
        red_discrepancies.append(
            {
                "code": "MISSING_TRANSFER_FOR_EXPORT",
                "field": "车管所转让待出口签注",
                "detail": "《机动车登记证书》尚未完成『转让待出口』签注！",
                "fix": "发运报关前必须在车管所办结转让待出口登记，并于出口通关后 2 个月内凭报关单办结注销登记。",
            }
        )

    if red_discrepancies:
        status = "RED"
        verdict = f"🔴 红牌扣单预警（检出 {len(red_discrepancies)} 处致命单证差错，未改单前严禁向铁路港/报关行发送舱单！）"
    elif warnings:
        status = "YELLOW"
        verdict = "🟡 黄灯提示（四单核心字段吻合，请复核随车附件明细）"
    else:
        status = "GREEN"
        verdict = "🟢 绿灯放行（全部 17 位 VIN 模 11 校验通过，CI/PL/许可证/SMGS 四单严丝合缝）"

    return {
        "shipment_id": bundle.get("shipment_id", "CIS-EXPORT-BATCH"),
        "route": bundle.get("route", ""),
        "status": status,
        "verdict": verdict,
        "vin_mod11_audits": vin_audits,
        "red_discrepancies": red_discrepancies,
        "warnings": warnings,
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(report: Dict[str, Any]) -> str:
    lines = [
        "=" * 84,
        "🚆 大衍千机 · 二手车与工程机械中亚/俄语出口四单 & VIN 模 11 交叉校对单",
        f"   发运批次 : {report['shipment_id']}  |  联运干线: {report['route']}",
        "=" * 84,
        f"• 关务放行结论 : {report['verdict']}",
        f"• 扫描车架号数 : {len(report['vin_mod11_audits'])} 个  |  🔴 单证冲突/错码: {len(report['red_discrepancies'])} 处",
        "-" * 84,
        "【一、17 位 VIN 车架号 ISO 3779 模 11 校验位真伪核验】",
    ]
    for va in report["vin_mod11_audits"]:
        if va["is_valid"]:
            lines.append(
                f"  ✅ {va['vin']}  -> 模11校验通过 (加权和={va['weighted_sum']}, 第9位校验码='{va['actual_check_digit']}')"
            )
        else:
            lines.append(f"  ❌ {va['vin']}  -> {va['error']}")

    lines.append("-" * 84)
    lines.append("【二、商业发票(CI) × 装箱单(PL) × 出口许可证(EL) × 铁路运单(SMGS) 交叉比对】")
    if report["red_discrepancies"]:
        for idx, rd in enumerate(report["red_discrepancies"], 1):
            lines.append(f"  ❌ [{idx}] [{rd['field']}] {rd['detail']}")
            lines.append(f"       └─ 纠偏指令: {rd['fix']}")
    else:
        lines.append("  ✅ 四份核心通关单证的 VIN 序列、台数、毛重(kg)与币种金额 100% 一致！")

    lines.extend(
        [
            "-" * 84,
            "⚖️  合规底线 : 正式报关及签发 SMGS 国际铁路联运运单前，须由关务主管对照《机动车登记证书》原件签字复核。",
            FOOTER_SIGN,
            "=" * 84,
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · 二手车与工程机械中亚/俄语出口单证交叉校对器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行青白江至阿拉木图二手车 SMGS 错单拦截演示")
    parser.add_argument("--vin", type=str, help="单独校验某一个 17 位 VIN 车架号的模 11 合法性")
    parser.add_argument("--input", type=str, help="读取四单数据 JSON 文件")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    if args.vin:
        v_res = verify_vin_mod11(args.vin)
        v_res["powered_by"] = "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)"
        if args.json:
            print(json.dumps(v_res, ensure_ascii=False, indent=2))
        else:
            badge = "✅ 合法 VIN" if v_res["is_valid"] else "❌ 非法/错录 VIN"
            print("=" * 72)
            print(f"{badge} : {v_res['vin']}")
            if v_res["is_valid"]:
                print(f"第 9 位模 11 校验码核验通过: '{v_res['actual_check_digit']}' (加权和 {v_res['weighted_sum']})")
            else:
                print(f"原因: {v_res['error']}")
            print(FOOTER_SIGN)
            print("=" * 72)
        return

    bundle = json.loads(json.dumps(DEMO_SHIPMENT_DOCS))
    if args.input:
        in_path = pathlib.Path(args.input)
        if not in_path.is_file():
            print(f"单证文件不存在: {in_path}", file=sys.stderr)
            sys.exit(1)
        bundle = json.loads(in_path.read_text(encoding="utf-8"))

    report = cross_check_cis_documents(bundle)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(report))


if __name__ == "__main__":
    main()
