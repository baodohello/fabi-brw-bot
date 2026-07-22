"""Lịch đổi tài khoản ngân hàng theo ca làm việc cho từng chi nhánh."""

import pytz

# Múi giờ Việt Nam
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

# Cấu hình chi nhánh → UID iPOS + lịch đổi số tài khoản theo khung giờ
BANK_SCHEDULE = {
    "Cửa Hàng 1 (BRW 1)": {
        "uid": "2f202b34-e339-4b89-85de-364b8cc61a18",
        "schedule": {
            "06:00": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
            "09:00": {"stk": "8613980666", "ten": "CONG TY TNHH NHA MAY SAN PHAM SINH HOC NUTRI PAX"},
            "11:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
            "13:30": {"stk": "8613980666", "ten": "CONG TY TNHH NHA MAY SAN PHAM SINH HOC NUTRI PAX"},
            "15:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
        },
    },
    "Cửa Hàng 2 (BRW 2)": {
        "uid": "1fbeca99-192e-4766-937a-c35e8f28737a",
        "schedule": {
            "06:00": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
            "09:00": {"stk": "8613980666", "ten": "CONG TY TNHH NHA MAY SAN PHAM SINH HOC NUTRI PAX"},
            "11:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
            "13:30": {"stk": "8613980666", "ten": "CONG TY TNHH NHA MAY SAN PHAM SINH HOC NUTRI PAX"},
            "15:30": {"stk": "8889060473", "ten": "TRAN THI VAN OANH"},
        },
    },
}
