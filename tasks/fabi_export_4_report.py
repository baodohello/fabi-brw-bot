"""Tác vụ tự động đổi số tài khoản ngân hàng hiển thị trên iPOS FABI theo khung giờ ca làm việc."""

import os
import time
import schedule
from datetime import datetime ,   timedelta
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from config import  VN_TZ
from modules.discord_logger import DiscordLogger
from modules.fabi_auth import SESSION_FILE, ensure_valid_session 

load_dotenv()
logger = DiscordLogger()

TARGET_DATE = datetime.now(VN_TZ) - timedelta(days=1)  # Mặc định là ngày hôm qua
FILE_DOWNLOAD_DIR = "./downloads"

def get_date_formats(date = TARGET_DATE) -> dict[str, str]:

   

    single_date = date.strftime("%d/%m/%Y")          # e.g., "26/11/2026"
    range_date = f"{single_date} - {single_date}"         # e.g., "26/11/2026 - 26/11/2026"
    prefix = date.strftime("%Y%m%d")                 # e.g., "20261126"

    return {
        "single": single_date,
        "range": range_date,
        "prefix": prefix,
    }


def update_target_date(page, date_value = None):
    """Cập nhật giá trị ngày trên input date picker."""
    if date_value is None:
        date_value = get_date_formats()["range"]  # Mặc định là ngày hôm qua

    date_input = page.locator(
        'input[placeholder*="Chọn thời gian" i], input[placeholder*="chon thoi gian" i]'
    ).first
    date_input.wait_for(state="visible", timeout=15000)

    # Set value via native setter and dispatch input/change events
    date_input.evaluate(
        """(el, val) => {
            el.removeAttribute("readonly");
            el.focus();
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            setter.call(el, val);
            el.dispatchEvent(new Event("input", { bubbles: true }));
            el.dispatchEvent(new Event("change", { bubbles: true }));
        }""",
        date_value,
    )

def update_target_store(page, store_name):
    store_picker = page.locator('div[role="button"][aria-label="Chọn cửa hàng"]').first
    store_picker.wait_for(state="visible", timeout=10000)
    store_picker.click()
    page.wait_for_timeout(1000)  # Chờ menu dropdown hiển thị
    target_store_option = page.locator(f'div:has-text("{store_name}")').last
    target_store_option.wait_for(state="visible", timeout=10000)
    target_store_option.click()



def perform_download(page,file_download_dir=FILE_DOWNLOAD_DIR, file_name_prefix=None):
    """Click nút xuất báo cáo và chờ sự kiện download."""
    if file_name_prefix is None:
        file_name_prefix = get_date_formats()["prefix"]

    export_btn = page.locator('button:has-text("Xuất báo cáo"), button:has-text("Tiện ích")').first
    export_btn.wait_for(state="visible", timeout=15000)
    export_btn.click()
    page.wait_for_timeout(1000)  # Chờ menu dropdown hiển thị
    export_all_stores = page.locator("a:has-text('Xuất báo cáo tất cả cửa hàng') , a:has-text('Xuất hoá đơn')").first
    export_all_stores.wait_for(state="visible", timeout=10000)

    downloaded_files = []
    page.on("download", lambda d: downloaded_files.append(d))
    export_all_stores.click()

    # Chờ 5 giây để các sự kiện download được kích hoạt
    page.wait_for_timeout(5000)

    for d in downloaded_files:
        print(f"Download event fired: {d.suggested_filename}, URL: {d.url}")
        target_path = f"{file_download_dir}/{file_name_prefix}_{d.suggested_filename}"
        d.save_as(target_path)
        print("Saved:", target_path)

    if not downloaded_files:
        print("No browser download event fired within 5s—check UI notifications or async export queue.")

def export_4_report():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()

        try:
            page.goto("https://fabi.ipos.vn/report/revenue/revenue/shift")
            update_target_date(page)
            perform_download(page)
            page.wait_for_timeout(3000)

            page.goto("https://fabi.ipos.vn/report/accounting/revenue/cash-in-cash-out")
            update_target_date(page)
            perform_download(page)
            page.wait_for_timeout(3000)

            page.goto("https://fabi.ipos.vn/report/revenue/invoices/sale-by-date")
            update_target_date(page)
            update_target_store(page, "BR-W Trung Kính")
            perform_download(page, file_name_prefix=f"{get_date_formats()['prefix']}_TK")
            page.wait_for_timeout(3000)
            update_target_store(page, "BR-W Dong Da")
            perform_download(page, file_name_prefix=f"{get_date_formats()['prefix']}_HK")
            page.wait_for_timeout(3000)

            browser.close()
            return True

        except Exception as e:
            logger.log(f"❌ Lỗi khi truy cập trang báo cáo: {e}", "error")
            browser.close()
            return False

def main():
   ensure_valid_session(force_refresh=True)  # Kiểm tra session trước khi chạy

   export_4_report()

if __name__ == "__main__":
    logger.log("🤖 FABI 4 REPORT đã khởi động chế độ trực chiến 24/7...", "info")
    schedule.every().day.at("06:00").do(main)
    # main()


    print("⏳ Đang chạy ngầm, hệ thống sẽ tự nổ máy khi đến khung giờ hẹn...")
    while True:
        schedule.run_pending()
        time.sleep(10)