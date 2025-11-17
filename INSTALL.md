# 🚀 HƯỚNG DẪN CÀI ĐẶT

## ✅ YÊU CẦU

### Python
- Python 3.7 trở lên
- Khuyến nghị: Python 3.9+

### Tesseract OCR
- Tải và cài đặt từ: https://github.com/UB-Mannheim/tesseract/wiki
- Đường dẫn mặc định: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### ADB (Android Debug Bridge)
- Tải platform-tools: https://developer.android.com/studio/releases/platform-tools
- Thêm vào PATH hoặc đặt trong thư mục project

## 📦 CÀI ĐẶT THỨ VIỆN

### Cách 1: Cài đặt tất cả (Khuyến nghị)
```bash
pip install -r requirements.txt
```

### Cách 2: Cài đặt từng thứ viện
```bash
# Core (BẮT BUỘC)
pip install opencv-python numpy Pillow pytesseract

# Requests - CHỈ CẦN nếu dùng ADB Bridge qua HTTP
pip install requests

# Audio - CHỈ CẦN nếu muốn cảnh báo âm thanh
pip install pygame
```

## ⚙️ CẤU HÌNH

### Nếu KHÔNG dùng ADB Bridge
Chỉnh file `config.py`:
```python
USE_ADB_BRIDGE = False  # Đổi từ True sang False
```

**Lợi ích:**
- Không cần cài `requests`
- Sử dụng ADB trực tiếp (nhanh hơn)
- Ít dependencies hơn

### Nếu dùng ADB Bridge
1. Cài đặt requests:
```bash
pip install requests
```

2. Đảm bảo ADB Bridge server đang chạy

3. Cập nhật URL trong `config.py`:
```python
USE_ADB_BRIDGE = True
ADB_BRIDGE_URL = "https://your-ngrok-url/"
```

## 🔍 KIỂM TRA CÀI ĐẶT

### Test Python modules
```bash
python -c "import cv2, numpy, PIL; print('OK')"
```

### Test ADB
```bash
adb devices
```

### Test Tesseract
```bash
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

## 🚀 CHẠY

### Bản mới (Modular)
```bash
python main_modular.py
```

### Bản cũ
```bash
python main.py
```

## ❌ XỬ LÝ LỖI

### Lỗi: "No module named 'requests'"
**Giải pháp 1:** Cài requests
```bash
pip install requests
```

**Giải pháp 2:** Tắt ADB Bridge
```python
# config.py
USE_ADB_BRIDGE = False
```

### Lỗi: "No module named 'cv2'"
```bash
pip install opencv-python
```

### Lỗi: "ADB not found"
- Cài đặt ADB platform-tools
- Thêm vào PATH
- Hoặc copy `adb.exe` vào thư mục project

### Lỗi: "Tesseract not found"
```python
# models.py hoặc đầu file sử dụng pytesseract
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## 📋 CHECKLIST CÀI ĐẶT

- [ ] Python 3.7+ đã cài
- [ ] Tesseract OCR đã cài
- [ ] ADB đã cài và trong PATH
- [ ] `pip install opencv-python numpy Pillow pytesseract`
- [ ] Nếu dùng ADB Bridge: `pip install requests`
- [ ] Nếu muốn audio: `pip install pygame`
- [ ] Test: `python -c "import cv2, numpy, PIL"`
- [ ] Test: `adb devices`
- [ ] Chỉnh `config.py` phù hợp
- [ ] Chạy thử: `python main_modular.py`

## 💡 KHUYẾN NGHỊ

### Cho người mới bắt đầu:
1. **KHÔNG dùng ADB Bridge** (set `USE_ADB_BRIDGE = False`)
2. Chỉ cài: `pip install opencv-python numpy Pillow pytesseract`
3. Bỏ qua pygame nếu không cần audio
4. Đơn giản và ít lỗi hơn!

### Cho người có kinh nghiệm:
1. Cài đầy đủ: `pip install -r requirements.txt`
2. Tùy chỉnh config theo nhu cầu
3. Sử dụng ADB Bridge nếu cần remote

## 🎯 TÓM TẮT NHANH

```bash
# Cài đặt tối thiểu
pip install opencv-python numpy Pillow pytesseract

# Chỉnh config
# config.py -> USE_ADB_BRIDGE = False

# Chạy
python main_modular.py
```

## ✅ DONE!

Sau khi cài đặt xong, đọc [QUICKSTART.md](QUICKSTART.md) để bắt đầu sử dụng!
