"""
ADB Bridge module - Xử lý tất cả các thao tác ADB
Hỗ trợ cả ADB trực tiếp và ADB Bridge qua HTTP
"""

import subprocess
import time
import random
import logging

from config import ADB_BRIDGE_URL, USE_ADB_BRIDGE

logger = logging.getLogger(__name__)

# Import requests with fallback
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    if USE_ADB_BRIDGE:
        logger.error("❌ Module 'requests' không có! Vui lòng cài: pip install requests")
        logger.error("   Hoặc tắt ADB Bridge trong config.py: USE_ADB_BRIDGE = False")

# ============================================
# SCREEN SIZE CACHE
# ============================================

_screen_size_cache = None

def get_screen_size():
    """Lấy kích thước màn hình từ ADB (có cache)"""
    global _screen_size_cache
    
    if _screen_size_cache is not None:
        return _screen_size_cache
    
    try:
        if USE_ADB_BRIDGE:
            if not REQUESTS_AVAILABLE:
                raise RuntimeError("Không thể dùng ADB Bridge: module 'requests' chưa cài đặt")
            response = requests.get(f'{ADB_BRIDGE_URL}/shell', 
                                   params={'cmd': 'wm size'}, 
                                   timeout=5)
            if response.status_code != 200:
                raise RuntimeError(f"ADB Bridge error: HTTP {response.status_code}")
            output = response.json()['output'].strip()
        else:
            result = subprocess.run(
                ["adb", "shell", "wm", "size"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError(f"Không thể lấy kích thước màn hình: {result.stderr}")
            output = result.stdout.strip()
        
        # Parse: "Physical size: 1080x2400"
        size_str = output.split(":")[-1].strip()
        width, height = map(int, size_str.split("x"))
        
        _screen_size_cache = (width, height)
        logger.info(f"📐 Kích thước màn hình: {width}x{height}")
        return width, height
        
    except Exception as e:
        raise RuntimeError(f"Lỗi lấy kích thước màn hình: {e}")

def clear_screen_size_cache():
    """Xóa cache kích thước màn hình"""
    global _screen_size_cache
    _screen_size_cache = None
    logger.info("🗑️  Đã xóa cache kích thước màn hình")

# ============================================
# SCREENSHOT
# ============================================

def adb_screencap_bytes():
    """Chụp ảnh màn hình qua ADB hoặc ADB Bridge"""
    if USE_ADB_BRIDGE:
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Không thể dùng ADB Bridge: module 'requests' chưa cài đặt")
        try:
            response = requests.get(f'{ADB_BRIDGE_URL}/screenshot', timeout=10)
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"ADB Bridge error: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Lỗi kết nối ADB Bridge: {e}")
            raise RuntimeError(f"Không thể chụp màn hình qua ADB Bridge: {e}")
    else:
        p = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=subprocess.PIPE)
        if p.returncode != 0:
            raise RuntimeError("adb chụp màn hình thất bại")
        return p.stdout

# ============================================
# INPUT ACTIONS
# ============================================

def adb_tap(x, y, randomize=True, invalidate_callback=None):
    """
    Tap với random offset
    
    Args:
        x, y: Tọa độ tap
        randomize: Có ngẫu nhiên hóa offset không
        invalidate_callback: Callback để invalidate screenshot buffer
    """
    if randomize:
        x += random.randint(-5, 5)
        y += random.randint(-5, 5)
    
    time.sleep(random.uniform(0.01, 0.03))
    
    x_int = int(x)
    y_int = int(y)
    
    if USE_ADB_BRIDGE:
        try:
            response = requests.get(f'{ADB_BRIDGE_URL}/tap', 
                                   params={'x': x_int, 'y': y_int}, 
                                   timeout=5)
            if response.status_code != 200:
                logger.error(f"ADB Bridge tap error: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Lỗi tap qua ADB Bridge: {e}")
    else:
        subprocess.run(["adb", "shell", "input", "tap", str(x_int), str(y_int)])
    
    logger.info(f"👆 Chạm tại ({x_int}, {y_int})")
    
    if invalidate_callback:
        invalidate_callback()

def adb_swipe(x1, y1, x2, y2, duration_ms=200, randomize=True, invalidate_callback=None):
    """
    Swipe với random offset
    
    Args:
        x1, y1: Tọa độ bắt đầu
        x2, y2: Tọa độ kết thúc
        duration_ms: Thời lượng swipe (ms)
        randomize: Có ngẫu nhiên hóa offset không
        invalidate_callback: Callback để invalidate screenshot buffer
    """
    if randomize:
        x1 += random.randint(-3, 3)
        y1 += random.randint(-3, 3)
        x2 += random.randint(-3, 3)
        y2 += random.randint(-3, 3)
    
    x1_int, y1_int = int(x1), int(y1)
    x2_int, y2_int = int(x2), int(y2)
    duration_int = int(duration_ms)
    
    if USE_ADB_BRIDGE:
        try:
            response = requests.get(f'{ADB_BRIDGE_URL}/swipe',
                                   params={
                                       'x1': x1_int, 'y1': y1_int,
                                       'x2': x2_int, 'y2': y2_int,
                                       'duration': duration_int
                                   },
                                   timeout=5)
            if response.status_code != 200:
                logger.error(f"ADB Bridge swipe error: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Lỗi swipe qua ADB Bridge: {e}")
    else:
        subprocess.run(["adb", "shell", "input", "swipe", 
                       str(x1_int), str(y1_int), str(x2_int), str(y2_int), str(duration_int)])
    
    logger.info(f"👉 Vuốt ({x1_int}, {y1_int}) -> ({x2_int}, {y2_int})")
    
    if invalidate_callback:
        invalidate_callback()

def adb_back(invalidate_callback=None):
    """
    Back button
    
    Args:
        invalidate_callback: Callback để invalidate screenshot buffer
    """
    time.sleep(random.uniform(0.01, 0.03))
    
    if USE_ADB_BRIDGE:
        try:
            response = requests.get(f'{ADB_BRIDGE_URL}/shell', 
                                   params={'cmd': 'input keyevent BACK'}, 
                                   timeout=5)
            if response.status_code != 200:
                logger.error(f"ADB Bridge back error: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Lỗi back qua ADB Bridge: {e}")
    else:
        subprocess.run(["adb", "shell", "input", "keyevent", "BACK"])
    
    logger.info("⬅️  Quay lại trang trước")
    
    if invalidate_callback:
        invalidate_callback()

# ============================================
# HIGH-LEVEL SCROLL FUNCTION
# ============================================

def scroll_up(scroll_percent=None, invalidate_callback=None):
    """
    Kéo lên để xem nội dung phía trên
    
    Args:
        scroll_percent: Phần trăm cuộn (None = tự động chọn)
        invalidate_callback: Callback để invalidate screenshot buffer
    """
    width, height = get_screen_size()
    
    x = random.randint(int(width * 0.4), int(width * 0.6))
    start_y = random.randint(int(height * 0.6), int(height * 0.7))
    
    if scroll_percent is not None:
        scroll_distance = (scroll_percent / 100) * height
        
        if scroll_percent <= 30:
            duration = random.randint(200, 300)
            pause = random.uniform(1.0, 2.0)
            scroll_type = f"{scroll_percent}%"
        elif scroll_percent <= 50:
            duration = random.randint(300, 500)
            pause = random.uniform(0.5, 1.5)
            scroll_type = f"{scroll_percent}%"
        else:
            duration = random.randint(400, 600)
            pause = random.uniform(0.3, 0.8)
            scroll_type = f"{scroll_percent}%"
    else:
        scroll_types = ['short', 'medium', 'long']
        scroll_type = random.choices(scroll_types, weights=[0.3, 0.5, 0.2])[0]
        
        if scroll_type == 'short':
            scroll_distance = random.uniform(0.2, 0.3) * height
            duration = random.randint(200, 300)
            pause = random.uniform(1.0, 2.0)
        elif scroll_type == 'medium':
            scroll_distance = random.uniform(0.4, 0.6) * height
            duration = random.randint(300, 500)
            pause = random.uniform(0.5, 1.5)
        else:
            scroll_distance = random.uniform(0.6, 0.8) * height
            duration = random.randint(400, 600)
            pause = random.uniform(0.3, 0.8)
    
    end_y = int(start_y - scroll_distance)
    
    adb_swipe(x, start_y, x, end_y, duration, randomize=True, invalidate_callback=invalidate_callback)
    time.sleep(pause)
    logger.info(f"📱 Kéo lên ({scroll_type})")

# ============================================
# INITIALIZATION
# ============================================

def init_adb_bridge():
    """Khởi tạo và kiểm tra kết nối ADB Bridge"""
    logger.info(f"🔧 ADB Bridge: {'Enabled' if USE_ADB_BRIDGE else 'Disabled'}")
    if USE_ADB_BRIDGE:
        logger.info(f"🌐 ADB Bridge URL: {ADB_BRIDGE_URL}")

# Auto-init khi import
init_adb_bridge()
