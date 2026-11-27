"""Tác vụ tự động đổi số tài khoản ngân hàng hiển thị trên iPOS FABI theo khung giờ ca làm việc."""

import os
import time
import schedule
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from config import BANK_SCHEDULE, VN_TZ
from modules.discord_logger import DiscordLogger
from modules.fabi_auth import SESSION_FILE, ensure_valid_session 

load_dotenv()
logger = DiscordLogger( webhook_url=os.getenv("DISCORD_WEBHOOK_URL_BANK_SWITCHER") )

# ---------------------------------------------------------------------------
# Hằng số
# ---------------------------------------------------------------------------
STORE_URL = "https://fabi.ipos.vn/micro/setting/store/detail/{store_uid}"
SEL_ACC = "input[placeholder='Nhập số tài khoản']"
SEL_NAME = "input[placeholder='Nhập tên tài khoản']"
SEL_SAVE = "button:has-text('Lưu')"

SLOT_TOLERANCE_MIN = 10  # sai lệch tối đa (phút) để khớp một mốc giờ
STORE_DELAY_SEC = 0      # nghỉ giữa các cửa hàng


def bank_check_or_update(store_uid, update = False, new_bank_acc=None, new_acc_name=None):
    """Dùng lại session đã lưu để cập nhật thông tin."""
    with sync_playwright() as p:
        logger.log(f"Agent khởi động trình duyệt bằng phiên đăng nhập để tiến hành {update and 'UPDATE' or 'CHECK'} ...", "info")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        page.goto(STORE_URL.format(store_uid=store_uid))

        # Thử khởi chạy và kiểm tra form VietQr
        try:
            page.wait_for_timeout(1000)
            page.wait_for_selector(SEL_ACC, timeout=30000) 
            if not update:
                info = {
                    "bank_acc": page.locator(SEL_ACC).input_value(),    
                "bank_acc_name": page.locator(SEL_NAME).input_value(),
                }
                browser.close()
                return info
            for selector, value in ((SEL_ACC, new_bank_acc), (SEL_NAME, new_acc_name)):
                    field = page.locator(selector)
                    if value is None:
                        logger.log(f"⚠️ Cảnh báo: Không có giá trị mới để điền cho selector {selector}. Bỏ qua.", "warning")
                        continue
                    field.fill(value)
                    field.dispatch_event("change")
            page.wait_for_timeout(1000)
            page.locator(SEL_SAVE).click() # Click nút Lưu
            page.wait_for_timeout(4000)
            browser.close()
            return True
        except Exception as e:
            browser.close()
            print(f"⚠️ Lỗi khi kiểm tra/cập nhật số tài khoản cho cửa hàng {store_uid}: {e}")
            logger.log(f"Phiên làm việc có thể đã hết hạn hoặc không tải được form VietQr.", "warning")
            return False

def run_bank_switcher():
    """Hàm chạy đồng bộ tác vụ Bank Switcher theo khung giờ."""

    now_vn = datetime.now(VN_TZ)
    now_str = now_vn.strftime("%H:%M")
    current_hour = now_vn.hour
    current_minute = now_vn.minute
    print("⏰ Giờ hệ thống (Múi giờ Việt Nam):", now_str)
    sample_schedule = list(BANK_SCHEDULE.values())[0]["schedule"]
    selected_slot = None

    # Tìm mốc giờ khớp với thời điểm hiện tại (trong khoảng sai lệch cho phép)
    for slot_time in sample_schedule.keys():
        slot_h, slot_m = map(int, slot_time.split(":"))
        if abs((current_hour * 60 + current_minute) - (slot_h * 60 + slot_m)) <= SLOT_TOLERANCE_MIN: #time limit for correct slot
            selected_slot = slot_time
            break
    if not selected_slot:
        logger.log(f"⚠️ Cảnh báo: Kích hoạt lúc {now_str} nhưng không khớp mốc giờ cấu hình nào!", "warning")
        return
    logger.log(f"🔔 **PHÁT HIỆN KHUNG GIỜ LÀM VIỆC: MỐC [{selected_slot}]**", "info")

    # Duyệt qua từng cửa hàng trong cấu hình BANK_SCHEDULE
    for store_name, store_data in BANK_SCHEDULE.items():
        ensure_valid_session(force_refresh=True)  # Kiểm tra session trước khi chạy

        logger.log(f"\n=================== 🏪 {store_name.upper()} ===================", "info")
        STORE_UID = store_data["uid"]
        account_target = store_data["schedule"][selected_slot]
        STK_MUC_TIEU = account_target["stk"]
        TEN_MUC_TIEU = account_target["ten"]

        logger.log(f"🎯 Tài khoản cần cài đặt: ***{STK_MUC_TIEU[-4:]} (***{TEN_MUC_TIEU[-4:]})", "info")
        update_success = bank_check_or_update(STORE_UID, update=True, new_bank_acc=STK_MUC_TIEU, new_acc_name=TEN_MUC_TIEU)
        if update_success:
            logger.log("🕵️ Tiến hành HẬU KIỂM độc lập sau khi Lưu...", "info")
            info_sau = bank_check_or_update(STORE_UID, update=False)

            if info_sau and isinstance(info_sau, dict):
                summary_msg = (
                    f"📊 **BÁO CÁO CẬP NHẬT: {store_name}**\n"
                    f"• Mốc giờ: `{selected_slot}`\n"
                    f"• Thực tế hiện tại: `**{info_sau['bank_acc'][-4:]} (***{info_sau['bank_acc_name'][-4:]})`\n"
                )
                if info_sau["bank_acc"] == STK_MUC_TIEU:
                    logger.log(f"🎉 Xác thực: Đổi số TK cho {store_name} THÀNH CÔNG!", "success")
                    logger.log(summary_msg + "\n\n🟢 **TRẠNG THÁI: HOÀN THÀNH**", "success")
                else:
                    logger.log(f"❌ Xác thực: Thao tác Lưu cho {store_name} thất bại!", "error")
                    logger.log(summary_msg + "\n\n🔴 **TRẠNG THÁI: LỖI ĐỒNG BỘ**", "error")
        else:
            logger.log(f"❌ Gặp lỗi trong luồng điền form của {store_name}.", "error")
            
        time.sleep(STORE_DELAY_SEC)

    logger.log("\n🏁 **HOÀN THÀNH TOÀN BỘ TIẾN TRÌNH CHO TẤT CẢ CỬA HÀNG**", "success")



    
if __name__ == "__main__":
    logger.log("🤖 FABI BANK SWITCHER đã khởi động chế độ trực chiến 24/7...", "info")

    # 🌟 Đăng ký các mốc giờ đổi ca của quán tại đây (Dễ dàng thêm/bớt ca)
    # Mỗi schedule.every() tạo 1 Job MỚI — gọi riêng để tránh .at() ghi đè lẫn nhau
    times = [
        "06:00", 
        "09:00", "11:30", 
        "12:00", "12:15",
        "13:30", "16:00",
        "17:00", "17:15",#hqua chua xuat
        "18:00", "18:15" #hqua chua xuat
        ]
    for t in times:
        schedule.every().monday.at(t).do(run_bank_switcher)
        schedule.every().tuesday.at(t).do(run_bank_switcher)
        schedule.every().wednesday.at(t).do(run_bank_switcher)
        schedule.every().thursday.at(t).do(run_bank_switcher)
        schedule.every().friday.at(t).do(run_bank_switcher)

    
    # 💡 Mẹo: Bỏ dấu '#' dòng dưới nếu muốn vừa bật file lên là bot chạy quét thử luôn
    # run_bank_switcher()

    print("⏳ Đang chạy ngầm, hệ thống sẽ tự nổ máy khi đến khung giờ hẹn...")
    
    while True:
        schedule.run_pending()
        time.sleep(10)