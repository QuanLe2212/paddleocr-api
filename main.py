from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
import base64
import io
from PIL import Image
import fitz  # PyMuPDF
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PaddleOCR API for Vietnamese Documents",
    description="OCR service optimized for Vietnamese administrative documents",
    version="1.0.0"
)

# CORS - cho phép Apps Script gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo PaddleOCR - CHỈ 1 LẦN khi start server
logger.info("Đang khởi tạo PaddleOCR...")
ocr = PaddleOCR(
    use_angle_cls=True,  # Tự động xoay ảnh
    lang='vi',           # Tiếng Việt
    show_log=False,      # Không spam log
    use_gpu=False,       # Railway dùng CPU
    det_db_thresh=0.3,   # Ngưỡng detect text
    det_db_box_thresh=0.5,  # Ngưỡng box
    rec_batch_num=6      # Batch size cho recognition
)
logger.info("PaddleOCR sẵn sàng!")

@app.get("/")
def home():
    """Trang chủ - Thông tin API"""
    return {
        "status": "running",
        "service": "PaddleOCR API for Vietnamese Documents",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API info",
            "GET /health": "Health check",
            "POST /ocr-pdf": "OCR PDF file (multipart/form-data)",
            "POST /ocr-base64": "OCR PDF from base64 string"
        },
        "features": [
            "Vietnamese language optimized",
            "Auto text rotation",
            "High accuracy detection",
            "Multiple page support"
        ]
    }

@app.get("/health")
def health_check():
    """Health check - Kiểm tra server còn sống không"""
    return {
        "status": "healthy",
        "ocr_engine": "PaddleOCR",
        "language": "Vietnamese",
        "ready": True
    }

@app.post("/ocr-pdf")
async def ocr_pdf_file(file: UploadFile = File(...)):
    """
    OCR PDF file - Upload trực tiếp
    
    Args:
        file: PDF file (multipart/form-data)
    
    Returns:
        JSON với text đã OCR
    """
    try:
        logger.info(f"📄 Nhận file: {file.filename} ({file.content_type})")
        
        # Kiểm tra file type
        if file.content_type != 'application/pdf':
            raise HTTPException(
                status_code=400, 
                detail=f"Chỉ chấp nhận PDF. Nhận: {file.content_type}"
            )
        
        # Đọc PDF
        pdf_bytes = await file.read()
        file_size_mb = len(pdf_bytes) / (1024 * 1024)
        logger.info(f"📊 Kích thước: {file_size_mb:.2f} MB")
        
        # Giới hạn size
        if file_size_mb > 10:
            raise HTTPException(
                status_code=400,
                detail="File quá lớn. Giới hạn 10MB"
            )
        
        # Mở PDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(pdf_document)
        logger.info(f"📑 Tổng số trang: {total_pages}")
        
        all_text = []
        
        # Xử lý tối đa 3 trang đầu (cho nhanh & tiết kiệm)
        max_pages = min(3, total_pages)
        
        for page_num in range(max_pages):
            logger.info(f"⚙️  Đang xử lý trang {page_num + 1}/{max_pages}...")
            
            page = pdf_document[page_num]
            
            # Convert page thành image với resolution cao (2x zoom)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")
            
            # OCR với PaddleOCR
            result = ocr.ocr(img_bytes, cls=True)
            
            if result and result[0]:
                page_text = []
                for line in result[0]:
                    if line[1] and line[1][0]:  # text content và confidence
                        text = line[1][0]
                        confidence = line[1][1]
                        
                        # Chỉ lấy text có confidence > 0.5
                        if confidence > 0.5:
                            page_text.append(text)
                
                page_content = "\n".join(page_text)
                all_text.append(page_content)
                
                logger.info(f"✅ Trang {page_num + 1}: {len(page_content)} ký tự")
            else:
                logger.warning(f"⚠️  Trang {page_num + 1}: Không detect được text")
        
        pdf_document.close()
        
        # Ghép tất cả text
        final_text = "\n\n=== TRANG MỚI ===\n\n".join(all_text)
        
        logger.info(f"🎉 Hoàn thành! Tổng: {len(final_text)} ký tự")
        
        return {
            "success": True,
            "text": final_text,
            "pages_processed": max_pages,
            "total_pages": total_pages,
            "total_chars": len(final_text),
            "filename": file.filename
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"❌ Lỗi OCR: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi xử lý PDF: {str(e)}"
        )

@app.post("/ocr-base64")
async def ocr_pdf_base64(data: dict):
    """
    OCR PDF từ base64 string - Dùng cho Apps Script
    
    Args:
        data: JSON với key "pdf_base64" (base64 encoded PDF)
    
    Returns:
        JSON với text đã OCR
    """
    try:
        logger.info("📥 Nhận base64 PDF từ Apps Script")
        
        # Validate input
        if 'pdf_base64' not in data:
            raise HTTPException(
                status_code=400, 
                detail="Thiếu trường 'pdf_base64' trong request"
            )
        
        # Decode base64
        try:
            pdf_bytes = base64.b64decode(data['pdf_base64'])
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Base64 decode lỗi: {str(e)}"
            )
        
        file_size_mb = len(pdf_bytes) / (1024 * 1024)
        logger.info(f"📊 Kích thước: {file_size_mb:.2f} MB")
        
        # Giới hạn size
        if file_size_mb > 10:
            raise HTTPException(
                status_code=400,
                detail="File quá lớn. Giới hạn 10MB"
            )
        
        # Mở PDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(pdf_document)
        logger.info(f"📑 Tổng số trang: {total_pages}")
        
        all_text = []
        max_pages = min(3, total_pages)
        
        for page_num in range(max_pages):
            logger.info(f"⚙️  Xử lý trang {page_num + 1}/{max_pages}...")
            
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")
            
            # OCR
            result = ocr.ocr(img_bytes, cls=True)
            
            if result and result[0]:
                page_text = []
                for line in result[0]:
                    if line[1] and line[1][0]:
                        text = line[1][0]
                        confidence = line[1][1]
                        if confidence > 0.5:
                            page_text.append(text)
                
                all_text.append("\n".join(page_text))
                logger.info(f"✅ Trang {page_num + 1} xong")
        
        pdf_document.close()
        
        final_text = "\n\n=== TRANG MỚI ===\n\n".join(all_text)
        
        logger.info(f"🎉 Hoàn thành! {len(final_text)} ký tự")
        
        return {
            "success": True,
            "text": final_text,
            "pages_processed": max_pages,
            "total_pages": total_pages,
            "total_chars": len(final_text)
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"❌ Lỗi: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý: {str(e)}"
        )

# Để Railway biết app đã sẵn sàng
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Server đã khởi động!")
    logger.info(f"🌍 PORT: {os.getenv('PORT', '8000')}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
