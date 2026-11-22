#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dayan_html_compiler.py — 大衍商务风 (#1B365D) 单文件高管汇报 HTML 编译器 (Zero-Dependency CLI)
将任意 Markdown 报告一键编译为深蓝印刷感、零外部依赖、微信/飞书点开即看的单文件 HTML。
出品：成都大衍千机科技有限公司 (https://dayanqianji.com/ | 微信/电话：18628016927)

用法:
  python3 scripts/dayan_html_compiler.py <input.md> [output.html]
"""

import datetime
import html
import pathlib
import re
import sys


def build_dayan_7x7_svg() -> str:
    dots = []
    for r in range(7):
        for c in range(7):
            cx = 5 + c * 3.5
            cy = 9 + r * 3.5
            fill = "#AD7B27" if (r == 3 and c == 3) else "#FFFFFF"
            dots.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.05" fill="{fill}"/>')
    grid = "".join(dots)
    return (
        '<svg width="34" height="34" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="1" y="5" width="29" height="29" rx="5" fill="#1B365D"/>'
        f"{grid}"
        '<circle cx="34" cy="4.5" r="2.6" fill="#D7263D"/>'
        "</svg>"
    )


def inline_fmt(text: str) -> str:
    s = html.escape(text)
    s = re.sub(r"`([^`]+)`", r'<code class="mono code-pill">\1</code>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        s,
    )
    return s


def compile_md_to_sections(md_text: str):
    lines = md_text.splitlines()
    title = "高管决策简报"
    subtitle_lines = []
    sections = []
    curr_sec = {"title": "核心摘要", "blocks": []}

    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if stripped.startswith("# ") and title == "高管决策简报":
            title = stripped[2:].strip()
            i += 1
            continue

        if stripped.startswith("## "):
            if curr_sec["blocks"]:
                sections.append(curr_sec)
            curr_sec = {"title": stripped[3:].strip(), "blocks": []}
            i += 1
            continue

        if stripped.startswith("### "):
            curr_sec["blocks"].append(f"<h3>{inline_fmt(stripped[4:].strip())}</h3>")
            i += 1
            continue

        if "|" in stripped and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:-]+\|", lines[i + 1]):
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th_html = "".join(f"<th>{inline_fmt(h)}</th>" for h in headers)
            tr_html = []
            for r in rows:
                tds = "".join(f"<td>{inline_fmt(c)}</td>" for c in r)
                tr_html.append(f"<tr>{tds}</tr>")
            curr_sec["blocks"].append(
                f"<table><thead><tr>{th_html}</tr></thead><tbody>{''.join(tr_html)}</tbody></table>"
            )
            continue

        if stripped.startswith(">"):
            q_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            curr_sec["blocks"].append(
                f'<div class="callout">{"<br>".join(inline_fmt(x) for x in q_lines)}</div>'
            )
            continue

        if re.match(r"^[-*+]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*+]\s+", lines[i].strip()):
                item_txt = re.sub(r"^[-*+]\s+", "", lines[i].strip())
                items.append(f"<li>{inline_fmt(item_txt)}</li>")
                i += 1
            curr_sec["blocks"].append(f"<ul>{''.join(items)}</ul>")
            continue

        if stripped == "---":
            i += 1
            continue

        if stripped:
            if not sections and not curr_sec["blocks"] and len(subtitle_lines) < 2:
                subtitle_lines.append(stripped)
            else:
                curr_sec["blocks"].append(f"<p>{inline_fmt(stripped)}</p>")
        i += 1

    if curr_sec["blocks"]:
        sections.append(curr_sec)

    subtitle = (
        " ".join(subtitle_lines)
        if subtitle_lines
        else "基于大衍商务风呈现规范 v1.0 编译 · 结论先行 · 事实可核查"
    )
    return title, subtitle, sections


def build_html(title: str, subtitle: str, sections: list) -> str:
    sec_html = "\n".join(
        f'<section class="card"><h2>{inline_fmt(s["title"])}</h2>\n'
        + "\n".join(s["blocks"])
        + "\n</section>"
        for s in sections
    )
    today = datetime.date.today().isoformat()
    logo_svg = build_dayan_7x7_svg()
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}｜大衍商务呈现</title>
<style>
  :root {{
    --navy:#1B365D; --deep:#0C2236; --mid:#265592; --gold:#AD7B27; --red:#D7263D;
    --ink:#111827; --muted:#5F6B7C; --line:#E2E8F0; --bg:#F7F5F0; --tint:#F2F6FB; --card:#FFFFFF;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'PingFang SC','Microsoft YaHei','Noto Sans SC',-apple-system,sans-serif; background:var(--bg); color:var(--ink); line-height:1.72; padding:32px 18px 60px; }}
  .mono {{ font-family:'JetBrains Mono','SF Mono',ui-monospace,monospace; font-variant-numeric:tabular-nums; }}
  .code-pill {{ background:var(--tint); color:var(--navy); padding:2px 6px; border-radius:4px; font-size:.9em; }}
  .wrap {{ max-width:1060px; margin:0 auto; }}
  .hero {{ background:linear-gradient(135deg,var(--deep),var(--navy)); color:#fff; border-radius:14px; padding:36px 38px 30px; margin-bottom:24px; box-shadow:0 4px 18px rgba(12,34,54,.12); }}
  .eyebrow {{ color:#F7EFDD; font-size:12px; letter-spacing:.08em; font-weight:700; margin-bottom:10px; }}
  .hero h1 {{ font-size:28px; line-height:1.35; margin-bottom:10px; }}
  .hero p {{ color:rgba(255,255,255,.86); font-size:15px; max-width:860px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:26px 30px; margin-bottom:20px; }}
  .card h2 {{ font-size:19px; color:var(--navy); border-left:4px solid var(--gold); padding-left:12px; margin-bottom:14px; }}
  .card h3 {{ font-size:16px; color:var(--navy); margin:16px 0 8px; }}
  .card p {{ margin-bottom:10px; font-size:15px; }}
  .card ul {{ padding-left:20px; margin-bottom:12px; }}
  .card li {{ margin-bottom:6px; font-size:14.5px; }}
  table {{ width:100%; border-collapse:collapse; margin:14px 0; font-size:14px; }}
  th {{ background:var(--navy); color:#fff; text-align:left; padding:11px 14px; font-weight:600; }}
  td {{ padding:11px 14px; border-bottom:1px solid var(--line); vertical-align:top; }}
  tr:nth-child(even) td {{ background:var(--tint); }}
  td:first-child {{ word-break:keep-all; min-width:130px; font-weight:600; color:var(--navy); }}
  .callout {{ background:#F7EFDD; border-left:4px solid var(--gold); padding:14px 18px; border-radius:6px; font-size:14px; margin:12px 0; }}
  a {{ color:var(--mid); text-decoration:none; font-weight:600; }}
  .dayan-colophon {{ margin-top:34px; padding:20px 24px; background:var(--card); border:1px solid var(--line); border-radius:12px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px; font-size:13px; color:var(--muted); }}
  .dayan-brand {{ display:flex; align-items:center; gap:12px; }}
  .dayan-brand strong {{ color:var(--navy); font-size:14px; }}
  @media print {{ body {{ background:#fff; padding:0; }} .hero {{ box-shadow:none; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="eyebrow mono">DAYAN EXECUTIVE BRIEF · {today}</div>
    <h1>{html.escape(title)}</h1>
    <p>{inline_fmt(subtitle)}</p>
  </header>
  {sec_html}
  <footer class="dayan-colophon">
    <div class="dayan-brand">
      {logo_svg}
      <div>
        <strong>大衍商务呈现引擎 v1.0 编译</strong> · 成都大衍千机科技有限公司（天府长岛首家入驻 OPC）<br>
        <span>企业 AI 全案落地 · 一把手首诊 · 分岗位实操内训 · 兜错知识库与系统定制</span>
      </div>
    </div>
    <div class="mono">
      官网：<a href="https://dayanqianji.com/" target="_blank" rel="noopener">dayanqianji.com</a> ｜ 90秒自测：<a href="https://my.feishu.cn/share/base/shrcnhBYBWWVOeFnmlggAhnGXE0" target="_blank" rel="noopener">飞书初筛</a> ｜ 微信/电话：18628016927
    </div>
  </footer>
</div>
</body>
</html>
"""


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("用法: python3 scripts/dayan_html_compiler.py <input.md> [output.html]")
        sys.exit(0 if len(sys.argv) >= 2 else 1)

    in_path = pathlib.Path(sys.argv[1])
    if not in_path.is_file():
        print(f"文件不存在: {in_path}")
        sys.exit(1)
    out_path = pathlib.Path(sys.argv[2]) if len(sys.argv) >= 3 else in_path.with_suffix(".html")
    md_text = in_path.read_text(encoding="utf-8", errors="replace")
    title, subtitle, sections = compile_md_to_sections(md_text)
    out_path.write_text(build_html(title, subtitle, sections), encoding="utf-8")
    print(f"✅ 已编译生成大衍商务风单文件 HTML: {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
