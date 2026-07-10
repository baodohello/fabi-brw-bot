import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from modules.discord_logger import DiscordLogger

load_dotenv()

USER = os.getenv("FABI_USERNAME", "brwcoffee2021@gmail.com")
PASSWORD = os.getenv("FABI_PASSWORD")
SESSION_FILE = "fabi_auth_state.json"

logger = DiscordLogger()

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
            
            page.wait_for_url("**/dashboard**", timeout=10000)
            logger.log("Đăng nhập thành công vào hệ thống quản trị iPOS!", "success")
            
            context.storage_state(path=SESSION_FILE)
            logger.log(f"Đã đóng gói và lưu phiên làm việc mới vào '{SESSION_FILE}'", "success")
            browser.close()
            return True
        except Exception as e:
            logger.log(f"Tự động đăng nhập thất bại hoặc sai thông tin: {str(e)}", "error")
            browser.close()
            return False

def ensure_valid_session(force_refresh=False):
    """
    Đảm bảo có session hợp lệ trước khi thao tác.
    Nếu force_refresh=True hoặc không thấy file session, tiến hành login lại.
    """
    if force_refresh and os.path.exists(SESSION_FILE):
        logger.log("🔄 Đang xóa phiên cũ theo yêu cầu làm mới...", "warning")
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass

    if not os.path.exists(SESSION_FILE):
        logger.log("Không tìm thấy file session. Tiến hành đăng nhập tạo mới...", "warning")
        return auto_login_and_save_session()
        
    return True