"""
lstm_model.py — STEP 7: Deep Learning dengan TensorFlow

Requirement yang dipenuhi:
  ✅ Functional API
  ✅ Custom Callback (EarlyStoppingWithLog)
  ✅ tf.GradientTape (custom training loop)
  ✅ TensorBoard (log loss per epoch)
  ✅ Save Model (.keras format)
  ✅ Inference pipeline

Arsitektur:
  Input (sequence) → LSTM → Dropout → LSTM → Dense → Output

Catatan metrik:
  - MAE ≤ 0.02  → dihitung pada data ternormalisasi (MinMaxScaler 0–1)
  - MAPE < 15%  → dihitung pada data asli (rupiah) = akurasi > 85%

Install:
  pip install tensorflow scikit-learn pandas numpy
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ══════════════════════════════════════════════════════════════════
# KONFIGURASI
# ══════════════════════════════════════════════════════════════════

CONFIG = {
    "sequence_length" : 14,      # pakai 14 hari terakhir untuk prediksi
    "lstm_units_1"    : 64,
    "lstm_units_2"    : 32,
    "dropout_rate"    : 0.2,
    "learning_rate"   : 0.001,
    "epochs"          : 100,
    "batch_size"      : 16,
    "patience"        : 10,      # early stopping
    "save_dir"        : "models/saved",
    "log_dir"         : "logs/tensorboard",
}


# ══════════════════════════════════════════════════════════════════
# 1. CUSTOM CALLBACK
# ══════════════════════════════════════════════════════════════════

class EarlyStoppingWithLog(keras.callbacks.Callback):
    """
    Custom Callback yang menggabungkan:
      - Early stopping jika val_loss tidak membaik selama N epoch
      - Log detail per epoch ke console
      - Simpan best val_loss untuk reporting
    """

    def __init__(self, patience: int = 10, min_delta: float = 1e-4):
        super().__init__()
        self.patience    = patience
        self.min_delta   = min_delta
        self.best_loss   = np.inf
        self.wait        = 0
        self.best_epoch  = 0
        self.best_weights = None

    def on_train_begin(self, logs=None):
        self.wait       = 0
        self.best_loss  = np.inf
        self.best_epoch = 0
        print(f"\nTraining dimulai — patience={self.patience}, min_delta={self.min_delta}")

    def on_epoch_end(self, epoch, logs=None):
        logs      = logs or {}
        val_loss  = logs.get("val_loss", np.inf)
        train_loss= logs.get("loss", np.inf)
        val_mae   = logs.get("val_mae", 0)

        # Cek improvement
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss    = val_loss
            self.best_epoch   = epoch + 1
            self.wait         = 0
            self.best_weights = self.model.get_weights()
            marker = "✓"
        else:
            self.wait += 1
            marker = f"({self.wait}/{self.patience})"

        # Log setiap 5 epoch atau saat ada improvement
        if (epoch + 1) % 5 == 0 or marker == "✓":
            print(
                f"  Epoch {epoch+1:3d} | "
                f"loss={train_loss:.4f} | "
                f"val_loss={val_loss:.4f} | "
                f"val_mae={val_mae:.4f} {marker}"
            )

        # Stop jika tidak ada improvement
        if self.wait >= self.patience:
            self.model.stop_training = True
            print(f"\nEarly stopping di epoch {epoch+1}.")
            print(f"Best val_loss={self.best_loss:.4f} di epoch {self.best_epoch}.")
            if self.best_weights:
                self.model.set_weights(self.best_weights)
                print("Best weights dikembalikan ke model.")

    def on_train_end(self, logs=None):
        print(f"\nTraining selesai. Best epoch: {self.best_epoch}, Best val_loss: {self.best_loss:.4f}")


# ══════════════════════════════════════════════════════════════════
# 2. DATA PREPARATION
# ══════════════════════════════════════════════════════════════════

class DataPreparer:
    """Siapkan data time series untuk LSTM."""

    def __init__(self, sequence_length: int = 14):
        self.sequence_length = sequence_length
        self.scaler          = MinMaxScaler(feature_range=(0, 1))
        self._fitted         = False

    def prepare(self, df: pd.DataFrame, category: str = "total") -> dict:
        """
        Ubah DataFrame transaksi → sequences siap masuk LSTM.

        Returns dict berisi X_train, y_train, X_val, y_val, X_test, y_test
        """
        daily = self._to_daily_series(df, category)

        # Normalisasi ke 0–1
        values         = daily["amount"].values.reshape(-1, 1)
        values_scaled  = self.scaler.fit_transform(values).flatten()
        self._fitted   = True
        self._last_sequence = values_scaled[-self.sequence_length:]
        self._dates    = daily["date"].values

        # Buat sequences
        X, y = [], []
        for i in range(self.sequence_length, len(values_scaled)):
            X.append(values_scaled[i - self.sequence_length:i])
            y.append(values_scaled[i])

        X = np.array(X)
        y = np.array(y)

        # Reshape untuk LSTM: (samples, timesteps, features)
        X = X.reshape((X.shape[0], X.shape[1], 1))

        # Split: 70% train, 15% val, 15% test
        n        = len(X)
        n_train  = int(n * 0.80)
        n_val    = int(n * 0.15)

        return {
            "X_train"   : X[:n_train],
            "y_train"   : y[:n_train],
            "X_val"     : X[n_train:n_train + n_val],
            "y_val"     : y[n_train:n_train + n_val],
            "X_test"    : X[n_train + n_val:],
            "y_test"    : y[n_train + n_val:],
            "n_samples" : n,
            "n_train"   : n_train,
            "n_val"     : n_val,
        }

    def inverse(self, values_scaled: np.ndarray) -> np.ndarray:
        """Kembalikan nilai ternormalisasi ke rupiah asli."""
        return self.scaler.inverse_transform(
            values_scaled.reshape(-1, 1)
        ).flatten()

    def get_last_sequence(self) -> np.ndarray:
        """Ambil sequence terakhir untuk prediksi masa depan."""
        return self._last_sequence.copy()

    def _to_daily_series(self, df: pd.DataFrame, category: str) -> pd.DataFrame:
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        
        exp = df[df["Transaction_Type"].str.upper() == "EXPENSE"]
        
        if category != "total":
            exp = exp[exp["Category"].str.lower() == category.lower()]

        daily = exp.groupby("Date")["Amount"].sum().reset_index()
        daily.columns = ["date", "amount"]

        # Isi hari kosong
        full = pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
        daily = (
            daily.set_index("date")
            .reindex(full, fill_value=0)
            .reset_index()
            .rename(columns={"index": "date"})
        )
        return daily


# ══════════════════════════════════════════════════════════════════
# 3. MODEL — FUNCTIONAL API
# ══════════════════════════════════════════════════════════════════

def build_lstm_model(
    sequence_length: int = 14,
    lstm_units_1   : int = 64,
    lstm_units_2   : int = 32,
    dropout_rate   : float = 0.2,
) -> keras.Model:

    inputs = keras.Input(shape=(sequence_length, 1), name="sequence_input")

    x = layers.LSTM(
        lstm_units_1,
        return_sequences=True,
        name="lstm_1"
    )(inputs)
    x = layers.Dropout(dropout_rate, name="dropout_1")(x)

    x = layers.LSTM(
        lstm_units_2,
        return_sequences=False,
        name="lstm_2"
    )(x)
    x = layers.Dropout(dropout_rate, name="dropout_2")(x)

    x = layers.Dense(16, activation="relu", name="dense_hidden")(x)
    output = layers.Dense(1, activation="linear", name="output")(x)

    model = keras.Model(inputs=inputs, outputs=output, name="ExpenseLSTM")
    return model


# ══════════════════════════════════════════════════════════════════
# 4. CUSTOM TRAINING LOOP — tf.GradientTape
# ══════════════════════════════════════════════════════════════════

def train_with_gradient_tape(
    model      : keras.Model,
    X_train    : np.ndarray,
    y_train    : np.ndarray,
    X_val      : np.ndarray,
    y_val      : np.ndarray,
    epochs     : int   = 100,
    batch_size : int   = 16,
    learning_rate: float = 0.001,
    patience   : int   = 10,
    log_dir    : str   = "logs/tensorboard",
) -> dict:
    """
    Custom training loop menggunakan tf.GradientTape.

    Keunggulan vs model.fit():
      - Kontrol penuh atas setiap langkah gradient update
      - Bisa tambahkan logika custom di setiap step
      - TensorBoard log manual lebih fleksibel

    Returns
    -------
    dict berisi history loss dan best metrics
    """
    optimizer  = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    loss_fn    = tf.keras.losses.MeanSquaredError()
    mae_metric = tf.keras.metrics.MeanAbsoluteError()

    # TensorBoard writers
    os.makedirs(log_dir, exist_ok=True)
    train_writer = tf.summary.create_file_writer(os.path.join(log_dir, "train"))
    val_writer   = tf.summary.create_file_writer(os.path.join(log_dir, "val"))

    # Dataset
    dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
    dataset = dataset.shuffle(buffer_size=256).batch(batch_size)

    X_val_tf = tf.constant(X_val, dtype=tf.float32)
    y_val_tf = tf.constant(y_val, dtype=tf.float32)

    history       = {"train_loss": [], "val_loss": [], "val_mae": []}
    best_val_loss = np.inf
    best_weights  = None
    wait          = 0
    best_epoch    = 0

    print(f"\nCustom Training Loop (tf.GradientTape)")
    print(f"Epochs={epochs} | Batch={batch_size} | LR={learning_rate} | Patience={patience}")
    print("-" * 60)

    for epoch in range(epochs):
        # ── TRAIN ────────────────────────────────────────────────
        epoch_loss = []
        for X_batch, y_batch in dataset:
            with tf.GradientTape() as tape:
                y_pred = model(X_batch, training=True)
                loss   = loss_fn(y_batch, y_pred)

            gradients = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(gradients, model.trainable_variables))
            epoch_loss.append(float(loss))

        train_loss = np.mean(epoch_loss)

        # ── VALIDATION ───────────────────────────────────────────
        y_val_pred = model(X_val_tf, training=False)
        val_loss   = float(loss_fn(y_val_tf, y_val_pred))
        mae_metric.update_state(y_val_tf, y_val_pred)
        val_mae    = float(mae_metric.result())
        mae_metric.reset_state()

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_mae"].append(val_mae)

        # ── TensorBoard Logging ───────────────────────────────────
        with train_writer.as_default():
            tf.summary.scalar("loss", train_loss, step=epoch)
        with val_writer.as_default():
            tf.summary.scalar("loss", val_loss, step=epoch)
            tf.summary.scalar("mae",  val_mae,  step=epoch)

        # ── Early Stopping ────────────────────────────────────────
        if val_loss < best_val_loss - 1e-4:
            best_val_loss = val_loss
            best_weights  = model.get_weights()
            best_epoch    = epoch + 1
            wait          = 0
            marker        = "✓"
        else:
            wait  += 1
            marker = f"({wait}/{patience})"

        if (epoch + 1) % 5 == 0 or marker == "✓":
            print(
                f"  Epoch {epoch+1:3d} | "
                f"loss={train_loss:.4f} | "
                f"val_loss={val_loss:.4f} | "
                f"val_mae={val_mae:.4f} {marker}"
            )

        if wait >= patience:
            print(f"\nEarly stopping di epoch {epoch+1}.")
            break

    # Kembalikan best weights
    if best_weights:
        model.set_weights(best_weights)
        print(f"Best weights dari epoch {best_epoch} dikembalikan.")

    print(f"\nBest val_loss : {best_val_loss:.4f}")
    print(f"Best val_mae  : {min(history['val_mae']):.4f}")
    print(f"\nTensorBoard log: {log_dir}")
    print(f"Jalankan: tensorboard --logdir={log_dir}")

    return {
        "history"       : history,
        "best_val_loss" : best_val_loss,
        "best_val_mae"  : min(history["val_mae"]),
        "best_epoch"    : best_epoch,
        "total_epochs"  : len(history["train_loss"]),
    }


# ══════════════════════════════════════════════════════════════════
# 5. EVALUASI TEST SET
# ══════════════════════════════════════════════════════════════════

def evaluate_on_test(
    model    : keras.Model,
    preparer : DataPreparer,
    X_test   : np.ndarray,
    y_test   : np.ndarray,
) -> dict:
    """
    Evaluasi model forecasting pada test set.

    Metrics:
    - MAE normalized
    - MAE rupiah
    - RMSE
    - MAPE
    - R² Score
    """

    # =========================================================
    # PREDIKSI
    # =========================================================

    y_pred_scaled = model.predict(X_test, verbose=0).flatten()

    y_pred_rupiah = preparer.inverse(y_pred_scaled)
    y_true_rupiah = preparer.inverse(y_test)

    # =========================================================
    # METRICS
    # =========================================================

    # MAE normalized
    mae_normalized = mean_absolute_error(
        y_test,
        y_pred_scaled
    )

    # MAE rupiah
    mae_rupiah = mean_absolute_error(
        y_true_rupiah,
        y_pred_rupiah
    )

    # RMSE
    rmse = np.sqrt(
        mean_squared_error(
            y_true_rupiah,
            y_pred_rupiah
        )
    )

    # =========================================================
    # SAFE MAPE
    # Hindari nilai kecil / nol
    # =========================================================

    epsilon = 1e-8

    mask = y_true_rupiah > 1000

    if np.any(mask):
        mape = np.mean(
            np.abs(
                (y_true_rupiah[mask] - y_pred_rupiah[mask]) /
                np.maximum(np.abs(y_true_rupiah[mask]), epsilon)
            )
        ) * 100
    else:
        mape = 0

    # =========================================================
    # R2 SCORE
    # =========================================================

    from sklearn.metrics import r2_score

    r2 = r2_score(
        y_true_rupiah,
        y_pred_rupiah
    )

    # =========================================================
    # PERFORMANCE LABEL
    # =========================================================

    if mae_normalized <= 0.02:
        performance = "Excellent"
    elif mae_normalized <= 0.05:
        performance = "Good"
    else:
        performance = "Needs Improvement"

    # =========================================================
    # PRINT
    # =========================================================

    print("\n=== EVALUASI TEST SET ===")

    print(
        f"  MAE (normalized) : "
        f"{mae_normalized:.4f} "
        f"({'✅ ≤ 0.02' if mae_normalized <= 0.02 else '❌ > 0.02'})"
    )

    print(f"  MAE (rupiah)     : Rp {mae_rupiah:,.0f}")
    print(f"  RMSE             : Rp {rmse:,.0f}")
    print(f"  MAPE             : {mape:.2f}%")
    print(f"  R² Score         : {r2:.4f}")
    print(f"  Performance      : {performance}")

    # =========================================================
    # RETURN
    # =========================================================

    return {
        "mae_normalized": round(mae_normalized, 4),
        "mae_rupiah"    : round(mae_rupiah, 0),
        "rmse"          : round(rmse, 0),
        "mape"          : round(mape, 2),
        "r2_score"      : round(r2, 4),

        "performance_label": performance,

        "meets_mae_req" : mae_normalized <= 0.02,
    }


# ══════════════════════════════════════════════════════════════════
# 6. INFERENCE — PREDIKSI MASA DEPAN
# ══════════════════════════════════════════════════════════════════

def predict_future(
    model    : keras.Model,
    preparer : DataPreparer,
    days     : int = 7,
) -> dict:
    """
    Prediksi pengeluaran N hari ke depan menggunakan model LSTM.
    Menggunakan rolling prediction: hasil prediksi dipakai sebagai
    input untuk prediksi hari berikutnya.
    """
    sequence    = preparer.get_last_sequence().tolist()
    predictions = []

    for _ in range(days):
        x = np.array(sequence[-preparer.sequence_length:]).reshape(1, preparer.sequence_length, 1)
        pred_scaled = float(model.predict(x, verbose=0)[0][0])
        pred_scaled = max(0, min(1, pred_scaled))   # clamp 0–1
        predictions.append(pred_scaled)
        sequence.append(pred_scaled)

    # Kembalikan ke rupiah
    pred_rupiah = preparer.inverse(np.array(predictions))

    # Format output
    last_date = pd.Timestamp.now().normalize()
    daily = []
    for i, amount in enumerate(pred_rupiah):
        date = last_date + timedelta(days=i + 1)
        daily.append({
            "date"     : date.strftime("%Y-%m-%d"),
            "day"      : date.strftime("%A"),
            "predicted": round(max(0, amount), 0),
        })

    total     = sum(d["predicted"] for d in daily)
    avg       = total / days
    peak      = max(daily, key=lambda x: x["predicted"])

    return {
        "days_ahead"     : days,
        "total_predicted": round(total, 0),
        "avg_per_day"    : round(avg, 0),
        "peak_day"       : peak["date"],
        "peak_day_name"  : peak["day"],
        "peak_amount"    : peak["predicted"],
        "daily"          : daily,
    }


# ══════════════════════════════════════════════════════════════════
# 7. SAVE & LOAD MODEL
# ══════════════════════════════════════════════════════════════════

def save_model(
    model    : keras.Model,
    preparer : DataPreparer,
    save_dir : str = "models/saved",
    name     : str = "lstm_expense",
) -> str:
    """
    Simpan model dalam format .keras (TensorFlow production format).
    Juga simpan scaler dan config sebagai JSON.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Model
    model_path = os.path.join(save_dir, f"{name}.keras")
    model.save(model_path)

    # Scaler (simpan parameter MinMaxScaler)
    scaler_path = os.path.join(save_dir, f"{name}_scaler.json")
    scaler_params = {
        "data_min_" : preparer.scaler.data_min_.tolist(),
        "data_max_" : preparer.scaler.data_max_.tolist(),
        "scale_"    : preparer.scaler.scale_.tolist(),
        "min_"      : preparer.scaler.min_.tolist(),
        "sequence_length": preparer.sequence_length,
        "last_sequence"  : preparer.get_last_sequence().tolist(),
    }
    with open(scaler_path, "w") as f:
        json.dump(scaler_params, f, indent=2)

    print(f"Model disimpan: {model_path}")
    print(f"Scaler disimpan: {scaler_path}")
    return model_path


def load_model_and_preparer(
    save_dir: str = "models/saved",
    name    : str = "lstm_expense",
) -> tuple[keras.Model, DataPreparer]:
    """Load model .keras dan scaler yang sudah disimpan."""
    model_path  = os.path.join(save_dir, f"{name}.keras")
    scaler_path = os.path.join(save_dir, f"{name}_scaler.json")

    model = keras.models.load_model(model_path)

    with open(scaler_path) as f:
        params = json.load(f)

    preparer = DataPreparer(sequence_length=params["sequence_length"])
    preparer.scaler.data_min_ = np.array(params["data_min_"])
    preparer.scaler.data_max_ = np.array(params["data_max_"])
    preparer.scaler.scale_    = np.array(params["scale_"])
    preparer.scaler.min_      = np.array(params["min_"])
    preparer._fitted          = True
    preparer._last_sequence   = np.array(params["last_sequence"])

    print(f"Model loaded: {model_path}")
    model.summary()
    return model, preparer


# ══════════════════════════════════════════════════════════════════
# 8. PIPELINE LENGKAP — satu fungsi untuk semua
# ══════════════════════════════════════════════════════════════════

def run_full_pipeline(
    df        : pd.DataFrame,
    category  : str = "total",
    days_ahead: int = 7,
    save_dir  : str = "models/saved",
    log_dir   : str = "logs/tensorboard",
) -> dict:
    """
    Jalankan pipeline lengkap:
    prepare → build → train → evaluate → predict → save

    Untuk dipakai di Colab atau script sekali jalan.
    """
    print("=" * 60)
    print("LSTM EXPENSE FORECASTING — FULL PIPELINE")
    print("=" * 60)

    # 1. Prepare data
    print("\n[1/5] Menyiapkan data...")
    preparer = DataPreparer(sequence_length=CONFIG["sequence_length"])
    data     = preparer.prepare(df, category=category)
    print(f"  Train: {data['n_train']} | Val: {data['n_val']} | "
          f"Test: {data['n_samples'] - data['n_train'] - data['n_val']}")

    # 2. Build model
    print("\n[2/5] Membangun model LSTM (Functional API)...")
    model = build_lstm_model(
        sequence_length = CONFIG["sequence_length"],
        lstm_units_1    = CONFIG["lstm_units_1"],
        lstm_units_2    = CONFIG["lstm_units_2"],
        dropout_rate    = CONFIG["dropout_rate"],
    )
    model.summary()

    # 3. Train dengan GradientTape
    print("\n[3/5] Training dengan tf.GradientTape...")
    train_result = train_with_gradient_tape(
        model         = model,
        X_train       = data["X_train"],
        y_train       = data["y_train"],
        X_val         = data["X_val"],
        y_val         = data["y_val"],
        epochs        = CONFIG["epochs"],
        batch_size    = CONFIG["batch_size"],
        learning_rate = CONFIG["learning_rate"],
        patience      = CONFIG["patience"],
        log_dir       = log_dir,
    )

    # 4. Evaluate
    print("\n[4/5] Evaluasi pada test set...")
    eval_result = evaluate_on_test(
        model    = model,
        preparer = preparer,
        X_test   = data["X_test"],
        y_test   = data["y_test"],
    )

    # 5. Predict
    print(f"\n[5/5] Prediksi {days_ahead} hari ke depan...")
    forecast = predict_future(model, preparer, days=days_ahead)
    print(f"  Total prediksi: Rp {forecast['total_predicted']:,.0f}")
    print(f"  Rata-rata/hari: Rp {forecast['avg_per_day']:,.0f}")
    print(f"  Puncak: {forecast['peak_day_name']} ({forecast['peak_day']}) "
          f"Rp {forecast['peak_amount']:,.0f}")

    # Save
    save_model(model, preparer, save_dir=save_dir)

    return {
        "training"  : train_result,
        "evaluation": eval_result,
        "forecast"  : forecast,
    }