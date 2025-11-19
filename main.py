from fastapi import FastAPI, File, UploadFile
from PIL import Image
import numpy as np
import io
import os
import uvicorn

app = FastAPI()

# Global variable for lazy loading
_ocr = None

def get_ocr():
    """Lazy load OCR model"""
    global _ocr
    if _ocr is None:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(use_angle_cls=True, lang='vi')
    return _ocr

@app.post("/ocr")
async def process_ocr(file: UploadFile = File(...)):
    """Process image and return OCR results"""
    try:
        # Lazy load OCR
        ocr = get_ocr()
        
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        img_array = np.array(image)
        
        # Perform OCR
        result = ocr.ocr(img_array, cls=True)
        
        # Extract text
        text_lines = []
        if result and result[0]:
            for line in result[0]:
                text_lines.append(line[1][0])
        
        return {
            "success": True,
            "text": "\n".join(text_lines),
            "lines": text_lines
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/")
async def root():
    return {"message": "PaddleOCR API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
