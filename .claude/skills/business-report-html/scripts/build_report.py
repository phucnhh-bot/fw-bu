#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jinja2", "markdown-it-py", "pyyaml"]
# ///
"""Sinh 1 file HTML tự chứa (Chart.js nhúng inline) theo design system chung.

Hai nguồn đầu vào:
  1. Template Markdown của từng loại báo cáo (templates/reports/<id>.md) + giá trị số liệu JSON:
       uv run build_report.py --md templates/reports/<id>.md --values values.json --out output/x.html
  2. JSON section (template mặc định, khi báo cáo chưa có template riêng):
       python3 build_report.py --data report.json --out output/x.html

  python3 build_report.py --check output/x.html      # chỉ kiểm tra file đã có

Chế độ --data và --check chỉ cần thư viện chuẩn; chế độ --md cần jinja2, markdown-it-py, pyyaml
(`uv run` tự cài theo khối script ở đầu file).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "assets" / "report-template.html"
VENDOR_DIR = SKILL_DIR / "assets" / "vendor"

SECTION_TYPES = {"kpis", "chart", "table", "text", "markdown"}
COMPONENT_FENCES = {"kpis", "chart", "table"}
TZ = "Asia/Ho_Chi_Minh"
CHART_TYPES = {"line", "area", "bar", "pie", "doughnut"}
FORMATS = {None, "number", "currency", "percent", "delta", "decimal", "text"}

DATA_BLOCK = re.compile(
    r'(<script type="application/json" id="report-data">)(.*?)(</script>)', re.S
)
LOCAL_SCRIPT = re.compile(r'<script src="([^"]+)"></script>')
EXTERNAL_REF = re.compile(
    r'<(?:script|link|img|iframe)\b[^>]*\b(?:src|href)="(?:https?:)?//', re.I
)


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    meta = data.get("meta")
    if not isinstance(meta, dict) or not meta.get("title"):
        errors.append("meta.title là bắt buộc")
    elif "period" in meta:
        p = meta["period"]
        if not (isinstance(p, dict) and p.get("from") and p.get("to")):
            errors.append("meta.period cần có from và to (YYYY-MM-DD)")
        elif p["from"] > p["to"]:
            errors.append("meta.period.from lớn hơn to")
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        errors.append("sections phải là danh sách không rỗng")
        return errors
    for i, s in enumerate(sections):
        where = f"sections[{i}]" + (f" ({s.get('title')})" if s.get("title") else "")
        t = s.get("type")
        if t not in SECTION_TYPES:
            errors.append(f"{where}: type '{t}' không hợp lệ, dùng {sorted(SECTION_TYPES)}")
            continue
        if t == "markdown":
            if not isinstance(s.get("html"), str):
                errors.append(f"{where}: markdown cần trường html")
            continue
        if s.get("format") not in FORMATS:
            errors.append(f"{where}: format '{s.get('format')}' không hợp lệ")
        if t == "chart":
            if s.get("chart") not in CHART_TYPES:
                errors.append(f"{where}: chart '{s.get('chart')}' không hợp lệ, dùng {sorted(CHART_TYPES)}")
            n = len(s.get("labels") or [])
            for sr in s.get("series") or []:
                if len(sr.get("data") or []) not in (0, n):
                    errors.append(f"{where}: series '{sr.get('name')}' có {len(sr['data'])} giá trị nhưng có {n} labels")
        if t == "table":
            keys = {c.get("key") for c in s.get("columns") or []}
            if not keys:
                errors.append(f"{where}: table cần columns")
            for c in s.get("columns") or []:
                if c.get("format") not in FORMATS:
                    errors.append(f"{where}: cột '{c.get('key')}' có format '{c.get('format')}' không hợp lệ")
            for j, r in enumerate(s.get("rows") or []):
                missing = keys - r.keys()
                if missing:
                    errors.append(f"{where}: rows[{j}] thiếu {sorted(missing)}")
        if t == "kpis":
            for k in s.get("items") or []:
                if "label" not in k or "value" not in k:
                    errors.append(f"{where}: mỗi KPI cần label và value")
                if k.get("format") not in FORMATS:
                    errors.append(f"{where}: KPI '{k.get('label')}' có format '{k.get('format')}' không hợp lệ")
    return errors


def inline_scripts(html: str) -> str:
    def repl(m: re.Match) -> str:
        src = m.group(1)
        path = (TEMPLATE.parent / src).resolve()
        if not path.is_file() or VENDOR_DIR not in path.parents:
            raise SystemExit(f"Không tìm thấy script cục bộ để nhúng: {src}")
        code = path.read_text(encoding="utf-8").replace("</script", "<\\/script")
        return f"<script>/* {path.name} */\n{code}\n</script>"

    return LOCAL_SCRIPT.sub(repl, html)


def check(html: str) -> list[str]:
    problems = []
    if EXTERNAL_REF.search(html):
        problems.append("Có tài nguyên tải từ bên ngoài (script/link/img src=http...) — file sẽ không chạy offline")
    if LOCAL_SCRIPT.search(html):
        problems.append("Còn <script src=...> chưa được nhúng inline")
    m = DATA_BLOCK.search(html)
    if not m:
        problems.append("Không tìm thấy khối <script id=\"report-data\">")
    else:
        try:
            problems += validate(json.loads(m.group(2)))
        except json.JSONDecodeError as e:
            problems.append(f"JSON dữ liệu không hợp lệ: {e}")
    return problems


# ---------- định dạng vi-VN (khớp với hàm fmt trong template) ----------

def _vi(v: float, digits: int, strip: bool) -> str:
    s = f"{v:,.{digits}f}"
    if strip and "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(",", "\0").replace(".", ",").replace("\0", ".")


def f_number(v, digits: int = 0, compact: bool = False) -> str:
    if v is None:
        return "—"
    if compact:
        for unit, name in ((1e9, " tỷ"), (1e6, " triệu"), (1e3, " nghìn")):
            if abs(v) >= unit:
                return _vi(v / unit, 2, True) + name
    return _vi(v, digits, True)


def f_currency(v, compact: bool = False) -> str:
    return "—" if v is None else f_number(v, 0, compact) + " ₫"


def f_percent(v, digits: int = 1) -> str:
    return "—" if v is None else _vi(v * 100, digits, False) + "%"


def f_delta(v, digits: int = 1) -> str:
    return "—" if v is None else ("+" if v > 0 else "") + f_percent(v, digits)


def f_pp(v, digits: int = 1) -> str:
    """Chênh lệch điểm phần trăm: 0.005 -> +0,5 điểm %."""
    return "—" if v is None else ("+" if v > 0 else "") + _vi(v * 100, digits, False) + " điểm %"


def f_date(v) -> str:
    y, m, d = str(v)[:10].split("-")
    return f"{d}/{m}/{y}"


# ---------- template Markdown ----------

def render_markdown_report(md_path: Path, values: dict) -> dict:
    import datetime as dt
    from zoneinfo import ZoneInfo

    import jinja2
    import yaml
    from markdown_it import MarkdownIt

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(md_path.parent)),
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
    )
    env.filters.update(number=f_number, currency=f_currency, percent=f_percent,
                       delta=f_delta, pp=f_pp, date=f_date)
    try:
        text = env.get_template(md_path.name).render(**values)
    except jinja2.UndefinedError as e:
        raise SystemExit(f"Template {md_path}: thiếu giá trị ({e.message}) — thêm vào file --values")
    except jinja2.TemplateError as e:
        raise SystemExit(f"Template {md_path}: lỗi cú pháp Jinja: {e}")

    meta: dict = {}
    fm = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if fm:
        meta = yaml.safe_load(fm.group(1)) or {}
        text = text[fm.end():]
    meta = json.loads(json.dumps(meta, default=str))  # date -> "YYYY-MM-DD"
    meta.setdefault("generated_at", dt.datetime.now(ZoneInfo(TZ)).isoformat(timespec="seconds"))

    md = MarkdownIt("commonmark", {"html": False, "typographer": False}).enable("table")
    tokens = md.parse(text)

    # tiêu đề = H1 đầu tiên nếu frontmatter không có title; H1 đó không render lại trong thân
    if tokens[:1] and tokens[0].type == "heading_open" and tokens[0].tag == "h1":
        meta.setdefault("title", tokens[1].content)
        tokens = tokens[3:]

    sections: list[dict] = []
    chunk: list = []

    def flush() -> None:
        if not chunk:
            return
        html = md.renderer.render(chunk, md.options, {})
        html = re.sub(r"<table>", '<div class="card"><div class="table-scroll"><table>', html)
        html = html.replace("</table>", "</table></div></div>")
        html = re.sub(r"<blockquote>\s*<p>\[!(good|warn|bad|note)\]\s*",
                      lambda m: f'<blockquote class="{m.group(1)}"><p>', html, flags=re.I)
        if html.strip():
            sections.append({"type": "markdown", "html": html})
        chunk.clear()

    for tok in tokens:
        lang = tok.info.strip().split()[0] if tok.type == "fence" and tok.info.strip() else ""
        if lang not in COMPONENT_FENCES:
            chunk.append(tok)
            continue
        try:
            body = yaml.safe_load(tok.content) or {}
        except yaml.YAMLError as e:
            raise SystemExit(f"Khối ```{lang} (dòng {tok.map[0] + 1}) không phải YAML/JSON hợp lệ: {e}")
        if lang == "kpis" and isinstance(body, list):
            body = {"items": body}
        section = {"type": lang, **body}
        # heading ngay trước khối component -> thành tiêu đề của component
        if len(chunk) >= 3 and chunk[-1].type == "heading_close" and chunk[-3].tag in ("h2", "h3") and "title" not in section:
            section["title"] = chunk[-2].content
            del chunk[-3:]
        flush()
        sections.append(section)
    flush()
    return {"meta": meta, "sections": sections}


def build(data: dict, out_path: Path) -> None:
    errors = validate(data)
    if errors:
        raise SystemExit("Dữ liệu báo cáo không hợp lệ:\n  - " + "\n  - ".join(errors))
    html = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    html = DATA_BLOCK.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(3), html, count=1)
    title = data["meta"]["title"].replace("&", "&amp;").replace("<", "&lt;")
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1)
    html = inline_scripts(html)
    problems = check(html)
    if problems:
        raise SystemExit("File đầu ra chưa đạt:\n  - " + "\n  - ".join(problems))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Đã tạo {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", type=Path, help="template Markdown của loại báo cáo (templates/reports/<id>.md)")
    ap.add_argument("--values", type=Path, help="file JSON giá trị cho các {{ biến }} trong template --md")
    ap.add_argument("--data", type=Path, help="file JSON section (template mặc định)")
    ap.add_argument("--out", type=Path, help="đường dẫn file HTML đầu ra")
    ap.add_argument("--check", type=Path, help="chỉ kiểm tra một file HTML đã sinh")
    a = ap.parse_args()
    if a.check:
        problems = check(a.check.read_text(encoding="utf-8"))
        if problems:
            print("Chưa đạt:\n  - " + "\n  - ".join(problems))
            sys.exit(1)
        print(f"OK: {a.check}")
        return
    if not a.out or bool(a.md) == bool(a.data):
        ap.error("cần --out và đúng một trong --md hoặc --data (hoặc dùng --check)")
    if a.md:
        values = json.loads(a.values.read_text(encoding="utf-8")) if a.values else {}
        data = render_markdown_report(a.md, values)
    else:
        data = json.loads(a.data.read_text(encoding="utf-8"))
    build(data, a.out)


if __name__ == "__main__":
    main()
