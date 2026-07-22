# File Route: tasks/vat_sync/helpers/select_filter.py

from tasks.vat_sync import selectors


def select_filter(
        page, 
        date_range_name: str,
        store_name: str,
        pttt_name: str
         ) -> bool:
    """
    Mở bộ chọn khoảng ngày (Daterange picker) và bấm chọn phím tắt theo tham số truyền vào.
    Các giá trị mặc định có sẵn trên giao diện: "Hôm nay", "Hôm qua", "7 ngày trước", "Tháng này", "Tháng trước"
    Mở bộ lọc điểm áp dụng và chọn cửa hàng theo tên cấu hình.
    Mở bộ lọc Phương thức thanh toán (PTTT) và chọn phương thức mong muốn theo tên cấu hình.

    """
    try:
        print(f"Đang mở bộ chọn khoảng thời gian báo cáo VAT để tìm '{date_range_name}'...", "info")
        # 1. Tìm và click mở wrapper hiển thị ngày
        date_trigger = page.locator(selectors.DATE_FILTER_TRIGGER)
        date_trigger.wait_for(state="visible", timeout=300)
        date_trigger.click()
        # Đợi danh sách các nút shortcut đổ xuống ổn định
        page.wait_for_timeout(300)
        print(f"Đang bấm chọn phím tắt ngày: '{date_range_name}'...", "info")
        date_option = page.locator(selectors.DATE_FILTER_OPTIONS).filter(has_text=date_range_name)
        date_option.wait_for(state="visible", timeout=300)
        date_option.click(force=True)
        page.wait_for_timeout(300)
        print(f"🎉 Đã áp dụng bộ lọc ngày '{date_range_name}' thành công.", "success")

        print(f"Đang mở danh sách chọn điểm áp dụng để tìm '{store_name}'...", "info")
        # 1. Tìm và click mở dropdown wrapper từ selector dùng chung
        dropdown_trigger = page.locator(selectors.DROPDOWN_STORES_FILTER)
        dropdown_trigger.wait_for(state="visible", timeout=300)
        dropdown_trigger.click()
        # Đợi hiệu ứng animation đổ danh sách xuống hoàn tất
        page.wait_for_timeout(300) 
        print(f"Đang tìm và bấm chọn điểm áp dụng: {store_name}...", "info")
        # 2. Lọc chính xác phần tử cửa hàng trong danh sách xổ xuống
        store_option = page.locator(selectors.DROPDOWN_STORE_ITEMS).filter(has_text=store_name)
        store_option.wait_for(state="visible", timeout=300)
        store_option.click(force=True)
        page.wait_for_timeout(1000) # Đợi 1 giây để giao diện load lại danh sách hóa đơn theo cửa hàng mới
        print(f"🎉 Đã chọn điểm áp dụng '{store_name}' thành công.", "success")

        print(f"Đang mở danh sách bộ lọc PTTT để tìm '{pttt_name}'...", "info")
        dropdown_trigger = page.locator(selectors.DROPDOWN_PTTT_FILTER).nth(1)  # Lấy dropdown thu 2 (PTTT)
        dropdown_trigger.wait_for(state="visible", timeout=300)
        dropdown_trigger.click()
        # Đợi hiệu ứng animation đổ danh sách xuống hoàn tất
        page.wait_for_timeout(1000) 
        print(f"Đang tìm và bấm chọn phương thức thanh toán: {pttt_name}...", "info")
        pttt_option = page.locator(selectors.DROPDOWN_PTTT_ITEMS).filter(has_text=pttt_name)
        pttt_option.wait_for(state="visible", timeout=300)
        pttt_option.click(force=True)
        page.wait_for_timeout(1000)
        print(f"🎉 Đã lọc Phương thức thanh toán '{pttt_name}' thành công.", "success")
        return True
    except Exception as e:
        print(f"❌ Thao tác chọn bộ lọc thất bại: {str(e)}", "error")
        return False