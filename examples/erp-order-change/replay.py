#!/usr/bin/env python3
"""Replay a fictional order-change acceptance test without accessing any system."""

import csv
import json
from pathlib import Path
import sys


DECISIONS = {
    "pending_approval": "原订单保留，等待主管审批",
    "simulated_accepted": "演示中批准生成下一版本，记录计划和仓库待办",
    "already_recorded": "核对请求号和结果，沿用既有记录",
    "version_conflict": "冻结旧草稿，重新读取订单并复核",
    "needs_reconciliation": "标记结果待核，先查 ERP 再决定如何处理",
    "approval_mismatch": "退回补齐与本次变更绑定的审批记录",
    "permission_unconfirmed": "等待有权限的操作人确认",
    "capacity_unconfirmed": "计划员确认缺口及承诺交期",
}


def evaluate(order, request, evidence):
    """Assess one snapshot. The write count represents simulated new writes."""
    match evidence["readback"]:
        case "matched":
            return "already_recorded", 0
        case "unknown" | "mismatch":
            return "needs_reconciliation", 0
        case "none":
            pass
        case _:
            raise ValueError("unknown readback state")

    if evidence["observed_version"] != request["expected_version"]:
        return "version_conflict", 0
    if evidence["approval"] != "approved":
        return "pending_approval", 0
    if not evidence["approval_matches"]:
        return "approval_mismatch", 0
    if not evidence["has_write_role"]:
        return "permission_unconfirmed", 0

    quantity_increase = max(request["quantity"] - order["quantity"], 0)
    available_extra = request["extra_stock"] + evidence["planned_extra"]
    if available_extra < quantity_increase or not evidence["delivery_confirmed"]:
        return "capacity_unconfirmed", 0
    return "simulated_accepted", 1


def main():
    fixture = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
    order, request = fixture["order"], fixture["request"]
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("用例", "场景", "演示订单", "预期", "结果", "新增模拟写入", "处理", "通过"))
    all_passed = True
    for case in fixture["cases"]:
        evidence = fixture["defaults"] | case["input"]
        decision, new_writes = evaluate(order, request, evidence)
        passed = (decision, new_writes) == (case["expected"], case["new_writes"])
        all_passed &= passed
        writer.writerow((case["id"], case["title"], order["id"], case["expected"], decision,
                         new_writes, DECISIONS[decision], "通过" if passed else "失败"))
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
