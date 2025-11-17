"""
Workflow module - Luồng xử lý chính cho automation
"""

import logging
import time
import random

from config import AUTOMATION_CONFIG
from template_matcher import load_screenshot_bgr, invalidate_screenshot_buffer
from task_detector import (
    ensure_task_visible,
    click_task_title,
    check_btn_start_video,
    click_start_video,
    check_time_cho,
    check_captra,
    check_btn_xn,
    click_confirm_button
)
from adb_bridge import adb_back

logger = logging.getLogger(__name__)

# Audio imports (optional)
try:
    from amthanh import start_alert, stop_alert
    AUDIO_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  Mô-đun âm thanh không khả dụng - cảnh báo tắt")
    AUDIO_AVAILABLE = False
    def start_alert(): pass
    def stop_alert(): pass

# ============================================
# CAPTCHA HANDLING
# ============================================

def wait_and_solve_captcha(max_wait=None, check_interval=None):
    """
    Chờ và xử lý captcha nếu xuất hiện
    
    Args:
        max_wait: Thời gian tối đa chờ (giây)
        check_interval: Khoảng thời gian kiểm tra (giây)
    
    Returns:
        True nếu captcha đã được giải hoặc không có captcha
        False nếu quá thời gian chờ
    """
    if max_wait is None:
        max_wait = AUTOMATION_CONFIG['captcha_timeout']
    if check_interval is None:
        check_interval = AUTOMATION_CONFIG['captcha_check_interval']
    
    logger.info("🔍 Kiểm tra captcha...")
    start_time = time.time()
    
    # Kiểm tra ban đầu
    screen = load_screenshot_bgr(force_refresh=True)
    
    if not check_captra(screen, threshold=0.5):
        logger.debug("✅ Không phát hiện captcha")
        return True
    
    # Phát hiện captcha
    logger.warning("🔒 PHÁT HIỆN CAPTCHA!")
    
    # Phát âm báo nếu có
    if AUDIO_AVAILABLE:
        start_alert()
        time.sleep(3)
        stop_alert()
    else:
        logger.info("🔔 [BEEP] Vui lòng giải captcha!")
    
    logger.info(f"⏳ Đang chờ tối đa {max_wait}s cho captcha được giải...")
    
    captcha_start = time.time()
    checks = 0
    
    while time.time() - captcha_start < max_wait:
        time.sleep(check_interval)
        checks += 1
        
        screen = load_screenshot_bgr(force_refresh=True)
        
        # Kiểm tra nếu captcha đã biến mất
        if not check_captra(screen, threshold=0.5):
            elapsed = time.time() - captcha_start
            logger.info(f"✅ Captcha đã được giải sau {elapsed:.1f}s ({checks} lần kiểm tra)")
            invalidate_screenshot_buffer()
            return True
        
        elapsed = time.time() - captcha_start
        remaining = max_wait - elapsed
        logger.debug(f"⏳ Vẫn đang chờ... ({remaining:.0f}s còn lại, kiểm tra #{checks})")
    
    # Hết thời gian chờ
    logger.error(f"❌ Hết thời gian chờ captcha sau {max_wait}s")
    return False

# ============================================
# BUTTON WAITING
# ============================================

def wait_for_button(check_intervals=None, threshold=0.7, is_long_task=False):
    """
    Chờ nút xác nhận xuất hiện với kiểm tra tăng dần
    
    Args:
        check_intervals: Danh sách khoảng thời gian kiểm tra
        threshold: Ngưỡng so khớp template
        is_long_task: True nếu là nhiệm vụ dài (video)
    
    Returns:
        (found, screen, wait_time) tuple
    """
    if check_intervals is None:
        if is_long_task:
            check_intervals = AUTOMATION_CONFIG['long_task_check_intervals']
        else:
            check_intervals = AUTOMATION_CONFIG['button_check_intervals']
    
    task_type = "nhiệm vụ DÀI (video)" if is_long_task else "nhiệm vụ NGẮN"
    max_time = sum(check_intervals)
    
    logger.info(f"🔍 Đang chờ nút xác nhận ({task_type})...")
    
    total_waited = 0
    milestone_25 = False
    milestone_60 = False
    milestone_120 = False
    
    for idx, interval in enumerate(check_intervals):
        # Nghỉ
        time.sleep(interval)
        total_waited += interval
        
        # Hiển thị milestone cho nhiệm vụ dài
        if is_long_task:
            if total_waited >= 25 and not milestone_25:
                logger.info(f"⏱️  [Milestone] Đã chờ 25s...")
                milestone_25 = True
            elif total_waited >= 60 and not milestone_60:
                logger.info(f"⏱️  [Milestone] Đã chờ 1 phút...")
                milestone_60 = True
            elif total_waited >= 120 and not milestone_120:
                logger.info(f"⏱️  [Milestone] Đã chờ 2 phút...")
                milestone_120 = True
        else:
            # Với nhiệm vụ ngắn, không log chi tiết
            pass
        
        # Chụp ảnh mới
        screen = load_screenshot_bgr(force_refresh=True)
        
        # Kiểm tra nút
        if check_btn_xn(screen_bgr=screen, threshold=threshold, debug=False):
            logger.info(f"✅ Đã tìm thấy nút sau {total_waited:.1f}s! ({task_type})")
            return True, screen, total_waited
        
        # Log tiến độ chi tiết cho nhiệm vụ dài
        if is_long_task:
            remaining = max_time - total_waited
            if idx % 5 == 0 or remaining < 10:
                logger.debug(f"⏳ Vẫn đang chờ... ({total_waited:.0f}s/{max_time:.0f}s)")
    
    logger.warning(f"⏱️  Hết thời gian chờ nút sau {total_waited:.1f}s ({task_type})")
    return False, None, total_waited

# ============================================
# MAIN TASK EXECUTION
# ============================================

def execute_single_task(stats):
    """
    Thực hiện một nhiệm vụ đơn
    
    Args:
        stats: Đối tượng thống kê để ghi lại kết quả
    
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    is_long_task = False  # Flag để theo dõi loại nhiệm vụ
    
    # Đảm bảo có nhiệm vụ trên màn hình
    if not ensure_task_visible():
        logger.warning("⚠️  Không thể tìm thấy nhiệm vụ sau khi scroll")
        return False
    
    # ============================================
    # Step 1: Click task
    # ============================================
    logger.info("📸 Step 1: Chụp màn hình và click nhiệm vụ...")
    screen = load_screenshot_bgr(use_cache=False, force_refresh=True)
    
    if not click_task_title(screen_bgr=screen, debug=False):
        logger.warning("⚠️  Không tìm thấy nhiệm vụ để click")
        return False
    
    logger.info("✅ Đã click nhiệm vụ")
    time.sleep(random.uniform(1.8, 2.0))  # Giảm từ 2.0-2.5
    
    # ============================================
    # Step 1.5: Kiểm tra loại nhiệm vụ
    # ============================================
    logger.info("📸 Chụp lại để kiểm tra loại nhiệm vụ...")
    screen = load_screenshot_bgr(use_cache=False, force_refresh=True)
    
    # Kiểm tra nếu là nhiệm vụ dài (video)
    if check_btn_start_video(screen_bgr=screen, debug=False):
        is_long_task = True
        stats.record_long_task()
        
        logger.info("🎥 NHIỆM VỤ DÀI! Bắt đầu video...")
        time.sleep(random.uniform(0.2, 0.5))  # Giảm từ 0.3-0.8
        
        if not click_start_video(screen_bgr=screen, debug=False):
            logger.warning("⚠️  Không thể nhấn nút bắt đầu video")
            return False
        
        logger.info("✅ Đã nhấn nút bắt đầu video")
        time.sleep(random.uniform(0.6, 1.2))  # Giảm từ 0.8-1.5
        adb_back(invalidate_callback=invalidate_screenshot_buffer)
        logger.info("✅ Quay lại sau khi bắt đầu video")
        
        time.sleep(random.uniform(0.4, 0.8))  # Giảm từ 0.5-1.0
        screen = load_screenshot_bgr(use_cache=False, force_refresh=True)
    
    # ============================================
    # Step 2: Kiểm tra trạng thái nhiệm vụ
    # ============================================
    has_time_wait = check_time_cho()
    
    if has_time_wait:
        logger.info("✅ Phát hiện thời gian chờ, tiếp tục chờ nút xác nhận...")
    else:
        logger.info("⏱️  Không có thời gian chờ, kiểm tra captcha...")
        
        # Giảm page load delay cho nhiệm vụ ngắn
        if is_long_task:
            page_load_time = random.uniform(*AUTOMATION_CONFIG['page_load_delay'])
        else:
            # 🚀 TỐI ƯU: Giảm delay cho nhiệm vụ ngắn
            page_load_time = random.uniform(1.5, 2.0)  # Giảm mạnh từ 2.5-3.5
        
        time.sleep(page_load_time)
        
        # Chụp lại để kiểm tra captcha
        screen = load_screenshot_bgr(use_cache=False, force_refresh=True)
        
        # Kiểm tra captcha
        if check_captra(screen, threshold=0.5):
            logger.warning("🔒 Phát hiện captcha, đang xử lý...")
            if not wait_and_solve_captcha():
                logger.error("❌ Failed to solve captcha")
                stats.record_captcha()
                return False
            
            stats.record_captcha()
            logger.info("⏳ Chờ UI refresh sau captcha...")
            post_captcha_delay = random.uniform(*AUTOMATION_CONFIG['post_captcha_delay'])
            time.sleep(post_captcha_delay)
            logger.info("✅ Captcha đã giải, tiếp tục...")
        else:
            logger.info("🔄 Không có captcha và không có thời gian chờ, chạy lại...")
            time.sleep(random.uniform(0.4, 0.8))  # Giảm từ 0.5-1.0
            return execute_single_task(stats)
    
    # ============================================
    # Step 3: Chờ nút xác nhận
    # ============================================
    task_type_label = "nhiệm vụ DÀI (video)" if is_long_task else "nhiệm vụ NGẮN"
    logger.info(f"🔍 Step 3: Chờ nút xác nhận ({task_type_label})...")
    
    btn_found, screen, wait_time = wait_for_button(
        check_intervals=None,
        is_long_task=is_long_task
    )
    
    if not btn_found:
        logger.warning(f"⏱️  Button timeout ({task_type_label})")
        return False
    
    stats.record_button_wait(wait_time, is_long_task=is_long_task)
    
    # Minimal delay trước khi click
    time.sleep(random.uniform(0.05, 0.15))
    
    # ============================================
    # Step 4: Click confirm
    # ============================================
    logger.info("👆 Step 4: Click nút xác nhận...")
    
    if not click_confirm_button(screen_bgr=screen, debug=False):
        logger.warning("⚠️  Failed to click confirm button")
        return False
    
    logger.info("✅ Đã click nút xác nhận")
    return True

# ============================================
# UTILITY FUNCTIONS
# ============================================

def should_take_break(count, interval=None):
    """Kiểm tra xem có đến lúc nghỉ không"""
    if interval is None:
        interval = AUTOMATION_CONFIG['break_interval']
    return count > 0 and count % interval == 0

def take_smart_break():
    """Thực hiện nghỉ với thời lượng ngẫu nhiên"""
    duration = random.uniform(*AUTOMATION_CONFIG['break_duration'])
    logger.info(f"⏸️  Nghỉ trong {duration:.1f}s...")
    time.sleep(duration)
    invalidate_screenshot_buffer()
    logger.info("▶️  Tiếp tục...")

def smart_wait(base=0.3, variance=0.15):
    """
    Chờ thông minh có ngẫu nhiên hóa
    
    Returns:
        float: Thời gian thực tế đã chờ
    """
    wait_time = max(0.1, base + random.uniform(-variance, variance))
    time.sleep(wait_time)
    return wait_time
