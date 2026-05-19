from fastapi import FastAPI
from pydantic import BaseModel
import tensorflow as tf
import pickle
import numpy as np
import warnings

app = FastAPI()

# Mengabaikan warning scaler dari scikit-learn
warnings.filterwarnings("ignore", message="X does not have valid feature names")

print("Loading model and scaler...")
model = tf.keras.models.load_model('model_peringatan.keras')
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# 1. Format Data disesuaikan menjadi persis 13 fitur
class TransactionInput(BaseModel):
    amount: float
    cumulative_expense: float
    total_income: float
    category_hiburan: int
    category_lain2: int
    category_makan_minum: int
    category_tagihan: int
    day_of_week_monday: int
    day_of_week_saturday: int
    day_of_week_sunday: int
    day_of_week_thursday: int
    day_of_week_tuesday: int
    day_of_week_wednesday: int

@app.post("/api/ai/warning")
def get_warning(data: TransactionInput):
    # 2. Urutan array disamakan persis dengan urutan kolom di Pandas Colab
    input_data = np.array([[
        data.amount,
        data.cumulative_expense,
        data.total_income,
        data.category_hiburan,
        data.category_lain2,
        data.category_makan_minum,
        data.category_tagihan,
        data.day_of_week_monday,
        data.day_of_week_saturday,
        data.day_of_week_sunday,
        data.day_of_week_thursday,
        data.day_of_week_tuesday,
        data.day_of_week_wednesday
    ]])

    # Scaling Data
    input_scaled = scaler.transform(input_data)

    # Prediksi
    prediction_prob = model.predict(input_scaled)[0][0]
    
    # Post-processing logika teks
    if prediction_prob > 0.7:
        status = "BAHAYA"
        message = "Peringatan! Kamu berisiko kehabisan uang sebelum akhir bulan. Batasi pengeluaranmu!"
    elif prediction_prob > 0.4:
        status = "WASPADA"
        message = "Pengeluaranmu mulai tinggi minggu ini. Mulai berhemat ya."
    else:
        status = "AMAN"
        message = "Keuanganmu bulan ini masih dalam batas aman. Pertahankan!"

    return {
        "probability": float(prediction_prob),
        "status": status,
        "message": message
    }   