import os
import sys
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from vat_config import STORES_SETTING 

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
            tab_locator.wait_for(state="visible", timeout=500)
            tab_locator.click(force=True)
            print(f"🎉 Đã chuyển thành công sang tab '{selectors.TAB_CHUA_XUAT_VAT}'.", "success")
            helpers.select_date_filter(page, "Hôm nay")   
            print(f"🎉 Đã áp dụng bộ lọc ngày 'Hôm nay' thành công.", "success")             


           # =========================================================================
            # 2. Xử lý dữ liệu cho chi nhánh 
            # =========================================================================
            # Giả định biến `setting` đã được khai báo như cấu trúc của bạn
            setting = STORES_SETTING  # Lấy cấu hình từ file config.py
            # --- VÒNG LẶP CHÍNH CỦA BOT ---
            # 1. Duyệt qua từng chi nhánh (Store)
            for store_name, pttt_configs in setting.items():
                print(f"==================================================", "info")
                logger.log(f"🚀 Bắt đầu xử lý chi nhánh: {store_name}", "info")
                
                # Thực hiện filter chọn Chi nhánh trên UI
                if helpers.select_store_filter(page, store_name):
                    logger.log(f"🎉 Đã chọn chi nhánh '{store_name}' thành công.", "success")
                    
                    # 2. Duyệt qua từng phương thức thanh toán (PTTT) có trong chi nhánh đó
                    for pttt_name, config in pttt_configs.items():
                        print(f"--------------------------------------------------", "info")
                        print(f"🔍 Đang xử lý PTTT: {pttt_name} của {store_name}", "info")
                        
                        # Đọc động cấu hình từ JSON cho PTTT hiện tại
                        buyer_name = config["buyer_name"]
                        start_time = config["start_time"]
                        end_time = config["end_time"]
                        
                        # Thực hiện filter chọn PTTT trên UI
                        if helpers.select_pttt_filter(page, pttt_name):
                            logger.log(f"🎉 Đã chọn phương thức thanh toán '{pttt_name}' thành công.", "success")
                            
                            # Chờ bảng dữ liệu tải lại ứng với bộ lọc mới
                            page.wait_for_timeout(3000) 
                            print(f"--- Bắt đầu quét hóa đơn [{start_time} - {end_time}] ---", "info")
                            
                            # Truyền dynamic tham số thời gian vào hàm xử lý
                            invoice_summary = helpers.process_and_tick_invoices(
                                page, 
                                start_time=start_time, 
                                end_time=end_time
                            )
                            
                            total_count = invoice_summary["total_processed_count"]
                            total_amount = invoice_summary["total_processed_amount"]

                            # Nếu có hóa đơn hợp lệ thì tiến hành xuất chi tiết
                            if total_count > 0:
                                # Truyền dynamic buyer_name tương ứng vào đây
                                helpers.export_vat_details(page, buyer_name=buyer_name, total_count=total_count)
                                
                                logger.log(
                                    f"🎉 Hoàn tất báo cáo VAT cho '{store_name}' - PTTT '{pttt_name}'.\n"
                                    f"- Khách hàng nhập: {buyer_name}\n"
                                    f"- Số lượng tích: {total_count} đơn\n"
                                    f"- Tổng tiền: {total_amount:,} ₫", 
                                    "success"
                                )
                            else:
                                print(f"⚠️ PTTT '{pttt_name}' của chi nhánh '{store_name}' không có hóa đơn nào thỏa mãn điều kiện.", "warning")
                        else:
                            logger.log(f"❌ Không thể chọn bộ lọc PTTT '{pttt_name}' trên giao diện.", "error")
                else:
                    logger.log(f"❌ Không thể chọn bộ lọc chi nhánh '{store_name}' trên giao diện.", "error")

            print("==================================================", "success")
            logger.log("🏁 Đã chạy xong toàn bộ danh sách chi nhánh và phương thức thanh toán cấu hình!", "success")
            page.wait_for_timeout(10000)
            return True
            
        except Exception as e:
            logger.log(f"❌ Gặp lỗi khi tải trang hoặc điều hướng báo cáo VAT: {str(e)}", "error")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    # Khối chạy thử nghiệm thủ công
    run_vat_sync_report_task()