"""Sửa Họ tên người mua trên form chi tiết hóa đơn MeInvoice dựa vào prefix."""

from tasks.invoice_validator import selectors
from config.invoice_validator import BUYER_NAME_MAP, BUYER_NAME_DEFAULT


def fix_buyer_name(page, invoice_code: str = "") -> bool:
    """
    Đọc giá trị Họ tên người mua, tra BUYER_NAME_MAP theo ký tự đầu tiên.
    Nếu không khớp → dùng BUYER_NAME_DEFAULT.

    :return: True nếu đã sửa thành công
    """
    try:
        buyer_input = page.locator(selectors.DETAIL_BUYER_NAME_INPUT)
        buyer_input.wait_for(state="visible", timeout=10000)

        current_value = buyer_input.input_value().strip()

        # Lấy ký tự đầu tiên làm prefix
        prefix = current_value[0] if current_value else ""
        new_name = BUYER_NAME_MAP.get(prefix, BUYER_NAME_DEFAULT)

        if invoice_code:
            print(f"  🔄 Hóa đơn {invoice_code}: '{current_value}' → '{new_name}'", "info")
        buyer_input.fill("")
        buyer_input.fill(new_name)
        page.wait_for_timeout(300)
        print(f"  ✅ Đã cập nhật Họ tên người mua thành '{new_name}'.", "success")
        return True

    except Exception as e:
        print(f"  ❌ Lỗi sửa Họ tên người mua: {str(e)}", "error")
        return False
