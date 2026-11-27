import time
import schedule

# Import hàm xử lý chính từ package tasks
from tasks.bank_switcher import run_bank_switcher
from config import VN_TZ
from modules.discord_logger import DiscordLogger

logger = DiscordLogger()

if __name__ == "__main__":
    logger.log("🤖 FABI BRW Bot đã khởi động chế độ trực chiến 24/7...", "info")

    # 🌟 Đăng ký các mốc giờ đổi ca của quán tại đây (Dễ dàng thêm/bớt ca)
    # Mỗi schedule.every() tạo 1 Job MỚI — gọi riêng để tránh .at() ghi đè lẫn nhau
    times = [
        "06:00", 
        "09:00", "11:30", 
        "12:00", "12:15",
        "13:30", "16:00",
        "17:00", "17:30",#hqua chua xuat
        "18:00", "18:30" #hqua chua xuat
        ]
    for t in times:
        schedule.every().monday.at(t).do(run_bank_switcher)
        schedule.every().tuesday.at(t).do(run_bank_switcher)
        schedule.every().wednesday.at(t).do(run_bank_switcher)
        schedule.every().thursday.at(t).do(run_bank_switcher)
        schedule.every().friday.at(t).do(run_bank_switcher)



    
    # 💡 Mẹo: Bỏ dấu '#' dòng dưới nếu muốn vừa bật file lên là bot chạy quét thử luôn
    run_bank_switcher()

    print("⏳ Đang chạy ngầm, hệ thống sẽ tự nổ máy khi đến khung giờ hẹn...")
    
    while True:
        schedule.run_pending()
        time.sleep(10)