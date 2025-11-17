"""
🚀 ULTRA SPEED AUTOMATION - MODULAR VERSION
Main entry point cho automation với kiến trúc module hóa

Cấu trúc module:
- config.py: Tất cả cấu hình
- adb_bridge.py: Thao tác ADB
- template_matcher.py: Matching và cache
- task_detector.py: Phát hiện UI elements
- workflow.py: Luồng xử lý chính
- stats.py: Thống kê và báo cáo
"""

import sys
import logging

# Setup logging
from config import LOG_LEVEL, LOG_FORMAT
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Import modules
try:
    from config import AUTOMATION_CONFIG
    from stats import Stats
    from workflow import (
        execute_single_task,
        should_take_break,
        take_smart_break,
        smart_wait
    )
    from template_matcher import invalidate_screenshot_buffer
except ImportError as e:
    logger.error(f"❌ Lỗi khi import module: {e}")
    logger.error("Vui lòng đảm bảo tất cả các module nằm cùng thư mục")
    sys.exit(1)

# ============================================
# MAIN LOOP
# ============================================

def main():
    """Main execution loop"""
    
    # Configuration
    max_count = AUTOMATION_CONFIG['max_count']
    
    # Statistics
    stats = Stats()
    count = 0
    
    # Print header
    logger.info("=" * 80)
    logger.info("🚀 ULTRA SPEED AUTOMATION - MODULAR VERSION với TỐI ƯU CHO NHIỆM VỤ NGẮN")
    logger.info("=" * 80)
    logger.info(f"🎯 Target: {max_count} nhiệm vụ")
    logger.info(f"⚡ Tối ưu hóa:")
    logger.info(f"   ✅ Kiến trúc module hóa - dễ bảo trì")
    logger.info(f"   ✅ Template cache với scaled versions")
    logger.info(f"   ✅ Screenshot buffer (TTL=300ms)")
    logger.info(f"   ✅ Early exit khi confidence > 0.85")
    logger.info(f"   ✅ Captcha detection & handling thông minh")
    logger.info(f"   ✅ 🔥 NHIỆM VỤ NGẮN: Check mỗi 0.4s trong 5s đầu (12 lần)")
    logger.info(f"   ✅ 🎥 NHIỆM VỤ DÀI: Check progressive lên tới 3 phút")
    logger.info(f"   ✅ Giảm delay tổng thể 30-40%")
    logger.info("=" * 80)
    logger.info("📋 Workflow:")
    logger.info("   Đảm bảo task visible → Click task → Check type → Handle video")
    logger.info("   → Check captcha → Wait button (tối ưu) → Confirm")
    logger.info("=" * 80)
    logger.info("")
    logger.info("🔥 CHIẾN LƯỢC MỚI CHO NHIỆM VỤ NGẮN:")
    logger.info("   - Video tự chạy: ~2s")
    logger.info("   - Còn lại: ~8s")
    logger.info("   - Delay kiểm tra: ~1s")
    logger.info("   - THỜI GIAN THỰC TẾ CÒN: ~7s")
    logger.info("   → Check liên tục mỗi 0.4s trong 5s đầu!")
    logger.info("=" * 80)
    
    # Initial delay
    import time, random
    time.sleep(random.uniform(0.5, 1.0))
    
    # Main loop
    while count < max_count:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Nhiệm vụ [{count + 1}/{max_count}]")
            logger.info(f"{'='*60}")
            
            # Take break if needed
            if should_take_break(count):
                take_smart_break()
            
            # Execute task
            success = execute_single_task(stats)
            
            if success:
                count += 1
                stats.record_success()
                stats.print_progress(count, max_count)
            else:
                stats.record_failure()
                logger.warning("❌ Nhiệm vụ thất bại. Đang thử lại...")
                smart_wait(*AUTOMATION_CONFIG['retry_delay'])
                continue
            
            # Inter-action delay
            inter_delay = smart_wait(*AUTOMATION_CONFIG['inter_action_delay'])
            logger.debug(f"⏱️  Inter-action delay: {inter_delay:.2f}s")
            
        except KeyboardInterrupt:
            logger.info("\n\n⛔ Dừng bởi người dùng (Ctrl+C)")
            break
            
        except Exception as e:
            logger.error(f"❌ Lỗi không mong đợi: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            stats.record_failure()
            logger.info("⏳ Chờ 2s trước khi thử lại...")
            smart_wait(2.0, 0.5)
            invalidate_screenshot_buffer()
            continue
    
    # Print final statistics
    stats.print_final(max_count)

# ============================================
# ENTRY POINT
# ============================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Lỗi nghiêm trọng: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
