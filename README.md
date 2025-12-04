# LLM Data Analyzer

> **Local LLM-powered Data Analysis on Mac M4**

A powerful, dual-mode data analysis platform that leverages local LLMs (via MLX on Apple Silicon) or containerized models (via Docker) to provide intelligent insights from your data. Built with FastAPI and designed for privacy and performance.

## 🚀 Features

- **Dual-Mode LLM Support**:
  - **MLX Mode (Default)**: Runs optimized local LLMs directly on Apple Silicon (M1/M2/M3/M4) using `mlx-lm`.
  - **Docker Model Runner**: Connects to OpenAI-compatible model runners (like `llama.cpp` server) running in Docker containers.
- **Intelligent Data Analysis**:
  - Upload CSV or Excel files.
  - Perform statistical analysis, trend detection, and outlier identification.
  - Get ML-driven suggestions for data improvement.
- **Interactive Chat**: Chat with your data using the integrated LLM.
- **Modern API**: Robust FastAPI backend with comprehensive documentation.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn
- **LLM Engine**: MLX (Apple Silicon), Docker (Containerized)
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Package Management**: `uv`

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **Package Manager**: `uv` (Recommended) or `pip`
- **Hardware**: Mac with Apple Silicon (for MLX mode) OR any system with Docker (for Docker mode)

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd llm-data-analyzer
```

### 2. Install Dependencies

Using `uv` (recommended):

```bash
uv sync
```

Or using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Configuration

Copy the example environment file:

```bash
cp .env.example .env.local
```

Edit `.env.local` to configure your settings:

- **`FASTAPI_ENV`**: Set to `development` for hot-reloading.
- **`DEBUG`**: Set to `true` to use **MLX (Local)** mode. Set to `false` to use **Docker Model Runner**.
- **`LLM_MODEL_NAME`**: Specify the Hugging Face model ID for MLX (e.g., `mlx-community/Llama-3.2-3B-Instruct-4bit`).

### 4. Run the Backend

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the server
python -m backend.app.main
```

The API will be available at `http://localhost:8000`.

## 📖 API Documentation

Once the server is running, access the interactive API docs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

- `POST /api/v1/chat`: Chat with the LLM.
- `POST /api/v1/upload`: Upload a dataset (CSV/Excel).
- `POST /api/v1/analyze`: Perform specific analysis on uploaded data.
- `POST /api/v1/suggestions`: Get ML-driven data improvement suggestions.
- `GET /api/v1/health`: Check system health and current LLM mode.

## 🏗️ Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/        # API Routes
│   │   ├── services/   # Business Logic (LLM, Analyzer, etc.)
│   │   ├── models/     # Pydantic Models
│   │   └── main.py     # Application Entry Point
├── frontend/           # (Under Development) Streamlit Frontend
├── pyproject.toml      # Project Dependencies
└── README.md           # Project Documentation
```

## ⚠️ Frontend Status

The Streamlit frontend is currently under active development. Please use the Backend API directly or via the Swagger UI for testing and interaction.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
