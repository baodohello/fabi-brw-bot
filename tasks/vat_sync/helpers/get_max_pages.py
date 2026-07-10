# File Route: tasks/vat_sync/helpers/get_max_pages.py

import os
from modules.discord_logger import DiscordLogger
from tasks.vat_sync import selectors

logger = DiscordLogger()

def get_max_pages(page) -> int:
    """
    Tìm số trang tối đa từ thanh điều hướng phân trang.
    """
    try:
        pagination_locator = page.locator(selectors.PAGINATION_ITEMS)
        pagination_locator.first.wait_for(state="visible", timeout=5000)
        
        # Thu thập dữ liệu text từ các nút phân trang
        page_elements = pagination_locator.all_inner_texts()
        page_numbers = [int(x.strip()) for x in page_elements if x.strip().isdigit()]
        
        if page_numbers:
            max_page = max(page_numbers)
            print(f"📋 Hệ thống phát hiện tổng cộng {max_page} trang dữ liệu.", "info")
            return max_page
        return 1
    except Exception as e:
        print(f"⚠️ Không tìm thấy thanh phân trang hoặc lỗi parse (Mặc định là 1 trang): {str(e)}", "warning")
        return 1