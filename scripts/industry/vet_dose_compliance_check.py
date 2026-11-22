#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vet_dose_compliance_check.py — 宠医专科给药安全与人药兽用合规核查器 (Zero-Dependency CLI)
内置犬猫体重(kg)转体表面积 BSA = K * (W_g ** (2/3)) / 10000 (犬 K=10.1, 猫 K=10.0) 精确公式、
常见犬猫绝对禁忌成分红牌库、兽药批准文号正则校验及“超范围使用人用药必须核查农业农村部急需目录
并由执业兽医签字知情同意”强制红牌预警。

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/vet_dose_compliance_check.py --demo
  python3 scripts/industry/vet_dose_compliance_check.py --demo --json
  python3 scripts/industry/vet_dose_compliance_check.py --input rx.json [--json]
"""

import argparse
import json
import pathlib
import re
import sys
from typing import Any, Dict, List, Optional

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"

BSA_K_FACTORS = {
    "dog": 10.1,
    "犬": 10.1,
    "cat": 10.0,
    "猫": 10.0,
}

# 农业农村部标准兽药批准文号（现行9位编码及含4位年号编码）与进口兽药注册证号正则
VET_APPROVAL_PATTERNS = [
    re.compile(r"^兽药(字|生字|原字|添字|临字|械字)(?:[（(]?\d{4}[)）]?\s*)?\d{9}$"),
    re.compile(r"^[（(]?\d{4}[)）]?外兽药证字\d{2,4}号$"),
]
HUMAN_DRUG_PATTERN = re.compile(r"^国药准字[HZSJBTC]\d{8}$")

# 犬猫绝对禁忌与高危中毒成分红牌库
CONTRAINDICATION_DB = [
    {
        "species": {"cat"},
        "keywords": ["对乙酰氨基酚", "扑热息痛", "acetaminophen", "paracetamol"],
        "level": "RED",
        "code": "CAT_ACETAMINOPHEN_LETHAL",
        "reason": "猫肝脏先天缺乏葡萄糖醛酸转移酶(UGT1A6)，极小剂量对乙酰氨基酚即可导致高铁血红蛋白血症、海因茨小体溶血与急性肝坏死致死！",
    },
    {
        "species": {"cat"},
        "keywords": ["氯菊酯", "二氯苯醚菊酯", "permethrin"],
        "level": "RED",
        "code": "CAT_PERMETHRIN_TOXIC",
        "reason": "猫对拟除虫菊酯类（常见于犬用体外驱虫滴剂）极度敏感，误用或同居舔舐会引发剧烈肌肉震颤、癫痫持续状态甚至死亡！",
    },
    {
        "species": {"cat", "dog"},
        "keywords": ["布洛芬", "萘普生", "氟比洛芬", "ibuprofen", "naproxen", "flurbiprofen"],
        "level": "RED",
        "code": "PET_HUMAN_NSAID_TOXIC",
        "reason": "人用非甾体抗炎药（布洛芬/萘普生/氟比洛芬）在犬猫体内安全窗极窄且消除缓慢，极易引发急性胃十二指肠穿孔与急性肾衰竭！",
    },
    {
        "species": {"dog", "cat"},
        "keywords": ["木糖醇", "xylitol"],
        "level": "RED",
        "code": "PET_XYLITOL_TOXIC",
        "reason": "木糖醇（常见于人用无糖口服液/咀嚼片辅料）会诱发犬胰岛素暴发性释放，30分钟内引发致死性低血糖及急性肝坏死！",
    },
    {
        "species": {"cat"},
        "keywords": ["苯佐卡因", "benzocaine"],
        "level": "RED",
        "code": "CAT_BENZOCAINE_TOXIC",
        "reason": "苯佐卡因局麻剂可诱发猫严重高铁血红蛋白血症与组织缺氧发绀，严禁用于猫咽喉或皮肤黏膜！",
    },
    {
        "species": {"cat"},
        "keywords": ["磷酸钠灌肠", "fleet enema"],
        "level": "RED",
        "code": "CAT_PHOSPHATE_ENEMA_TOXIC",
        "reason": "含磷酸钠灌肠剂会导致猫致命性高磷血症、严重低钙抽搐与心律失常，猫便秘绝对禁用！",
    },
]

DEMO_PRESCRIPTIONS: List[Dict[str, Any]] = [
    {
        "case_id": "RX-2026-01",
        "pet_name": "糯米（英短蓝猫）",
        "species": "cat",
        "breed": "英国短毛猫",
        "weight_kg": 4.2,
        "drug_name": "复方对乙酰氨基酚感冒颗粒（人用制剂）",
        "ingredients": "对乙酰氨基酚 250mg、咖啡因、马来酸氯苯那敏",
        "approval_no": "国药准字H44021068",
        "is_human_drug": True,
        "in_moa_urgent_list": False,
        "vet_signed_consent": False,
        "dose_mg_per_kg": 15.0,
        "max_safe_mg_per_kg": 0.0,
    },
    {
        "case_id": "RX-2026-02",
        "pet_name": "闪电（边境牧羊犬）",
        "species": "dog",
        "breed": "边境牧羊犬",
        "weight_kg": 18.0,
        "drug_name": "宠物用美洛昔康内服混悬液",
        "ingredients": "美洛昔康 (Meloxicam)",
        "approval_no": "兽药字220152512",
        "is_human_drug": False,
        "in_moa_urgent_list": False,
        "vet_signed_consent": True,
        "dose_mg_per_kg": 0.1,
        "max_safe_mg_per_kg": 0.2,
        "dose_mg_per_m2": 3.0,
    },
    {
        "case_id": "RX-2026-03",
        "pet_name": "豆豆（泰迪犬·ICU重症）",
        "species": "dog",
        "breed": "贵宾犬",
        "weight_kg": 6.5,
        "drug_name": "注射用美罗培南（重症临床急需人用药）",
        "ingredients": "美罗培南",
        "approval_no": "国药准字H20083344",
        "is_human_drug": True,
        "in_moa_urgent_list": True,
        "vet_signed_consent": False,
        "dose_mg_per_kg": 12.0,
        "max_safe_mg_per_kg": 20.0,
    },
]


def normalize_species(raw: str) -> str:
    val = str(raw).strip().lower()
    if val in ("dog", "犬", "canine", "狗"):
        return "dog"
    if val in ("cat", "猫", "feline"):
        return "cat"
    raise ValueError(f"暂不支持的物种标识 '{raw}'（仅支持 dog/犬 或 cat/猫）")


def calc_bsa_m2(species: str, weight_kg: float) -> float:
    """
    精确计算伴侣动物体表面积 (Body Surface Area, m²):
    BSA = K * (W_g ** (2/3)) / 10000
    犬 K = 10.1，猫 K = 10.0，W_g 为克(g)为单位体重。
    """
    sp = normalize_species(species)
    if weight_kg <= 0:
        raise ValueError("动物体重 weight_kg 必须大于 0")
    k_val = BSA_K_FACTORS[sp]
    weight_g = weight_kg * 1000.0
    return k_val * (weight_g ** (2.0 / 3.0)) / 10000.0


def validate_vet_approval_no(approval_no: str) -> Dict[str, Any]:
    """校验兽药批准文号格式是否合法，或识别是否为国药准字人用药。"""
    cleaned = str(approval_no or "").strip()
    if not cleaned:
        return {"is_valid_vet_no": False, "is_human_approval_no": False, "detail": "缺失批准文号"}
    for pat in VET_APPROVAL_PATTERNS:
        if pat.match(cleaned):
            return {"is_valid_vet_no": True, "is_human_approval_no": False, "detail": "符合农业农村部兽药批准文号规范"}
    if HUMAN_DRUG_PATTERN.match(cleaned):
        return {"is_valid_vet_no": False, "is_human_approval_no": True, "detail": "识别为国家药监局『国药准字』人用药品批文"}
    return {"is_valid_vet_no": False, "is_human_approval_no": False, "detail": "文号格式不符合『兽药字/兽药生字+4位年份+9位编号』标准"}


def check_prescription(rx: Dict[str, Any]) -> Dict[str, Any]:
    """对单张宠医处方执行 BSA 换算、禁忌毒理拦截与人药兽用合规审查。"""
    sp = normalize_species(rx["species"])
    weight_kg = float(rx["weight_kg"])
    bsa_m2 = calc_bsa_m2(sp, weight_kg)

    drug_name = str(rx.get("drug_name", ""))
    ingredients = str(rx.get("ingredients", ""))
    combined_text = f"{drug_name} {ingredients}".lower()
    breed = str(rx.get("breed", ""))

    approval_no = str(rx.get("approval_no", "")).strip()
    approval_check = validate_vet_approval_no(approval_no)
    is_human_drug = bool(rx.get("is_human_drug", False)) or approval_check["is_human_approval_no"]
    in_moa_urgent_list = bool(rx.get("in_moa_urgent_list", False))
    vet_signed_consent = bool(rx.get("vet_signed_consent", False))

    red_cards: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []

    # 1. 禁忌成分红牌扫描
    for rule in CONTRAINDICATION_DB:
        if sp in rule["species"]:
            matched = [kw for kw in rule["keywords"] if kw.lower() in combined_text]
            if matched:
                red_cards.append(
                    {
                        "code": rule["code"],
                        "title": f"物种绝对禁忌成分命中（{', '.join(matched)}）",
                        "message": rule["reason"],
                    }
                )

    # 柯利犬系 MDR1 基因敏感品种额外核查
    if sp == "dog" and any(b in breed for b in ("牧羊犬", "边牧", "柯利", "喜乐蒂", "澳牧")):
        if any(kw in combined_text for kw in ("伊维菌素", "多拉菌素", "阿维菌素", "洛哌丁胺", "ivermectin")):
            red_cards.append(
                {
                    "code": "MDR1_BREED_NEUROTOXICITY",
                    "title": "MDR1 突变高危犬种大环内酯/止泻药神经毒性红牌",
                    "message": "牧羊犬系高频携带 MDR1 基因缺陷，超常规驱虫剂量伊维菌素或洛哌丁胺可穿透血脑屏障引发昏迷致死！",
                }
            )

    # 2. 批准文号与人药兽用强监管红牌核查
    if is_human_drug:
        if not in_moa_urgent_list or not vet_signed_consent:
            red_cards.append(
                {
                    "code": "HUMAN_DRUG_COMPLIANCE_RED_CARD",
                    "title": "人药兽用合规强制红牌阻断",
                    "message": (
                        "超范围使用人用药必须核查农业农村部急需目录并由执业兽医签字知情同意！"
                        f"（当前状态：急需目录核验={'已通过' if in_moa_urgent_list else '未在目录/未核验'}，"
                        f"执业兽医与宠主签字知情同意={'已签署' if vet_signed_consent else '缺失'}）"
                    ),
                }
            )
        else:
            warnings.append(
                {
                    "code": "HUMAN_DRUG_RECORD_KEEPING",
                    "title": "临床急需人用药专账留存提醒",
                    "message": "已核验农业农村部急需人用药目录并签署知情同意书；请确保单独建账登记购进与使用记录，严禁拆零转售或用于食用动物。",
                }
            )
    elif not approval_check["is_valid_vet_no"]:
        red_cards.append(
            {
                "code": "INVALID_VET_APPROVAL_NO",
                "title": "兽药批准文号异常或疑似假劣兽药/无证制剂",
                "message": f"批准文号『{approval_no or '空'}』校验未通过：{approval_check['detail']}。严禁使用无合法批文制剂，防范职业打假与行政重罚！",
            }
        )

    # 3. 给药剂量与 BSA 换算核查
    dose_mg_per_kg: Optional[float] = (
        float(rx["dose_mg_per_kg"]) if rx.get("dose_mg_per_kg") is not None else None
    )
    max_safe_mg_per_kg: Optional[float] = (
        float(rx["max_safe_mg_per_kg"]) if rx.get("max_safe_mg_per_kg") is not None else None
    )
    dose_mg_per_m2: Optional[float] = (
        float(rx["dose_mg_per_m2"]) if rx.get("dose_mg_per_m2") is not None else None
    )

    calc_mg_by_weight = round(weight_kg * dose_mg_per_kg, 3) if dose_mg_per_kg is not None else None
    calc_mg_by_bsa = round(bsa_m2 * dose_mg_per_m2, 3) if dose_mg_per_m2 is not None else None

    if (
        dose_mg_per_kg is not None
        and max_safe_mg_per_kg is not None
        and max_safe_mg_per_kg > 0
        and dose_mg_per_kg > max_safe_mg_per_kg
    ):
        red_cards.append(
            {
                "code": "OVERDOSE_RED_CARD",
                "title": "单次给药剂量超安全上限红牌",
                "message": f"处方剂量 {dose_mg_per_kg} mg/kg 超过物种安全上限 {max_safe_mg_per_kg} mg/kg！",
            }
        )

    if red_cards:
        status = "RED"
        verdict = "🔴 红牌拦截（严禁发药注射！须由执业兽医重开合规处方）"
    elif warnings:
        status = "YELLOW"
        verdict = "🟡 黄灯专账放行（符合急需人用药豁免前提，须双签留档备查）"
    else:
        status = "GREEN"
        verdict = "🟢 绿灯合规通过（批文有效、剂量与物种毒理核查正常）"

    return {
        "case_id": rx.get("case_id", "RX-UNSPECIFIED"),
        "pet_name": rx.get("pet_name", "未命名患宠"),
        "species": sp,
        "weight_kg": round(weight_kg, 3),
        "bsa_m2": round(bsa_m2, 4),
        "drug_name": drug_name,
        "approval_no": approval_no,
        "approval_validation": approval_check,
        "dosing_calc": {
            "dose_mg_per_kg": dose_mg_per_kg,
            "calculated_total_mg_by_weight": calc_mg_by_weight,
            "dose_mg_per_m2": dose_mg_per_m2,
            "calculated_total_mg_by_bsa": calc_mg_by_bsa,
        },
        "status": status,
        "verdict": verdict,
        "red_cards": red_cards,
        "warnings": warnings,
    }


def evaluate_batch(prescriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = [check_prescription(rx) for rx in prescriptions]
    red_count = sum(1 for r in results if r["status"] == "RED")
    yellow_count = sum(1 for r in results if r["status"] == "YELLOW")
    green_count = sum(1 for r in results if r["status"] == "GREEN")
    return {
        "summary": {
            "total_prescriptions": len(results),
            "red_blocked": red_count,
            "yellow_conditional": yellow_count,
            "green_passed": green_count,
        },
        "results": results,
        "compliance_notice": "超范围使用人用药必须核查农业农村部急需目录并由执业兽医签字知情同意；所有处方须经本院注册执业兽医师最终签字生效。",
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(report: Dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "=" * 80,
        "🐾 大衍千机 · 宠医专科给药安全(BSA)与人药兽用合规红线审查单",
        "=" * 80,
        f"• 审查处方总数 : {s['total_prescriptions']} 张  |  🔴 红牌拦截: {s['red_blocked']}  |  🟡 黄灯专账: {s['yellow_conditional']}  |  🟢 绿灯合规: {s['green_passed']}",
        "• BSA 梅氏公式 : BSA(m²) = K × W_g^(2/3) / 10000  （犬 K=10.1，猫 K=10.0）",
        "-" * 80,
    ]
    for r in report["results"]:
        sp_cn = "犬" if r["species"] == "dog" else "猫"
        dc = r["dosing_calc"]
        dose_parts = []
        if dc["calculated_total_mg_by_weight"] is not None:
            dose_parts.append(f"按体重单次应给: {dc['calculated_total_mg_by_weight']} mg ({dc['dose_mg_per_kg']} mg/kg)")
        if dc["calculated_total_mg_by_bsa"] is not None:
            dose_parts.append(f"按BSA单次应给: {dc['calculated_total_mg_by_bsa']} mg ({dc['dose_mg_per_m2']} mg/m²)")
        dose_str = " | ".join(dose_parts) if dose_parts else "未指定毫克剂量"

        lines.append(f"[{r['case_id']}] {r['pet_name']} ({sp_cn}, {r['weight_kg']} kg -> BSA={r['bsa_m2']:.4f} m²)")
        lines.append(f"  ├─ 拟开药品 : {r['drug_name']}  [批文: {r['approval_no'] or '缺失'}]")
        lines.append(f"  ├─ 精确剂量 : {dose_str}")
        lines.append(f"  └─ 审查结论 : {r['verdict']}")
        for rc in r["red_cards"]:
            lines.append(f"       ❌ [{rc['code']}] {rc['title']}: {rc['message']}")
        for wn in r["warnings"]:
            lines.append(f"       ⚠️  [{wn['code']}] {wn['title']}: {wn['message']}")
        lines.append("-" * 80)

    lines.append(f"⚖️  法规底线 : {report['compliance_notice']}")
    lines.append(FOOTER_SIGN)
    lines.append("=" * 80)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · 宠医专科给药安全与人药兽用合规核查器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行内置犬猫临床处方红绿牌对照演示")
    parser.add_argument("--input", type=str, help="读取处方 JSON 文件（支持单张对象或数组）")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    if args.input:
        path = pathlib.Path(args.input)
        if not path.is_file():
            print(f"处方文件不存在: {path}", file=sys.stderr)
            sys.exit(1)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        prescriptions = loaded if isinstance(loaded, list) else loaded.get("prescriptions", [loaded])
    else:
        prescriptions = DEMO_PRESCRIPTIONS

    report = evaluate_batch(prescriptions)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(report))


if __name__ == "__main__":
    main()
