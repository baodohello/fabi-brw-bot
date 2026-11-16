
import requests
import os
from dotenv import load_dotenv
from get_fabi_access_token import get_fabi_access_token
from datetime import datetime, time, timezone, timedelta

# Múi giờ Việt Nam (UTC+7)
ICT = timezone(timedelta(hours=7))

load_dotenv()



def export_sales_data(target_date_str: str, store_uid: str, store_name: str):
    ICT = timezone(timedelta(hours=7))
    dt_date = datetime.strptime(target_date_str, "%Y-%m-%d")
    # Bước 1: Lấy User Token
    print("Đang đăng nhập vào hệ thống iPOS...")
    user_token = get_fabi_access_token()
    if not user_token:
        print("Lỗi: Không thể lấy được user token từ phản hồi đăng nhập!")
        return
    print("Đăng nhập thành công, đã cấp User Token.")

    # Bước 2: Gọi API Export Sales JSON với payload bạn cung cấp
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "access_token": os.getenv("FABI_APP_TOKEN"),              # Xác thực ứng dụng
        "Authorization": f"{user_token}", # Xác thực tài khoản người dùng
        "Origin": "https://pos.ipos.vn",
        "Referer": "https://pos.ipos.vn/"
    }

    payload = {
        "company_uid": os.getenv("FABI_COMPANY_ID"),
        "brand_uid": os.getenv("FABI_BRAND_ID"),
        "store_uid": os.getenv("FABI_STORE_ID_BRW1"),
        "start_date":int(datetime.combine(dt_date, time.min).replace(tzinfo=ICT).timestamp() * 1000),
        "end_date": int(datetime.combine(dt_date, time.max).replace(tzinfo=ICT).timestamp() * 1000),
        "store_open_at": 0,
        "list_tran_id": []
    }

    print("Đang gửi yêu cầu export dữ liệu bán hàng...")
    response = requests.post(os.getenv("FABI_EXPORT_SALE_URL") or "", json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    res_json = response.json()

    # Bước 3: Lấy link S3 từ response
    s3_link = res_json.get("data", {}).get("link")
    if not s3_link:
        print("Không tìm thấy link tải file trong response:", res_json)
        return

    print(f"Lấy link S3 thành công:\n{s3_link}")

    # Bước 4: Tải trực tiếp file JSON từ link S3 về máy
    print("Đang tải file JSON về máy...")
    file_response = requests.get(s3_link, timeout=60)
    file_response.raise_for_status()

    filename = f"sales_{target_date_str}_{store_name}.json"
    with open(filename, "wb") as f:
        f.write(file_response.content)

    print(f"Đã tải và lưu thành công file tại: {os.path.abspath(filename)}")

if __name__ == "__main__":
    export_sales_data( 
        target_date_str="2026-11-12", 
        store_uid=os.getenv("FABI_STORE_ID_BRW1") or "",
        store_name="BRW1"
        )