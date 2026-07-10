# File Route: tasks/vat_sync/helpers/select_store_filter.py

import os
from tasks.vat_sync import selectors


def select_store_filter(page, store_name: str) -> bool:
    """
    Mở bộ lọc điểm áp dụng và chọn cửa hàng theo tên cấu hình.
    """
    try:
        print(f"Đang mở danh sách chọn điểm áp dụng để tìm '{store_name}'...", "info")
        
        # 1. Tìm và click mở dropdown wrapper từ selector dùng chung
        dropdown_trigger = page.locator(selectors.DROPDOWN_STORES_FILTER)
        dropdown_trigger.wait_for(state="visible", timeout=500)
        dropdown_trigger.click()
        
        # Đợi hiệu ứng animation đổ danh sách xuống hoàn tất
        page.wait_for_timeout(500) 
        print(f"Đang tìm và bấm chọn điểm áp dụng: {store_name}...", "info")
        
        # 2. Lọc chính xác phần tử cửa hàng trong danh sách xổ xuống
        store_option = page.locator(selectors.DROPDOWN_STORE_ITEMS).filter(has_text=store_name)
        store_option.wait_for(state="visible", timeout=500)
        store_option.click(force=True)
        
        page.wait_for_timeout(500) 
        print(f"🎉 Đã chọn điểm áp dụng '{store_name}' thành công.", "success")
        return True
    except Exception as e:
        print(f"❌ Thao tác chọn điểm áp dụng '{store_name}' thất bại: {str(e)}", "error")
        return False