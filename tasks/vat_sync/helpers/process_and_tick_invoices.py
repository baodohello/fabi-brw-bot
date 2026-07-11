from datetime import datetime
from playwright.sync_api import Page, TimeoutError  
from tasks.vat_sync import selectors


def process_and_tick_invoices(
    page: Page, 
    start_time: str = "06:00", 
    end_time: str = "22:00"
) -> dict:
    """
    Duyệt danh sách hóa đơn, tính toán tổng tiền, kiểm tra điều kiện thời gian
    và tích chọn các checkbox hợp lệ.
    
    :param page: Đối tượng Page của Playwright
    :param start_time: Giờ bắt đầu hợp lệ (định dạng "HH:MM", mặc định "06:00")
    :param end_time: Giờ kết thúc hợp lệ (định dạng "HH:MM", mặc định "22:00")
    :return: dict thống kê kết quả xử lý số lượng và tổng tiền
    """
    summary = {
        "total_processed_count": 0,    # Tổng số hóa đơn được tích chọn hợp lệ
        "total_processed_amount": 0    # Tổng số tiền của các hóa đơn hợp lệ
    }
    
    try:
        # Chuyển đổi chuỗi tham số thời gian thành đối tượng time để so sánh
        start_valid_time = datetime.strptime(start_time, "%H:%M").time()
        end_valid_time = datetime.strptime(end_time, "%H:%M").time()
        
        rows = []
        try:
            page.wait_for_selector(selectors.TABLE_ROWS, timeout=3000) 
            rows = page.locator(selectors.TABLE_ROWS).all()
        except TimeoutError:
            print("⚠️ Không tìm thấy phần tử hàng hóa đơn nào trên giao diện (Timeout).", "warning")
            
        # Xử lý trường hợp tìm thấy 0 dòng hóa đơn
        if not rows:
            print("⚠️ Danh sách hóa đơn trống (0 dòng). Bỏ qua quy trình kiểm tra và tích chọn.", "warning")
            print("📊 KẾT QUẢ TRANG HIỆN TẠI:\n- Không có hóa đơn nào để xử lý (0 dòng).", "info")
            return summary
        
        print(f"Tìm thấy {len(rows)} hóa đơn trên trang hiện tại. Bắt đầu kiểm tra (Khung giờ: {start_time} - {end_time})...", "info")
        
        for index, row in enumerate(rows, start=1):
            invoice_code = row.locator(selectors.ROW_INVOICE_CODE).text_content().strip()
            amount_str = row.locator(selectors.ROW_TOTAL_AMOUNT).text_content().strip()
            # Xóa chữ '₫' và dấu phẩy ngăn cách hàng nghìn (ví dụ: "45,000 ₫" -> 45000)
            amount = int(amount_str.replace("₫", "").replace(",", "").strip())
            # 3. Lấy dữ liệu Thời gian ra và chuyển đổi thành Object datetime để so sánh giờ
            time_str = row.locator(selectors.ROW_OUT_TIME).text_content().strip()
            # Định dạng trong HTML là "dd/mm/yyyy HH:MM" (ví dụ: "10/07/2026 15:45")
            invoice_datetime = datetime.strptime(time_str, "%d/%m/%Y %H:%M")
            invoice_time = invoice_datetime.time()
            
            # 4. Kiểm tra sự thỏa mãn của cả 2 điều kiện
            is_amount_valid = amount > 0
            is_time_valid = start_valid_time < invoice_time < end_valid_time
            
            if is_amount_valid and is_time_valid:
                checkbox_input = row.locator(selectors.ROW_CHECKBOX_INPUT)
                checkbox_label = row.locator(selectors.ROW_CHECKBOX_LABEL)
                if not checkbox_input.is_checked():
                    checkbox_label.evaluate("element => element.click()")
                # Cộng dồn số liệu vào bảng thống kê
                summary["total_processed_count"] += 1
                summary["total_processed_amount"] += amount
                
                print(f"  [Dòng {index}] Hóa đơn {invoice_code} HỢP LỆ ({amount_str} - {time_str}) -> Đã tích chọn.", "info")
            else:
                reason = []
                if not is_amount_valid: reason.append("Số tiền không lớn hơn 0")
                if not is_time_valid: reason.append(f"Thời gian nằm ngoài khung {start_time} - {end_time}")
                print(f"  [Dòng {index}] Hóa đơn {invoice_code} BỊ BỎ QUA. Lý do: {', '.join(reason)} ({amount_str} - {time_str})", "warning")
                
    except Exception as e:
        print(f"❌ Thao tác xử lý tính toán dữ liệu bảng hóa đơn thất bại: {str(e)}", "error")
        
    return summary