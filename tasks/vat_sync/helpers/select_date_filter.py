# File Route: tasks/vat_sync/helpers/select_date_filter.py

import os
from tasks.vat_sync import selectors


def select_date_filter(page, date_range_name: str = "Hôm nay") -> bool:
    """
    Mở bộ chọn khoảng ngày (Daterange picker) và bấm chọn phím tắt theo tham số truyền vào.
    Các giá trị mặc định có sẵn trên giao diện: "Hôm nay", "Hôm qua", "7 ngày trước", "Tháng này", "Tháng trước"
    """
    try:
        print(f"Đang mở bộ chọn khoảng thời gian báo cáo VAT để tìm '{date_range_name}'...", "info")
        
        # 1. Tìm và click mở wrapper hiển thị ngày
        date_trigger = page.locator(selectors.DATE_FILTER_TRIGGER)
        date_trigger.wait_for(state="visible", timeout=500)
        date_trigger.click()
        
        # Đợi danh sách các nút shortcut đổ xuống ổn định
        page.wait_for_timeout(500)
        
        print(f"Đang bấm chọn phím tắt ngày: '{date_range_name}'...", "info")
        
        # 2. Định vị thẻ <li> chứa text được truyền từ tham số trong daterangepicker
        date_option = page.locator(selectors.DATE_FILTER_OPTIONS).filter(has_text=date_range_name)
        date_option.wait_for(state="visible", timeout=500)
        date_option.click(force=True)
        
        # Đợi hệ thống tải lại/render dữ liệu theo ngày mới chọn
        page.wait_for_timeout(500)
        print(f"🎉 Đã áp dụng bộ lọc ngày '{date_range_name}' thành công.", "success")
        return True
    except Exception as e:
        print(f"❌ Thao tác chọn bộ lọc ngày '{date_range_name}' thất bại: {str(e)}", "error")
        return False