"""Cấu hình cho tác vụ xác thực hóa đơn MeInvoice."""

# Ánh xạ tiền tố Họ tên người mua → tên hiển thị trên hóa đơn
BUYER_NAME_MAP = {
    "3": "Bán cho người tiêu dùng BRW2",
    "4": "Bán cho người tiêu dùng BRW1",
}

# Mặc định nếu không khớp tiền tố nào
BUYER_NAME_DEFAULT = "Bán cho người tiêu dùng"

# Danh sách tiền tố cần xử lý (theo thứ tự)
BUYER_PREFIXES = ["3", "4"]
