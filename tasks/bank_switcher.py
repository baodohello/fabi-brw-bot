import os
import time
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# IMPORT MODULE DISCORD VỪA TẠO
from modules.discord_logger import DiscordLogger

# Khởi tạo một bản dùng chung cho toàn bộ file
logger = DiscordLogger()

load_dotenv()
USER = os.getenv("FABI_USERNAME", "brwcoffee2021@gmail.com")
PASSWORD = os.getenv("FABI_PASSWORD")
SESSION_FILE = "fabi_auth_state.json"

def auto_login_and_save_session():
    """Hàm tự động điền tài khoản từ .env để đăng nhập và đóng gói session."""
    if not PASSWORD:
        logger.log("Chưa cấu hình FABI_PASSWORD trong file .env!", "error")
        return False

    with sync_playwright() as p:
        logger.log(f"Agent khởi động trình duyệt để tự động đăng nhập tài khoản: {USER}...", "info")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://fabi.ipos.vn/#/login")
        
        try:
            page.wait_for_selector("input[name='email_input']", timeout=10000)
            page.locator("input[name='email_input']").fill(USER)
            page.locator("input[type='password']").fill(PASSWORD)
            
            logger.log("Đang nhấn nút Đăng nhập hệ thống...", "info")
            page.locator("button[type='submit']").click()
            
            page.wait_for_url("**/dashboard**", timeout=20000)
            logger.log("Đăng nhập thành công vào hệ thống quản trị iPOS!", "success")
            
            context.storage_state(path=SESSION_FILE)
            logger.log(f"Đã đóng gói và lưu phiên làm việc mới vào '{SESSION_FILE}'", "success")
            browser.close()
            return True
        except Exception as e:
            logger.log(f"Tự động đăng nhập thất bại hoặc sai thông tin: {str(e)}", "error")
            browser.close()
            return False


def check_current_bank_info(store_uid):
    """Hàm CHỈ ĐỌC: Truy cập vào trang cấu hình để kiểm tra thông tin tài khoản hiện tại."""
    if not os.path.exists(SESSION_FILE):
        logger.log("Không tìm thấy file session. Tiến hành đăng nhập tạo mới...", "warning")
        if not auto_login_and_save_session():
            return None

    with sync_playwright() as p:
        logger.log("Agent đang mở trình duyệt ở chế độ CHỈ ĐỌC để kiểm tra dữ liệu...", "info")
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        
        target_url = f"https://fabi.ipos.vn/setting/store/detail/{store_uid}"
        page.goto(target_url)
        
        try:
            # Chờ xem có bị đá về trang login do hết hạn token không
            page.wait_for_selector("input[placeholder='Nhập số tài khoản']", timeout=15000)
            
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
            # ĐÂY LÀ ĐIỂM CẢI TIẾN: Nếu lỗi do hết hạn phiên (bị đá ra form login), tự động xóa session cũ và báo để luồng chính xử lý
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
            page.wait_for_selector("input[placeholder='Nhập số tài khoản']", timeout=60)
            
            logger.log(f"Đang ghi đè Số tài khoản mới: {new_bank_acc}", "info")
            stk_field = page.locator("input[placeholder='Nhập số tài khoản']")
            stk_field.fill(new_bank_acc)
            stk_field.dispatch_event("change") # CẢI TIẾN: Ép giao diện Angular/Vue cập nhật model
            
            logger.log(f"Đang ghi đè Tên tài khoản mới: {new_acc_name}", "info")
            name_field = page.locator("input[placeholder='Nhập tên tài khoản']")
            name_field.fill(new_acc_name)
            name_field.dispatch_event("change") # CẢI TIẾN: Ép giao diện Angular/Vue cập nhật model
            
            page.wait_for_timeout(1000)
            
            logger.log("Đang kích hoạt nút 'Lưu' trên thanh công cụ tiêu đề...", "info")
            page.locator("#detailHeader button:has-text('Lưu')").click()
            logger.log("Đã nhấn nút Lưu trên giao diện Web thành công.", "success")
            
            logger.log("Chờ 4 giây cho hệ thống đồng bộ dữ liệu lên máy chủ...", "info")
            page.wait_for_timeout(4000)
            return True
        except Exception as e:
            logger.log(f"Thao tác cập nhật thông tin trên form thất bại: {str(e)}", "error")
            return False
        finally:
            browser.close()


# --- KỊCH BẢN PHỐI HỢP ---
if __name__ == "__main__":
    # 1. Ma trận cấu hình tài khoản theo khung giờ của cả 2 cửa hàng
    STORES_CONFIG = {
        "Cửa Hàng 1 (BRW 1)": {
            "uid": "2f202b34-e339-4b89-85de-364b8cc61a18",
            # 8h30 và 1h30 cài sang stk cty còn lại dùng stk cá nhân
            "schedule": {
                "06:00": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
                "08:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
                "11:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
                "13:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
                "16:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
            }
        },
        "Cửa Hàng 2 (BRW 2)": {
            "uid": "1fbeca99-192e-4766-937a-c35e8f28737a",
            # 8h30 và 1h30 cài sang stk cty còn lại dùng stk cá nhân
            "schedule": {
                "06:00": {"stk": "8807988664", "ten": "DO TUAN BAO"},
                "08:30": {"stk": "8807988664", "ten": "DO TUAN BAO"},
                "11:30": {"stk": "8807988664", "ten": "DO TUAN BAO"},
                "13:30": {"stk": "8807988664", "ten": "DO TUAN BAO"},
                "16:30": {"stk": "8807988664", "ten": "DO TUAN BAO"}
            }
        }
    }

    # 2. Tự động xác định mốc giờ hệ thống khi kích hoạt kích hoạt script
    now_str = datetime.now().strftime("%H:%M")
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute

    # Lấy đại diện lịch trình của cửa hàng đầu tiên để tìm slot giờ khớp
    sample_schedule = list(STORES_CONFIG.values())[0]["schedule"]
    selected_slot = None
    
    for slot_time in sample_schedule.keys():
        slot_h, slot_m = map(int, slot_time.split(":"))
        if abs((current_hour * 60 + current_minute) - (slot_h * 60 + slot_m)) <= 1500:
            selected_slot = slot_time
            break

    if not selected_slot:
        logger.log(f"⚠️ Cảnh báo: Kích hoạt lúc {now_str} nhưng không khớp mốc giờ cấu hình nào!", "warning")
        exit()

    logger.log(f"🔔 **PHÁT HIỆN KHUNG GIỜ LÀM VIỆC: MỐC [{selected_slot}]**", "info")

    # 3. VÒNG LẶP CHẠY TUẦN TỰ LẦN LƯỢT TỪNG CỬA HÀNG
    for store_name, store_data in STORES_CONFIG.items():
        logger.log(f"\n=================== 🏪 {store_name.upper()} ===================", "info")
        
        STORE_UID = store_data["uid"]
        account_target = store_data["schedule"][selected_slot]
        STK_MUC_TIEU = account_target["stk"]
        TEN_MUC_TIEU = account_target["ten"]

        logger.log(f"🎯 Tài khoản cần cài đặt: {STK_MUC_TIEU} ({TEN_MUC_TIEU})", "info")

        # --- LUỒNG PHỐI HỢP CHECK & UPDATE CHO TỪNG QUÁN ---
        info_truoc = None
        for attempt in range(2):
            info_truoc = check_current_bank_info(STORE_UID)
            
            if info_truoc == "EXPIRED":
                logger.log("🔄 Session hết hạn. Tiến hành xóa file và đăng nhập lại...", "warning")
                if os.path.exists(SESSION_FILE):
                    os.remove(SESSION_FILE)
                if not auto_login_and_save_session():
                    logger.log("❌ Không thể làm mới phiên đăng nhập. Dừng tiến trình.", "error")
                    exit()
                continue
            break

        if info_truoc and isinstance(info_truoc, dict):
            logger.log(f"Số TK hiện tại trên iPOS: {info_truoc['bank_acc']} ({info_truoc['bank_acc_name']})", "info")
            
            if info_truoc["bank_acc"] == STK_MUC_TIEU and info_truoc["bank_acc_name"] == TEN_MUC_TIEU:
                logger.log(f"✅ Kết quả: {store_name} đã đúng số tài khoản. Bỏ qua bước cập nhật.", "success")
            else:
                logger.log("🔄 Kết quả: Số tài khoản lệch pha! Kích hoạt Agent ghi đè dữ liệu...", "warning")
                
                # Thực hiện UPDATE
                update_success = run_fabi_agent_with_session(STORE_UID, STK_MUC_TIEU, new_acc_name=TEN_MUC_TIEU)
                
                if update_success:
                    logger.log("🕵️ Tiến hành HẬU KIỂM độc lập sau khi Lưu...", "info")
                    info_sau = check_current_bank_info(STORE_UID)
                    
                    if info_sau and isinstance(info_sau, dict):
                        summary_msg = (
                            f"📊 **BÁO CÁO CẬP NHẬT: {store_name}**\n"
                            f"• Mốc giờ: `{selected_slot}`\n"
                            f"• Trước khi chạy: `{info_truoc['bank_acc']}`\n"
                            f"• Thực tế hiện tại: `{info_sau['bank_acc']}`\n"
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
            
        # Nghỉ ngắn 3 giây giữa các cửa hàng để chuyển đổi mượt mà, không bị dồn dập request
        time.sleep(3)

    logger.log("\n🏁 **HOÀN THÀNH TOÀN BỘ TIẾN TRÌNH CHO TẤT CẢ CỬA HÀNG**", "success")