FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

---

## 🚀 CÁCH SỬA (15 GIÂY)
```
1. GitHub → Dockerfile → Edit (bút ✏️)
2. Xóa TẤT CẢ
3. Paste 13 dòng trên
4. Commit
5. Railway auto-deploy (10 phút)
6. XONG! ✅
```

---

## 📦 HOẶC DOWNLOAD ZIP MỚI

[**paddleocr-api.zip**](computer:///mnt/user-data/outputs/paddleocr-api.zip) - **ĐÃ FIX package names!**

Deploy từ đầu với files đúng!

---

## 📚 HƯỚNG DẪN

- [PACKAGE_FIX_QUICK.md](computer:///mnt/user-data/outputs/PACKAGE_FIX_QUICK.md) - Quick (1 trang)
- [FIX_PACKAGE_NAME.md](computer:///mnt/user-data/outputs/FIX_PACKAGE_NAME.md) - Chi tiết

---

## ✅ SAU KHI FIX

Railway logs:
```
✅ FROM python:3.11-slim
✅ Installing libgl1 (package mới)
✅ Installing libgomp1
✅ Successfully installed paddleocr-2.8.1
✅ Server đã khởi động!
```

Health check:
```
https://your-app.railway.app/health
→ {"status": "healthy"} ✅
