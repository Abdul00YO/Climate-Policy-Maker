# Use Python 3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose both ports (Render will only map one, but we need both internally)
EXPOSE 8501 8000

# Run FastAPI (backend) + Streamlit (frontend)
CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
