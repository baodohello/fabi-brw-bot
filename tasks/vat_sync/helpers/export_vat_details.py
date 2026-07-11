

import os


def export_vat_details(page, buyer_name: str = "3C") -> bool:
    """
    Thực hiện quy trình xuất VAT chi tiết: Bấm nút xuất chi tiết -> Chọn Cá nhân -> Nhập tên -> Bấm Xuất VAT.
    :param page: Đối tượng Page của Playwright
    :param buyer_name: Tên khách hàng cần điền vào ô input (Mặc định nếu không truyền là "3C")
    :return: True nếu thành công, False nếu có lỗi xảy ra
    """
    try:
        print("--- Tiến hành click nút 'Xuất chi tiết' ---")
        # Định vị và xử lý nút Xuất chi tiết
        export_button = page.locator("button.export-btn-detail:has-text('Xuất chi tiết')")
        export_button.wait_for(state="visible", timeout=5000) # Khuyên dùng 5000ms thay vì 500ms để tránh timeout khi mạng chậm
        
        # Click an toàn bằng evaluate phòng trường hợp bị che khuất layout
        export_button.evaluate("element => element.click()")
        print("-> Đã click nút 'Xuất chi tiết' thành công!")

        # 1. Định vị và tích chọn mục 'Cá nhân' bằng JS
        radio_ca_nhan_label = page.locator("label.label--real:has-text('Cá nhân')")
        radio_ca_nhan_label.wait_for(state="attached", timeout=5000)
        radio_ca_nhan_label.evaluate("element => element.click()")
        print("-> Đã tích chọn mục 'Cá nhân' thành công bằng JavaScript!")

        # 2. Định vị ô nhập tên khách hàng và điền giá trị tùy biến
        buyer_name_input = page.locator("input[name='inv_buyerDisplayName']")
        buyer_name_input.wait_for(state="visible", timeout=5000)
        buyer_name_input.fill(buyer_name)
        print(f"-> Đã nhập tên khách hàng '{buyer_name}' thành công!")

        # 3. Định vị và click nút "Xuất VAT"
        vat_button = page.locator("button.btn-primary:has-text('Xuất VAT')")
        vat_button.wait_for(state="visible", timeout=5000) # Khuyên dùng 5000ms để đợi modal render xong form
        vat_button.evaluate("element => element.click()")
        print("-> Đã click nút 'Xuất VAT' thành công. Hoàn thành quy trình!")
        
        return True

    except Exception as e:
        print(f"❌ Thao tác xuất VAT chi tiết thất bại: {str(e)}")
        return False