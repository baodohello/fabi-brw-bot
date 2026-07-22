"""Tác vụ chính: đăng nhập MeInvoice, duyệt danh sách hóa đơn máy tính tiền và xác thực."""

import os
import sys
from playwright.sync_api import sync_playwright

# Auto-adjust Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from modules.discord_logger import DiscordLogger
from tasks.invoice_validator.helpers.auth import (
    MEINVOICE_SESSION_FILE,
    ensure_meinvoice_session,
    auto_login_on_page,
)
from tasks.invoice_validator.helpers import select_filter, process_invoice_rows
from config.invoice_validator import BUYER_PREFIXES

logger = DiscordLogger()


def run_invoice_validator_task() -> bool:
    """
    Tác vụ chính: Duyệt danh sách hóa đơn máy tính tiền trên MeInvoice,
    kiểm tra trạng thái và xác thực các hóa đơn cần thiết.

    :return: True nếu thành công, False nếu thất bại
    """
    logger.log("📋 Bắt đầu tiến trình kiểm tra & xác thực hóa đơn MeInvoice...", "info")

    # Kiểm tra session trước khi mở trình duyệt
    if not ensure_meinvoice_session():
        logger.log("❌ Không thể xác thực phiên MeInvoice. Hủy tác vụ.", "error")
        return False

    with sync_playwright() as p:
        logger.log("🚀 Khởi động trình duyệt với session MeInvoice đã lưu...", "info")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=MEINVOICE_SESSION_FILE)
        page = context.new_page()

        try:
            # Điều hướng đến trang hóa đơn máy tính tiền
            page.goto("https://app3.meinvoice.vn/v3/hoa-don-may-tinh-tien")
            page.wait_for_timeout(1000)

            # Kiểm tra nếu session hết hạn → tự động điền mật khẩu và tiếp tục
            if "/login" in page.url:
                logger.log("🔄 Session MeInvoice hết hạn. Tự động đăng nhập lại...", "warning")
                if not auto_login_on_page(page, context):
                    logger.log("❌ Tự động đăng nhập thất bại.", "error")
                    browser.close()
                    return False
                # Đăng nhập xong → điều hướng lại trang hóa đơn
                page.goto("https://app3.meinvoice.vn/v3/hoa-don-may-tinh-tien")
                page.wait_for_timeout(2000)

            logger.log(f"✅ Truy cập thành công MeInvoice! URL: {page.url}", "success")

            total_processed = 0
            for prefix in BUYER_PREFIXES:
                logger.log(f"🔍 Bắt đầu xử lý tiền tố '{prefix}'...", "info")

                # Áp dụng bộ lọc: Hôm nay + Chưa phát hành + lọc theo prefix
                if not select_filter(page, buyer_prefix=prefix):
                    logger.log(f"❌ Không thể áp dụng bộ lọc cho prefix '{prefix}'. Bỏ qua.", "error")
                    continue

                page.wait_for_timeout(2000)

                # Duyệt từng dòng hóa đơn và bấm "Sửa"
                count = process_invoice_rows(page)
                total_processed += count
                logger.log(f"✅ Đã xử lý {count} hóa đơn với prefix '{prefix}'.", "success")

            logger.log(f"🎉 Hoàn tất! Tổng cộng đã xử lý {total_processed} hóa đơn.", "success")
            return True

        except Exception as e:
            logger.log(f"❌ Lỗi khi chạy tác vụ MeInvoice: {str(e)}", "error")
            return False

        finally:
            browser.close()


# Cho phép chạy trực tiếp: python -m tasks.invoice_validator.main
if __name__ == "__main__":
    run_invoice_validator_task()
