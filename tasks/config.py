# config.py
import pytz
from datetime import datetime

# Định nghĩa múi giờ Việt Nam để xử lý logic so khớp giờ chính xác
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

STORES_CONFIG = {
    "Cửa Hàng 1 (BRW 1)": {
        "uid": "2f202b34-e339-4b89-85de-364b8cc61a18",
        "schedule": {
            # 8h30 và 13h30 dùng STK CÔNG TY, các khung giờ khác dùng STK CÁ NHÂN
            "06:00": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"}, # Cá nhân
            "08:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"}, # Công ty
            "11:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"}, # Cá nhân
            "13:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"}, # Công ty
            "16:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"}, # Cá nhân
        }
    },
    "Cửa Hàng 2 (BRW 2)": {
        "uid": "1fbeca99-192e-4766-937a-c35e8f28737a",
        "schedule": {
            # 8h30 và 13h30 dùng STK CÔNG TY, các khung giờ khác dùng STK CÁ NHÂN
            "06:00": {"stk": "8807988664", "ten": "DO TUAN BAO"}, # Cá nhân
            "08:30": {"stk": "8807988664", "ten": "DO TUAN BAO"}, # Công ty
            "11:30": {"stk": "8807988664", "ten": "DO TUAN BAO"}, # Cá nhân
            "13:30": {"stk": "8807988664", "ten": "DO TUAN BAO"}, # Công ty
            "16:30": {"stk": "8807988664", "ten": "DO TUAN BAO"}  # Cá nhân
        }
    }
}

def get_current_vn_time_str():
    """Hàm bổ trợ lấy giờ hiện tại theo định dạng HH:MM chuẩn múi giờ Việt Nam."""
    now_vn = datetime.now(VN_TZ)
    return now_vn.strftime("%H:%M")