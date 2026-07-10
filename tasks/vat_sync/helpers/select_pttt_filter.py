# File Route: tasks/vat_sync/helpers/select_pttt_filter.py

import os
from tasks.vat_sync import selectors


def select_pttt_filter(page, pttt_name: str = "Tất cả PTTT") -> bool:
    """
    Mở bộ lọc Phương thức thanh toán (PTTT) và chọn phương thức mong muốn theo tên cấu hình.
    """
    try:
        print(f"Đang mở danh sách bộ lọc PTTT để tìm '{pttt_name}'...", "info")
        
        # 1. Tìm và click mở dropdown wrapper từ selector dùng chung của PTTT
        dropdown_trigger = page.locator(selectors.DROPDOWN_PTTT_FILTER)
        dropdown_trigger.wait_for(state="visible", timeout=500)
        dropdown_trigger.click()
        
        # Đợi hiệu ứng animation đổ danh sách xuống hoàn tất
        page.wait_for_timeout(500) 
        
        print(f"Đang tìm và bấm chọn phương thức thanh toán: {pttt_name}...", "info")
        
        # 2. Lọc chính xác phần tử PTTT trong danh sách xổ xuống
        pttt_option = page.locator(selectors.DROPDOWN_PTTT_ITEMS).filter(has_text=pttt_name)
        pttt_option.wait_for(state="visible", timeout=500)
        pttt_option.click(force=True)

        page.wait_for_timeout(500)
        print(f"🎉 Đã lọc Phương thức thanh toán '{pttt_name}' thành công.", "success")
        return True
    except Exception as e:
        print(f"❌ Thao tác chọn PTTT '{pttt_name}' thất bại: {str(e)}", "error")
        return False