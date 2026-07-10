from datetime import datetime
from playwright.sync_api import Page, TimeoutError  # Thêm TimeoutError để bắt lỗi nếu bảng trống
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
            # Đợi bảng dữ liệu hiển thị ổn định
            page.wait_for_selector(selectors.TABLE_ROWS, timeout=2000) # Tăng nhẹ timeout hoặc giữ nguyên tùy cấu trúc trang
            rows = page.locator(selectors.TABLE_ROWS).all()
        except TimeoutError:
            # Bắt trường hợp không có dòng nào hiển thị (bảng trống hoàn toàn)
            print("⚠️ Không tìm thấy phần tử hàng hóa đơn nào trên giao diện (Timeout).", "warning")
            
        # Xử lý trường hợp tìm thấy 0 dòng hóa đơn
        if not rows:
            print("⚠️ Danh sách hóa đơn trống (0 dòng). Bỏ qua quy trình kiểm tra và tích chọn.", "warning")
            print("📊 KẾT QUẢ TRANG HIỆN TẠI:\n- Không có hóa đơn nào để xử lý (0 dòng).", "info")
            return summary
        
        print(f"Tìm thấy {len(rows)} hóa đơn trên trang hiện tại. Bắt đầu kiểm tra (Khung giờ: {start_time} - {end_time})...", "info")
        
        for index, row in enumerate(rows, start=1):
            # 1. Lấy mã hóa đơn để ghi log báo cáo
            invoice_code = row.locator(selectors.ROW_INVOICE_CODE).text_content().strip()
            
            # 2. Lấy dữ liệu Tổng tiền và chuẩn hóa sang dạng số nguyên (Int)
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
                # Tìm thẻ Checkbox của dòng hiện tại
                # 1. Định vị chính xác thẻ input ẩn (để kiểm tra trạng thái true/false)
                checkbox_input = row.locator(selectors.ROW_CHECKBOX_INPUT)

                # 2. Định vị chính xác thẻ label hiển thị
                checkbox_label = row.locator(selectors.ROW_CHECKBOX_LABEL)

                # Kiểm tra xem hóa đơn này đã được chọn hay chưa bằng input ẩn
                if not checkbox_input.is_checked():
                    # Sử dụng evaluate để kích hoạt click bằng JavaScript trực tiếp trên phần tử label
                    checkbox_label.evaluate("element => element.click()")
                    
                    # Ghi log xác nhận dòng đã được xử lý
                    print(f"  -> Đã kích hoạt click JavaScript thành công cho hóa đơn {invoice_code}", "info")
                
                # Cộng dồn số liệu vào bảng thống kê
                summary["total_processed_count"] += 1
                summary["total_processed_amount"] += amount
                
                print(f"  [Dòng {index}] Hóa đơn {invoice_code} HỢP LỆ ({amount_str} - {time_str}) -> Đã tích chọn.", "info")
            else:
                reason = []
                if not is_amount_valid: reason.append("Số tiền không lớn hơn 0")
                if not is_time_valid: reason.append(f"Thời gian nằm ngoài khung {start_time} - {end_time}")
                print(f"  [Dòng {index}] Hóa đơn {invoice_code} BỊ BỎ QUA. Lý do: {', '.join(reason)} ({amount_str} - {time_str})", "warning")
                
        # In báo cáo tổng hợp kết quả sau khi duyệt xong trang
        print(
            f"📊 KẾT QUẢ TRANG HIỆN TẠI:\n"
            f"- Tổng số hóa đơn hợp lệ đã tích: {summary['total_processed_count']} đơn\n"
            f"- Tổng số tiền tích lũy: {summary['total_processed_amount']:,} ₫", 
            "success"
        )
        
    except Exception as e:
        print(f"❌ Thao tác xử lý tính toán dữ liệu bảng hóa đơn thất bại: {str(e)}", "error")
        
    return summary