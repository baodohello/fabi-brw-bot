"""Chọn bộ lọc trên trang hóa đơn máy tính tiền MeInvoice."""

from tasks.invoice_validator import selectors


def select_filter(
    page,
    period: str = "Hôm nay",
    publish_status: str = "Chưa phát hành",
    buyer_prefix: str = "3",
) -> bool:
    """
    Mở popup bộ lọc, chọn Kỳ (Hôm nay), Trạng thái phát hành (Chưa phát hành),
    áp dụng, sau đó lọc cột Người mua hàng theo buyer_prefix.

    :param page: Playwright Page object
    :param period: Tên tùy chọn trong dropdown Kỳ (mặc định: "Hôm nay")
    :param publish_status: Tên tùy chọn trong dropdown Trạng thái phát hành
    :param buyer_prefix: Tiền tố lọc cột Người mua hàng (mặc định: "3")
    :return: True nếu thành công, False nếu thất bại
    """
    try:
        # 1. Mở popup bộ lọc
        print("🔍 Đang mở popup bộ lọc...", "info")
        filter_btn = page.locator(selectors.BTN_FILTER_TOGGLE)
        filter_btn.wait_for(state="visible", timeout=5000)
        filter_btn.click()
        page.wait_for_timeout(500)

        # 2. Chọn Kỳ = "Hôm nay" qua custom combobox input
        print(f"📅 Đang chọn Kỳ: '{period}'...", "info")
        period_input = page.locator(selectors.FILTER_PERIOD_INPUT)
        period_input.click()
        period_input.fill("")
        period_input.fill(period)
        page.wait_for_timeout(500)
        # Chọn option từ autocomplete dropdown
        autocomplete_option = page.locator(selectors.AUTOCOMPLETE_ITEM).filter(has_text=period)
        autocomplete_option.click()
        page.wait_for_timeout(300)
        print(f"✅ Đã chọn Kỳ '{period}'.", "success")

        # 3. Chọn Trạng thái phát hành = "Chưa phát hành" qua custom combobox input
        print(f"📋 Đang chọn Trạng thái phát hành: '{publish_status}'...", "info")
        status_input = page.locator(selectors.FILTER_PUBLISH_STATUS_INPUT)
        status_input.click()
        status_input.fill("")
        status_input.fill(publish_status)
        page.wait_for_timeout(500)
        autocomplete_option = page.locator(selectors.AUTOCOMPLETE_ITEM).filter(has_text=publish_status)
        autocomplete_option.click()
        page.wait_for_timeout(300)
        print(f"✅ Đã chọn Trạng thái phát hành '{publish_status}'.", "success")

        # 4. Bấm nút Áp dụng
        print("🔄 Đang áp dụng bộ lọc...", "info")
        apply_btn = page.locator(selectors.BTN_APPLY_FILTER)
        apply_btn.click()
        page.wait_for_timeout(2000)  # Chờ dữ liệu tải lại
        print("✅ Đã áp dụng bộ lọc thành công.", "success")

        # Lọc thêm cột Người mua hàng
        return filter_by_buyer_name(page, buyer_prefix)

    except Exception as e:
        print(f"❌ Thao tác chọn bộ lọc thất bại: {str(e)}", "error")
        return False


def filter_by_buyer_name(page, buyer_prefix: str = "3") -> bool:
    """
    Lọc cột "Người mua hàng" theo giá trị chứa prefix.
    Ghi trực tiếp vào input và bấm nút (popup đã có trong DOM).

    :param page: Playwright Page object
    :param buyer_prefix: Giá trị lọc (mặc định "3")
    :return: True nếu thành công
    """
    try:
        print(f"🔍 Đang lọc cột Người mua hàng chứa '{buyer_prefix}'...", "info")

        # Hover vào text "Người mua hàng" để icon hiện ra, rồi click icon
        header_text = page.locator(".dataTables_scrollHeadInner th[data-field='ContactName'] span")
        header_text.hover()
        page.wait_for_timeout(300)

        filter_icon = page.locator(".dataTables_scrollHeadInner th[data-field='ContactName'] .grid-filter-display")
        filter_icon.click()
        page.wait_for_timeout(500)

        filter_input = page.locator(selectors.COL_FILTER_CONTACT_NAME_INPUT)
        filter_input.fill(buyer_prefix)
        page.wait_for_timeout(200)

        ok_btn = page.locator(selectors.COL_FILTER_BTN_OK)
        ok_btn.click()
        page.wait_for_timeout(1000)

        print(f"✅ Đã lọc Người mua hàng chứa '{buyer_prefix}'.", "success")
        return True

    except Exception as e:
        print(f"❌ Lọc Người mua hàng thất bại: {str(e)}", "error")
        return False
