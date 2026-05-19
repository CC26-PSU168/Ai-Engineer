"""
trainer.py — Training, Evaluasi, dan Manajemen Model

Fungsi:
  train_and_save()   → training penuh + simpan model
  evaluate()         → ukur akurasi dengan walk-forward validation
  load_forecaster()  → load model yang sudah disimpan
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional

from forecast import ExpenseForecaster


# ══════════════════════════════════════════════════════════════════
# TRAINING
# ══════════════════════════════════════════════════════════════════

def train_and_save(
    df          : pd.DataFrame,
    save_dir    : str = "models/saved",
    verbose     : bool = True,
) -> ExpenseForecaster:
    """
    Training model lengkap (total + semua kategori) lalu simpan.

    Parameters
    ----------
    df       : DataFrame transaksi lengkap
    save_dir : folder penyimpanan model
    verbose  : tampilkan progress

    Returns
    -------
    ExpenseForecaster yang sudah terlatih
    """
    print("=" * 50)
    print("EXPENSE FORECASTING — TRAINING")
    print("=" * 50)

    df["Date"] = pd.to_datetime(df["Date"])
    expense_df = df[df["Transaction_Type"] == "Expense"]

    # Info dataset
    date_min  = df["Date"].min().strftime("%d %b %Y")
    date_max  = df["Date"].max().strftime("%d %b %Y")
    n_days    = (df["Date"].max() - df["Date"].min()).days
    n_txn     = len(expense_df)
    cats      = expense_df["Category"].unique().tolist()

    print(f"\nDataset info:")
    print(f"  Rentang   : {date_min} → {date_max} ({n_days} hari)")
    print(f"  Transaksi : {n_txn} expense")
    print(f"  Kategori  : {len(cats)} ({', '.join(cats)})")
    print()

    # Training
    forecaster = ExpenseForecaster()
    forecaster.fit(df, verbose=verbose)

    # Simpan
    forecaster.save(directory=save_dir)

    print("\nTraining selesai.")
    return forecaster


# ══════════════════════════════════════════════════════════════════
# EVALUASI — Walk-Forward Validation
# ══════════════════════════════════════════════════════════════════

def evaluate(
    df          : pd.DataFrame,
    horizon     : int = 7,
    n_folds     : int = 4,
    category    : str = "total",
    verbose     : bool = True,
) -> dict:
    """
    Evaluasi akurasi model dengan walk-forward validation.

    Cara kerja:
      - Data dibagi jadi beberapa fold
      - Setiap fold: train dengan data sebelumnya, prediksi N hari ke depan
      - Bandingkan prediksi vs aktual, hitung error

    Metrik:
      MAE  = rata-rata error absolut (dalam rupiah)
      MAPE = rata-rata error persentase (%)
      RMSE = root mean square error

    Parameters
    ----------
    df       : DataFrame transaksi
    horizon  : berapa hari ke depan yang dievaluasi
    n_folds  : jumlah fold validasi
    category : "total" atau nama kategori
    verbose  : tampilkan detail per fold
    """
    print(f"\nEvaluasi model '{category}' — {n_folds} fold, horizon {horizon} hari")
    print("-" * 50)

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[df["Transaction_Type"] == "Expense"]

    # Buat daily series
    if category == "total":
        daily = df.groupby("Date")["Amount"].sum().reset_index()
    else:
        daily = (
            df[df["Category"].str.lower() == category.lower()]
            .groupby("Date")["Amount"]
            .sum()
            .reset_index()
        )

    daily = daily.rename(columns={"Date": "ds", "Amount": "y"})
    daily["ds"] = pd.to_datetime(daily["ds"])
    daily = daily.sort_values("ds").reset_index(drop=True)

    total_days = len(daily)
    min_train  = max(30, total_days // 2)   # minimal 30 hari training data

    if total_days < min_train + horizon:
        return {"error": f"Data terlalu sedikit untuk evaluasi. Butuh minimal {min_train + horizon} hari."}

    # Tentukan titik evaluasi
    eval_starts = []
    step = (total_days - min_train - horizon) // max(n_folds - 1, 1)
    for i in range(n_folds):
        cutoff_idx = min_train + i * step
        if cutoff_idx + horizon <= total_days:
            eval_starts.append(cutoff_idx)

    fold_results = []

    for fold_i, cutoff_idx in enumerate(eval_starts):
        train_data = daily.iloc[:cutoff_idx]
        test_data  = daily.iloc[cutoff_idx:cutoff_idx + horizon]

        # Training
        from prophet import Prophet
        m = Prophet(
            weekly_seasonality=True,
            daily_seasonality=False,
            yearly_seasonality=False,
            seasonality_mode="multiplicative",
            changepoint_prior_scale=0.05,
            interval_width=0.80,
        )
        m.fit(train_data)

        # Prediksi
        future = m.make_future_dataframe(periods=horizon, freq="D")
        fc     = m.predict(future)
        fc_future = fc.tail(horizon)

        # Aktual vs prediksi
        actuals    = test_data["y"].values
        predicted  = np.maximum(0, fc_future["yhat"].values)

        mae  = np.mean(np.abs(actuals - predicted))
        rmse = np.sqrt(np.mean((actuals - predicted) ** 2))

        # MAPE — hindari division by zero
        nonzero = actuals != 0
        mape = np.mean(np.abs((actuals[nonzero] - predicted[nonzero]) / actuals[nonzero])) * 100 if nonzero.any() else 0

        fold_results.append({"mae": mae, "rmse": rmse, "mape": mape})

        if verbose:
            cutoff_date = train_data["ds"].iloc[-1].strftime("%d %b %Y")
            print(f"  Fold {fold_i+1}: cutoff={cutoff_date} | MAE=Rp{mae:,.0f} | MAPE={mape:.1f}% | RMSE=Rp{rmse:,.0f}")

    # Rata-rata semua fold
    avg_mae  = np.mean([r["mae"]  for r in fold_results])
    avg_mape = np.mean([r["mape"] for r in fold_results])
    avg_rmse = np.mean([r["rmse"] for r in fold_results])

    # Interpretasi akurasi
    if avg_mape < 20:
        accuracy_label = "Baik"
    elif avg_mape < 35:
        accuracy_label = "Cukup"
    else:
        accuracy_label = "Perlu perbaikan"

    print(f"\nHasil rata-rata ({n_folds} fold):")
    print(f"  MAE  : Rp {avg_mae:,.0f}")
    print(f"  MAPE : {avg_mape:.1f}%  → {accuracy_label}")
    print(f"  RMSE : Rp {avg_rmse:,.0f}")

    return {
        "category"      : category,
        "horizon_days"  : horizon,
        "n_folds"       : n_folds,
        "avg_mae"       : round(avg_mae, 0),
        "avg_mape"      : round(avg_mape, 2),
        "avg_rmse"      : round(avg_rmse, 0),
        "accuracy_label": accuracy_label,
        "fold_details"  : fold_results,
    }


# ══════════════════════════════════════════════════════════════════
# LOAD
# ══════════════════════════════════════════════════════════════════

def load_forecaster(directory: str = "models/saved") -> ExpenseForecaster:
    """Load model yang sudah disimpan sebelumnya."""
    forecaster = ExpenseForecaster()
    forecaster.load(directory=directory)
    return forecaster


# ══════════════════════════════════════════════════════════════════
# RETRAINING — update model dengan data baru
# ══════════════════════════════════════════════════════════════════

def retrain(
    df      : pd.DataFrame,
    save_dir: str = "models/saved",
    verbose : bool = True,
) -> ExpenseForecaster:
    """
    Retrain model dengan data terbaru.
    Panggil fungsi ini secara berkala (misal tiap bulan)
    agar model selalu up-to-date.
    """
    print("Retraining model dengan data terbaru...")
    return train_and_save(df, save_dir=save_dir, verbose=verbose)


# ══════════════════════════════════════════════════════════════════
# DEMO — contoh penggunaan lengkap
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

    df = pd.read_csv(r"C:\Users\Aditya P J\Documents\Magang dan Lisensi\BoothCamp\CapStone\data\Data_Final_Combine.csv")

    # # 1. Training
    forecaster = train_and_save(df)

    # # 2. Evaluasi akurasi
    eval_result = evaluate(df, horizon=7, n_folds=4)
    print(json.dumps(eval_result, indent=2, ensure_ascii=False, default=str))

    # # 3. Prediksi 7 hari ke depan (total)
    pred = forecaster.predict(days=7)
    print(json.dumps(pred, indent=2, ensure_ascii=False, default=str))

    # # 4. Prediksi semua kategori
    pred_all = forecaster.predict_all_categories(days=14)
    print(json.dumps(pred_all, indent=2, ensure_ascii=False, default=str))

    # # 5. Load model yang sudah disimpan (tidak perlu retrain)
    forecaster2 = load_forecaster()
    pred2 = forecaster2.predict(days=7)
    pass