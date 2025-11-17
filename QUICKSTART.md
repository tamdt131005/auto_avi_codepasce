# ⚡ QUICK START GUIDE

## 🚀 CHẠY NGAY

```bash
# Chạy bản mới (modular + optimized)
python main_modular.py

# Hoặc giữ bản cũ
python main.py
```

## 🎯 CẤU HÌNH NHANH

### File: `config.py`

```python
# Số nhiệm vụ cần hoàn thành
AUTOMATION_CONFIG = {
    'max_count': 50,  # ← Đổi số này
    
    # Nghỉ sau bao nhiêu nhiệm vụ
    'break_interval': 25,  # ← Đổi số này
    
    # Thời gian nghỉ (giây)
    'break_duration': (2, 5),  # (min, max)
}
```

## 🔧 TÙY CHỈNH TỐC ĐỘ

### Level 1: An toàn (Khuyến nghị)
```python
# File: config.py
'button_check_intervals': [
    *[0.4] * 12,  # ← GIỮ NGUYÊN
    *[0.6] * 5,
    *[1.0] * 4
]
# Tốc độ: ~6-7 nhiệm vụ/phút
```

### Level 2: Nhanh hơn (Nếu muốn)
```python
'button_check_intervals': [
    *[0.3] * 15,  # ← Đổi 0.4 thành 0.3
    *[0.5] * 7,
    *[0.8] * 4
]
# Tốc độ: ~8-9 nhiệm vụ/phút
```

### Level 3: Cực nhanh (Không khuyến khích)
```python
'button_check_intervals': [
    *[0.2] * 20,  # ← Quá nhanh!
    *[0.4] * 8,
    *[0.6] * 5
]
# Tốc độ: ~10-12 nhiệm vụ/phút
# ⚠️ Có thể bị phát hiện!
```

## 📊 XEM THỐNG KÊ

### Trong quá trình chạy:
```
✅ Đã hoàn thành 25/50
📊 Thành công: 25 | Thất bại: 2 | Captcha: 3 | Video: 5
⚡ Tốc độ: 7.2/phút | Trung bình: 8.3s/nhiệm vụ
⏱️ Thời gian chờ nút TB: 4.2s
```

### Chú ý:
- **Thời gian chờ nút TB > 5s**: Tăng frequency check
- **Miss rate > 20%**: Mở rộng check window
- **Nhiều lỗi**: Giảm frequency

## 🐛 DEBUG

### Bật debug mode:
```python
# File: main_modular.py hoặc workflow.py
# Tìm dòng:
click_task_title(screen_bgr=screen, debug=False)

# Đổi thành:
click_task_title(screen_bgr=screen, debug=True)
```

### Kết quả:
- Tạo file ảnh `debug_*.png` 
- Vẽ bounding box và confidence score
- Giúp kiểm tra template matching

## 📁 CẤU TRÚC FILES

```
d:\auto_aviso_model\
├── main_modular.py      ← RUN THIS!
├── config.py            ← EDIT CONFIG HERE
├── workflow.py
├── task_detector.py
├── template_matcher.py
├── adb_bridge.py
├── stats.py
├── amthanh.py
├── models.py            (legacy)
├── main.py              (old version)
└── templates/
    ├── item_nv.jpg
    ├── btn_xacnhan.jpg
    ├── captra.jpg
    ├── time_cho.jpg
    └── start_video.png
```

## ⚠️ TROUBLESHOOTING

### Lỗi: "Module not found"
```bash
# Kiểm tra tất cả files có đầy đủ không
ls *.py

# Cần có:
# config.py
# adb_bridge.py
# template_matcher.py
# task_detector.py
# workflow.py
# stats.py
# main_modular.py
```

### Lỗi: "Template not found"
```bash
# Kiểm tra folder templates
ls templates/

# Cần có:
# item_nv.jpg
# btn_xacnhan.jpg
# captra.jpg
# time_cho.jpg
# start_video.png
```

### Lỗi: "ADB not found"
```bash
# Kiểm tra ADB
adb devices

# Nếu dùng ADB Bridge:
# Kiểm tra config.py
USE_ADB_BRIDGE = True
ADB_BRIDGE_URL = "https://your-ngrok-url/"
```

## 🔄 SO SÁNH KẾT QUẢ

### Chạy bản cũ:
```bash
python main.py
# Ghi lại: Tốc độ, thời gian TB, miss rate
```

### Chạy bản mới:
```bash
python main_modular.py
# So sánh với kết quả trên
```

### Kỳ vọng:
- Tốc độ: +40-60%
- Thời gian TB: -25-33%
- Miss rate: -62%

## 💾 BACKUP

### Trước khi chạy:
```bash
# Backup config cũ
copy config.py config.py.backup

# Hoặc toàn bộ
xcopy /E /I . ..\backup_auto_aviso
```

## 🎉 CHECKLIST

- [ ] Đã có đầy đủ files `.py`
- [ ] Đã có folder `templates/` với đủ ảnh
- [ ] Đã chỉnh `max_count` trong `config.py`
- [ ] ADB hoặc ADB Bridge hoạt động
- [ ] Test chạy `python main_modular.py`
- [ ] Monitor stats trong vài nhiệm vụ đầu
- [ ] Fine-tune config nếu cần
- [ ] Chạy full và so sánh với bản cũ

## 📞 HỖ TRỢ

### Đọc thêm:
- `README_MODULAR.md` - Hướng dẫn chi tiết
- `STRATEGY_OPTIMIZATION.md` - Giải thích chiến lược
- `ARCHITECTURE.md` - Kiến trúc hệ thống
- `SUMMARY.md` - Tóm tắt nhanh

### Key points:
1. Bắt đầu với config mặc định (Level 1)
2. Monitor stats để điều chỉnh
3. Không chỉnh sửa logic, chỉ config
4. Backup trước khi thay đổi lớn

## 🚀 QUICK WINS

### 1. Chạy ngay với config mặc định
```bash
python main_modular.py
```

### 2. Nếu chạy tốt, tăng tốc độ
```python
# config.py
*[0.3] * 15  # thay vì 0.4
```

### 3. Nếu gặp vấn đề, giảm tốc độ
```python
# config.py
*[0.5] * 10  # thay vì 0.4
```

### 4. Monitor và fine-tune
- Xem "Thời gian chờ nút TB"
- Điều chỉnh intervals cho phù hợp

## ✅ DONE!

Giờ bạn đã sẵn sàng chạy automation với tốc độ tăng 40-60%! 🎉
