import time
from datetime import datetime
import schedule

# Import hàm xử lý chính từ package tasks
from tasks.bank_switcher import job_run_sync
from tasks.config import VN_TZ
from modules.discord_logger import DiscordLogger

logger = DiscordLogger()

if __name__ == "__main__":
    logger.log("🤖 FABI BRW Bot đã khởi động chế độ trực chiến 24/7...", "info")

    # 🌟 Đăng ký các mốc giờ đổi ca của quán tại đây (Dễ dàng thêm/bớt ca)
    schedule.every().day.at("06:00").do(job_run_sync)
    schedule.every().day.at("08:30").do(job_run_sync)
    schedule.every().day.at("11:30").do(job_run_sync)
    schedule.every().day.at("13:30").do(job_run_sync)
    schedule.every().day.at("16:30").do(job_run_sync)
    
    # 💡 Mẹo: Bỏ dấu '#' dòng dưới nếu muốn vừa bật file lên là bot chạy quét thử luôn
    job_run_sync()

    print("⏳ Đang chạy ngầm, hệ thống sẽ tự nổ máy khi đến khung giờ hẹn...")
    
    while True:
        schedule.run_pending()
        time.sleep(10)