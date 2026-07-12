# 🤖 FABI BRW Bot

Bot tự động hóa nền tảng **iPOS FABI** cho chuỗi cà phê BR-W, gồm 2 tính năng chính:
- **Bank Switcher**: Tự động đổi số tài khoản ngân hàng hiển thị theo ca làm việc
- **VAT Sync**: Tự động lọc và xuất hóa đơn VAT chưa xuất

## 🚀 Cài đặt & Chạy

```bash
# Tạo virtual environment
python -m venv venv
.\venv\Scripts\activate

# Cài dependencies
pip install -r requirements.txt
playwright install chromium

# Tạo file .env (xem mẫu bên dưới)
```

## ⚙️ Biến môi trường (.env)

```
FABI_USERNAME=brwcoffee2021@gmail.com
FABI_PASSWORD=your_password_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## ▶️ Chạy

```bash
# Chạy scheduler 24/7 (tự động đổi ca + VAT sync)
python main.py

# Chạy riêng tác vụ VAT Sync
python -m tasks.vat_sync.main_task

# Chạy riêng tác vụ
python -m tasks.invoice_validator.main
```


chrome user data dir 
C:\Users\ADMIN\AppData\Local\Google\Chrome\User Data


## 📋 Mã quy ước

| Mã | Ý nghĩa |
|---|---|
| `3` / `4` | Cửa hàng: Đống Đa / Trung Kính |
| `A` / `B` / `C` | Phương thức: Chuyển khoản / Tiền mặt / Quẹt thẻ |

## 📁 Cấu trúc dự án

Xem chi tiết trong [`AGENTS.md`](./AGENTS.md).