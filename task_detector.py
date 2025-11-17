"""
Task Detector module - Phát hiện các thành phần UI và thực hiện hành động
"""

import logging
import time
import random

from config import (
    TEMPLATE_PATHS, 
    TEMPLATE_SCALES, 
    THRESHOLDS,
    DEFAULT_SCALES
)
from template_matcher import (
    load_screenshot_bgr,
    match_template_multiscale,
    invalidate_screenshot_buffer
)
from adb_bridge import adb_tap, scroll_up

logger = logging.getLogger(__name__)

# ============================================
# CHECK FUNCTIONS (Chỉ kiểm tra, không thao tác)
# ============================================

def check_nv(screen_bgr=None, threshold=None, debug=False):
    """Kiểm tra xem có nhiệm vụ trên màn hình không"""
    if threshold is None:
        threshold = THRESHOLDS['item_nv']
    
    if screen_bgr is None:
        screen_bgr = load_screenshot_bgr(use_cache=True)
    
    template_path = TEMPLATE_PATHS['item_nv']
    scales = TEMPLATE_SCALES.get('item_nv', DEFAULT_SCALES)
    
    result = match_template_multiscale(
        screen_bgr, template_path, 
        threshold=threshold, 
        scales=scales, 
        debug=debug
    )
    
    if result['found']:
        return True
    return False

def check_btn_start_video(screen_bgr=None, threshold=None, debug=False):
    """Kiểm tra xem có nút start video không"""
    if threshold is None:
        threshold = THRESHOLDS['btn_start_video']
    
    if screen_bgr is None:
        screen_bgr = load_screenshot_bgr(use_cache=True)
    
    template_path = TEMPLATE_PATHS['start_video']
    scales = TEMPLATE_SCALES.get('btn_xacnhan', DEFAULT_SCALES)
    
    result = match_template_multiscale(
        screen_bgr, template_path,
        threshold=threshold,
        scales=scales,
        debug=debug
    )
    
    if result['found']:
        return True
    return False

def check_btn_xn(screen_bgr=None, threshold=None, debug=False):
    """Kiểm tra xem có nút xác nhận không"""
    if threshold is None:
        threshold = THRESHOLDS['btn_xacnhan']
    
    if screen_bgr is None:
        screen_bgr = load_screenshot_bgr(use_cache=True)
    
    template_path = TEMPLATE_PATHS['btn_xacnhan']
    scales = TEMPLATE_SCALES.get('btn_xacnhan', DEFAULT_SCALES)
    
    result = match_template_multiscale(
        screen_bgr, template_path,
        threshold=threshold,
        scales=scales,
        debug=debug
    )
    
    if result['found']:
        return True
    return False

def check_time_cho(screen_bgr=None, threshold=None, debug=False):
    """Kiểm tra xem có thời gian chờ không (nhiệm vụ đang chạy)"""
    if threshold is None:
        threshold = THRESHOLDS['time_cho']
    
    if screen_bgr is None:
        screen_bgr = load_screenshot_bgr(use_cache=True)
    
    template_path = TEMPLATE_PATHS['time_cho']
    scales = TEMPLATE_SCALES.get('item_nv', DEFAULT_SCALES)
    
    result = match_template_multiscale(
        screen_bgr, template_path,
        threshold=threshold,
        scales=scales,
        debug=debug
    )
    
    if result['found']:
        return True
    return False

def check_captra(screen_bgr=None, threshold=None, debug=False):
    """Kiểm tra xem có captcha không"""
    if threshold is None:
        threshold = THRESHOLDS['captra']
    
    logger.info(f"🔍 Đang kiểm tra captcha (ngưỡng={threshold})...")
    
    if screen_bgr is None:
        screen_bgr = load_screenshot_bgr(use_cache=True)
    
    template_path = TEMPLATE_PATHS['captra']
    scales = TEMPLATE_SCALES.get('captra', DEFAULT_SCALES)
    
    result = match_template_multiscale(
        screen_bgr, template_path,
        threshold=threshold,
        scales=scales,
        early_exit_conf=0.9,
        debug=debug
    )
    
    return result['found']

# ============================================
# CLICK FUNCTIONS (Tìm và click)
# ============================================

def click_task_title(screen_bgr=None, max_attempts=2, debug=False):
    """
    Tìm và click vào tiêu đề nhiệm vụ
    
    Args:
        screen_bgr: Screenshot BGR (None = tự chụp)
        max_attempts: Số lần thử tối đa
        debug: Debug mode
    
    Returns:
        bool: True nếu thành công
    """
    logger.info("🔍 Tìm tiêu đề nhiệm vụ...")
    time.sleep(random.uniform(0.05, 0.15))
    
    if screen_bgr is None:
        screen_bgr = load_screenshot_bgr(use_cache=True)
    
    template_path = TEMPLATE_PATHS['item_nv']
    
    for attempt in range(max_attempts):
        try:
            scales = TEMPLATE_SCALES.get('item_nv', DEFAULT_SCALES)
            result = match_template_multiscale(
                screen_bgr, template_path,
                threshold=THRESHOLDS['item_nv'],
                scales=scales,
                debug=debug
            )
            
            if result['found']:
                center_x, center_y = result['location']
                # Offset để click vào phần tiêu đề
                offset_left = 110
                click_x = center_x - offset_left
                click_y = result['bbox'][1] + int(result['bbox'][3] * 0.35)
                
                logger.info(f"✅ Tiêu đề đã tìm thấy (độ tin cậy={result['confidence']:.3f})")
                logger.info(f"👆 Nhấn tại ({click_x}, {click_y})")
                
                if not debug:
                    adb_tap(click_x, click_y, randomize=True, 
                           invalidate_callback=invalidate_screenshot_buffer)
                return True
            
            logger.debug(f"Lần thử {attempt+1}/{max_attempts} không thành công")
        except Exception as e:
            logger.error(f"Lỗi ở lần thử {attempt+1}: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(random.uniform(0.1, 0.2))
            screen_bgr = load_screenshot_bgr(force_refresh=True)
    
    logger.error("❌ Không tìm thấy tiêu đề nhiệm vụ!")
    return False

def click_confirm_button(screen_bgr=None, max_attempts=2, debug=False):
    """
    Tìm và click vào nút xác nhận
    
    Args:
        screen_bgr: Screenshot BGR (None = tự chụp)
        max_attempts: Số lần thử tối đa
        debug: Debug mode
    
    Returns:
        bool: True nếu thành công
    """
    logger.info("🔍 Đang tìm nút xác nhận...")
    time.sleep(random.uniform(0.05, 0.1))
    
    if screen_bgr is None:
        screen_bgr = load_screenshot_bgr(use_cache=True)
    
    template_path = TEMPLATE_PATHS['btn_xacnhan']
    
    for attempt in range(max_attempts):
        try:
            scales = TEMPLATE_SCALES.get('btn_xacnhan', DEFAULT_SCALES)
            result = match_template_multiscale(
                screen_bgr, template_path,
                threshold=THRESHOLDS['btn_xacnhan'],
                scales=scales,
                debug=debug
            )
            
            if result['found']:
                click_x, click_y = result['location']
                logger.info(f"✅ Nút xác nhận đã tìm thấy (độ tin cậy={result['confidence']:.3f})")
                
                if not debug:
                    adb_tap(click_x, click_y, randomize=True,
                           invalidate_callback=invalidate_screenshot_buffer)
                return True
            
            logger.debug(f"Lần thử {attempt+1}/{max_attempts} không thành công")
        except Exception as e:
            logger.error(f"Lỗi ở lần thử {attempt+1}: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(random.uniform(0.1, 0.15))
            screen_bgr = load_screenshot_bgr(force_refresh=True)
    
    logger.error("❌ Không tìm thấy nút xác nhận!")
    return False

def click_start_video(screen_bgr=None, max_attempts=2, debug=False):
    """
    Tìm và click vào nút start video
    
    Args:
        screen_bgr: Screenshot BGR (None = tự chụp)
        max_attempts: Số lần thử tối đa
        debug: Debug mode
    
    Returns:
        bool: True nếu thành công
    """
    logger.info("🔍 Đang tìm nút start video...")
    time.sleep(random.uniform(0.05, 0.1))
    
    if screen_bgr is None:
        screen_bgr = load_screenshot_bgr(use_cache=True)
    
    template_path = TEMPLATE_PATHS['start_video']
    
    for attempt in range(max_attempts):
        try:
            scales = TEMPLATE_SCALES.get('btn_xacnhan', DEFAULT_SCALES)
            result = match_template_multiscale(
                screen_bgr, template_path,
                threshold=THRESHOLDS['btn_start_video'],
                scales=scales,
                debug=debug
            )
            
            if result['found']:
                click_x, click_y = result['location']
                logger.info(f"✅ Nút start video đã tìm thấy (độ tin cậy={result['confidence']:.3f})")
                
                if not debug:
                    adb_tap(click_x, click_y, randomize=True,
                           invalidate_callback=invalidate_screenshot_buffer)
                return True
            
            logger.debug(f"Lần thử {attempt+1}/{max_attempts} không thành công")
        except Exception as e:
            logger.error(f"Lỗi ở lần thử {attempt+1}: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(random.uniform(0.1, 0.15))
            screen_bgr = load_screenshot_bgr(force_refresh=True)
    
    logger.error("❌ Không tìm thấy nút start video!")
    return False

# ============================================
# HIGH-LEVEL UI FUNCTIONS
# ============================================

def ensure_task_visible():
    """Đảm bảo có nhiệm vụ hiển thị trên màn hình (scroll nếu cần)"""
    if not check_nv():
        logger.info("📱 Không thấy nhiệm vụ, đang scroll lên...")
        scroll_up(30, invalidate_callback=invalidate_screenshot_buffer)
        time.sleep(random.uniform(0.5, 1.0))
        return check_nv()
    return True
