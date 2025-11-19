from fastapi import FastAPI, File, UploadFile, HTTPException
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io
import os
import uvicorn
import cv2

app = FastAPI()

# Initialize PaddleOCR
ocr = None

def get_ocr():
    """Lazy load OCR model"""
    global ocr
    if ocr is None:
        print("🚀 Initializing PaddleOCR...")
        ocr = PaddleOCR(use_angle_cls=True, lang='vi')
        print("✅ PaddleOCR initialized successfully")
    return ocr

@app.post("/ocr")
async def process_ocr(file: UploadFile = File(...)):
    """Process image and return OCR results"""
    print(f"📥 Received file: {file.filename}, content_type: {file.content_type}")
    
    try:
        # Read file contents
        contents = await file.read()
        print(f"📊 File size: {len(contents)} bytes")
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file received")
        
        # Convert to PIL Image
        try:
            image = Image.open(io.BytesIO(contents))
            print(f"🖼️ Image opened: {image.format}, size: {image.size}, mode: {image.mode}")
        except Exception as e:
            print(f"❌ Failed to open image: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Invalid image format: {str(e)}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            print(f"🔄 Converting from {image.mode} to RGB")
            image = image.convert('RGB')
        
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        print(f"📐 Array shape: {img_array.shape}, dtype: {img_array.dtype}")
        
        # Validate array
        if img_array.size == 0:
            raise HTTPException(status_code=422, detail="Image array is empty")
        
        # Convert RGB to BGR for OpenCV/PaddleOCR
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Get OCR engine
        ocr_engine = get_ocr()
        
        # Perform OCR
        print("🔍 Performing OCR...")
        result = ocr_engine.ocr(img_array, cls=True)
        print(f"✅ OCR completed, result type: {type(result)}")
        
        # Extract text
        text_lines = []
        full_text = ""
        
        if result and result[0]:
            print(f"📝 Found {len(result[0])} text lines")
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1])
                    text_lines.append(text)
            
            full_text = "\n".join(text_lines)
            print(f"✅ Extracted {len(full_text)} characters")
        else:
            print("⚠️ No text found in image")
        
        return {
            "success": True,
            "text": full_text,
            "lines": text_lines,
            "line_count": len(text_lines)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

@app.get("/")
async def root():
    return {
        "message": "PaddleOCR API v1.1 - Vietnamese OCR",
        "status": "running",
        "endpoints": {
            "/ocr": "POST - Upload image for OCR",
            "/health": "GET - Health check",
            "/test": "GET - Test endpoint"
        }
    }

@app.get("/health")
async def health():
    try:
        # Test if OCR is loadable
        ocr_engine = get_ocr()
        return {
            "status": "healthy",
            "ocr_loaded": ocr_engine is not None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/test")
async def test():
    """Test endpoint to verify server is running"""
    return {
        "status": "ok",
        "message": "Server is running properly",
        "ocr_status": "loaded" if ocr is not None else "not_loaded"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
