# AGENTS.md — FABI BRW Bot

## Project Identity
**Tên**: FABI BRW Bot  
**Mục đích**: Bot tự động hóa nền tảng **iPOS FABI** (https://fabi.ipos.vn) cho chuỗi cà phê BR-W:
1. **Bank Switcher** — Tự động đổi số tài khoản ngân hàng hiển thị trên iPOS theo khung giờ ca làm việc.
2. **VAT Sync** — Tự động lọc, tích chọn và xuất hóa đơn VAT chưa xuất theo chi nhánh & phương thức thanh toán.
3. **Invoice Validator** — Tự động kiểm tra & xác thực hóa đơn máy tính tiền trên cổng MeInvoice.

**Tech stack**: Python 3, Playwright (Chromium headless), schedule, Discord webhook, pytz, dotenv

---

## Kiến trúc thư mục

```
fabi-brw-bot/
├── main.py                  # Entry point: scheduler chạy ngầm 24/7, gọi các task theo giờ
├── requirements.txt         # Dependencies (certifi, playwright, schedule, etc.)
├── start_fabi_bot.bat       # Batch script khởi động bot
├── .env                     # Biến môi trường (KHÔNG commit)
├── fabi_auth_state.json     # Session iPOS (auto-generated, KHÔNG commit)
├── meinvoice_auth_state.json # Session MeInvoice (auto-generated, KHÔNG commit)
│
├── config/
│   ├── __init__.py          # Re-export: BANK_SCHEDULE, VN_TZ, STORES_SETTING
│   ├── bank_schedule.py     # Cấu hình store: uid + schedule tài khoản ngân hàng theo ca
│   └── vat.py               # Cấu hình VAT: store → PTTT → buyer_name + khung giờ
│
├── modules/
│   ├── fabi_auth.py         # Đăng nhập iPOS + lưu/kiểm tra session (fabi_auth_state.json)
│   └── discord_logger.py    # Gửi log màu lên Discord qua Webhook
│
├── tasks/
│   ├── bank_switcher.py     # Task đổi tài khoản ngân hàng trên iPOS
│   ├── vat_sync/
│   │   ├── __init__.py
│   │   ├── main_task.py     # Task chính: duyệt báo cáo VAT → lọc → xuất
│   │   ├── selectors.py     # Tập trung tất cả CSS selector cho giao diện iPOS
│   │   └── helpers/
│   │       ├── select_filter.py        # Chọn bộ lọc: ngày, chi nhánh, PTTT
│   │       ├── process_and_tick_invoices.py  # Duyệt hóa đơn, kiểm tra điều kiện, tích checkbox
│   │       ├── export_vat_details.py   # Xuất VAT chi tiết (modal chọn Cá nhân + nhập tên)
│   │       └── loop_through_report_pages.py  # Điều hướng phân trang
│   └── invoice_validator/
│       ├── __init__.py
│       ├── main.py          # Task chính: duyệt hóa đơn MeInvoice → kiểm tra → xác thực
│       ├── selectors.py     # CSS selector cho cổng MeInvoice
│       └── helpers/
```

---

## Luồng hoạt động (Data Flow)

### Bank Switcher (`main.py` → `tasks/bank_switcher.py`)
```
Scheduler (06:00, 08:30, 11:30, 13:30, 16:30)
    → job_run_sync()
    → Xác định slot giờ hiện tại từ config/bank_schedule.py
    → check_current_bank_info(uid) — đọc STK hiện tại trên iPOS
    → Nếu khác → run_fabi_agent_with_session(uid, stk_mới) — cập nhật
```

### VAT Sync (`main.py` hoặc `python -m tasks.vat_sync.main_task`)
```
run_vat_sync_report_task()
    → Đăng nhập iPOS (dùng session cache)
    → Vào trang /report/accounting/invoices/sale-sync-vat
    → Chọn tab "Hóa đơn chưa xuất VAT"
    → Lặp qua STORES_SETTING từ config/vat.py:
        → Với mỗi store + PTTT:
            → select_filter() — chọn ngày, chi nhánh, PTTT
            → process_and_tick_invoices() — duyệt hóa đơn, tích checkbox theo khung giờ
            → export_vat_details() — xuất VAT với tên buyer_name
```

### Invoice Validator (`python -m tasks.invoice_validator.main`)
```
run_invoice_validator_task()
    → Đăng nhập MeInvoice (app3.meinvoice.vn)
    → Vào trang /v3/hoa-don-may-tinh-tien
    → TODO: Duyệt hóa đơn, kiểm tra trạng thái, xác thực
```

---

## Quy ước code (Conventions)

- **Ngôn ngữ log**: Tiếng Việt, dùng `print(message, status)` với status: `"info"`, `"success"`, `"warning"`, `"error"`
- **DiscordLogger.log()**: Vừa print ra terminal, vừa gửi embed màu lên Discord
- **Playwright**: Dùng `sync_playwright()`, headless=True (trừ VAT task có thể headless=False để debug)
- **Session**: Lưu trong `fabi_auth_state.json`, tự động refresh nếu hết hạn
- **Thời gian**: Múi giờ `Asia/Ho_Chi_Minh` (pytz)
- **Selector**: Tập trung trong `tasks/vat_sync/selectors.py`, dùng CSS selector + text matching

---

## Cách chạy (How to Run)

```bash
# Tạo & kích hoạt venv
python -m venv venv
venv\Scripts\activate

# Cài dependencies
pip install -r requirements.txt
playwright install chromium

# Tạo file .env với các biến:
#   FABI_USERNAME=brwcoffee2021@gmail.com
#   FABI_PASSWORD=...
#   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Chạy scheduler 24/7
python main.py

# Chạy riêng tác vụ VAT Sync
python -m tasks.vat_sync.main_task

# Chạy riêng tác vụ Invoice Validator
python -m tasks.invoice_validator.main
```

---

## Biến môi trường (.env)

| Biến | Mô tả | Bắt buộc |
|---|---|---|
| `FABI_USERNAME` | Email đăng nhập iPOS | Có |
| `FABI_PASSWORD` | Mật khẩu iPOS | Có |
| `DISCORD_WEBHOOK_URL` | Webhook Discord để gửi log | Không |
| `MEINVOICE_USERNAME` | Email/TK đăng nhập MeInvoice | Không |
| `MEINVOICE_PASSWORD` | Mật khẩu MeInvoice | Không |

---

## Lưu ý khi chỉnh sửa code (AI Editing Rules)

- **Không hardcode** selector trong code logic — luôn thêm vào `selectors.py`
- **Giữ nguyên cấu trúc thư mục**: `modules/` cho shared, `tasks/` cho từng tính năng
- **Mỗi file `.py` nên có docstring mô tả ngắn gọn ở đầu file**
- **Khi thêm store mới**: sửa `config/bank_schedule.py` (bank) và `config/vat.py` (VAT)
- **Khi thêm PTTT mới**: sửa `config/vat.py` > `STORES_SETTING`
- **Encoding**: UTF-8 cho tất cả file
- **Terminal**: Dùng PowerShell 5.1, không dùng `&&` mà dùng `;`
