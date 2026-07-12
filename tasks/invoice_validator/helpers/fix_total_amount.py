"""Kiểm tra & cân đối: tổng các dòng Thành tiền + Tiền thuế GTGT = Tổng tiền thanh toán."""

from tasks.invoice_validator import selectors


def fix_total_amount(page, items_total: float, invoice_code: str = "") -> float:
    """
    Kiểm tra: tổng các dòng Thành tiền + Tiền thuế GTGT có khớp Tổng tiền thanh toán.
    Nếu lệch, sửa Thành tiền dòng đầu tiên để cân đối.

    :param page: Playwright Page object
    :param items_total: Tổng Thành tiền từ các dòng mặt hàng
    :param invoice_code: Mã hóa đơn để log
    :return: Tổng Thành tiền mới (sau khi cân đối, nếu có)
    """
    try:
        total_input = page.locator(selectors.DETAIL_TOTAL_AMOUNT)
        vat_input = page.locator(selectors.DETAIL_TOTAL_VAT)

        if total_input.count() == 0:
            print("  ⚠️ Không tìm thấy ô Tổng tiền thanh toán — bỏ qua kiểm tra.", "warning")
            return items_total

        # Đọc Tổng tiền thanh toán & Tiền thuế GTGT (giá trị nằm trong title)
        total_str = total_input.input_value() 
        vat_str = vat_input.input_value() 
        invoice_total = float(total_str.replace(".", "").replace(",", "."))
        vat = float(vat_str.replace(".", "").replace(",", "."))

        # Công thức: items_total + VAT = TotalAmount
        expected_items_total = round(invoice_total - vat, 2)
        diff = round(expected_items_total - items_total, 2)

        if abs(diff) < 0.01:
            print(f"  ✅ {items_total:,.0f} + {vat:,.0f} = {invoice_total:,.0f} — KHỚP.", "success")
            return items_total

        # Lệch → sửa Thành tiền dòng đầu tiên
        print(f"  ⚠️ {items_total:,.0f} + {vat:,.0f} ≠ {invoice_total:,.0f}. Chênh: {diff:,.0f} ₫", "warning")

        first_row = page.locator(selectors.DETAIL_GRID_ROWS).first
        current_amount_str = first_row.locator(selectors.DETAIL_GRID_AMOUNT).inner_text().strip()
        current_amount = float(current_amount_str.replace(".", "").replace(",", "."))
        new_amount = current_amount + diff

        print(f"  🔧 Sửa Thành tiền dòng 1: {current_amount:,.0f} → {new_amount:,.0f}", "warning")

        # Click ô Thành tiền dòng 1 để mở editor
        amount_cell = first_row.locator(selectors.DETAIL_GRID_AMOUNT)
        amount_cell.scroll_into_view_if_needed()
        amount_cell.click(force=True, no_wait_after=True)
        page.wait_for_timeout(800)
        page.wait_for_timeout(500)

        # Debug: in HTML của cell sau khi click
        # cell_html = first_row.locator(selectors.DETAIL_GRID_AMOUNT).evaluate("el => el.outerHTML")
        # cell_inner = first_row.locator(selectors.DETAIL_GRID_AMOUNT).evaluate("el => el.innerHTML")
        # print(f"  🔍 DEBUG td:nth-child(7) outerHTML: {cell_html[:300]}", "info")
        # print(f"  🔍 DEBUG td:nth-child(7) innerHTML: {cell_inner[:300]}", "info")

        editor = page.locator(selectors.EDITOR_AMOUNT)
        editor.fill("")
        editor.fill(str(int(new_amount)))
        page.wait_for_timeout(300)

        editor.press("Enter")
        page.wait_for_timeout(500)

        new_total = items_total + diff
        print(f"  ✅ Đã cân đối: {new_total:,.0f} + {vat:,.0f} = {new_total + vat:,.0f} ₫", "success")
        return new_total

    except Exception as e:
        print(f"  ❌ Lỗi cân đối tổng tiền: {str(e)}", "error")
        return items_total
