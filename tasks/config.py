# config.py
import os
import json
import pytz
from datetime import datetime
# Định nghĩa múi giờ Việt Nam để xử lý logic so khớp giờ chính xác
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

# Lấy đường dẫn thư mục gốc của dự án để tìm file JSON ở local
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_JSON_PATH = os.path.join(BASE_DIR, "stores_config.json")

STORES_CONFIG = {}

# 1. Ưu tiên lấy cấu hình từ biến môi trường (Dành cho GitHub Actions)
STORES_CONFIG_RAW = os.getenv("STORES_CONFIG_JSON")

if STORES_CONFIG_RAW:
    try:
        STORES_CONFIG = json.loads(STORES_CONFIG_RAW)
        print("🌐 [Config]: Đã nạp cấu hình thành công từ GitHub Secrets.")
    except Exception as e:
        print(f"❌ [Lỗi Config]: Chuỗi JSON từ Secrets bị sai định dạng: {str(e)}")
else:
    # 2. Nếu không có biến môi trường, tự động tìm đọc file JSON ở local
    if os.path.exists(LOCAL_JSON_PATH):
        try:
            with open(LOCAL_JSON_PATH, "r", encoding="utf-8") as f:
                STORES_CONFIG = json.load(f)
                print("📂 [Config]: Đã nạp cấu hình thành công từ file 'stores_config.json' ở local.")
        except Exception as e:
            print(f"❌ [Lỗi Config]: Không thể đọc hoặc giải mã file 'stores_config.json': {str(e)}")
    else:
        print("⚠️ [Cảnh báo]: Không tìm thấy cả biến môi trường lẫn file JSON cấu hình!")