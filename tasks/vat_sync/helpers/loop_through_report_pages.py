# File Route: tasks/vat_sync/helpers/loop_through_report_pages.py

from tasks.vat_sync import selectors


def get_max_pages(page) -> int:
    """
    Tìm số trang tối đa từ thanh điều hướng phân trang.
    """
    try:
        pagination_locator = page.locator(selectors.PAGINATION_ITEMS)
        pagination_locator.first.wait_for(state="visible", timeout=5000)
        
        # Thu thập dữ liệu text từ các nút phân trang
        page_elements = pagination_locator.all_inner_texts()
        page_numbers = [int(x.strip()) for x in page_elements if x.strip().isdigit()]
        
        if page_numbers:
            max_page = max(page_numbers)
            print(f"📋 Hệ thống phát hiện tổng cộng {max_page} trang dữ liệu.", "info")
            return max_page
        return 1
    except Exception as e:
        print(f"⚠️ Không tìm thấy thanh phân trang hoặc lỗi parse (Mặc định là 1 trang): {str(e)}", "warning")
        return 1



def loop_through_report_pages(page):
    """
    Vòng lặp duyệt qua từng trang báo cáo và in tiến trình.
    """
    max_pages = get_max_pages(page)
    
    for current_page in range(1, max_pages + 1):
        print(f"📄 Đang xử lý trang dữ liệu: {current_page} / {max_pages}")
        print(f"🔎 Đang duyệt kiểm tra dữ liệu tại Trang {current_page}...", "info")
        
        if current_page > 1:
            # Tìm nút bấm link tương ứng với số trang kế tiếp
            next_page_btn = page.locator(selectors.PAGINATION_ITEMS).get_by_role("link", name=str(current_page), exact=True)
            if next_page_btn.count() > 0:
                next_page_btn.click()
                page.wait_for_timeout(2000) # Chờ dữ liệu bảng tải xong
            else:
                print(f"⚠️ Không tìm thấy nút bấm chuyển sang trang {current_page}", "warning")
                break
                
        # --- Thực hiện bóc tách dữ liệu hoặc xử lý của trang hiện tại ở đây ---
        # Ví dụ: cào dữ liệu bảng hóa đơn...
        
    print(f"🎉 Đã hoàn thành duyệt qua tất cả {max_pages} trang dữ liệu!", "success")