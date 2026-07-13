"""Tác vụ chính đồng bộ hóa đơn VAT: lọc hóa đơn chưa xuất theo chi nhánh & PTTT, tích chọn và xuất VAT."""

import os
import sys
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from config import STORES_SETTING 

# Auto-adjust Python path hỗ trợ chạy kiểm tra thủ công file này từ terminal
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from modules.fabi_auth import SESSION_FILE, ensure_valid_session
from modules.discord_logger import DiscordLogger

# Import các thành phần trong cùng gói tính năng gói gọn
from tasks.vat_sync import selectors
import tasks.vat_sync.helpers as helpers

logger = DiscordLogger()
load_dotenv()

def run_vat_sync_report_task() -> bool:
    """Tác vụ chính kiểm tra báo cáo đồng bộ hóa hóa đơn VAT."""
    logger.log("📋 Bắt đầu tiến trình kiểm tra báo cáo đồng bộ hóa hóa đơn VAT...", "info")
    
    if not ensure_valid_session():
        logger.log("❌ Không thể xác thực phiên đăng nhập. Hủy tác vụ báo cáo VAT.", "error")
        return False

    with sync_playwright() as p:
        logger.log("Agent khởi động trình duyệt bằng phiên đăng nhập để tải trang VAT...", "info")
        browser = p.chromium.launch(headless=False) # Để chạy debug hiển thị UI
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        
        target_url = "https://fabi.ipos.vn/report/accounting/invoices/sale-sync-vat?page=1"
        
        try:
            page.goto(target_url)
            page.wait_for_timeout(3000)
            
            # Kiểm tra trạng thái phiên làm việc
            if "/login" in page.url:
                logger.log("🔄 Phát hiện phiên đăng nhập hết hạn tại trang VAT. Tiến hành làm mới...", "warning")
                browser.close()
                if ensure_valid_session(force_refresh=True):
                    return run_vat_sync_report_task() 
                return False
                
            logger.log(f"✅ Truy cập thành công báo cáo VAT! URL Hiện tại: {page.url}", "success")
            
            # 1. Chuyển sang tab "Hóa đơn chưa xuất VAT" bằng Selector tập trung
            print(f"Đang kích hoạt chọn tab '{selectors.TAB_CHUA_XUAT_VAT}'...", "info")
            tab_locator = page.get_by_role("tab", name=selectors.TAB_CHUA_XUAT_VAT)
            tab_locator.wait_for(state="visible", timeout=300)
            tab_locator.click(force=True)
            print(f"🎉 Đã chuyển thành công sang tab '{selectors.TAB_CHUA_XUAT_VAT}'.", "success")

           # =========================================================================
            # 2. Xử lý dữ liệu cho chi nhánh 
            # =========================================================================
            setting = STORES_SETTING  # Lấy cấu hình từ file config.py
            # --- VÒNG LẶP CHÍNH CỦA BOT ---
            # 1. Duyệt qua từng chi nhánh (Store)

            for store_name, pttt_configs in setting.items():
                for pttt_name, config in pttt_configs.items():
                    if helpers.select_filter(page,date_range_name="Hôm nay", store_name=store_name,  pttt_name=pttt_name):
                        page.wait_for_timeout(3000)
                        print(f"🎉 Đã áp dụng bộ lọc: Chi nhánh '{store_name}', PTTT '{pttt_name}', Ngày 'Hôm nay'.", "success")

                        buyer_name = config["buyer_name"]
                        start_time = config["start_time"]
                        end_time = config["end_time"]

                        print(f"--- Bắt đầu quét hóa đơn [{start_time} - {end_time}] ---", "info")
                        
                        # Truyền dynamic tham số thời gian vào hàm xử lý
                        invoice_summary = helpers.process_and_tick_invoices(
                            page, 
                            start_time=start_time, 
                            end_time=end_time
                        )
                        
                        total_count = invoice_summary["total_processed_count"]
                        total_amount = invoice_summary["total_processed_amount"]

                        if total_count > 0:
                            helpers.export_vat_details(page, buyer_name=buyer_name)
                            logger.log(
                                f"🎉 Hoàn tất báo cáo VAT cho '{store_name}' - PTTT '{pttt_name}'.\n"
                                f"- Khách hàng nhập: {buyer_name}\n"
                                f"- Số lượng: {total_count} đơn\n"
                                f"- Tổng tiền: {total_amount:,} ₫", 
                                "success"
                            )
                            page.wait_for_timeout(10000)  # Đợi 10 giây để modal xuất VAT hoàn tất

                        else:
                            logger.log(f"⚠️ PTTT '{pttt_name}' của chi nhánh '{store_name}' không có hóa đơn nào thỏa mãn điều kiện.", "warning")
            
            
            logger.log("🏁 Đã chạy xong toàn bộ danh sách chi nhánh và phương thức thanh toán cấu hình!", "success")
            page.wait_for_timeout(5000)
            return True
            
        except Exception as e:
            logger.log(f"❌ Gặp lỗi khi tải trang hoặc điều hướng báo cáo VAT: {str(e)}", "error")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    # Khối chạy thử nghiệm thủ công
    run_vat_sync_report_task()