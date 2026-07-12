"""
Quản lý tập trung tất cả các Selectors (Bộ định vị UI) cho cổng MeInvoice.
"""

# TODO: Xác định selector thực tế sau khi inspect giao diện MeInvoice
# --- LOGIN (https://app3.meinvoice.vn/login/1?TaxCode=0101815552) ---
# Step 1: nhập email/SĐT
LOGIN_USERNAME_INPUT = "#UserName"
LOGIN_STEP1_SUBMIT = "#btnLogin"

# Step 2: nhập mật khẩu (trang /login/2)
LOGIN_PASSWORD_INPUT = "#Password"
LOGIN_STEP2_SUBMIT = "#btnLogin"

# Step 3: OTP (chỉ hiện khi browser mới, checkbox "Không hỏi lại" mặc định được tick)
LOGIN_OTP_CONTAINER = ".activeStep3"
LOGIN_OTP_INPUT = ".value-otp"
LOGIN_OTP_SUBMIT = "#btnActiveAcount"

# --- TRANG HÓA ĐƠN MÁY TÍNH TIỀN ---
# URL: https://app3.meinvoice.vn/v3/hoa-don-may-tinh-tien
TABLE_TBODY_ROWS = "#grdInvoiceCashRegister tbody tr[role='row']"
ROW_INVOICE_SERIES = "td:nth-child(2)"       # Cột "Ký hiệu"
ROW_INVOICE_NUMBER = "td:nth-child(4)"       # Cột "Số hóa đơn"
ROW_PUBLISH_STATUS = "td:nth-child(12)"      # Cột "Phát hành" (trạng thái phát hành)
ROW_BTN_EDIT = "a.action[data-commandname='edit']"  # Nút "Sửa"

# --- FORM CHI TIẾT HÓA ĐƠN (SAInvoice Detail) ---
DETAIL_BUYER_NAME_INPUT = "#select-buyer"  # Họ tên người mua (input name="ContactName")

# Bảng chi tiết mặt hàng trong form sửa hóa đơn
DETAIL_GRID_ROWS = "#grdSAOrderViewDetail tbody tr"
DETAIL_GRID_DESCRIPTION = "td:nth-child(3)"   # Tên hàng hóa
DETAIL_GRID_QUANTITY = "td:nth-child(5)"      # Số lượng
DETAIL_GRID_UNIT_PRICE = "td:nth-child(6)"    # Đơn giá
DETAIL_GRID_AMOUNT = "td:nth-child(7)"        # Thành tiền

# Editor input cho Đơn giá (sau khi click vào cell)
EDITOR_UNIT_PRICE = "#editor-UnitPrice"

# Tổng tiền trong footer form
DETAIL_TOTAL_AMOUNT = "#div-totalamount input[name='TotalAmount']"       # Tổng tiền thanh toán
DETAIL_TOTAL_VAT = ".div-totalvatamount input[name='TotalVATAmount']"   # Tiền thuế GTGT

# Nút Lưu & popup xác nhận
BTN_SAVE = "button[data-command='Save']"
POPUP_CONFIRM_BTN_CO = ".ui-dialog button.blue"       # Nút "Có" trong popup xác nhận
LOADING_INDICATOR = "img[src*='loading.gif']"          # Ảnh loading

# Column filter cho cột "Người mua hàng" (ContactName)
COL_FILTER_CONTACT_NAME_ICON = ".dataTables_scrollHead th[data-field='ContactName'] .grid-filter-display"
COL_FILTER_CONTACT_NAME_INPUT = "#grdInvoiceCashRegister_filter_ContactName_input"
COL_FILTER_BTN_OK = "#grdInvoiceCashRegister_filter_ContactName button[data-command='ok']"

# Tổng tiền hàng trên form chi tiết (trong div-notdetailtotal)
DETAIL_TOTAL_AMOUNT_INPUT = "#div-notdetailtotal input[name='TotalAmount']"

# Editor cho Thành tiền (sau khi click vào cell)
EDITOR_AMOUNT = "#editor-Amount"

# --- NÚT THAO TÁC ---
BTN_SEARCH = "button:has-text('Tìm kiếm')"
BTN_VALIDATE = "button:has-text('Xác thực')"  # TODO: Xác định đúng text nút

# --- BỘ LỌC (FILTER POPUP) ---
BTN_FILTER_TOGGLE = "#btnFilterToggle"
FILTER_POPUP = "#invoicecashregister-filter-popup"

# Kỳ (Period) — dùng custom combobox input, không phải <select> gốc
FILTER_PERIOD_INPUT = "#invoicecashregister-filter-popup .period-box .custom-combobox-input"

# Trạng thái phát hành (PublishStatus) — custom combobox input
FILTER_PUBLISH_STATUS_INPUT = "#invoicecashregister-filter-popup #cboPublishStatus + .custom-combobox .custom-combobox-input"

# jQuery UI autocomplete dropdown item
AUTOCOMPLETE_ITEM = ".ui-autocomplete .ui-menu-item"

# Nút áp dụng bộ lọc
BTN_APPLY_FILTER = "#btnFilter"
BTN_RESET_FILTER = "#btnCancelFilter"
