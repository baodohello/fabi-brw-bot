import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class DiscordLogger:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        # Định nghĩa bảng màu trực quan cho từng trạng thái
        self.colors = {
            "info": 3447003,     # Xanh lam
            "success": 3066993,  # Xanh lá
            "warning": 15105570, # Vàng
            "error": 15158332    # Đỏ
        }
        self.prefixes = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }

    def log(self, message, status="info"):
        """Vừa print ra Terminal, vừa bắn thẳng lên Discord Webhook."""
        status = status.lower()
        prefix = self.prefixes.get(status, "ℹ️")
        full_message = f"{prefix} {message}"
        
        # 1. Xuất ra Terminal của anh
        print(full_message)
        
        # 2. Gửi qua Discord (Nếu đã cấu hình URL trong .env)
        if not self.webhook_url:
            return

        payload = {
            "embeds": [
                {
                    "description": full_message,
                    "color": self.colors.get(status, 3447003),
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            ]
        }

        try:
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception as e:
            print(f"⚠️ [Discord Error]: Không thể gửi log tới Discord: {str(e)}")

    def send_raw_text(self, text):
        """Hàm phụ nếu anh chỉ muốn gửi text thô không bọc khung màu trên Discord."""
        if not self.webhook_url:
            return
        try:
            requests.post(self.webhook_url, json={"content": text}, timeout=5)
        except Exception:
            pass

# --- ĐOẠN CODE TEST KHI CHẠY TRỰC TIẾP FILE NÀY ---
if __name__ == "__main__":
    print("🧪 Khởi động tiến trình kiểm tra kết nối Discord Logger...\n")
    
    # Khởi tạo đối tượng logger
    logger = DiscordLogger()
    
    if not logger.webhook_url:
        print("❌ Lỗi: Chưa tìm thấy cấu hình DISCORD_WEBHOOK_URL trong file .env!")
        print("Vui lòng kiểm tra lại file .env đặt cùng cấp thư mục.")
    else:
        print("🔗 Đã tìm thấy cấu hình Webhook. Tiến hành bắn tin nhắn test...\n")
        
        # 1. Gửi tin nhắn dạng raw text (không bọc khung màu)
        logger.send_raw_text("📢 **[TEST]** Hệ thống kích hoạt thử nghiệm Discord Logger Module")
        
        # 2. Test đầy đủ 4 trạng thái màu sắc kèm icon
        logger.log("Đây là tin nhắn thông báo (INFO log test)", "info")
        logger.log("Hệ thống xử lý cập nhật thành công (SUCCESS log test)", "success")
        logger.log("Phát hiện số tài khoản không đồng bộ (WARNING log test)", "warning")
        logger.log("Kết nối tới máy chủ iPOS thất bại (ERROR log test)", "error")
        
        print("\n🚀 Đã chạy xong toàn bộ lệnh test! Anh hãy mở Discord xem các dòng log hiển thị đúng màu chưa nhé.")