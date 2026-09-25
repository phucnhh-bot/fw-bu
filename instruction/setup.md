# Cài đặt môi trường

Đã kiểm tra trên Ubuntu (Linux), Node 24, Python 3.12.

## 1. Node.js + OpenSpec (lên plan)

OpenSpec cần Node.js ≥ 20.19.

```bash
# nếu chưa có Node: cài qua nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
nvm install --lts

npm install -g @fission-ai/openspec@latest
openspec --version        # repo được khởi tạo với 1.13.2
```

Repo đã được `openspec init --tools claude`: skill trong `.claude/skills/openspec-*`, lệnh trong `.claude/commands/opsx/`, cấu hình ở `openspec/config.yaml`. Sau khi nâng cấp OpenSpec, chạy lại để làm mới các file sinh tự động:

```bash
openspec update
```

Bật thêm workflow (new, continue, ff, verify, onboard, bulk-archive) nếu cần: `openspec config profile`.

## 2. Python + uv (xử lý dữ liệu, pipeline báo cáo)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Các script trong skill chỉ dùng thư viện chuẩn của Python 3.12, chạy trực tiếp bằng `python3`.
Khi cần pandas/openpyxl cho phân tích nhanh, dùng `uv run --with pandas --with openpyxl python ...` (không cần cài vào hệ thống).

Khi package `reportkit` đã được dựng (xem `openspec/changes/setup-report-platform/`):

```bash
uv sync                      # cài dependencies theo uv.lock
uv run reportkit --help
```

## 3. Trình duyệt để kiểm tra báo cáo

Dùng Google Chrome/Chromium headless để chụp ảnh và in PDF báo cáo:

```bash
google-chrome --version || chromium-browser --version
```

## 4. Secrets / API key

```bash
cp .env.example .env         # rồi điền token thật
```

`.env` đã được gitignore. Không commit token, không dán token vào chat hay file báo cáo.

## 5. Obsidian (second brain, tuỳ chọn)

```bash
sudo snap install obsidian --classic
```

Mở `second-brain/` làm vault — chi tiết: [second-brain.md](second-brain.md).

## 6. Claude Code

Mở Claude Code tại thư mục gốc repo; skill trong `.claude/skills/` được nạp tự động:

- `business-report-html` — dựng báo cáo HTML
- `fetch-business-data` — lấy dữ liệu từ API/CSV/Excel
- `openspec-*` và lệnh `/opsx:propose`, `/opsx:explore`, `/opsx:apply`, `/opsx:archive`, … — lên plan và triển khai
