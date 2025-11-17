# ⚡ GIẢI QUYẾT LỖI "No module named 'requests'"

## 🎯 GIẢI PHÁP NHANH NHẤT (KHUYẾN NGHỊ)

### Bước 1: Tắt ADB Bridge
Mở file `config.py` và thay đổi:

```python
# Tìm dòng này:
USE_ADB_BRIDGE = os.getenv('USE_ADB_BRIDGE', 'true').lower() == 'true'

# Đổi thành:
USE_ADB_BRIDGE = False
```

### Bước 2: Chạy lại
```bash
python main_modular.py
```

**✅ XONG! Bạn không cần cài requests nữa!**

---

## 🔧 GIẢI PHÁP 2: CÀI ĐẶT REQUESTS

Nếu bạn thực sự cần dùng ADB Bridge:

```bash
pip install requests
```

Hoặc cài đầy đủ:
```bash
pip install -r requirements.txt
```

---

## 📊 SO SÁNH HAI CÁCH

### Không dùng ADB Bridge (USE_ADB_BRIDGE = False)
✅ Không cần cài requests  
✅ Đơn giản hơn  
✅ Nhanh hơn (ADB trực tiếp)  
✅ Ít lỗi hơn  
❌ Chỉ chạy được trên máy có kết nối ADB trực tiếp  

### Dùng ADB Bridge (USE_ADB_BRIDGE = True)
✅ Có thể control từ xa qua HTTP  
✅ Flexible hơn  
❌ Cần cài requests  
❌ Cần setup server ADB Bridge  
❌ Phức tạp hơn  

---

## 🚀 HƯỚNG DẪN ĐẦY ĐỦ

Xem file [INSTALL.md](INSTALL.md) để biết thêm chi tiết.

---

## ✅ CHECKLIST

- [ ] Đã chỉnh `USE_ADB_BRIDGE = False` trong config.py
- [ ] Chạy lại: `python main_modular.py`
- [ ] Nếu vẫn lỗi khác, xem [INSTALL.md](INSTALL.md)
