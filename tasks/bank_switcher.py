"""Tác vụ tự động đổi số tài khoản ngân hàng hiển thị trên iPOS FABI theo khung giờ ca làm việc."""

import os
import time
import schedule
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

from config import BANK_SCHEDULE, VN_TZ
from modules.discord_logger import DiscordLogger

# IMPORT AUTH MODULE VỪA TÁCH
from modules.fabi_auth import SESSION_FILE, ensure_valid_session

logger = DiscordLogger()
load_dotenv()

def check_current_bank_info(store_uid):
    """Hàm CHỈ ĐỌC: Truy cập vào trang cấu hình để kiểm tra thông tin tài khoản hiện tại."""
    # SỬ DỤNG AUTH MODULE ĐỂ KIỂM TRA SESSION
    if not ensure_valid_session():
        return None

    with sync_playwright() as p:
        logger.log("Agent đang mở trình duyệt ở chế độ CHỈ ĐỌC để kiểm tra dữ liệu...", "info")
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        
        target_url = f"https://fabi.ipos.vn/setting/store/detail/{store_uid}"
        page.goto(target_url)
        
        try:
            page.wait_for_selector("input[placeholder='Nhập số tài khoản']", timeout=10000)
            
            current_bank_name = page.locator(".text-selected p.text-link-blue b").inner_text()
            current_bank_acc = page.locator("input[placeholder='Nhập số tài khoản']").input_value()
            current_acc_name = page.locator("input[placeholder='Nhập tên tài khoản']").input_value()
            
            browser.close()
            return {
                "bank_name": current_bank_name,
                "bank_acc": current_bank_acc,
                "bank_acc_name": current_acc_name
            }
        except Exception as e:
            browser.close()
            logger.log(f"Phiên làm việc có thể đã hết hạn hoặc không tải được form VietQr.", "warning")
            return "EXPIRED"

def run_fabi_agent_with_session(store_uid, new_bank_acc, new_acc_name="DO TUAN BAO"):
    """Dùng lại session đã lưu để cập nhật thông tin."""
    with sync_playwright() as p:
        logger.log("Agent khởi động trình duyệt bằng phiên đăng nhập để tiến hành UPDATE...", "info")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        
        target_url = f"https://fabi.ipos.vn/setting/store/detail/{store_uid}"
        page.goto(target_url)
        
        try:
            page.wait_for_selector("input[placeholder='Nhập số tài khoản']", timeout=10000)
            
            stk_field = page.locator("input[placeholder='Nhập số tài khoản']")
            stk_field.fill(new_bank_acc)
            stk_field.dispatch_event("change")
            
            name_field = page.locator("input[placeholder='Nhập tên tài khoản']")
            name_field.fill(new_acc_name)
            name_field.dispatch_event("change")
            
            page.wait_for_timeout(1000)
            
            page.locator("#detailHeader button:has-text('Lưu')").click()
            page.wait_for_timeout(4000)
            return True
        except Exception as e:
            logger.log(f"Thao tác cập nhật thông tin trên form thất bại: {str(e)}", "error")
            return False
        finally:
            browser.close()

def job_run_sync():
    now_vn = datetime.now(VN_TZ)
    now_str = now_vn.strftime("%H:%M")
    current_hour = now_vn.hour
    current_minute = now_vn.minute
    print("⏰ Giờ hệ thống (Múi giờ Việt Nam):", now_str)

    sample_schedule = list(BANK_SCHEDULE.values())[0]["schedule"]
    selected_slot = None
    
    for slot_time in sample_schedule.keys():
        slot_h, slot_m = map(int, slot_time.split(":"))
        if abs((current_hour * 60 + current_minute) - (slot_h * 60 + slot_m)) <= 30:
            selected_slot = slot_time
            break

    if not selected_slot:
        logger.log(f"⚠️ Cảnh báo: Kích hoạt lúc {now_str} nhưng không khớp mốc giờ cấu hình nào!", "warning")
        return

    logger.log(f"🔔 **PHÁT HIỆN KHUNG GIỜ LÀM VIỆC: MỐC [{selected_slot}]**", "info")

    for store_name, store_data in BANK_SCHEDULE.items():
        logger.log(f"\n=================== 🏪 {store_name.upper()} ===================", "info")
        
        STORE_UID = store_data["uid"]
        account_target = store_data["schedule"][selected_slot]
        STK_MUC_TIEU = account_target["stk"]
        TEN_MUC_TIEU = account_target["ten"]

        logger.log(f"🎯 Tài khoản cần cài đặt: ********{STK_MUC_TIEU[-4:]} ({TEN_MUC_TIEU})", "info")

        info_truoc = None
        for attempt in range(2):
            info_truoc = check_current_bank_info(STORE_UID)
            
            if info_truoc == "EXPIRED":
                logger.log("🔄 Session hết hạn. Tiến hành làm mới qua Auth Module...", "warning")
                # GỌI HÀM LÀM MỚI VỚI THAM SỐ THAY THẾ CHO LUỒNG XÓA THỦ CÔNG CŨ
                if not ensure_valid_session(force_refresh=True):
                    logger.log("❌ Không thể làm mới phiên đăng nhập. Dừng tiến trình.", "error")
                    return 
                continue
            break

        if info_truoc and isinstance(info_truoc, dict):
            logger.log(f"Số TK hiện tại trên iPOS: ********{info_truoc['bank_acc'][-4:]} ({info_truoc['bank_acc_name']})", "info")
            
            if info_truoc["bank_acc"] == STK_MUC_TIEU and info_truoc["bank_acc_name"] == TEN_MUC_TIEU:
                logger.log(f"✅ Kết quả: {store_name} đã đúng số tài khoản. Bỏ qua bước cập nhật.", "success")
            else:
                logger.log("🔄 Kết quả: Số tài khoản lệch pha! Kích hoạt Agent ghi đè dữ liệu...", "warning")
                
                update_success = run_fabi_agent_with_session(STORE_UID, STK_MUC_TIEU, new_acc_name=TEN_MUC_TIEU)
                
                if update_success:
                    logger.log("🕵️ Tiến hành HẬU KIỂM độc lập sau khi Lưu...", "info")
                    info_sau = check_current_bank_info(STORE_UID)
                    
                    if info_sau and isinstance(info_sau, dict):
                        summary_msg = (
                            f"📊 **BÁO CÁO CẬP NHẬT: {store_name}**\n"
                            f"• Mốc giờ: `{selected_slot}`\n"
                            f"• Trước khi chạy: `********{info_truoc['bank_acc'][-4:]}`\n"
                            f"• Thực tế hiện tại: `********{info_sau['bank_acc'][-4:]}`\n"
                            f"• Chủ tài khoản: `{info_sau['bank_acc_name']}`"
                        )
                        
                        if info_sau["bank_acc"] == STK_MUC_TIEU:
                            logger.log(f"🎉 Xác thực: Đổi số TK cho {store_name} THÀNH CÔNG!", "success")
                            logger.log(summary_msg + "\n\n🟢 **TRẠNG THÁI: HOÀN THÀNH**", "success")
                        else:
                            logger.log(f"❌ Xác thực: Thao tác Lưu cho {store_name} thất bại!", "error")
                            logger.log(summary_msg + "\n\n🔴 **TRẠNG THÁI: LỖI ĐỒNG BỘ**", "error")
                else:
                    logger.log(f"❌ Gặp lỗi trong luồng điền form của {store_name}.", "error")
        else:
            logger.log(f"❌ Bỏ qua {store_name} do không lấy được dữ liệu hiện tại.", "error")
            
        time.sleep(3)

    logger.log("\n🏁 **HOÀN THÀNH TOÀN BỘ TIẾN TRÌNH CHO TẤT CẢ CỬA HÀNG**", "success")


    
if __name__ == "__main__":
    # Test block to run manually
    job_run_sync()