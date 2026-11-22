#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gjb_kit_shortage_audit.py — 航空军工配套多工序外协齐套与不出域算力精算器 (Zero-Dependency CLI)
输入零件工序链（机加→热处理→阳极氧化/无损检测）、外协合格供方特种资质到期日、库存与需求数，
自动拦截超期外协供方红牌、定位断料工序，并附带涉密断网环境下本地部署 32B/70B 大模型的
FP16/INT4 显存与并发 KV Cache 硬件测算。

出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信: 18628016927)

用法:
  python3 scripts/industry/gjb_kit_shortage_audit.py --demo
  python3 scripts/industry/gjb_kit_shortage_audit.py --demo --json
  python3 scripts/industry/gjb_kit_shortage_audit.py --input gjb_kit.json [--json]
"""

import argparse
import datetime
import json
import math
import pathlib
import sys
from typing import Any, Dict, List

FOOTER_SIGN = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"

MODEL_ARCH_PRESETS: Dict[str, Dict[str, Any]] = {
    "32B": {
        "model_label": "32B 企业主力推理模型 (如 Qwen2.5-32B / DeepSeek-R1-32B)",
        "params_b": 32.5,
        "num_layers": 64,
        "num_kv_heads": 8,
        "head_dim": 128,
    },
    "70B": {
        "model_label": "70B 复杂工艺/审图旗舰模型 (如 Qwen2.5-72B / Llama-3.3-70B)",
        "params_b": 70.6,
        "num_layers": 80,
        "num_kv_heads": 8,
        "head_dim": 128,
    },
}

DEMO_GJB_WORKLOAD: Dict[str, Any] = {
    "batch_name": "某型无人机主承力框科研试制批（12 架份齐套排产与涉密算力测算）",
    "audit_date": "2026-11-22",
    "airgap_llm_config": {
        "concurrency": 8,
        "context_len": 8192,
    },
    "parts": [
        {
            "part_no": "AVIC-7050-F01",
            "part_name": "7050铝合金五轴主承力框",
            "required_qty": 12,
            "scrap_buffer_rate": 0.08,
            "steps": [
                {
                    "seq": 10,
                    "process": "五轴联动粗精机加",
                    "is_special_process": False,
                    "vendor": "本厂数控二车间",
                    "cert_no": "GJB9001C-INTERNAL",
                    "cert_expiry": "2028-06-30",
                    "available_qty": 14,
                    "lead_time_days": 5,
                },
                {
                    "seq": 20,
                    "process": "铝合金固溶时效真空热处理",
                    "is_special_process": True,
                    "vendor": "川西航宇特种热处理厂",
                    "cert_no": "NADCAP-HT-202309",
                    "cert_expiry": "2026-10-15",
                    "available_qty": 8,
                    "lead_time_days": 4,
                },
                {
                    "seq": 30,
                    "process": "荧光渗透与X射线无损检测(NDT)",
                    "is_special_process": True,
                    "vendor": "蓉城航材无损检测中心",
                    "cert_no": "GJB-NDT-202512",
                    "cert_expiry": "2026-12-08",
                    "available_qty": 6,
                    "lead_time_days": 3,
                },
                {
                    "seq": 40,
                    "process": "硫酸阳极氧化与封闭表面处理",
                    "is_special_process": True,
                    "vendor": "新都航空表处协作厂",
                    "cert_no": "NADCAP-CP-202588",
                    "cert_expiry": "2027-09-30",
                    "available_qty": 4,
                    "lead_time_days": 3,
                },
            ],
        },
        {
            "part_no": "AVIC-TC4-B09",
            "part_name": "TC4钛合金起落架耳片接头",
            "required_qty": 24,
            "scrap_buffer_rate": 0.05,
            "steps": [
                {
                    "seq": 10,
                    "process": "钛合金深孔镗铣机加",
                    "is_special_process": False,
                    "vendor": "本厂精密一车间",
                    "cert_no": "GJB9001C-INTERNAL",
                    "cert_expiry": "2028-06-30",
                    "available_qty": 26,
                    "lead_time_days": 6,
                },
                {
                    "seq": 20,
                    "process": "真空退火除氢热处理",
                    "is_special_process": True,
                    "vendor": "德阳精工真空热表中心",
                    "cert_no": "GJB-HT-202504",
                    "cert_expiry": "2027-11-20",
                    "available_qty": 26,
                    "lead_time_days": 3,
                },
            ],
        },
    ],
}


def parse_iso_date(date_str: str) -> datetime.date:
    return datetime.date.fromisoformat(str(date_str).strip())


def calc_airgap_llm_vram(
    model_key: str,
    concurrency: int = 8,
    context_len: int = 8192,
) -> Dict[str, Any]:
    """
    涉密物理断网（Air-Gap）环境下本地部署 32B / 70B 大模型的显存与并发 KV Cache 精算：
    - FP16 权重显存 = params_b * 2.0 GB
    - INT4(AWQ/GPTQ) 权重显存 = params_b * 0.55 GB (含 group quantization scale 开销)
    - FP16 KV Cache 显存 = concurrency * context_len * 2(K+V) * layers * kv_heads * head_dim * 2(bytes) / 1024^3
    - 运行时与激活缓冲 = 2.5 + 0.08 * params_b GB
    """
    if model_key not in MODEL_ARCH_PRESETS:
        raise ValueError(f"不支持的模型档位: {model_key}，可选 {list(MODEL_ARCH_PRESETS)}")
    if concurrency <= 0 or context_len <= 0:
        raise ValueError("并发数与上下文长度必须大于 0")

    spec = MODEL_ARCH_PRESETS[model_key]
    params_b = float(spec["params_b"])
    layers = int(spec["num_layers"])
    kv_heads = int(spec["num_kv_heads"])
    head_dim = int(spec["head_dim"])

    weight_fp16_gb = params_b * 2.0
    weight_int4_gb = params_b * 0.55

    kv_bytes_per_token = 2 * layers * kv_heads * head_dim * 2
    kv_cache_gb = (concurrency * context_len * kv_bytes_per_token) / (1024.0 ** 3)
    runtime_overhead_gb = 2.5 + 0.08 * params_b

    total_fp16_gb = weight_fp16_gb + kv_cache_gb + runtime_overhead_gb
    total_int4_gb = weight_int4_gb + kv_cache_gb + runtime_overhead_gb

    def recommend_gpu(vram_needed: float) -> str:
        if vram_needed <= 22.0:
            return "单卡 1×24GB (RTX 4090D / L20 裁剪档)"
        if vram_needed <= 44.0:
            return "双卡 2×24GB 或 单卡 1×48GB (NVIDIA L20 / A40)"
        if vram_needed <= 90.0:
            return "双卡 2×48GB (NVIDIA L20×2) 或 国产昇腾 910B 2×64GB"
        if vram_needed <= 180.0:
            return "四卡 4×48GB (NVIDIA L20×4) 或 国产昇腾 910B 4×64GB 一体机"
        return "八卡 8×48GB/64GB 高密推理服务器节点"

    return {
        "model_tier": model_key,
        "model_label": spec["model_label"],
        "concurrency": concurrency,
        "context_len": context_len,
        "weight_fp16_gb": round(weight_fp16_gb, 2),
        "weight_int4_gb": round(weight_int4_gb, 2),
        "kv_cache_fp16_gb": round(kv_cache_gb, 2),
        "runtime_overhead_gb": round(runtime_overhead_gb, 2),
        "total_vram_fp16_gb": round(total_fp16_gb, 2),
        "total_vram_int4_gb": round(total_int4_gb, 2),
        "recommended_hw_int4": recommend_gpu(total_int4_gb),
        "recommended_hw_fp16": recommend_gpu(total_fp16_gb),
    }


def audit_gjb_kit_and_airgap(payload: Dict[str, Any]) -> Dict[str, Any]:
    """执行多工序外协齐套、特种工艺资质效期拦截与涉密本地大模型硬件精算。"""
    batch_name = str(payload.get("batch_name", "航空军工配套多工序齐套审查"))
    audit_date = parse_iso_date(payload.get("audit_date", datetime.date.today().isoformat()))

    red_cards: List[Dict[str, Any]] = []
    yellow_alerts: List[Dict[str, Any]] = []
    part_reports: List[Dict[str, Any]] = []
    max_recovery_days = 0

    for part in payload.get("parts", []):
        pno = str(part["part_no"])
        pname = str(part["part_name"])
        req_qty = int(part["required_qty"])
        scrap_rate = float(part.get("scrap_buffer_rate", 0.0))
        gross_target_qty = math.ceil(req_qty * (1.0 + scrap_rate))

        step_rows = []
        part_recovery_days = 0
        first_shortage_step = None

        for st in part.get("steps", []):
            seq = int(st["seq"])
            proc = str(st["process"])
            is_special = bool(st.get("is_special_process", False))
            vendor = str(st["vendor"])
            cert_no = str(st.get("cert_no", ""))
            expiry_date = parse_iso_date(st["cert_expiry"])
            avail_qty = int(st["available_qty"])
            lead_days = int(st.get("lead_time_days", 1))

            days_to_expiry = (expiry_date - audit_date).days
            shortage_qty = max(0, gross_target_qty - avail_qty)

            cert_status = "VALID"
            if days_to_expiry < 0:
                cert_status = "EXPIRED_RED"
                red_cards.append(
                    {
                        "code": "EXPIRED_SPECIAL_VENDOR_CERT",
                        "part_no": pno,
                        "step_seq": seq,
                        "process": proc,
                        "vendor": vendor,
                        "message": (
                            f"外协供方『{vendor}』资质证书 ({cert_no}) 已于 {expiry_date.isoformat()} 超期 "
                            f"{abs(days_to_expiry)} 天！违反 GJB 9001C 合格供方与特种工艺强条，严禁外发投料！"
                        ),
                    }
                )
            elif days_to_expiry <= 30:
                cert_status = "EXPIRING_SOON_YELLOW"
                yellow_alerts.append(
                    {
                        "code": "VENDOR_CERT_EXPIRING_30D",
                        "part_no": pno,
                        "step_seq": seq,
                        "vendor": vendor,
                        "message": f"外协供方『{vendor}』证书 ({cert_no}) 仅剩 {days_to_expiry} 天到期，须在流转入厂前核验续期批件。",
                    }
                )

            if shortage_qty > 0:
                part_recovery_days += lead_days
                if first_shortage_step is None:
                    first_shortage_step = f"OP{seq}-{proc} (缺 {shortage_qty} 件)"

            step_rows.append(
                {
                    "seq": seq,
                    "process": proc,
                    "is_special_process": is_special,
                    "vendor": vendor,
                    "cert_no": cert_no,
                    "cert_expiry": expiry_date.isoformat(),
                    "days_to_expiry": days_to_expiry,
                    "cert_status": cert_status,
                    "gross_target_qty": gross_target_qty,
                    "available_qty": avail_qty,
                    "shortage_qty": shortage_qty,
                    "lead_time_days": lead_days,
                }
            )

        max_recovery_days = max(max_recovery_days, part_recovery_days)
        if first_shortage_step:
            yellow_alerts.append(
                {
                    "code": "PROCESS_KIT_SHORTAGE",
                    "part_no": pno,
                    "message": f"图号 {pno}（{pname}）首道断料卡口：{first_shortage_step}，补齐串行周期约 {part_recovery_days} 天。",
                }
            )

        part_reports.append(
            {
                "part_no": pno,
                "part_name": pname,
                "net_required_qty": req_qty,
                "gross_target_qty": gross_target_qty,
                "first_shortage_bottleneck": first_shortage_step,
                "estimated_recovery_days": part_recovery_days,
                "is_kitted": first_shortage_step is None,
                "steps": step_rows,
            }
        )

    llm_cfg = payload.get("airgap_llm_config", {})
    concurrency = int(llm_cfg.get("concurrency", 8))
    context_len = int(llm_cfg.get("context_len", 8192))
    sizing_32b = calc_airgap_llm_vram("32B", concurrency=concurrency, context_len=context_len)
    sizing_70b = calc_airgap_llm_vram("70B", concurrency=concurrency, context_len=context_len)

    if red_cards:
        overall_status = "RED"
        verdict = "🔴 红牌拦截（检出超期特种工艺外协供方，未换证/切换合格供方前严禁放行外发！）"
    elif any(not p["is_kitted"] for p in part_reports) or yellow_alerts:
        overall_status = "YELLOW"
        verdict = f"🟡 黄灯齐套预警（存在工序缺口或临期证书，预计关键路径追赶周期 {max_recovery_days} 天）"
    else:
        overall_status = "GREEN"
        verdict = "🟢 绿灯齐套放行（全工序良品足额且外协特种资质均在有效期内）"

    return {
        "batch_name": batch_name,
        "audit_date": audit_date.isoformat(),
        "overall_status": overall_status,
        "verdict": verdict,
        "critical_path_recovery_days": max_recovery_days,
        "red_cards": red_cards,
        "yellow_alerts": yellow_alerts,
        "parts": part_reports,
        "airgap_llm_sizing": {
            "32B": sizing_32b,
            "70B": sizing_70b,
        },
        "powered_by": "成都大衍千机科技有限公司 (https://dayanqianji.com/ | 18628016927)",
    }


def render_cli_report(report: Dict[str, Any]) -> str:
    lines = [
        "=" * 84,
        "🛡️  大衍千机 · 航空军工配套多工序外协齐套 & 涉密不出域算力精算表",
        f"   批次任务 : {report['batch_name']}  |  审查基准日: {report['audit_date']}",
        "=" * 84,
        f"• 质量与生管结论 : {report['verdict']}",
        f"• 特种资质红牌数 : {len(report['red_cards'])} 项  |  齐套/临期黄灯数: {len(report['yellow_alerts'])} 项  |  最长追赶期: {report['critical_path_recovery_days']} 天",
        "-" * 84,
        "【一、多工序外协齐套与合格供方资质扫描】",
    ]
    for p in report["parts"]:
        kit_badge = "✅ 已齐套" if p["is_kitted"] else f"⚠️ 断料卡口: {p['first_shortage_bottleneck']}"
        lines.append(
            f"  ▪ 图号 {p['part_no']} 《{p['part_name']}》 | 净需 {p['net_required_qty']} 件 (含备品目标 {p['gross_target_qty']} 件) -> {kit_badge}"
        )
        for st in p["steps"]:
            sp_tag = "[特种]" if st["is_special_process"] else "[常规]"
            if st["cert_status"] == "EXPIRED_RED":
                c_tag = f"❌超期({st['cert_expiry']})"
            elif st["cert_status"] == "EXPIRING_SOON_YELLOW":
                c_tag = f"⚠️临期剩{st['days_to_expiry']}天"
            else:
                c_tag = f"有效至{st['cert_expiry']}"
            short_str = f"缺 {st['shortage_qty']} 件" if st["shortage_qty"] > 0 else "足额"
            lines.append(
                f"      OP{st['seq']:02d} {sp_tag} {st['process']} | 供方: {st['vendor']} ({c_tag}) | 在制/库存:{st['available_qty']} -> {short_str}"
            )

    if report["red_cards"]:
        lines.append("-" * 84)
        lines.append("【二、GJB 9001C 质量体系强制拦截红牌】")
        for rc in report["red_cards"]:
            lines.append(f"  ❌ [{rc['part_no']} OP{rc['step_seq']}] {rc['message']}")

    s32 = report["airgap_llm_sizing"]["32B"]
    s70 = report["airgap_llm_sizing"]["70B"]
    lines.extend(
        [
            "-" * 84,
            f"【三、涉密物理断网（不出厂区）本地大模型显存与一体机选型测算】（并发={s32['concurrency']}路, 上下文={s32['context_len']}）",
            f"  1. {s32['model_label']}",
            f"     ├─ FP16 全精度总显存 : {s32['total_vram_fp16_gb']:.1f} GB (权重 {s32['weight_fp16_gb']:.1f}G + KV缓存 {s32['kv_cache_fp16_gb']:.1f}G + 运行余量 {s32['runtime_overhead_gb']:.1f}G) -> {s32['recommended_hw_fp16']}",
            f"     └─ INT4 量化总显存   : {s32['total_vram_int4_gb']:.1f} GB (权重 {s32['weight_int4_gb']:.1f}G + KV缓存 {s32['kv_cache_fp16_gb']:.1f}G + 运行余量 {s32['runtime_overhead_gb']:.1f}G) -> {s32['recommended_hw_int4']}",
            f"  2. {s70['model_label']}",
            f"     ├─ FP16 全精度总显存 : {s70['total_vram_fp16_gb']:.1f} GB (权重 {s70['weight_fp16_gb']:.1f}G + KV缓存 {s70['kv_cache_fp16_gb']:.1f}G + 运行余量 {s70['runtime_overhead_gb']:.1f}G) -> {s70['recommended_hw_fp16']}",
            f"     └─ INT4 量化总显存   : {s70['total_vram_int4_gb']:.1f} GB (权重 {s70['weight_int4_gb']:.1f}G + KV缓存 {s70['kv_cache_fp16_gb']:.1f}G + 运行余量 {s70['runtime_overhead_gb']:.1f}G) -> {s70['recommended_hw_int4']}",
            "-" * 84,
            "⚖️  合规底线 : 特种工艺外协放行与涉密网络架构建设须经质量总师及保密办主任书面签字确认；严禁涉密图号上传公网。",
            FOOTER_SIGN,
            "=" * 84,
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="大衍千机 · 航空军工配套多工序外协齐套与不出域算力精算器 (https://dayanqianji.com/)"
    )
    parser.add_argument("--demo", action="store_true", help="运行航空结构件多工序外协齐套与断网算力演示样例")
    parser.add_argument("--input", type=str, help="读取外部工序齐套与算力参数 JSON 文件")
    parser.add_argument("--concurrency", type=int, help="覆盖本地大模型并发请求数")
    parser.add_argument("--context-len", type=int, help="覆盖本地大模型单路最大上下文 Token 长度")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    payload = json.loads(json.dumps(DEMO_GJB_WORKLOAD))
    if args.input:
        in_path = pathlib.Path(args.input)
        if not in_path.is_file():
            print(f"输入文件不存在: {in_path}", file=sys.stderr)
            sys.exit(1)
        payload = json.loads(in_path.read_text(encoding="utf-8"))

    if args.concurrency is not None:
        payload.setdefault("airgap_llm_config", {})["concurrency"] = args.concurrency
    if args.context_len is not None:
        payload.setdefault("airgap_llm_config", {})["context_len"] = args.context_len

    report = audit_gjb_kit_and_airgap(payload)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_cli_report(report))


if __name__ == "__main__":
    main()
