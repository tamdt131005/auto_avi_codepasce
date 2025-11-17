"""
Statistics module - Theo dõi và báo cáo thống kê
"""

import logging
import time

logger = logging.getLogger(__name__)

# ============================================
# STATISTICS CLASS
# ============================================

class Stats:
    """Theo dõi thống kê trong quá trình automation"""
    
    def __init__(self):
        self.success_count = 0
        self.fail_count = 0
        self.captcha_count = 0
        self.long_task_count = 0
        self.start_time = time.time()
        self.button_wait_times = []
        self.long_task_wait_times = []
    
    def record_success(self):
        """Ghi nhận thành công"""
        self.success_count += 1
    
    def record_failure(self):
        """Ghi nhận thất bại"""
        self.fail_count += 1
    
    def record_captcha(self):
        """Ghi nhận gặp captcha"""
        self.captcha_count += 1
    
    def record_long_task(self):
        """Ghi nhận gặp nhiệm vụ dài"""
        self.long_task_count += 1
    
    def record_button_wait(self, wait_time, is_long_task=False):
        """
        Ghi nhận thời gian chờ nút
        
        Args:
            wait_time: Thời gian chờ (giây)
            is_long_task: Có phải nhiệm vụ dài không
        """
        self.button_wait_times.append(wait_time)
        if is_long_task:
            self.long_task_wait_times.append(wait_time)
    
    def get_elapsed(self):
        """Lấy thời gian đã chạy"""
        return time.time() - self.start_time
    
    def get_avg_time(self):
        """Lấy thời gian trung bình mỗi nhiệm vụ"""
        if self.success_count == 0:
            return 0
        return self.get_elapsed() / self.success_count
    
    def get_rate(self):
        """Lấy tốc độ nhiệm vụ/phút"""
        elapsed_minutes = self.get_elapsed() / 60
        if elapsed_minutes == 0:
            return 0
        return self.success_count / elapsed_minutes
    
    def get_success_rate(self):
        """Lấy tỉ lệ thành công %"""
        total = self.success_count + self.fail_count
        if total == 0:
            return 0
        return (self.success_count / total) * 100
    
    def get_avg_button_wait(self):
        """Lấy thời gian chờ nút trung bình"""
        if not self.button_wait_times:
            return 0
        return sum(self.button_wait_times) / len(self.button_wait_times)
    
    def get_avg_long_task_wait(self):
        """Lấy thời gian chờ nhiệm vụ dài trung bình"""
        if not self.long_task_wait_times:
            return 0
        return sum(self.long_task_wait_times) / len(self.long_task_wait_times)
    
    def format_time(self, seconds):
        """Định dạng giây thành chuỗi dễ đọc"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    
    def print_progress(self, current, target):
        """In tiến độ hiện tại"""
        elapsed = self.get_elapsed()
        avg_time = self.get_avg_time()
        remaining = avg_time * (target - current)
        rate = self.get_rate()
        
        logger.info(f"✅ Đã hoàn thành {current}/{target}")
        logger.info(f"📊 Thành công: {self.success_count} | Thất bại: {self.fail_count} | Captcha: {self.captcha_count} | Video: {self.long_task_count}")
        logger.info(f"⚡ Tốc độ: {rate:.1f}/phút | Trung bình: {avg_time:.1f}s/nhiệm vụ")
        logger.info(f"🕐 Đã chạy: {self.format_time(elapsed)} | ETA: {self.format_time(remaining)}")
        
        if self.button_wait_times:
            avg_btn_wait = self.get_avg_button_wait()
            logger.info(f"⏱️  Thời gian chờ nút TB: {avg_btn_wait:.1f}s")
            
            if self.long_task_wait_times:
                avg_long_wait = self.get_avg_long_task_wait()
                logger.info(f"🎥 Thời gian chờ nhiệm vụ dài TB: {avg_long_wait:.1f}s")
    
    def print_final(self, target):
        """In thống kê cuối cùng"""
        total_time = self.get_elapsed()
        
        logger.info(f"\n{'='*60}")
        logger.info("🎉 HOÀN THÀNH TỰ ĐỘNG HÓA!")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Thành công: {self.success_count}/{target}")
        logger.info(f"❌ Thất bại: {self.fail_count}")
        logger.info(f"🔒 Số lần gặp captcha: {self.captcha_count}")
        logger.info(f"🎥 Số lần gặp nhiệm vụ dài: {self.long_task_count}")
        logger.info(f"⏱️  Tổng thời gian: {self.format_time(total_time)}")
        
        if self.success_count > 0:
            avg = self.get_avg_time()
            rate = self.get_rate()
            efficiency = self.get_success_rate()
            
            logger.info(f"📊 Thời gian trung bình: {avg:.2f}s mỗi nhiệm vụ")
            logger.info(f"⚡ Tốc độ: {rate:.1f} nhiệm vụ/phút")
            logger.info(f"🎯 Tỉ lệ thành công: {efficiency:.1f}%")
            
            if self.captcha_count > 0:
                captcha_rate = (self.captcha_count / target) * 100
                logger.info(f"🔒 Tỉ lệ captcha: {captcha_rate:.1f}%")
            
            if self.long_task_count > 0:
                long_task_rate = (self.long_task_count / self.success_count) * 100
                logger.info(f"🎥 Tỉ lệ nhiệm vụ dài: {long_task_rate:.1f}%")
            
            if self.button_wait_times:
                avg_btn_wait = self.get_avg_button_wait()
                min_wait = min(self.button_wait_times)
                max_wait = max(self.button_wait_times)
                logger.info(f"⏱️  Thời gian đợi nút: TB={avg_btn_wait:.1f}s, min={min_wait:.1f}s, max={max_wait:.1f}s")
                
                if self.long_task_wait_times:
                    avg_long_wait = self.get_avg_long_task_wait()
                    min_long_wait = min(self.long_task_wait_times)
                    max_long_wait = max(self.long_task_wait_times)
                    logger.info(f"🎥 Thời gian đợi nút (video): TB={avg_long_wait:.1f}s, min={min_long_wait:.1f}s, max={max_long_wait:.1f}s")
        
        logger.info(f"{'='*60}")
