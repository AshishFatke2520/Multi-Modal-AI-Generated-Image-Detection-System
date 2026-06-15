# --- Step 1: Build the React Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Step 2: Run the Python Backend ---
FROM python:3.10-slim

# Create a non-root user for Hugging Face Spaces (UID 1000)
RUN useradd -m -u 1000 user
WORKDIR /app

# Install system dependencies needed for OpenCV & PyTorch
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Copy built frontend files from Step 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Set permissions for Hugging Face environment
RUN chown -R user:user /app
USER user

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
