"""Duyệt và xử lý từng dòng hóa đơn trong bảng MeInvoice."""

from playwright.sync_api import Page

from tasks.invoice_validator import selectors
from tasks.invoice_validator.helpers.fix_buyer_name import fix_buyer_name
from tasks.invoice_validator.helpers.fix_item_prices import fix_item_prices
from tasks.invoice_validator.helpers.fix_total_amount import fix_total_amount


def process_invoice_rows(
    page: Page,
) -> int:
    """
    Duyệt danh sách hóa đơn, xử lý từng dòng một (luôn lấy dòng đầu tiên).
    Sau mỗi lần lưu, load lại bảng vì hóa đơn mới luôn lên đầu.

    :param page: Playwright Page object
    :return: Số lượng hóa đơn đã xử lý
    """
    processed_count = 0

    try:
        page.wait_for_selector(selectors.TABLE_TBODY_ROWS, timeout=10000)

        while True:
            rows = page.locator(selectors.TABLE_TBODY_ROWS).all()
            if not rows:
                print("✅ Không còn hóa đơn nào để xử lý.", "success")
                break

            row = rows[0]  # Luôn lấy dòng đầu tiên
            try:
                invoice_code = row.locator(selectors.ROW_INVOICE_SERIES).inner_text()
                print(f"  [#{processed_count + 1}] Đang xử lý hóa đơn: {invoice_code}", "info")

                # Bấm nút "Sửa"
                edit_btn = row.locator(selectors.ROW_BTN_EDIT)
                edit_btn.evaluate("element => element.click()")
                page.wait_for_timeout(2000)
                print(f"  ✅ Đã click 'Sửa' cho hóa đơn {invoice_code}.", "success")

                # Sửa Họ tên người mua, kiểm tra đơn giá, cân đối tổng tiền
                fix_buyer_name(page, invoice_code)
                page.wait_for_timeout(2000)
                result = fix_item_prices(page, invoice_code)
                final_total = fix_total_amount(page, result["total_amount"], invoice_code)

                # Lưu hóa đơn
                print(f"  💾 Đang lưu hóa đơn {invoice_code}...", "info")
                save_btn = page.locator(selectors.BTN_SAVE)
                save_btn.click()
                page.wait_for_timeout(1000)

                # Bấm "Có" trên popup xác nhận (nếu có)
                popup_btn = page.locator(selectors.POPUP_CONFIRM_BTN_CO)
                if popup_btn.count() > 0:
                    popup_btn.click()
                    print(f"  ✅ Đã bấm 'Có' trên popup xác nhận.", "success")

                # Chờ loading biến mất + bảng load lại
                try:
                    page.wait_for_selector(selectors.LOADING_INDICATOR, state="detached", timeout=10000)
                except Exception:
                    pass
                page.wait_for_timeout(1000)

                print(f"  ✅ Đã lưu hóa đơn {invoice_code}.", "success")
                processed_count += 1

            except Exception as e:
                print(f"  ❌ Lỗi xử lý: {str(e)}", "error")
                break  # Thoát nếu lỗi lặp lại

    except Exception as e:
        print(f"❌ Không thể duyệt bảng hóa đơn: {str(e)}", "error")

    return processed_count
