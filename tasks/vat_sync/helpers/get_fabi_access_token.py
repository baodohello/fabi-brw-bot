import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("FABI_LOGIN_URL") or "" # Lấy URL từ biến môi trường

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "access_token": os.getenv("FABI_APP_TOKEN")  # Lấy token từ biến môi trường,
}

payload = {
    "email": os.getenv("FABI_USERNAME"),
    "password": os.getenv("FABI_PASSWORD"),
    "required_change": True
}

def get_fabi_access_token():
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()  # Báo lỗi nếu status code là 4xx hoặc 5xx
        
        res_json = response.json()
        
        # Tự động trích xuất token dựa trên các cấu trúc phổ biến của iPOS API
        data_field = res_json.get("data", {})
        token = (
            data_field.get("token") 
            or data_field.get("access_token") 
            or res_json.get("token") 
            or res_json.get("access_token")
        )
        
        if token:
            print("Lấy token thành công:")
            print(token)
            return token
        else:
            print("Đăng nhập thành công nhưng chưa tìm thấy key token, cấu trúc response:")
            print(res_json)
            return None

    except requests.exceptions.HTTPError as errh:
        print(f"Lỗi HTTP ({response.status_code}):", response.text)
    except requests.exceptions.RequestException as err:
        print("Lỗi kết nối:", err)
    return None

if __name__ == "__main__":
    access_token = get_fabi_access_token()