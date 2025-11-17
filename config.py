"""
Configuration module for automation
Tập trung tất cả các cấu hình để dễ quản lý và điều chỉnh
"""

# ============================================
# ADB BRIDGE CONFIGURATION
# ============================================
import os

ADB_BRIDGE_URL = "https://wkp78mcg-8080.asse.devtunnels.ms/"
USE_ADB_BRIDGE = os.getenv('USE_ADB_BRIDGE', 'true').lower() == 'true'

# ============================================
# TEMPLATE MATCHING CONFIGURATION
# ============================================

DEFAULT_SCALES = [ 0.9, 1.0, 1.1]  # Giảm từ 11 scales xuống 5

TEMPLATE_SCALES = {
    'item_nv': [0.9, 1.0, 1.1],              # Giảm từ 5 xuống 3 - tập trung vùng chính
    'btn_xacnhan': [0.9, 1.0,1.1],               # Giảm từ 4 xuống 2 - SIÊU NHANH!
    'captra': [0.8, 0.9, 1.0, 1.1, 1.2],     # Giảm từ 11 xuống 5 - captcha cần linh hoạt hơn
}

# Template paths
TEMPLATE_PATHS = {
    'item_nv': r"./templates/item_nv.jpg",
    'btn_xacnhan': r"./templates/btn_xacnhan.jpg",
    'captra': r"./templates/captra.jpg",
    'time_cho': r"./templates/time_cho.jpg",
    'start_video': r"./templates/start_video.png",
}

# ============================================
# CACHE CONFIGURATION
# ============================================

SCREENSHOT_BUFFER_TTL = 0.3  # seconds

# ============================================
# TASK AUTOMATION CONFIGURATION
# ============================================

AUTOMATION_CONFIG = {
    'max_count': 50,                    # Tổng số nhiệm vụ cần hoàn thành
    'break_interval': 25,               # Nghỉ sau mỗi N nhiệm vụ
    'break_duration': (1, 3),           # Thời gian nghỉ (min, max) - giảm từ (2,5)
    'captcha_timeout': 60,              # Thời gian tối đa chờ captcha được giải (giây)
    'captcha_check_interval': 2,        # Khoảng kiểm tra captcha (giây)
    
    # 🚀 CHIẾN LƯỢC MỚI: Tối ưu cho nhiệm vụ ngắn (7s thực tế)
    # Check liên tục trong 5s đầu, sau đó giảm dần
    'button_wait_max': 12,              # Giảm từ 15s xuống 12s
    'button_check_intervals': [
        # 5 giây đầu: check mỗi 0.4s (16 lần) - TĂNG TỐC HƠN NỮA!
        *[0.4] * 16,
        # 3 giây tiếp: check mỗi 0.5s (6 lần)
        *[0.5] * 6,
        # 4 giây cuối: check mỗi 1.0s (4 lần)
        *[1.0] * 4
    ],  # Tổng: 4.8 + 3.0 + 4.0 = 11.8s
    
    # Chiến lược chờ cho nhiệm vụ dài (video) - giữ nguyên
    'long_task_button_wait_max': 180,   # Thời gian tối đa chờ nút (3 phút)
    'long_task_check_intervals': [
        # 30 giây đầu: check mỗi 2s (15 lần)
        *[2.0] * 15,
        # 60 giây tiếp: check mỗi 3s (20 lần) 
        *[3.0] * 20,
        # 90 giây cuối: check mỗi 5s (18 lần)
        *[5.0] * 18
    ],  # Tổng: 30 + 60 + 90 = 180s
    
    'page_load_delay': (1.8, 2.5),      # Giảm từ (2.5, 3.5) - chờ load trang
    'post_captcha_delay': (0.5, 1.0),   # Giảm từ (0.8, 1.5) - delay sau captcha
    'inter_action_delay': (0.2, 0.15),  # Giảm từ (0.3, 0.2) - delay giữa các hành động
    'retry_delay': (0.4, 0.15),         # Giảm từ (0.6, 0.2) - delay trước khi retry
}

# ============================================
# THRESHOLDS
# ============================================

THRESHOLDS = {
    'item_nv': 0.6,
    'btn_xacnhan': 0.65,
    'btn_start_video': 0.7,
    'time_cho': 0.6,
    'captra': 0.5,
    'early_exit_conf': 0.9,
}

# ============================================
# LOGGING
# ============================================

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
