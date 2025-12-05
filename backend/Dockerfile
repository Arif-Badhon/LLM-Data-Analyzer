FROM python:3.12-slim

WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install dependencies using uv
RUN pip install uv && uv pip install --system -r requirements.txt

# Copy backend code
COPY backend ./

# Expose port
EXPOSE 8000

# Run backend
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
