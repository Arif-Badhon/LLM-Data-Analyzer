FROM python:3.12-slim

WORKDIR /app

# Copy requirements
COPY frontend/requirements.txt .

# Install dependencies using uv
RUN pip install uv && uv pip install --system -r requirements.txt

# Copy frontend code
COPY frontend ./

# Expose port
EXPOSE 8501

# Run frontend
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
