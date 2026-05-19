"""
Rule-Based AI — Sistem keputusan berbasis aturan untuk analisis keuangan.

Kenapa rule-based dulu?
  - Dataset masih kecil → model ML butuh ribuan sampel per kategori
  - Insight finansial lebih cocok logika deterministik
  - Mudah di-debug, mudah ditambah rule baru
  - Transparan: user bisa tahu KENAPA dapat skor tertentu

Struktur:
  RuleEngine          ← orchestrator utama
  ├── ScoreCalculator ← hitung financial score 0–100
  ├── InsightEngine   ← hasilkan insight teks dari data
  └── RecommendEngine ← hasilkan rekomendasi spesifik
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


# ══════════════════════════════════════════════════════════════════
# DATA CLASSES — struktur output yang konsisten
# ══════════════════════════════════════════════════════════════════

@dataclass
class ScoreResult:
    score: int
    status: str
    grade: str                          # A / B / C / D / F
    deductions: list[dict]              # log potongan poin per rule
    bonuses: list[dict]                 # log bonus poin
    breakdown: dict[str, float]         # skor per dimensi


@dataclass
class InsightResult:
    insights: list[str]                 # insight faktual dari data
    warnings: list[str]                 # peringatan yang perlu perhatian
    positives: list[str]                # hal positif yang ditemukan


@dataclass
class RecommendResult:
    recommendations: list[dict]         # {"priority": "high", "action": "..."}
    focus_category: str                 # kategori yang paling perlu dibenahi
    estimated_saving: float             # estimasi penghematan jika ikut saran


# ══════════════════════════════════════════════════════════════════
# HELPER INTERNAL
# ══════════════════════════════════════════════════════════════════

def _filter_month(df: pd.DataFrame, month: int, year: int) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    mask = (df["Date"].dt.month == month) & (df["Date"].dt.year == year)
    return df[mask]


def _split_expense_income(df: pd.DataFrame):
    exp = df[df["Transaction_Type"] == "Expense"]
    inc = df[df["Transaction_Type"] == "Income"]
    return exp, inc


def _get_category_ratios(expense_df: pd.DataFrame) -> dict[str, float]:
    """Persentase pengeluaran per kategori terhadap total expense."""
    total = expense_df["Amount"].sum()
    if total == 0:
        return {}
    return (
        expense_df.groupby("Category")["Amount"]
        .sum()
        .div(total)
        .round(4)
        .to_dict()
    )


def _label_status(score: int) -> tuple[str, str]:
    if score >= 85: return "Sangat Sehat", "A"
    if score >= 70: return "Cukup Stabil", "B"
    if score >= 55: return "Perlu Perhatian", "C"
    if score >= 40: return "Kurang Baik", "D"
    return "Kritis", "F"


# ══════════════════════════════════════════════════════════════════
# 1. SCORE CALCULATOR
# ══════════════════════════════════════════════════════════════════

class ScoreCalculator:
    """
    Hitung financial score 0–100 menggunakan rule-based deduction system.

    Dimulai dari 100, dikurangi jika melanggar rule, ditambah jika ada
    perilaku positif. Setiap rule transparan dan bisa di-trace.
    """

    BASE_SCORE = 100

    def calculate(
        self,
        df: pd.DataFrame,
        month: int,
        year: int,
    ) -> ScoreResult:

        mdf         = _filter_month(df, month, year)
        expense_df, income_df = _split_expense_income(mdf)

        total_expense = expense_df["Amount"].sum()
        total_income  = income_df["Amount"].sum()

        cat_ratios   = _get_category_ratios(expense_df)
        score        = self.BASE_SCORE
        deductions   = []
        bonuses      = []
        dim_scores   = {}

        # ── BLOK 1: Rasio Tabungan ────────────────────────────────
        if total_income > 0:
            savings_rate = (total_income - total_expense) / total_income
        else:
            savings_rate = 0

        if savings_rate < 0:
            cut = 25
            score -= cut
            deductions.append({
                "rule"   : "Pengeluaran melebihi pemasukan",
                "detail" : f"Defisit {abs(savings_rate)*100:.1f}% dari income",
                "points" : -cut,
            })
        elif savings_rate < 0.10:
            cut = 15
            score -= cut
            deductions.append({
                "rule"   : "Tabungan sangat rendah (< 10%)",
                "detail" : f"Savings rate: {savings_rate*100:.1f}%",
                "points" : -cut,
            })
        elif savings_rate < 0.20:
            cut = 8
            score -= cut
            deductions.append({
                "rule"   : "Tabungan di bawah ideal (< 20%)",
                "detail" : f"Savings rate: {savings_rate*100:.1f}%",
                "points" : -cut,
            })
        elif savings_rate >= 0.30:
            bonus = 5
            score += bonus
            bonuses.append({
                "rule"   : "Tabungan sangat baik (≥ 30%)",
                "detail" : f"Savings rate: {savings_rate*100:.1f}%",
                "points" : +bonus,
            })

        dim_scores["savings"] = round(max(0, min(30, savings_rate / 0.30 * 30)), 1)

        # ── BLOK 2: Rasio Kategori Pengeluaran ────────────────────

        # Entertainment / Hiburan
        entertainment = cat_ratios.get("Hiburan", cat_ratios.get("Entertainment", 0))
        if entertainment > 0.30:
            cut = 15
            score -= cut
            deductions.append({
                "rule"   : "Pengeluaran hiburan terlalu tinggi (> 30%)",
                "detail" : f"Hiburan: {entertainment*100:.1f}% dari total expense",
                "points" : -cut,
            })
        elif entertainment > 0.20:
            cut = 7
            score -= cut
            deductions.append({
                "rule"   : "Pengeluaran hiburan cukup tinggi (> 20%)",
                "detail" : f"Hiburan: {entertainment*100:.1f}% dari total expense",
                "points" : -cut,
            })

        # F&B / Makan
        food = cat_ratios.get("Makan & Minum", cat_ratios.get("Food", 0))
        if food > 0.40:
            cut = 10
            score -= cut
            deductions.append({
                "rule"   : "Pengeluaran makanan sangat tinggi (> 40%)",
                "detail" : f"Makan & Minum: {food*100:.1f}% dari total expense",
                "points" : -cut,
            })

        # Shopping
        shopping = cat_ratios.get("Belanja", cat_ratios.get("Shopping", 0))
        if shopping > 0.25:
            cut = 10
            score -= cut
            deductions.append({
                "rule"   : "Pengeluaran belanja tinggi (> 25%)",
                "detail" : f"Belanja: {shopping*100:.1f}% dari total expense",
                "points" : -cut,
            })

        dim_scores["category_control"] = round(
            max(0, 25 - (entertainment + max(0, food - 0.35) + max(0, shopping - 0.20)) * 50), 1
        )

        # ── BLOK 3: Weekend vs Weekday ────────────────────────────
        if "Is_Weekend" in expense_df.columns:
            weekend_spend = expense_df[expense_df["Is_Weekend"]]["Amount"].sum()
            weekday_spend = expense_df[~expense_df["Is_Weekend"]]["Amount"].sum()
        else:
            expense_df = expense_df.copy()
            expense_df["Date"] = pd.to_datetime(expense_df["Date"])
            expense_df["_is_wknd"] = expense_df["Date"].dt.dayofweek.isin([5, 6])
            weekend_spend = expense_df[expense_df["_is_wknd"]]["Amount"].sum()
            weekday_spend = expense_df[~expense_df["_is_wknd"]]["Amount"].sum()

        if total_expense > 0:
            weekend_ratio = weekend_spend / total_expense
        else:
            weekend_ratio = 0

        if weekend_spend > weekday_spend:
            cut = 10
            score -= cut
            deductions.append({
                "rule"   : "Weekend spending > weekday spending",
                "detail" : f"Weekend: {weekend_ratio*100:.1f}% dari total expense",
                "points" : -cut,
            })
        elif weekend_ratio > 0.35:
            cut = 5
            score -= cut
            deductions.append({
                "rule"   : "Weekend spending cukup tinggi (> 35%)",
                "detail" : f"Weekend: {weekend_ratio*100:.1f}% dari total expense",
                "points" : -cut,
            })

        dim_scores["weekend_control"] = round(max(0, 20 * (1 - max(0, weekend_ratio - 0.28) / 0.22)), 1)

        # ── BLOK 4: Konsistensi Pengeluaran Harian ────────────────
        daily = expense_df.groupby("Date")["Amount"].sum()
        if len(daily) > 3:
            cv = daily.std() / daily.mean()     # Coefficient of Variation
            if cv > 1.5:
                cut = 10
                score -= cut
                deductions.append({
                    "rule"   : "Pengeluaran harian sangat tidak konsisten",
                    "detail" : f"CV = {cv:.2f} (ideal < 0.8)",
                    "points" : -cut,
                })
            elif cv > 1.0:
                cut = 5
                score -= cut
                deductions.append({
                    "rule"   : "Pengeluaran harian kurang konsisten",
                    "detail" : f"CV = {cv:.2f} (ideal < 0.8)",
                    "points" : -cut,
                })
            elif cv < 0.5:
                bonus = 3
                score += bonus
                bonuses.append({
                    "rule"   : "Pengeluaran harian sangat konsisten",
                    "detail" : f"CV = {cv:.2f}",
                    "points" : +bonus,
                })
            dim_scores["consistency"] = round(max(0, 20 - cv * 10), 1)
        else:
            dim_scores["consistency"] = 10

        # ── BLOK 5: Transaksi Besar ───────────────────────────────
        if len(expense_df) > 0:
            q90 = expense_df["Amount"].quantile(0.90)
            big_txn_count = (expense_df["Amount"] > q90 * 2).sum()
            big_txn_ratio = big_txn_count / len(expense_df)
            if big_txn_ratio > 0.10:
                cut = 8
                score -= cut
                deductions.append({
                    "rule"   : "Terlalu banyak transaksi nilai sangat besar",
                    "detail" : f"{big_txn_count} transaksi ({big_txn_ratio*100:.1f}%) di atas 2× persentil 90",
                    "points" : -cut,
                })
            dim_scores["large_txn_control"] = round(max(0, 15 * (1 - big_txn_ratio / 0.10)), 1)
        else:
            dim_scores["large_txn_control"] = 15

        # ── BLOK 6: Bonus Perilaku Positif ────────────────────────
        n_categories = len(cat_ratios)
        if n_categories >= 5:
            bonus = 3
            score += bonus
            bonuses.append({
                "rule"   : "Pengeluaran terdiversifikasi baik",
                "detail" : f"{n_categories} kategori aktif",
                "points" : +bonus,
            })

        # Clamp 0–100
        score = max(0, min(100, score))
        status, grade = _label_status(score)

        return ScoreResult(
            score      = score,
            status     = status,
            grade      = grade,
            deductions = deductions,
            bonuses    = bonuses,
            breakdown  = dim_scores,
        )


# ══════════════════════════════════════════════════════════════════
# 2. INSIGHT ENGINE
# ══════════════════════════════════════════════════════════════════

class InsightEngine:
    """
    Hasilkan insight, warning, dan hal positif secara otomatis
    dari pola data — bukan teks hardcoded.
    """

    def analyze(
        self,
        df: pd.DataFrame,
        month: int,
        year: int,
    ) -> InsightResult:

        mdf = _filter_month(df, month, year)
        expense_df, income_df = _split_expense_income(mdf)

        # Bulan sebelumnya untuk komparasi
        prev_dt  = (datetime(year, month, 1) - pd.DateOffset(months=1))
        prev_mdf = _filter_month(df, prev_dt.month, prev_dt.year)
        prev_exp, _ = _split_expense_income(prev_mdf)

        insights  = []
        warnings  = []
        positives = []

        total_exp  = expense_df["Amount"].sum()
        total_inc  = income_df["Amount"].sum()
        prev_total = prev_exp["Amount"].sum()

        # ── Tren total ────────────────────────────────────────────
        if prev_total > 0:
            delta_pct = (total_exp - prev_total) / prev_total * 100
            if delta_pct > 20:
                warnings.append(
                    f"Pengeluaran naik {delta_pct:.0f}% dibanding bulan lalu — perlu diperiksa."
                )
            elif delta_pct > 0:
                insights.append(
                    f"Pengeluaran bulan ini naik {delta_pct:.0f}% dari bulan sebelumnya."
                )
            elif delta_pct < -10:
                positives.append(
                    f"Pengeluaran turun {abs(delta_pct):.0f}% dari bulan lalu — efisiensi membaik."
                )
            else:
                insights.append(
                    f"Pengeluaran relatif stabil ({delta_pct:+.0f}% dari bulan lalu)."
                )

        # ── Savings rate ──────────────────────────────────────────
        if total_inc > 0:
            sr = (total_inc - total_exp) / total_inc * 100
            if sr < 0:
                warnings.append(f"Pengeluaran melebihi pemasukan sebesar {abs(sr):.1f}%.")
            elif sr < 10:
                warnings.append(f"Savings rate sangat rendah: hanya {sr:.1f}%.")
            elif sr >= 20:
                positives.append(f"Savings rate bulan ini {sr:.1f}% — sudah di atas target ideal.")

        # ── Tren per kategori ─────────────────────────────────────
        curr_cat = expense_df.groupby("Category")["Amount"].sum()
        prev_cat = prev_exp.groupby("Category")["Amount"].sum()

        for cat in curr_cat.index:
            c = curr_cat[cat]
            p = prev_cat.get(cat, 0)
            if p > 0:
                pct = (c - p) / p * 100
                if pct > 30:
                    warnings.append(f"Kategori '{cat}' melonjak {pct:.0f}% dari bulan lalu.")
                elif pct < -20:
                    positives.append(f"Pengeluaran '{cat}' berkurang {abs(pct):.0f}% — bagus.")

        # ── Weekend behavior ──────────────────────────────────────
        expense_df = expense_df.copy()
        expense_df["Date"] = pd.to_datetime(expense_df["Date"])
        expense_df["_wknd"] = expense_df["Date"].dt.dayofweek.isin([5, 6])
        wknd = expense_df[expense_df["_wknd"]]["Amount"].sum()
        wkdy = expense_df[~expense_df["_wknd"]]["Amount"].sum()

        if total_exp > 0:
            wknd_ratio = wknd / total_exp * 100
            if wknd > wkdy:
                warnings.append(
                    f"Pengeluaran weekend ({wknd_ratio:.0f}%) lebih besar dari weekday — pola boros."
                )
            elif wknd_ratio < 25:
                positives.append(f"Pengeluaran weekend terkontrol: hanya {wknd_ratio:.0f}% dari total.")

        # ── Hari paling aktif ─────────────────────────────────────
        if "Day_of_Week" in expense_df.columns:
            busiest = expense_df.groupby("Day_of_Week")["Amount"].sum().idxmax()
            insights.append(f"Hari dengan pengeluaran tertinggi: {busiest}.")

        # ── Kategori dominan ──────────────────────────────────────
        cat_ratios = _get_category_ratios(expense_df)
        if cat_ratios:
            top_cat, top_ratio = max(cat_ratios.items(), key=lambda x: x[1])
            if top_ratio > 0.50:
                warnings.append(
                    f"Kategori '{top_cat}' mendominasi {top_ratio*100:.0f}% pengeluaran."
                )
            else:
                insights.append(
                    f"Kategori terbesar: '{top_cat}' ({top_ratio*100:.0f}% dari total expense)."
                )

        # ── Transaksi unik ────────────────────────────────────────
        n_txn = len(expense_df)
        insights.append(f"Total {n_txn} transaksi pengeluaran bulan ini.")

        return InsightResult(
            insights  = insights,
            warnings  = warnings,
            positives = positives,
        )


# ══════════════════════════════════════════════════════════════════
# 3. RECOMMEND ENGINE
# ══════════════════════════════════════════════════════════════════

class RecommendEngine:
    """
    Hasilkan rekomendasi aksi spesifik berdasarkan kondisi keuangan.
    Setiap rekomendasi punya priority (high/medium/low) dan estimasi dampak.
    """

    def recommend(
        self,
        df: pd.DataFrame,
        month: int,
        year: int,
    ) -> RecommendResult:

        mdf = _filter_month(df, month, year)
        expense_df, income_df = _split_expense_income(mdf)

        total_exp = expense_df["Amount"].sum()
        total_inc = income_df["Amount"].sum()
        cat_ratios = _get_category_ratios(expense_df)

        recommendations = []
        estimated_saving = 0.0

        # ── Rule: tabungan rendah ─────────────────────────────────
        if total_inc > 0 and (total_inc - total_exp) / total_inc < 0.20:
            target_saving = total_inc * 0.20 - (total_inc - total_exp)
            recommendations.append({
                "priority"        : "high",
                "category"        : "Tabungan",
                "action"          : f"Kurangi pengeluaran Rp {target_saving:,.0f} untuk mencapai savings rate 20%.",
                "estimated_impact": round(target_saving, 0),
            })
            estimated_saving += target_saving

        # ── Rule: hiburan berlebih ────────────────────────────────
        entertain_ratio = cat_ratios.get("Hiburan", cat_ratios.get("Entertainment", 0))
        if entertain_ratio > 0.20:
            excess = (entertain_ratio - 0.20) * total_exp
            recommendations.append({
                "priority"        : "high" if entertain_ratio > 0.30 else "medium",
                "category"        : "Hiburan",
                "action"          : f"Pangkas anggaran hiburan ~{entertain_ratio*100:.0f}% → target 20%. Hemat ≈ Rp {excess:,.0f}.",
                "estimated_impact": round(excess, 0),
            })
            estimated_saving += excess

        # ── Rule: makan & minum ───────────────────────────────────
        food_ratio = cat_ratios.get("Makan & Minum", cat_ratios.get("Food", 0))
        if food_ratio > 0.35:
            excess = (food_ratio - 0.35) * total_exp
            recommendations.append({
                "priority"        : "medium",
                "category"        : "Makan & Minum",
                "action"          : f"Coba meal prep atau masak sendiri untuk kurangi pengeluaran makan ({food_ratio*100:.0f}% saat ini). Potensi hemat Rp {excess:,.0f}.",
                "estimated_impact": round(excess, 0),
            })
            estimated_saving += excess

        # ── Rule: weekend boros ───────────────────────────────────
        expense_df = expense_df.copy()
        expense_df["Date"] = pd.to_datetime(expense_df["Date"])
        expense_df["_wknd"] = expense_df["Date"].dt.dayofweek.isin([5, 6])
        wknd = expense_df[expense_df["_wknd"]]["Amount"].sum()
        wkdy = expense_df[~expense_df["_wknd"]]["Amount"].sum()

        if wknd > wkdy and total_exp > 0:
            excess = wknd - (total_exp * 0.30)
            if excess > 0:
                recommendations.append({
                    "priority"        : "medium",
                    "category"        : "Weekend",
                    "action"          : f"Buat anggaran khusus weekend. Pengeluaran weekend saat ini {wknd/total_exp*100:.0f}% dari total — coba tekan ke 30%.",
                    "estimated_impact": round(excess, 0),
                })
                estimated_saving += excess

        # ── Rule: belanja impulsif ────────────────────────────────
        shopping_ratio = cat_ratios.get("Belanja", cat_ratios.get("Shopping", 0))
        if shopping_ratio > 0.25:
            excess = (shopping_ratio - 0.25) * total_exp
            recommendations.append({
                "priority"        : "medium",
                "category"        : "Belanja",
                "action"          : f"Terapkan 'waiting list 3 hari' sebelum beli barang non-esensial. Belanja saat ini {shopping_ratio*100:.0f}% dari budget.",
                "estimated_impact": round(excess, 0),
            })
            estimated_saving += excess

        # Tidak ada masalah ditemukan
        if not recommendations:
            recommendations.append({
                "priority"        : "low",
                "category"        : "Umum",
                "action"          : "Keuangan bulan ini sudah baik. Pertimbangkan investasi dari kelebihan tabungan.",
                "estimated_impact": 0,
            })

        # Fokus ke kategori dengan potensi penghematan terbesar
        if len(recommendations) > 1:
            focus = max(recommendations, key=lambda x: x["estimated_impact"])
            focus_category = focus["category"]
        else:
            focus_category = recommendations[0]["category"]

        # Urutkan: high → medium → low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return RecommendResult(
            recommendations  = recommendations,
            focus_category   = focus_category,
            estimated_saving = round(estimated_saving, 0),
        )


# ══════════════════════════════════════════════════════════════════
# RULE ENGINE — ORCHESTRATOR UTAMA
# ══════════════════════════════════════════════════════════════════

class RuleEngine:
    """
    Entry point tunggal untuk seluruh rule-based AI.

    Cara pakai:
        engine = RuleEngine()
        result = engine.run(df, month=5, year=2026)

        result["score"]           → ScoreResult
        result["insights"]        → InsightResult
        result["recommendations"] → RecommendResult
    """

    def __init__(self):
        self.scorer    = ScoreCalculator()
        self.inspector = InsightEngine()
        self.advisor   = RecommendEngine()

    def run(
        self,
        df: pd.DataFrame,
        month: Optional[int] = None,
        year: Optional[int]  = None,
    ) -> dict:

        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        if month is None or year is None:
            latest = df["Date"].max()
            month  = month or latest.month
            year   = year  or latest.year

        period = datetime(year, month, 1).strftime("%B %Y")

        score   = self.scorer.calculate(df, month, year)
        insight = self.inspector.analyze(df, month, year)
        reco    = self.advisor.recommend(df, month, year)

        return {
            "period" : period,
            "score"  : {
                "value"     : score.score,
                "status"    : score.status,
                "grade"     : score.grade,
                "deductions": score.deductions,
                "bonuses"   : score.bonuses,
                "breakdown" : score.breakdown,
            },
            "insights": {
                "insights" : insight.insights,
                "warnings" : insight.warnings,
                "positives": insight.positives,
            },
            "recommendations": {
                "items"           : reco.recommendations,
                "focus_category"  : reco.focus_category,
                "estimated_saving": reco.estimated_saving,
            },
        }


# ══════════════════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

    # engine = RuleEngine()
    # df     = pd.read_csv("transaksi.csv")
    # result = engine.run(df, month=5, year=2026)
    # print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    pass