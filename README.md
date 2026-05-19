# AI Finance Engine

Engine analitik keuangan berbasis AI untuk aplikasi **Budgetly** — menggabungkan Rule-Based AI, Prophet Forecasting, LSTM Neural Network, dan Gemini LLM.

## Arsitektur

```
Transaksi DB (PostgreSQL)
     ↓
┌─────────────────────────────────────────────┐
│  FastAPI Backend (main.py)                  │
│                                             │
│  Layer 1: Rule-Based AI (rule_based_ai.py)  │  ← Skor keuangan & rekomendasi
│  Layer 2: Prophet Forecaster (forecast.py)  │  ← Prediksi masa depan
│  Layer 3: LSTM Model (lstm_model.py)        │  ← Deep learning time series
│  Layer 4: Gemini Narrator (gemininarator.py)│  ← Narasi natural language
└─────────────────────────────────────────────┘
     ↓
Backend Node.js (proxy /ml/*)
     ↓
Frontend Next.js
```

## Endpoints

| Method | Path | Deskripsi |
|--------|------|-----------|
| GET | `/` | Info API |
| GET | `/summary` | Ringkasan bulanan |
| GET | `/financial-score` | Skor keuangan 0–100 |
| GET | `/behavior-analysis` | Insight perilaku belanja |
| GET | `/recommendations` | Rekomendasi aksi AI |
| GET | `/forecast/prophet` | Prediksi Prophet |
| GET | `/forecast/lstm` | Prediksi LSTM |
| POST | `/train/lstm` | Training model LSTM |
| GET | `/narrative` | Narasi Gemini AI |
| GET | `/full-report` | Semua data sekaligus |

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Salin dan isi environment variables
cp .env.example .env
# Edit .env: isi GEMINI_API_KEY dan DATABASE_URL

# Jalankan server
uvicorn main:app --reload --port 8000
```

## Environment Variables

Buat file `.env` berdasarkan `.env.example`:

```
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@host:5432/dbname
```