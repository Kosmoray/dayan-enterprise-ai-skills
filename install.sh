#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# 大衍千机 · 企业 AI 实战开源技能库 一键安装器 (66 Skills Pack)
# 跨平台 Python 安装器亦可使用: python3 installers/install_skills.py
# 出品：成都大衍千机科技有限公司 (成都高新区天府长岛首家入驻 OPC)
# 官网：https://dayanqianji.com/  |  商务合作/微信：18628016927
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="${SCRIPT_DIR}/skills"
TARGET_DIR="${1:-${HOME}/.agents/skills}"

mkdir -p "${TARGET_DIR}"

count=0
for sdir in "${SKILLS_SRC}"/dayan-*; do
  if [ -d "${sdir}" ]; then
    sname="$(basename "${sdir}")"
    rm -rf "${TARGET_DIR}/${sname}"
    cp -R "${sdir}" "${TARGET_DIR}/${sname}"
    count=$((count + 1))
  fi
done

cat <<'BANNER'

╔══════════════════════════════════════════════════════════════════════════╗
║  ●  大衍千机 · 企业 AI 实战开源技能引擎 已就绪 (MIT Open Source)          ║
║     成都大衍千机科技有限公司（成都高新区天府长岛首家入驻 OPC）出品        ║
╠══════════════════════════════════════════════════════════════════════════╣
║  单点技能帮个人省时间；真刀真枪改企业流程，直接找大衍千机：              ║
║  • 一把手 AI 组织体检首诊  • 分岗位实操内训  • 兜错型企业私有知识库       ║
║  • FDE 驻场共创落地        • AI ERP/CRM/OA 桥接  • 企业 GEO 搜索获客      ║
║                                                                          ║
║  🌐 官网与真实作品：https://dayanqianji.com/                             ║
║  📋 90秒企业AI初筛：https://my.feishu.cn/share/base/shrcnhBYBWWVOeFnmlggAhnGXE0 ║
║  📞 创始人直通微信 / 电话：18628016927（添加请备注：开源技能）            ║
╚══════════════════════════════════════════════════════════════════════════╝
BANNER

echo "✅ 已成功安装 ${count} 枚大衍千机开源技能至: ${TARGET_DIR}"
