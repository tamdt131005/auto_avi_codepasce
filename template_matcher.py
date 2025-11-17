"""
Template Matcher module - Xử lý cache và matching logic
"""

import cv2
import numpy as np
import threading
import logging
import os
import time
from PIL import Image
import io

from config import (
    DEFAULT_SCALES, 
    TEMPLATE_SCALES, 
    SCREENSHOT_BUFFER_TTL,
    THRESHOLDS
)
from adb_bridge import adb_screencap_bytes

logger = logging.getLogger(__name__)

# ============================================
# CACHE CLASSES
# ============================================

class TemplateCache:
    """Cache cho các template đã scale"""
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
    
    def get(self, path, scales=None):
        """Lấy hoặc tạo cache cho template với các tỉ lệ"""
        if scales is None:
            scales = DEFAULT_SCALES
        
        cache_key = (path, tuple(scales))
        
        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            template = cv2.imread(path)
            if template is None:
                logger.error(f"❌ Không đọc được template: {path}")
                return None
            
            scaled_templates = []
            temp_h, temp_w = template.shape[:2]
            
            for scale in scales:
                if scale == 1.0:
                    scaled_templates.append((template, scale, temp_w, temp_h))
                else:
                    new_w = int(temp_w * scale)
                    new_h = int(temp_h * scale)
                    resized = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                    scaled_templates.append((resized, scale, new_w, new_h))
            
            self._cache[cache_key] = scaled_templates
            logger.info(f"✅ Đã cache template: {os.path.basename(path)} với {len(scales)} tỉ lệ")
            return scaled_templates
    
    def clear(self):
        """Xóa toàn bộ cache"""
        with self._lock:
            self._cache.clear()
            logger.info("🗑️  Đã xóa cache template")

class ScreenshotBuffer:
    """Buffer để tái sử dụng screenshot trong khoảng thời gian ngắn"""
    
    def __init__(self, ttl=SCREENSHOT_BUFFER_TTL):
        self._buffer = None
        self._timestamp = 0
        self._ttl = ttl
        self._lock = threading.Lock()
    
    def get(self, force_refresh=False):
        """Lấy screenshot từ buffer hoặc chụp mới"""
        with self._lock:
            current_time = time.time()
            
            if not force_refresh and self._buffer is not None:
                age = current_time - self._timestamp
                if age < self._ttl:
                    logger.debug(f"♻️  Tái sử dụng ảnh chụp (tuổi: {age:.2f}s)")
                    return self._buffer
            
            logger.debug("📸 Đang chụp ảnh màn hình mới")
            data = adb_screencap_bytes()
            img = Image.open(io.BytesIO(data))
            self._buffer = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            self._timestamp = current_time
            
            return self._buffer
    
    def invalidate(self):
        """Làm vô hiệu buffer để buộc chụp lại"""
        with self._lock:
            self._timestamp = 0

# ============================================
# GLOBAL INSTANCES
# ============================================

_template_cache = TemplateCache()
_screenshot_buffer = ScreenshotBuffer()

# ============================================
# TEMPLATE MATCHING
# ============================================

def match_template_multiscale(screen_bgr, template_path, threshold=0.6, 
                              scales=None, early_exit_conf=None, debug=False):
    """
    Tìm kiếm template trên màn hình với nhiều tỉ lệ khác nhau
    
    Args:
        screen_bgr: Ảnh màn hình dạng BGR
        template_path: Đường dẫn đến template
        threshold: Ngưỡng confidence tối thiểu
        scales: Danh sách tỉ lệ để thử (None = dùng default)
        early_exit_conf: Dừng sớm khi đạt confidence này
        debug: Lưu ảnh debug
    
    Returns:
        dict với keys: found, confidence, location, bbox, scale
    """
    if early_exit_conf is None:
        early_exit_conf = THRESHOLDS['early_exit_conf']
    
    result = {
        'found': False,
        'confidence': 0.0,
        'location': None,
        'bbox': None,
        'scale': 1.0
    }
    
    screen_h, screen_w = screen_bgr.shape[:2]
    
    scaled_templates = _template_cache.get(template_path, scales=scales)
    if scaled_templates is None:
        return result
    
    best_val = 0
    best_match = None
    best_scale = 1.0
    
    for template, scale, temp_w, temp_h in scaled_templates:
        if temp_w > screen_w or temp_h > screen_h:
            logger.debug(f"⏭️  Skip scale {scale:.2f} (quá lớn: {temp_w}x{temp_h})")
            continue
        
        match_result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(match_result)
        
        logger.debug(f"📏 Scale {scale:.2f} ({temp_w}x{temp_h}) -> conf={max_val:.4f}")
        
        if max_val > best_val:
            best_val = max_val
            best_match = (max_loc, temp_w, temp_h)
            best_scale = scale
            
            if max_val >= early_exit_conf:
                logger.debug(f"⚡ Dừng sớm ở tỉ lệ {scale:.2f} (độ tin cậy={max_val:.4f})")
                break
    
    if best_val >= threshold and best_match:
        top_left, w, h = best_match
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        
        result = {
            'found': True,
            'confidence': best_val,
            'location': (center_x, center_y),
            'bbox': (top_left[0], top_left[1], w, h),
            'scale': best_scale
        }

        if debug:
            debug_img = screen_bgr.copy()
            cv2.rectangle(debug_img, top_left, (top_left[0] + w, top_left[1] + h), (0, 255, 0), 3)
            cv2.circle(debug_img, (center_x, center_y), 8, (0, 0, 255), -1)
            text = f"Conf: {best_val:.3f} | Scale: {best_scale:.2f}"
            cv2.putText(debug_img, text, (top_left[0], top_left[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            debug_filename = f"debug_{os.path.basename(template_path).split('.')[0]}.png"
            cv2.imwrite(debug_filename, debug_img)
            logger.info(f"💾 Đã lưu {debug_filename}")
    else:
        logger.debug(f"❌ Không tìm thấy (độ tin cậy tốt nhất={best_val:.4f} < ngưỡng={threshold})")
        
        if debug and best_match:
            debug_img = screen_bgr.copy()
            top_left, w, h = best_match
            cv2.rectangle(debug_img, top_left, (top_left[0] + w, top_left[1] + h), (0, 0, 255), 3)
            text = f"LOW: {best_val:.3f} | Scale: {best_scale:.2f}"
            cv2.putText(debug_img, text, (top_left[0], top_left[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            debug_filename = f"debug_{os.path.basename(template_path).split('.')[0]}_failed.png"
            cv2.imwrite(debug_filename, debug_img)
            logger.info(f"💾 Đã lưu {debug_filename}")
    
    return result

# ============================================
# SCREENSHOT FUNCTIONS
# ============================================

def load_screenshot_bgr(use_cache=True, force_refresh=False):
    """
    Load screenshot dạng BGR
    
    Args:
        use_cache: Có sử dụng cache không
        force_refresh: Buộc chụp mới (bỏ qua cache)
    
    Returns:
        np.array: Ảnh màn hình dạng BGR
    """
    if not use_cache:
        data = adb_screencap_bytes()
        img = Image.open(io.BytesIO(data))
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    return _screenshot_buffer.get(force_refresh=force_refresh)

def invalidate_screenshot_buffer():
    """Làm vô hiệu screenshot buffer"""
    _screenshot_buffer.invalidate()

# ============================================
# TEMPLATE PRELOADING
# ============================================

def preload_templates():
    """Pre-load tất cả templates phổ biến vào cache"""
    from config import TEMPLATE_PATHS
    
    templates = {
        'item_nv': (TEMPLATE_PATHS['item_nv'], TEMPLATE_SCALES.get('item_nv')),
        'btn_xacnhan': (TEMPLATE_PATHS['btn_xacnhan'], TEMPLATE_SCALES.get('btn_xacnhan')),
        'captra': (TEMPLATE_PATHS['captra'], TEMPLATE_SCALES.get('captra')),
    }
    
    logger.info("🔄 Pre-loading templates...")
    for name, (path, scales) in templates.items():
        if os.path.exists(path):
            _template_cache.get(path, scales=scales)
    logger.info("✅ Đã nạp trước tất cả templates!")

# Auto-preload khi import module
try:
    preload_templates()
except Exception as e:
    logger.warning(f"Không thể nạp trước templates: {e}")
