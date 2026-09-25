#!/usr/bin/env python3
"""Gọi REST API lấy dữ liệu kinh doanh, hỗ trợ phân trang, lưu JSON thô vào cache.

Secret truyền dạng ${TEN_BIEN}; giá trị lấy từ biến môi trường hoặc file .env ở gốc repo
và được che (***) trong mọi thông báo. Chỉ dùng thư viện chuẩn.

Ví dụ:
  python3 fetch_api.py --url "https://api.example.com/v1/orders" \
    --header "Authorization: Bearer ${ORDERS_API_TOKEN}" \
    --param from=2026-08-01 --param to=2026-08-31 \
    --records-path data.items --page-param page --page-size-param limit --page-size 500 \
    --out data/cache/doanh-thu-thang/orders/2026-08-01_2026-08-31.json

  # POST body JSON:
  python3 fetch_api.py --url ... --method POST --json '{"from":"2026-08-01"}' --out ...
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
VAR = re.compile(r"\$\{([A-Z0-9_]+)\}")
SECRETS: set[str] = set()


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def expand(s: str) -> str:
    def repl(m: re.Match) -> str:
        name = m.group(1)
        if name not in os.environ:
            raise SystemExit(f"Thiếu biến môi trường {name} (đặt trong .env hoặc export)")
        val = os.environ[name]
        if val:
            SECRETS.add(val)
        return val

    return VAR.sub(repl, s)


def redact(s: str) -> str:
    for v in sorted(SECRETS, key=len, reverse=True):
        s = s.replace(v, "***")
    return s


def dig(obj, path: str | None):
    if not path:
        return obj
    for part in path.split("."):
        obj = obj[int(part)] if isinstance(obj, list) else (obj or {}).get(part)
    return obj


def request(url: str, method: str, headers: dict, body: bytes | None, retries: int, timeout: float):
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code < 500 and e.code != 429 or attempt == retries:
                detail = e.read().decode("utf-8", "replace")[:300]
                raise SystemExit(redact(f"HTTP {e.code} khi gọi {method} {url}: {detail}"))
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == retries:
                raise SystemExit(redact(f"Lỗi kết nối {method} {url}: {e}"))
        time.sleep(2**attempt)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True)
    ap.add_argument("--method", default="GET")
    ap.add_argument("--header", action="append", default=[], help='"Tên: giá trị", lặp lại được')
    ap.add_argument("--param", action="append", default=[], help="k=v query param, lặp lại được")
    ap.add_argument("--json", help="body JSON (POST/PUT)")
    ap.add_argument("--records-path", help="đường dẫn tới mảng bản ghi trong response, vd data.items")
    ap.add_argument("--page-param", help="tên query param số trang (phân trang theo trang)")
    ap.add_argument("--page-start", type=int, default=1)
    ap.add_argument("--page-size-param")
    ap.add_argument("--page-size", type=int, default=100)
    ap.add_argument("--cursor-path", help="đường dẫn tới cursor trang sau trong response (phân trang cursor)")
    ap.add_argument("--cursor-param", default="cursor")
    ap.add_argument("--max-pages", type=int, default=1000)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=30)
    ap.add_argument("--out", type=Path, required=True, help="file JSON đầu ra (nên nằm trong data/cache/)")
    ap.add_argument("--refresh", action="store_true", help="gọi lại kể cả khi --out đã tồn tại")
    a = ap.parse_args()

    if a.out.exists() and not a.refresh:
        print(f"Dùng cache: {a.out} (thêm --refresh để gọi lại)")
        return

    load_dotenv(REPO_ROOT / ".env")
    base_url = expand(a.url)
    headers = {"Accept": "application/json", "User-Agent": "fw-bu-report/0.1"}
    for h in a.header:
        k, _, v = h.partition(":")
        headers[k.strip()] = expand(v.strip())
    params = dict(p.split("=", 1) for p in (expand(x) for x in a.param))
    body = None
    if a.json:
        body = expand(a.json).encode("utf-8")
        headers["Content-Type"] = "application/json"

    records, pages, page, cursor = [], 0, a.page_start, None
    while pages < a.max_pages:
        q = dict(params)
        if a.page_param:
            q[a.page_param] = str(page)
        if a.page_size_param:
            q[a.page_size_param] = str(a.page_size)
        if cursor:
            q[a.cursor_param] = cursor
        url = base_url + ("&" if "?" in base_url else "?") + urllib.parse.urlencode(q) if q else base_url
        data = request(url, a.method.upper(), headers, body, a.retries, a.timeout)
        pages += 1
        batch = dig(data, a.records_path)
        if not a.records_path:
            records = data
            break
        if not isinstance(batch, list):
            raise SystemExit(f"records-path '{a.records_path}' không trỏ tới một mảng")
        records.extend(batch)
        if a.cursor_path:
            cursor = dig(data, a.cursor_path)
            if not cursor:
                break
        elif a.page_param:
            if len(batch) < a.page_size or not batch:
                break
            page += 1
        else:
            break

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    n = len(records) if isinstance(records, list) else 1
    print(f"Đã lưu {n} bản ghi ({pages} trang) vào {a.out}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
