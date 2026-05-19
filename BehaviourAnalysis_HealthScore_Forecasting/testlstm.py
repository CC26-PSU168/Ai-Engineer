"""
test_lstm.py — Test Script LSTM Expense Forecasting
"""

import os
import pandas as pd

# =========================================================
# SUPPRESS TF LOG
# =========================================================

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# =========================================================
# IMPORT
# =========================================================

from lstm_model import (
    DataPreparer,
    build_lstm_model,
    train_with_gradient_tape,
    evaluate_on_test,
    predict_future,
    save_model,
    load_model_and_preparer,
    run_full_pipeline,
)

# =========================================================
# CONFIG
# =========================================================

CSV_PATH = r"C:\Users\Aditya P J\Documents\Magang dan Lisensi\BoothCamp\CapStone\data\Data_Final_Combine.csv"

MODE = "full"
# full | train | predict | eval

DAYS_AHEAD = 7
CATEGORY   = "total"
SAVE_DIR   = "models/saved"

# =========================================================
# LOAD DATA
# =========================================================

print("=" * 60)
print("LSTM EXPENSE FORECASTING")
print("=" * 60)

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV tidak ditemukan: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)

# Normalisasi text
df["Transaction_Type"] = (
    df["Transaction_Type"]
    .astype(str)
    .str.strip()
    .str.capitalize()
)

df["Date"] = pd.to_datetime(df["Date"])

expense_df = df[df["Transaction_Type"] == "Expense"]

print(f"\nDataset loaded")
print(f"Rows         : {len(df)}")
print(f"Expense rows : {len(expense_df)}")

print(
    f"Date range   : "
    f"{df['Date'].min().strftime('%d %b %Y')} "
    f"→ "
    f"{df['Date'].max().strftime('%d %b %Y')}"
)

print(f"Categories   : {expense_df['Category'].nunique()}")

# =========================================================
# HELPER PRINT METRICS
# =========================================================

def print_evaluation(ev: dict):

    print("\n📊 EVALUASI MODEL")

    mae_ok = ev["mae_normalized"] <= 0.02

    print(
        f"  MAE (normalized) : "
        f"{ev['mae_normalized']:.4f} "
        f"{'✅' if mae_ok else '❌'}"
    )

    print(f"  MAE (rupiah)     : Rp {ev['mae_rupiah']:,.0f}")
    print(f"  RMSE             : Rp {ev['rmse']:,.0f}")

    # =====================================================
    # MAPE LABEL
    # =====================================================

    mape = ev["mape"]

    if mape < 10:
        mape_label = "✅ Sangat Baik"
    elif mape < 20:
        mape_label = "✅ Baik"
    elif mape < 35:
        mape_label = "⚠️ Cukup"
    else:
        mape_label = "❌ Perlu Perbaikan"

    print(f"  MAPE             : {mape:.2f}% → {mape_label}")

    # =====================================================
    # R2
    # =====================================================

    if "r2_score" in ev:

        r2 = ev["r2_score"]

        if r2 >= 0.7:
            r2_label = "✅ Baik"
        elif r2 >= 0.4:
            r2_label = "⚠️ Cukup"
        else:
            r2_label = "❌ Lemah"

        print(
            f"  R² Score         : "
            f"{r2:.4f} → {r2_label}"
        )

# =========================================================
# MODE FULL
# =========================================================

if MODE == "full":

    result = run_full_pipeline(
        df=df,
        category=CATEGORY,
        days_ahead=DAYS_AHEAD,
        save_dir=SAVE_DIR,
        log_dir="logs/tensorboard",
    )

    print("\n" + "=" * 60)
    print("HASIL AKHIR")
    print("=" * 60)

    # =====================================================
    # EVALUATION
    # =====================================================

    print_evaluation(result["evaluation"])

    # =====================================================
    # FORECAST
    # =====================================================

    fc = result["forecast"]

    print(f"\n🔮 PREDIKSI {DAYS_AHEAD} HARI")

    print(f"  Total prediksi : Rp {fc['total_predicted']:,.0f}")
    print(f"  Avg/hari       : Rp {fc['avg_per_day']:,.0f}")

    print(
        f"  Peak day       : "
        f"{fc['peak_day_name']} "
        f"(Rp {fc['peak_amount']:,.0f})"
    )

    print("\nDetail harian:")

    for day in fc["daily"]:

        print(
            f"  {day['date']} "
            f"({day['day']:<10}) "
            f"Rp {day['predicted']:>12,.0f}"
        )

    print("\n📁 TensorBoard")
    print("tensorboard --logdir=logs/tensorboard")

# =========================================================
# MODE TRAIN
# =========================================================

elif MODE == "train":

    preparer = DataPreparer(sequence_length=14)

    data = preparer.prepare(
        df,
        category=CATEGORY
    )

    print("\nData prepared")

    model = build_lstm_model()

    model.summary()

    train_with_gradient_tape(
        model=model,
        X_train=data["X_train"],
        y_train=data["y_train"],
        X_val=data["X_val"],
        y_val=data["y_val"],
        epochs=100,
        patience=10,
        log_dir="logs/tensorboard",
    )

    save_model(
        model,
        preparer,
        save_dir=SAVE_DIR
    )

    print("\n✅ Training selesai")

# =========================================================
# MODE PREDICT
# =========================================================

elif MODE == "predict":

    model, preparer = load_model_and_preparer(
        SAVE_DIR
    )

    result = predict_future(
        model,
        preparer,
        days=DAYS_AHEAD
    )

    print(f"\n🔮 Prediksi {DAYS_AHEAD} Hari")

    print(f"Total   : Rp {result['total_predicted']:,.0f}")
    print(f"Avg/day : Rp {result['avg_per_day']:,.0f}")

    for day in result["daily"]:

        print(
            f"{day['date']} "
            f"({day['day']:<10}) "
            f"Rp {day['predicted']:>12,.0f}"
        )

# =========================================================
# MODE EVAL
# =========================================================

elif MODE == "eval":

    model, _ = load_model_and_preparer(SAVE_DIR)

    preparer = DataPreparer(sequence_length=14)

    data = preparer.prepare(
        df,
        category=CATEGORY
    )

    ev = evaluate_on_test(
        model=model,
        preparer=preparer,
        X_test=data["X_test"],
        y_test=data["y_test"],
    )

    print_evaluation(ev)

else:
    print(f"❌ MODE tidak dikenali: {MODE}")