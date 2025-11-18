# PaddleOCR API for Vietnamese Documents

🚀 FastAPI service cung cấp OCR cho văn bản tiếng Việt sử dụng PaddleOCR

## ✨ Tính năng

- ✅ OCR tối ưu cho tiếng Việt
- ✅ Tự động xoay ảnh
- ✅ Hỗ trợ PDF nhiều trang
- ✅ High accuracy detection
- ✅ RESTful API đơn giản

## 📚 API Endpoints

### GET /
Thông tin API

### GET /health
Health check

### POST /ocr-pdf
OCR PDF file (multipart/form-data)

**Request:**
```bash
curl -X POST "https://your-api.railway.app/ocr-pdf" \
  -F "file=@document.pdf"
```

### POST /ocr-base64
OCR PDF từ base64 string (dành cho Apps Script)

**Request:**
```bash
curl -X POST "https://your-api.railway.app/ocr-base64" \
  -H "Content-Type: application/json" \
  -d '{"pdf_base64": "..."}'
```

**Response:**
```json
{
  "success": true,
  "text": "Nội dung văn bản...",
  "pages_processed": 3,
  "total_pages": 10,
  "total_chars": 5420
}
```

## 🚀 Deploy

Xem file `HUONG_DAN_DEPLOY.md` để biết chi tiết.

**Tóm tắt:**
1. Upload code lên GitHub
2. Deploy từ Railway.app
3. Lấy URL public
4. Tích hợp vào Apps Script

## 🔧 Tech Stack

- **FastAPI** - Web framework
- **PaddleOCR** - OCR engine
- **PyMuPDF** - PDF processing
- **Pillow** - Image processing
- **Railway** - Cloud platform

## 📊 Performance

- **Tốc độ:** ~2-3s/file
- **Độ chính xác:** 96-98% (Vietnamese)
- **RAM:** ~500MB
- **Giới hạn file:** 10MB

## 📝 License

Free to use

## 👨‍💻 Author

Phát triển cho hệ thống xử lý văn bản hành chính Việt Nam
