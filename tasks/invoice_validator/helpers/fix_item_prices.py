"""Kiểm tra & sửa đơn giá trên bảng chi tiết mặt hàng trong form sửa hóa đơn MeInvoice."""

from tasks.invoice_validator import selectors


def fix_item_prices(page, invoice_code: str = "") -> dict:
    """
    Kiểm tra từng dòng mặt hàng: Đơn giá × Số lượng có khớp Thành tiền không.
    Nếu sai, click vào ô Đơn giá và sửa đúng giá.

    :return: dict {"fixed_count": int, "total_amount": float}
    """
    fixed_count = 0
    total_amount = 0.0

    try:
        item_rows = page.locator(selectors.DETAIL_GRID_ROWS).all()

        if not item_rows:
            print("  ⚠️ Không tìm thấy dòng mặt hàng nào.", "warning")
            return {"fixed_count": 0, "total_amount": 0.0}

        for idx, item_row in enumerate(item_rows, start=1):
            try:
                desc = item_row.locator(selectors.DETAIL_GRID_DESCRIPTION).inner_text().strip()
                qty_str = item_row.locator(selectors.DETAIL_GRID_QUANTITY).inner_text().strip()
                price_str = item_row.locator(selectors.DETAIL_GRID_UNIT_PRICE).inner_text().strip()
                amount_str = item_row.locator(selectors.DETAIL_GRID_AMOUNT).inner_text().strip()

                # Parse số: "1,00" → 1.0, "48.148,00" → 48148.0
                qty = float(qty_str.replace(".", "").replace(",", "."))
                price = float(price_str.replace(".", "").replace(",", "."))
                amount = float(amount_str.replace(".", "").replace(",", "."))

                expected_amount = round(qty * price, 2)

                if abs(amount - expected_amount) < 0.01:
                    print(f"    ✅ Dòng {idx} ({desc}): {qty} × {price:,.0f} = {amount:,.0f} — KHỚP.", "info")
                else:
                    # Sai khớp → sửa Đơn giá
                    correct_price = amount / qty if qty != 0 else 0
                    print(f"    ⚠️ Dòng {idx} ({desc}): {qty} × {price:,.0f} ≠ {amount:,.0f} → SỬA Đơn giá thành {correct_price:,.0f}", "warning")

                    # Click vào ô Đơn giá để kích hoạt editor
                    price_cell = item_row.locator(selectors.DETAIL_GRID_UNIT_PRICE)
                    price_cell.scroll_into_view_if_needed()
                    price_cell.click(force=True, no_wait_after=True)
                    page.wait_for_timeout(800)

                    # Fill giá đúng
                    editor = page.locator(selectors.EDITOR_UNIT_PRICE)
                    editor.fill(str(int(correct_price)))
                    page.wait_for_timeout(300)

                    editor.press("Enter")
                    page.wait_for_timeout(500)

                    print(f"    ✅ Dòng {idx}: Đã sửa Đơn giá → {correct_price:,.0f}", "success")
                    fixed_count += 1

                total_amount += amount

            except Exception as e:
                print(f"    ❌ Lỗi kiểm tra dòng {idx}: {str(e)}", "error")

        total_items = len(item_rows)
        if fixed_count == 0:
            print(f"  ✅ Tất cả {total_items} dòng mặt hàng khớp đơn giá × số lượng.", "success")
        else:
            print(f"  🔧 Đã sửa {fixed_count}/{total_items} dòng bị sai đơn giá.", "warning")

        print(f"  💰 Tổng Thành tiền: {total_amount:,.0f} ₫", "info")

    except Exception as e:
        print(f"  ❌ Lỗi duyệt bảng mặt hàng: {str(e)}", "error")

    return {"fixed_count": fixed_count, "total_amount": total_amount}
