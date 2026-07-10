"""
Quản lý tập trung tất cả các Selectors (Bộ định vị UI) cho tính năng báo cáo hóa đơn VAT.
"""
# Tên các thành phần giao diện cố định
TAB_CHUA_XUAT_VAT = "Hóa đơn chưa xuất VAT"
# --- THÊM SELECTOR CHO BỘ LỌC KHOẢNG NGÀY (DATE RANGE) ---
DATE_FILTER_TRIGGER = ".report-date-range-picker .reportrange-text"
DATE_FILTER_OPTIONS = ".daterangepicker .ranges li"

# Selector bộ lọc điểm áp dụng (Cửa hàng)
DROPDOWN_STORES_FILTER = ".select-store-filter .select-on-list"
DROPDOWN_STORE_ITEMS = "ul.list-group__container li"

# --- THÊM SELECTOR CHO PHƯƠNG THỨC THANH TOÁN (PTTT) ---
# Dùng locator có chứa text mặc định để tìm đúng thẻ div bao ngoài của cụm PTTT
DROPDOWN_PTTT_FILTER = ".kit-select__container:has-text('Tất cả PTTT')"
DROPDOWN_PTTT_ITEMS = "ul.list-group__container li" 


# Selector phân trang dữ liệu
PAGINATION_ITEMS = "ul.pagination li.page-item"


# Cấu trúc bảng hóa đơn VAT dựa trên mã HTML cung cấp
TABLE_ROWS = "table.list-view__table tbody tr.tr-content"
ROW_INVOICE_CODE = "td.sticky-col-33 span"
ROW_TOTAL_AMOUNT = "td:nth-last-child(4)"      # Cột Tổng tiền (tính từ phải qua trái)
ROW_OUT_TIME = "td:nth-last-child(2)"          # Cột Thời gian ra
ROW_CHECKBOX_INPUT = "td.sticky-col-r input[type='checkbox']"
ROW_CHECKBOX_LABEL = "td.sticky-col-r label.custom-control-label"
