# File Route: tasks/vat_sync/helpers/loop_through_report_pages.py

import os
from modules.discord_logger import DiscordLogger
from tasks.vat_sync import selectors
from tasks.vat_sync.helpers.get_max_pages import get_max_pages

logger = DiscordLogger()

def loop_through_report_pages(page):
    """
    Vòng lặp duyệt qua từng trang báo cáo và in tiến trình.
    """
    max_pages = get_max_pages(page)
    
    for current_page in range(1, max_pages + 1):
        print(f"📄 Đang xử lý trang dữ liệu: {current_page} / {max_pages}")
        logger.log(f"🔎 Đang duyệt kiểm tra dữ liệu tại Trang {current_page}...", "info")
        
        if current_page > 1:
            # Tìm nút bấm link tương ứng với số trang kế tiếp
            next_page_btn = page.locator(selectors.PAGINATION_ITEMS).get_by_role("link", name=str(current_page), exact=True)
            if next_page_btn.count() > 0:
                next_page_btn.click()
                page.wait_for_timeout(2000) # Chờ dữ liệu bảng tải xong
            else:
                logger.log(f"⚠️ Không tìm thấy nút bấm chuyển sang trang {current_page}", "warning")
                break
                
        # --- Thực hiện bóc tách dữ liệu hoặc xử lý của trang hiện tại ở đây ---
        # Ví dụ: cào dữ liệu bảng hóa đơn...
        
    logger.log(f"🎉 Đã hoàn thành duyệt qua tất cả {max_pages} trang dữ liệu!", "success")