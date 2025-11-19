FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for OpenCV and PaddleOCR
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port (documentation only, Railway uses $PORT)
EXPOSE 8000

# Run with Python to use PORT environment variable
CMD ["python", "main.py"]
