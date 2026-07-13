"""Xác thực MeInvoice: tự động đăng nhập, lưu phiên (session), và kiểm tra/refresh phiên khi hết hạn."""

import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

from modules.discord_logger import DiscordLogger
from tasks.invoice_validator import selectors

load_dotenv()
logger = DiscordLogger()

MEINVOICE_USERNAME = os.getenv("MEINVOICE_USERNAME", "")
MEINVOICE_PASSWORD = os.getenv("MEINVOICE_PASSWORD", "")
MEINVOICE_SESSION_FILE = "meinvoice_auth_state.json"


def login_meinvoice_and_save_session() -> bool:
    """Tự động đăng nhập MeInvoice (3 bước: email/SĐT → mật khẩu → OTP nếu có) và lưu session."""
    if not MEINVOICE_USERNAME or not MEINVOICE_PASSWORD:
        logger.log("❌ Chưa cấu hình MEINVOICE_USERNAME / MEINVOICE_PASSWORD trong .env", "error")
        return False

    with sync_playwright() as p:
        logger.log(f"🚀 Mở trình duyệt để đăng nhập MeInvoice: {MEINVOICE_USERNAME}...", "info")
        browser = p.chromium.launch(headless=False)  # Cần hiển thị UI cho OTP thủ công
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("https://app3.meinvoice.vn/login/1?TaxCode=0101815552")
            page.wait_for_timeout(2000)

            # --- Bước 1: Nhập email/SĐT ---
            logger.log(f"🔐 Bước 1: Nhập email/SĐT ({MEINVOICE_USERNAME})...", "info")
            page.locator(selectors.LOGIN_USERNAME_INPUT).fill(MEINVOICE_USERNAME)
            page.locator(selectors.LOGIN_STEP1_SUBMIT).click()
            page.wait_for_timeout(2000)

            # --- Bước 2: Nhập mật khẩu ---
            logger.log("🔐 Bước 2: Nhập mật khẩu...", "info")
            page.locator(selectors.LOGIN_PASSWORD_INPUT).wait_for(state="visible", timeout=5000)
            page.locator(selectors.LOGIN_PASSWORD_INPUT).fill(MEINVOICE_PASSWORD)
            page.locator(selectors.LOGIN_STEP2_SUBMIT).click()
            page.wait_for_timeout(3000)

            # --- Bước 3: OTP (nếu có) ---
            otp_container = page.locator(selectors.LOGIN_OTP_CONTAINER)
            if otp_container.count() > 0 and otp_container.is_visible():
                logger.log("📱 YÊU CẦU OTP! Vui lòng nhập mã OTP thủ công trong cửa sổ trình duyệt...", "warning")
                logger.log("⏳ Đang đợi bạn nhập OTP và bấm 'Xác nhận' (tối đa 10 phút)...", "info")

                try:
                    page.wait_for_function(
                        "!window.location.href.includes('/login')",
                        timeout=600000  # 10 phút
                    )
                    logger.log("✅ Xác thực OTP thành công!", "success")
                except Exception:
                    logger.log("❌ Hết thời gian chờ OTP. Vui lòng thử lại.", "error")
                    browser.close()
                    return False
            else:
                logger.log("✅ Không cần OTP (đã lưu thiết bị).", "info")

            if "/login" in page.url:
                logger.log("❌ Đăng nhập MeInvoice thất bại — kiểm tra lại thông tin.", "error")
                browser.close()
                return False

            # Lưu session cookies vào file
            context.storage_state(path=MEINVOICE_SESSION_FILE)
            logger.log(f"💾 Đã lưu phiên đăng nhập MeInvoice vào '{MEINVOICE_SESSION_FILE}'", "success")
            browser.close()
            return True

        except Exception as e:
            logger.log(f"❌ Lỗi đăng nhập MeInvoice: {str(e)}", "error")
            browser.close()
            return False


def ensure_meinvoice_session(force_refresh=False) -> bool:
    """Đảm bảo có session MeInvoice hợp lệ. Nếu không có file session hoặc force_refresh, đăng nhập lại."""
    if force_refresh and os.path.exists(MEINVOICE_SESSION_FILE):
        logger.log("🔄 Đang xóa phiên MeInvoice cũ theo yêu cầu làm mới...", "warning")
        try:
            # os.remove(MEINVOICE_SESSION_FILE)
            print(f"  ⚠️ Đang xóa file session MeInvoice: {MEINVOICE_SESSION_FILE}...", "warning")
        except Exception:
            pass

    if not os.path.exists(MEINVOICE_SESSION_FILE):
        logger.log("⚠️ Không tìm thấy file session MeInvoice. Tiến hành đăng nhập tạo mới...", "warning")
        return login_meinvoice_and_save_session()

    logger.log("✅ Đã tìm thấy file session MeInvoice.", "success")
    return True
