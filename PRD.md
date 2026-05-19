# KampusCuan — Product Requirements Document

> **Versi:** 1.0.0 | **Program:** Coding Camp 2026 — DBS Foundation | **Tim:** CC26-PSU168
>
> **Anggota:** Ahmad Faris Al-Aziz · Muhammad Omar Wylie · Zaky Pratama · Renaldi Simamora · Nikita · Aditya Pratama

---

> ⚠️ **Dokumen ini adalah sumber kebenaran tunggal (single source of truth) proyek KampusCuan.**
> Setiap keputusan arsitektur, struktur folder, skema database, spesifikasi API, dan konvensi kode mengacu pada dokumen ini. Dokumen ini juga dirancang untuk digunakan sebagai konteks oleh AI agent dalam proses pengembangan.

---

## Daftar Isi

1. [Gambaran Umum Proyek](#bab-1--gambaran-umum-proyek)
2. [Struktur Folder Lengkap](#bab-2--struktur-folder-lengkap)
3. [Skema Database](#bab-3--skema-database-prisma--supabase-postgresql)
4. [Spesifikasi Halaman & Fitur](#bab-4--spesifikasi-halaman--fitur-detail)
5. [Spesifikasi API Lengkap](#bab-5--spesifikasi-api-lengkap)
6. [Spesifikasi ML Service](#bab-6--spesifikasi-ml-service-flaskfastapi)
7. [Alur Bisnis & Logic Kritis](#bab-7--alur-bisnis--logic-kritis)
8. [Strategi Performa](#bab-8--strategi-performa)
9. [Keamanan](#bab-9--keamanan)
10. [Environment Variables](#bab-10--environment-variables)
11. [Rencana Pengerjaan](#bab-11--rencana-pengerjaan-development-phases)
12. [Konvensi Kode & Best Practices](#bab-12--konvensi-kode--best-practices)
13. [Decision Log & Catatan Arsitektur](#bab-13--decision-log--catatan-arsitektur)

---

## BAB 1 — Gambaran Umum Proyek

### 1.1 Deskripsi Singkat

KampusCuan adalah aplikasi web manajemen keuangan pribadi yang dirancang khusus untuk mahasiswa Indonesia. Platform ini membantu mahasiswa mencatat transaksi harian, mengatur anggaran bulanan, merencanakan tabungan, membagi tagihan bersama teman, dan memahami kesehatan keuangan mereka melalui insight berbasis kecerdasan buatan (AI).

Berbeda dari aplikasi keuangan umum yang terlalu kompleks atau generik, KampusCuan memahami konteks unik kehidupan mahasiswa: uang kiriman bulanan, pengeluaran kos, makan sehari-hari, langganan digital, dan target tabungan jangka pendek. AI terintegrasi hadir bukan sebagai fitur pelengkap, melainkan sebagai inti pengalaman — mengklasifikasikan pola belanja, memprediksi pengeluaran bulan depan, memberikan rekomendasi personal, dan menjawab pertanyaan keuangan melalui chatbot kontekstual.

### 1.2 Segmen Pengguna

| Peran | Deskripsi | Akses Khusus |
|-------|-----------|--------------|
| Guest | Pengunjung tanpa akun | Landing page, fitur preview (read-only) |
| User (Mahasiswa) | Akun terdaftar via Email/Password atau Google OAuth | Semua fitur utama: transaksi, anggaran, tabungan, split bill, AI features, investasi |
| Admin | Pengelola platform (internal) | Panel admin (opsional MVP): manajemen user, monitoring sistem |

> **Catatan:** Tidak ada multi-role kompleks untuk MVP. Semua pengguna terdaftar memiliki akses penuh ke semua fitur aplikasi. Admin panel bersifat opsional untuk fase pertama.

### 1.3 Tech Stack

| Layer | Teknologi | Versi | Alasan Pemilihan |
|-------|-----------|-------|-----------------|
| Frontend Framework | Next.js (App Router) | 16.x (latest) | SSR/SSG/ISR built-in, performa tinggi, SEO friendly, server components |
| Language | TypeScript | 5+ | Type safety, maintainability, AI-assisted development |
| Styling | Tailwind CSS | 3+ | Utility-first, bundle kecil, rapid development |
| UI Components | Shadcn/ui | latest | Komponen primitif berbasis Radix UI + Tailwind, accessible, customizable |
| Auth | NextAuth.js (Auth.js v5) | v5 | OAuth 2.0 support (Google), credential login, session management built-in |
| Backend Framework | Express.js | latest (5.x) | Lightweight, fleksibel, mudah dikustomisasi, ekosistem luas |
| ORM | Prisma | 5+ | Type-safe queries, auto-migration, schema as code |
| Database | PostgreSQL (Supabase) | 15+ | Reliable relational DB, Supabase menyediakan managed PostgreSQL + Storage + Realtime |
| ML Service | Flask / FastAPI | latest | Python microservice untuk model ML/AI: klasifikasi, prediksi, health score, chatbot |
| State (Client) | Zustand | 4+ | Ringan, tidak butuh boilerplate Redux |
| Server State | TanStack Query | 5+ | Cache otomatis, refetch, optimistic updates, deduplicate requests |
| Form Validation | Zod + React Hook Form | latest | Schema validation shared antara client dan server |
| HTTP Client | Axios | latest | Komunikasi antar layanan: Next.js → Express.js → Flask |
| Charts | Recharts | latest | Chart library untuk visualisasi data keuangan (line, bar, donut) |
| Deployment FE | Vercel | latest | Optimal untuk Next.js, continuous deployment dari GitHub |
| Deployment BE | Railway / Render | latest | PaaS untuk Express.js backend |
| Deployment ML | Railway / Render | latest | Hosting Flask/FastAPI microservice |

### 1.4 Design System

KampusCuan menggunakan design system bertema **"Neon Brutalist"** — menggabungkan estetika editorial premium dengan dark mode yang elegan.

#### Color Tokens

| Token | Nilai Hex | Penggunaan |
|-------|-----------|-----------|
| Primary (Lime) | `#BCFF4F` | Aksi utama, data penting, CTA buttons, aksen navigasi |
| Surface | `#0A0A0A` | Background utama (dark mode) |
| Surface-Container | `#141414` | Background kartu dan modul interaktif |
| On-Surface | `#F4F4F0` | Teks utama dan ikon primer |
| Muted Text | `#888888` | Teks tersier, metadata, placeholder |
| Surface-Container-High | `#2A2A2A` | State hover pada list item |
| Outline-Variant | `#424936` | Ghost border accessibility (20% opacity) |

#### Typography & Component Rules

| Elemen | Spesifikasi |
|--------|------------|
| Font Family | Inter (Google Fonts) — Display: Black 900, Headline: Bold 700, Body: Regular 400 |
| Display Type | Inter Black 900, min 3.5rem, letter-spacing: -0.04em |
| Button Style | Pill shape (border-radius: 100px). Primary: bg `#BCFF4F`, text `#0A0A0A`. Secondary: outline `#BCFF4F` |
| Input Fields | Minimalist, no bounding box, single 2px bottom border, focus → lime gradient |
| Cards | Tonal layering, tidak menggunakan drop shadow. Elevation ditunjukkan dengan perbedaan background |
| List Items | Tidak ada horizontal divider. Spacing minimum 24px, hover: bg `#2A2A2A` + 4px lime left accent |
| No-Line Rule | Dilarang menggunakan 1px solid grey border. Pemisahan konten menggunakan background shift |

---

## BAB 2 — Struktur Folder Lengkap

Proyek menggunakan **monorepo sederhana** dengan tiga direktori utama: `/frontend` (Next.js), `/backend` (Express.js), dan `/ml-service` (Flask/FastAPI). Setiap file dibatasi satu tanggung jawab (Single Responsibility Principle).

### 2.1 Root Monorepo

```
/kampuscuan/
+-- /frontend/              # Next.js 15 App (App Router)
+-- /backend/               # Express.js REST API
+-- /ml-service/            # Python Flask/FastAPI microservice
+-- .gitignore
+-- README.md
`-- package.json            # root scripts (concurrently dev)
```

### 2.2 Frontend — Struktur Lengkap

```
/frontend/
+-- /src/
|   +-- /app/                          # Next.js App Router
|   |   +-- layout.tsx                 # Root layout (font, metadata, providers)
|   |   +-- page.tsx                   # Landing Page (/)
|   |   +-- /auth/
|   |   |   +-- /login/page.tsx        # Login Page
|   |   |   +-- /register/page.tsx     # Register Page
|   |   |   `-- /forgot-password/page.tsx
|   |   +-- /dashboard/page.tsx        # Dashboard utama
|   |   +-- /transactions/page.tsx     # Transaksi & Jurnal Bulanan
|   |   +-- /budgeting/page.tsx        # Budgeting & Kalender Pembayaran
|   |   +-- /savings/page.tsx          # Target Tabungan
|   |   +-- /split-bill/page.tsx       # Split Bill & Utang Piutang
|   |   +-- /financial-health/page.tsx # Financial Health & AI Warnings
|   |   +-- /forecast/page.tsx         # Prediksi Pengeluaran (AI)
|   |   +-- /chatbot/page.tsx          # Chatbot Cuan AI
|   |   +-- /investment/page.tsx       # Pantau Investasi
|   |   +-- /profile/page.tsx          # Profil & Pengaturan
|   |   `-- /api/                      # Next.js API Routes (Auth.js callbacks)
|   |       `-- /auth/[...nextauth]/route.ts
|   |
|   +-- /components/
|   |   +-- /ui/                       # Shadcn/ui primitives
|   |   |   +-- button.tsx
|   |   |   +-- input.tsx
|   |   |   +-- modal.tsx (dialog.tsx)
|   |   |   +-- badge.tsx
|   |   |   +-- toast.tsx (sonner)
|   |   |   +-- skeleton.tsx
|   |   |   +-- card.tsx
|   |   |   +-- tabs.tsx
|   |   |   +-- progress.tsx
|   |   |   +-- dropdown-menu.tsx
|   |   |   +-- calendar.tsx
|   |   |   +-- popover.tsx
|   |   |   `-- avatar.tsx
|   |   +-- /layout/
|   |   |   +-- Sidebar.tsx            # Sidebar navigasi dark navy
|   |   |   +-- TopBar.tsx             # Header dengan user avatar & notif
|   |   |   +-- AppLayout.tsx          # Wrapper layout autentikasi
|   |   |   `-- LandingNavbar.tsx      # Navbar landing page
|   |   +-- /dashboard/
|   |   |   +-- MetricCard.tsx         # Kartu ringkasan (saldo, pengeluaran, dll)
|   |   |   +-- SpendingTrendChart.tsx # Line/bar chart 6 bulan
|   |   |   +-- CategoryDonutChart.tsx # Donut chart per kategori
|   |   |   +-- RecentTransactions.tsx # Daftar 5 transaksi terbaru
|   |   |   +-- BudgetOverview.tsx     # Progress bar anggaran
|   |   |   `-- AIInsightCard.tsx      # Kartu insight AI
|   |   +-- /transactions/
|   |   |   +-- TransactionList.tsx    # Daftar transaksi grouped by date
|   |   |   +-- TransactionItem.tsx    # Satu baris transaksi
|   |   |   +-- AddTransactionModal.tsx
|   |   |   +-- TransactionFilter.tsx  # Filter & search
|   |   |   `-- AIJournalSection.tsx   # Analisis AI bulanan
|   |   +-- /budgeting/
|   |   |   +-- BudgetCategoryList.tsx
|   |   |   +-- BudgetProgressBar.tsx
|   |   |   +-- PaymentCalendar.tsx    # Grid kalender tagihan
|   |   |   `-- ScheduledPaymentForm.tsx
|   |   +-- /savings/
|   |   |   +-- SavingsGoalCard.tsx    # Kartu goal dengan progress ring
|   |   |   +-- AddGoalModal.tsx
|   |   |   `-- AddFundsModal.tsx
|   |   +-- /split-bill/
|   |   |   +-- SplitBillCard.tsx
|   |   |   +-- CreateSplitModal.tsx
|   |   |   `-- ParticipantStatusBadge.tsx
|   |   +-- /financial-health/
|   |   |   +-- HealthScoreGauge.tsx   # Gauge/ring 0-100
|   |   |   +-- SpendingProfileCard.tsx
|   |   |   +-- AnomalyAlertCard.tsx
|   |   |   `-- RecommendationCard.tsx
|   |   +-- /forecast/
|   |   |   +-- ForecastChart.tsx      # Line chart aktual + prediksi
|   |   |   `-- CategoryForecastTable.tsx
|   |   +-- /chatbot/
|   |   |   +-- ChatInterface.tsx
|   |   |   +-- MessageBubble.tsx
|   |   |   `-- SuggestedQuestions.tsx
|   |   `-- /investment/
|   |       +-- PriceCard.tsx          # Kartu harga emas/crypto/kurs
|   |       `-- MiniSparkline.tsx
|   |
|   +-- /hooks/
|   |   +-- useAuth.ts                 # Auth state dari NextAuth session
|   |   +-- useTransactions.ts
|   |   +-- useBudget.ts
|   |   +-- useSavings.ts
|   |   +-- useSplitBill.ts
|   |   +-- useFinancialHealth.ts      # Fetch AI health score
|   |   +-- useForecast.ts             # Fetch ML prediction
|   |   `-- useToast.ts
|   |
|   +-- /lib/
|   |   +-- api.ts                     # Axios instance + interceptors
|   |   +-- auth.ts                    # NextAuth config (OAuth + credentials)
|   |   +-- formatters.ts              # Format IDR, tanggal, persentase
|   |   +-- constants.ts               # Kategori, warna status, payment methods
|   |   `-- queryClient.ts             # TanStack Query config
|   |
|   +-- /store/
|   |   `-- authStore.ts               # Zustand: user session state
|   |
|   +-- /types/
|   |   +-- transaction.ts
|   |   +-- budget.ts
|   |   +-- savings.ts
|   |   +-- splitbill.ts
|   |   +-- ai.ts                      # Types untuk AI responses
|   |   `-- api.ts
|   |
|   `-- /validators/
|       +-- transactionSchema.ts       # Zod: validasi form transaksi
|       +-- budgetSchema.ts
|       +-- savingsSchema.ts
|       `-- authSchema.ts
|
+-- /public/
+-- next.config.ts
+-- tailwind.config.ts
+-- components.json                    # Shadcn/ui config
`-- tsconfig.json
```

### 2.3 Backend — Struktur Lengkap

```
/backend/
+-- /prisma/
|   +-- schema.prisma                  # Semua model database
|   +-- /migrations/                   # File migrasi otomatis
|   `-- seed.ts                        # Data awal (user demo, kategori)
|
+-- /src/
|   +-- server.ts                      # Entry point Express
|   +-- /config/
|   |   +-- env.ts                     # Validasi env via Zod
|   |   +-- database.ts                # Prisma client singleton
|   |   `-- cors.ts                    # CORS config
|   |
|   +-- /routes/
|   |   +-- index.ts                   # Mount semua router ke /api/v1
|   |   +-- auth.routes.ts
|   |   +-- transaction.routes.ts
|   |   +-- budget.routes.ts
|   |   +-- savings.routes.ts
|   |   +-- splitbill.routes.ts
|   |   +-- ai.routes.ts               # Proxy ke ML service
|   |   +-- investment.routes.ts       # Fetch API publik harga aset
|   |   +-- profile.routes.ts
|   |   `-- notification.routes.ts
|   |
|   +-- /controllers/
|   |   +-- auth.controller.ts
|   |   +-- transaction.controller.ts
|   |   +-- budget.controller.ts
|   |   +-- savings.controller.ts
|   |   +-- splitbill.controller.ts
|   |   +-- ai.controller.ts
|   |   +-- investment.controller.ts
|   |   `-- profile.controller.ts
|   |
|   +-- /services/
|   |   +-- auth.service.ts            # Login, register, OAuth, token mgmt
|   |   +-- transaction.service.ts     # CRUD transaksi, filter, agregasi
|   |   +-- budget.service.ts          # CRUD budget, hitung usage
|   |   +-- savings.service.ts         # Goals, progress, estimasi
|   |   +-- splitbill.service.ts       # Buat split, update status
|   |   +-- ai.service.ts              # Komunikasi ke Flask ML service
|   |   +-- investment.service.ts      # Fetch & cache harga aset
|   |   `-- notification.service.ts    # Alert budget overrun
|   |
|   +-- /middlewares/
|   |   +-- authenticate.ts            # Verifikasi JWT
|   |   +-- authorize.ts               # Cek role
|   |   +-- validate.ts                # Zod validation middleware
|   |   +-- rateLimiter.ts
|   |   `-- errorHandler.ts
|   |
|   +-- /validators/
|   |   +-- auth.validator.ts
|   |   +-- transaction.validator.ts
|   |   +-- budget.validator.ts
|   |   `-- savings.validator.ts
|   |
|   `-- /helpers/
|       +-- jwt.helper.ts
|       +-- hash.helper.ts
|       +-- response.helper.ts
|       `-- dateHelper.ts
|
+-- .env
`-- package.json
```

### 2.4 ML Service — Struktur Lengkap

```
/ml-service/
+-- /models/                           # Model terlatih (.pkl / .joblib)
|   +-- spending_classifier.pkl        # Model klasifikasi pola belanja
|   +-- expense_forecaster.pkl         # Model prediksi pengeluaran
|   `-- anomaly_detector.pkl           # Model deteksi anomali
|
+-- /data/
|   `-- df_combined_clean.csv          # Dataset pelatihan
|
+-- /notebooks/
|   +-- 01_eda.ipynb
|   +-- 02_classification.ipynb
|   `-- 03_forecasting.ipynb
|
+-- /app/
|   +-- main.py                        # FastAPI entry point
|   +-- /routers/
|   |   +-- classify.py                # POST /classify/spending-pattern
|   |   +-- forecast.py                # POST /forecast/next-month
|   |   +-- health_score.py            # POST /health-score
|   |   +-- anomaly.py                 # POST /anomaly/detect
|   |   +-- categorize.py              # POST /categorize/auto
|   |   `-- chatbot.py                 # POST /chatbot/chat
|   +-- /schemas/
|   |   `-- request_schemas.py         # Pydantic models untuk request/response
|   +-- /services/
|   |   +-- classifier_service.py
|   |   +-- forecaster_service.py
|   |   +-- health_score_service.py
|   |   +-- anomaly_service.py
|   |   +-- categorizer_service.py
|   |   `-- chatbot_service.py         # Integrasi Gemini/OpenAI API
|   `-- /utils/
|       +-- preprocessing.py           # Feature engineering pipeline
|       `-- model_loader.py            # Load & cache model saat startup
|
+-- requirements.txt
`-- Dockerfile
```

---

## BAB 3 — Skema Database (Prisma + Supabase PostgreSQL)

Semua model didefinisikan di `prisma/schema.prisma`. Database di-host di **Supabase PostgreSQL**. Gunakan UUID sebagai primary key untuk semua tabel. Setiap tabel memiliki field `createdAt` dan `updatedAt` secara default.

### 3.1 Model: User

| Field | Tipe Prisma | Constraint | Keterangan |
|-------|-------------|-----------|-----------|
| id | String | @id @default(uuid()) | PK UUID otomatis |
| name | String | required | Nama lengkap pengguna |
| email | String | @unique, required | Email untuk login |
| passwordHash | String? | optional | Null jika login via OAuth |
| provider | AuthProvider | default: CREDENTIALS | CREDENTIALS, GOOGLE |
| providerAccountId | String? | optional | ID akun dari OAuth provider |
| university | String? | optional | Nama universitas mahasiswa |
| monthlyAllowance | Decimal? | optional | Uang bulanan (untuk referensi budget) |
| avatarUrl | String? | optional | URL foto profil |
| role | Role | default: USER | USER atau ADMIN |
| preferredCurrency | String | default: IDR | Mata uang preferensi |
| notifBudgetAlert | Boolean | default: true | Toggle notif overbudget |
| notifWeeklyReport | Boolean | default: true | Toggle laporan mingguan |
| createdAt | DateTime | @default(now()) | auto |
| updatedAt | DateTime | @updatedAt | auto |

### 3.2 Model: Transaction

Model utama aplikasi. Setiap record merepresentasikan satu transaksi keuangan (pemasukan atau pengeluaran). Kolom ini sesuai dengan dataset pelatihan ML dan input form aplikasi.

| Field | Tipe Prisma | Constraint | Keterangan |
|-------|-------------|-----------|-----------|
| id | String | @id @default(uuid()) | PK |
| userId | String | FK → User | Pemilik transaksi |
| type | TransactionType | required | INCOME atau EXPENSE |
| date | DateTime | required | Tanggal transaksi |
| amount | Decimal | required, > 0 | Nominal transaksi dalam IDR |
| category | String | required | Kategori (lihat 3.2.1) |
| paymentMethod | String | required | Metode pembayaran (lihat 3.2.2) |
| description | String | required | Deskripsi/nama transaksi |
| notes | String? | optional | Catatan tambahan dari user |
| isAutoCateg | Boolean | default: false | True jika kategori di-assign otomatis oleh AI |
| isAnomaly | Boolean | default: false | True jika terdeteksi anomali oleh ML service |
| createdAt | DateTime | @default(now()) | auto |
| updatedAt | DateTime | @updatedAt | auto |

#### 3.2.1 Daftar Kategori Standar

Diturunkan dari analisis dataset `df_combined_clean.csv` dan disesuaikan untuk konteks mahasiswa:

| Kategori (DB value) | Label Tampilan | Tipe Default | Keterangan |
|--------------------|---------------|-------------|-----------|
| Makan & Minum | Makan & Minum | EXPENSE | Makanan, minuman, warung, kafe, food delivery |
| Transportasi | Transportasi | EXPENSE | Ojol, bensin, parkir, KRL, busway |
| Tagihan | Tagihan & Utilitas | EXPENSE | Kos, listrik, air, internet, iuran |
| Hiburan | Hiburan | EXPENSE | Streaming, game, bioskop, konser, rekreasi |
| Belanja | Belanja | EXPENSE | Pakaian, elektronik, kebutuhan rumah |
| Pendidikan | Pendidikan | EXPENSE | SPP, buku, kursus, alat tulis |
| Kesehatan | Kesehatan | EXPENSE | Obat, dokter, suplemen, gym |
| Household | Kebutuhan Rumah | EXPENSE | Perlengkapan kos, kebersihan |
| Apparel | Pakaian & Fashion | EXPENSE | Baju, sepatu, aksesoris |
| Goals | Tabungan/Goals | EXPENSE | Transfer ke rekening tabungan/goals |
| Gaji | Gaji / Pendapatan | INCOME | Gaji, upah kerja |
| Allowance | Uang Kiriman | INCOME | Kiriman orang tua, beasiswa bulanan |
| Salary | Penghasilan Lain | INCOME | Freelance, part-time, komisi |
| Other | Lainnya | EXPENSE/INCOME | Tidak termasuk kategori di atas |
| Uncategorized | Belum Dikategorikan | EXPENSE | Default untuk auto-kategorisasi yang tidak confident |

#### 3.2.2 Daftar Metode Pembayaran

| Value (DB) | Label Tampilan |
|-----------|---------------|
| Gopay | GoPay |
| OVO | OVO |
| DANA | DANA |
| BCA | BCA (Transfer/Debit) |
| BRI | BRI (Transfer/Debit) |
| Mandiri | Mandiri (Transfer/Debit) |
| BNI | BNI (Transfer/Debit) |
| Dompet Tunai | Tunai / Cash |
| Kartu Kredit | Kartu Kredit |
| Other | Lainnya |

### 3.3 Model: Budget

| Field | Tipe | Keterangan |
|-------|------|-----------|
| id | String | PK UUID |
| userId | String | FK → User |
| category | String | Kategori yang diatur budgetnya |
| limitAmount | Decimal | Batas pengeluaran per bulan untuk kategori ini |
| month | Int | Bulan (1-12) |
| year | Int | Tahun (YYYY) |
| createdAt | DateTime | auto |
| updatedAt | DateTime | auto |

> **Unique constraint:** `(userId, category, month, year)` — satu user hanya bisa punya satu budget per kategori per bulan.

### 3.4 Model: SavingsGoal

| Field | Tipe | Keterangan |
|-------|------|-----------|
| id | String | PK UUID |
| userId | String | FK → User |
| name | String | Nama goal, contoh: "Beli Laptop" |
| targetAmount | Decimal | Target nominal yang ingin dicapai |
| currentAmount | Decimal | default: 0, Jumlah yang sudah terkumpul |
| deadline | DateTime? | optional, Target tanggal tercapai |
| icon | String? | Emoji atau nama ikon representasi goal |
| isCompleted | Boolean | default: false |
| createdAt | DateTime | auto |
| updatedAt | DateTime | auto |

### 3.5 Model: SavingsTransaction

Setiap kali user menambah atau menarik dana dari savings goal, dicatat di sini.

| Field | Tipe | Keterangan |
|-------|------|-----------|
| id | String | PK UUID |
| goalId | String | FK → SavingsGoal |
| userId | String | FK → User |
| amount | Decimal | Nominal yang ditambahkan/ditarik |
| type | SavingsTransactionType | DEPOSIT atau WITHDRAWAL |
| note | String? | Catatan opsional |
| createdAt | DateTime | auto |

### 3.6 Model: SplitBill

| Field | Tipe | Keterangan |
|-------|------|-----------|
| id | String | PK UUID |
| userId | String | FK → User (pembuat split) |
| title | String | Nama tagihan, contoh: "Makan Yoshinoya" |
| totalAmount | Decimal | Total tagihan sebelum dibagi |
| date | DateTime | Tanggal kejadian |
| isSettled | Boolean | default: false, True jika semua sudah bayar |
| createdAt | DateTime | auto |
| updatedAt | DateTime | auto |

### 3.7 Model: SplitBillParticipant

| Field | Tipe | Keterangan |
|-------|------|-----------|
| id | String | PK UUID |
| splitBillId | String | FK → SplitBill |
| name | String | Nama peserta (input manual, bukan FK User) |
| shareAmount | Decimal | Jumlah yang harus dibayar peserta ini |
| isPaid | Boolean | default: false |
| paidAt | DateTime? | Waktu konfirmasi bayar |

### 3.8 Model: ScheduledPayment (Tagihan Rutin)

| Field | Tipe | Keterangan |
|-------|------|-----------|
| id | String | PK UUID |
| userId | String | FK → User |
| name | String | Nama tagihan, contoh: "Bayar Kos" |
| amount | Decimal | Nominal tagihan |
| category | String | Kategori tagihan |
| dueDay | Int | Tanggal jatuh tempo setiap bulan (1-31) |
| frequency | PaymentFrequency | MONTHLY, WEEKLY, ONE_TIME |
| nextDueDate | DateTime | Tanggal jatuh tempo berikutnya |
| isActive | Boolean | default: true |
| createdAt | DateTime | auto |

### 3.9 Model: Notification

| Field | Tipe | Keterangan |
|-------|------|-----------|
| id | String | PK UUID |
| userId | String | FK → User |
| type | NotificationType | BUDGET_ALERT, ANOMALY, AI_INSIGHT, PAYMENT_REMINDER |
| title | String | Judul notifikasi |
| message | String | Isi pesan notifikasi |
| isRead | Boolean | default: false |
| metadata | Json? | Data tambahan (category, amount, dll) |
| createdAt | DateTime | auto |

---

## BAB 4 — Spesifikasi Halaman & Fitur Detail

### 4.0 Daftar Halaman & Routing

| Route | Nama Halaman | Auth | Rendering |
|-------|-------------|------|----------|
| `/` | Landing Page | Public | SSG |
| `/auth/login` | Login | Public (redirect jika sudah login) | CSR |
| `/auth/register` | Register | Public | CSR |
| `/auth/forgot-password` | Lupa Password | Public | CSR |
| `/dashboard` | Dashboard | Protected | SSR |
| `/transactions` | Transaksi & Jurnal | Protected | SSR |
| `/budgeting` | Budgeting & Kalender | Protected | SSR |
| `/savings` | Target Tabungan | Protected | SSR |
| `/split-bill` | Split Bill | Protected | SSR |
| `/financial-health` | Financial Health & AI | Protected | SSR |
| `/forecast` | Prediksi Pengeluaran | Protected | CSR |
| `/chatbot` | Chatbot Cuan AI | Protected | CSR |
| `/investment` | Pantau Investasi | Protected | ISR (60s) |
| `/profile` | Profil & Pengaturan | Protected | SSR |

### 4.1 Landing Page (/) — SSG

**Tujuan:** Halaman publik yang memperkenalkan KampusCuan dan mendorong pengunjung untuk mendaftar.

| Section | Komponen | Konten |
|---------|----------|--------|
| Hero | LandingNavbar + Hero section | Headline besar (Inter Black), tagline, dua CTA: "Mulai Gratis" (→ /register) dan "Login". Background dark dengan lime accent. Preview dashboard mockup. |
| Fitur Unggulan | FeatureGrid | 6 kartu fitur: Catat Transaksi, Budgeting Cerdas, Tabungan Goal, AI Insight, Split Bill, Pantau Investasi. |
| AI Showcase | AIShowcaseSection | Highlight fitur AI: health score, prediksi, chatbot. Animasi angka atau grafik sederhana. |
| Testimoni | TestimonialSection | Quote dari pengguna mahasiswa (static untuk MVP). |
| CTA Footer | CTASection + Footer | "Mulai kelola keuanganmu hari ini" + tombol register. |

### 4.2 Autentikasi

**Teknologi:** NextAuth.js (Auth.js v5) dengan dua provider: Credentials (email/password) dan Google OAuth 2.0.

#### 4.2.1 Login (`/auth/login`)

- Form: Email input + Password input (toggle show/hide)
- Tombol "Masuk" — POST ke NextAuth credentials provider
- Tombol "Lanjut dengan Google" — trigger Google OAuth flow
- Link "Lupa password?" → `/auth/forgot-password`
- Link "Belum punya akun? Daftar" → `/auth/register`
- Validasi client-side dengan Zod: email format, password min 8 karakter
- Jika sudah login: redirect otomatis ke `/dashboard`

#### 4.2.2 Register (`/auth/register`)

- Form: Nama Lengkap, Email, Password, Konfirmasi Password
- Field opsional: Nama Universitas, Uang Bulanan
- Tombol "Daftar" — POST `/api/v1/auth/register`
- Tombol "Daftar dengan Google" — trigger Google OAuth
- Setelah berhasil: auto-login → redirect ke `/dashboard`

#### 4.2.3 Forgot Password (`/auth/forgot-password`)

- Form: Email input
- Submit: kirim email reset link via backend
- Rate limited: max 3 request per jam per email
- OAuth users (Google) tidak bisa reset password — tampilkan pesan informatif

### 4.3 Dashboard (`/dashboard`) — SSR

**Tujuan:** Halaman utama setelah login. Menampilkan ringkasan keuangan bulan ini secara komprehensif.

| Section | Komponen | Data Source | Detail |
|---------|----------|------------|--------|
| Greeting + Bulan | TopBar | Session user | Sapaan dengan nama user, bulan & tahun aktif |
| 4 Metric Cards | MetricCard x4 | GET /transactions/summary | Saldo, Total pengeluaran, Total pemasukan, Total tabungan. Perubahan vs bulan lalu (↑↓%) |
| Spending Trend Chart | SpendingTrendChart | GET /transactions/monthly-trend?months=6 | Line/bar chart 6 bulan. Dua line: pemasukan & pengeluaran. |
| Category Donut | CategoryDonutChart | GET /transactions/by-category | Donut chart pengeluaran per kategori bulan ini + legend |
| Recent Transactions | RecentTransactions | GET /transactions?limit=5 | 5 transaksi terbaru. Link "Lihat semua" |
| Budget Overview | BudgetOverview | GET /budget/overview | 3-4 kategori sebagai horizontal progress bar. Merah jika overbudget. |
| AI Insight Card | AIInsightCard | GET /ai/insight (cached 1 jam) | Teks insight AI singkat (1-2 kalimat). Tombol "Lihat detail" → /financial-health |

### 4.4 Transaksi & Jurnal Bulanan (`/transactions`) — SSR

**Tujuan:** Riwayat lengkap semua transaksi dengan filter, dan analisis AI per periode.

| Elemen | Detail |
|--------|--------|
| Header | Judul "Transactions", month-year selector, tombol "Tambah Transaksi" |
| Summary Chips | 3 chip: Total Pemasukan, Total Pengeluaran, Net Balance |
| Filter & Search | Search by deskripsi (debounce 400ms), filter kategori, tipe, metode pembayaran, date range |
| Transaction List | Dikelompokkan berdasarkan tanggal. Setiap item: ikon kategori, nama, kategori badge, jam, nominal. Badge "AI" jika auto-kategorisasi. |
| Pagination | 20 transaksi per halaman |
| AI Journal Section | Paragraph ringkasan AI bulan ini: kategori terbesar, perbandingan bulan lalu, saran. 2-3 insight chip. |

#### 4.4.1 Modal Tambah / Edit Transaksi

| Field | Tipe Input | Validasi | Catatan |
|-------|-----------|---------|--------|
| Tipe Transaksi | Toggle: Pemasukan / Pengeluaran | Required | Maps ke INCOME / EXPENSE |
| Tanggal | Date picker (default: hari ini) | Required, tidak bisa future date | Format: DD MMM YYYY |
| Nominal | Number input (format IDR otomatis) | Required, > 0, max 99.999.999 | Input: angka, display: "Rp 50.000" |
| Kategori | Dropdown dengan ikon | Required | Auto-suggest dari AI saat user ketik deskripsi |
| Metode Pembayaran | Dropdown | Required | Daftar dari constants.ts |
| Deskripsi | Text input | Required, max 100 char | Trigger auto-kategorisasi AI saat blur |
| Catatan | Textarea | Optional, max 255 char | Catatan tambahan user |

> **Auto-kategorisasi:** Saat user selesai mengetik deskripsi dan blur dari field, frontend memanggil `POST /api/v1/ai/categorize`. Jika confidence ≥ 0.6: auto-fill dropdown + badge "AI". User tetap bisa mengubah manual.

### 4.5 Budgeting & Kalender (`/budgeting`) — SSR

**Tujuan:** Mengatur anggaran per kategori dan menjadwalkan pembayaran rutin. Dua tab utama.

#### Tab 1: Budget Bulanan

- Header: bulan aktif + total overview (progress bar besar: total terpakai / total budget)
- Daftar kategori budget: nama, ikon, limit, terpakai, sisa, progress bar
- Progress bar: hijau < 80%, kuning 80–99%, merah ≥ 100% (overbudget)
- Tombol "Edit" per baris. Tombol "Tambah Kategori Budget" di atas
- AI Prediction chip: "AI prediksi kamu akan overbudget 15%"

#### Tab 2: Kalender Tagihan

- Grid kalender bulanan dengan "tagihan chip" per tanggal (warna lime)
- Klik tanggal: side panel detail tagihan (nama, nominal, kategori, frekuensi, tombol "Tandai Lunas")
- Tombol "Tambah Tagihan Rutin" di atas kalender
- Section "Tagihan Bulan Ini" di bawah: list urut berdasarkan due date

### 4.6 Target Tabungan (`/savings`) — SSR

**Tujuan:** Membuat dan memantau progress goals tabungan dengan estimasi waktu tercapai.

| Elemen | Detail |
|--------|--------|
| Header | Total tabungan aktif, tombol "Buat Goal Baru" |
| Grid Goal Cards | 2 kolom. Setiap kartu: nama goal, ikon/emoji, target amount, current amount, circular progress ring (%), deadline, estimasi tanggal tercapai, tombol "Tambah Dana" dan "Edit" |
| Tambah Dana Modal | Input nominal, note opsional, konfirmasi. Update currentAmount + buat SavingsTransaction record |
| AI Saving Tips | 2-3 tip AI personal berdasarkan data pengeluaran user |
| State Kosong | Ilustrasi + "Belum ada goals. Mulai rencanakan tabunganmu!" + CTA |

### 4.7 Split Bill (`/split-bill`) — SSR

**Tujuan:** Mencatat dan melacak tagihan bersama teman.

| Elemen | Detail |
|--------|--------|
| Tab Filter | Tab: "Belum Lunas" dan "Riwayat" |
| Split Bill Card | Judul, total, tanggal, jumlah peserta, daftar nama + share amount + status (✓ / ○). Tombol "Tandai Lunas" per peserta. Badge "Lunas Semua" jika settled. |
| Buat Split Modal | Judul, total amount, daftar peserta (add by name). Pilih split: Equal atau Custom. Tanggal. |
| Riwayat Tab | List split bill settled. Summary: judul, tanggal, total, jumlah peserta |
| Tombol Tambah | "Buat Split Baru" — lime pill button di top right |

### 4.8 Financial Health & AI Warnings (`/financial-health`) — SSR

**Tujuan:** Skor kesehatan keuangan AI, profil pola belanja, peringatan aktif, dan rekomendasi personal.

| Section | Komponen | Detail |
|---------|----------|--------|
| Health Score | HealthScoreGauge | Gauge circular, skor 0–100. Label: Kritis (0–40), Perlu Perhatian (41–60), Cukup Baik (61–80), Sehat (81–100). Penjelasan AI 2–3 kalimat. |
| Spending Profile | SpendingProfileCard | Label: "Hemat", "Normal", atau "Boros". Badge besar dengan warna. Deskripsi faktor yang menentukan label. |
| Active Warnings | AnomalyAlertCard | List peringatan: ikon severity (⚠️/🚨), pesan singkat, badge keparahan, tombol dismiss. |
| Recommendations | RecommendationCard | 3–4 kartu rekomendasi + estimasi penghematan per bulan. Tombol "Tandai Sudah Dilakukan" |
| Refresh | inline | Tombol refresh. Rate limited: max 3x per hari |

### 4.9 Prediksi Pengeluaran (`/forecast`) — CSR

**Tujuan:** Prediksi pengeluaran bulan depan berbasis ML, per kategori dan total.

| Elemen | Detail |
|--------|--------|
| Header | "Prediksi Pengeluaran" + subtitle "Proyeksi AI untuk bulan depan berdasarkan riwayatmu" |
| Forecast Chart | Line chart dual: aktual 3 bulan lalu (putih) + prediksi bulan depan (lime). Shaded area = confidence interval. |
| By Category Table | Per kategori: bulan lalu aktual \| prediksi bulan depan \| trend indicator (↑ merah / ↓ hijau / → abu). Kolom sortable. |
| AI Summary | 2–3 kalimat penjelasan AI: kategori yang diprediksi naik, saran persiapan |
| Accuracy Note | Disclaimer: "Prediksi berdasarkan min. 2 bulan data." |

### 4.10 Chatbot Cuan AI (`/chatbot`) — CSR

**Tujuan:** Chat interaktif dengan AI yang memahami data keuangan user.

| Elemen | Detail |
|--------|--------|
| Intro Panel | Nama: "Cuan AI", avatar ikon. 4 suggested questions sebagai pill chips: "Berapa pengeluaranku bulan ini?", "Kategori apa yang paling banyak?", "Gimana cara hemat bulan depan?", "Kapan goals tabunganku tercapai?" |
| Chat Interface | Thread percakapan: user kanan (lime bubble), AI kiri (dark bubble). AI bisa berisi teks, kartu data kecil, atau bullet list. |
| Context Injection | Setiap request menyertakan: summary transaksi 3 bulan, budget bulan ini, health score, goals aktif. AI sudah "tahu" kondisi user. |
| Input | Text input full-width + tombol send (lime). Support Enter untuk kirim. |
| Loading State | Typing indicator (3 dot animation) |
| History | Riwayat chat di localStorage untuk sesi yang sama. Tidak persisten lintas sesi (MVP). |

### 4.11 Pantau Investasi (`/investment`) — ISR (60s)

**Tujuan:** Menampilkan harga aset investasi dari API publik. Informatif dan edukatif, bukan platform trading.

| Elemen | Detail |
|--------|--------|
| Header | "Investment Watch" + disclaimer "Hanya untuk informasi edukatif" |
| Price Cards (3) | Harga emas (Logam Mulia), USD/IDR, Bitcoin. Setiap kartu: nama aset, harga IDR, perubahan harian, 7-day sparkline, timestamp update. |
| Beginner Guide | 2–3 kartu artikel edukasi investasi untuk mahasiswa |
| Disclaimer | "Data untuk tujuan edukasi. KampusCuan tidak memberikan saran investasi." |

> **Data source:** Harga emas dari logammulia.com / API alternatif. Kurs dari exchangerate-api.com (free tier). Bitcoin dari CoinGecko API (free). Di-cache di backend, revalidate setiap 60 detik.

### 4.12 Profil & Pengaturan (`/profile`) — SSR

**Tujuan:** Mengelola data profil, preferensi, dan pengaturan akun.

| Section | Detail |
|---------|--------|
| Header Profil | Avatar (foto atau inisial), nama lengkap, email, universitas. Tombol "Edit Profil" |
| Informasi Pribadi | Edit: nama lengkap, universitas, uang bulanan. Email tidak bisa diubah. |
| Preferensi Notifikasi | Toggle: Alert overbudget, Reminder tagihan, Notif insight AI baru, Laporan mingguan |
| Manajemen Kategori | Daftar kategori custom. Tambah, rename, hapus (jika tidak ada transaksi). |
| Keamanan | Credentials: form "Ganti Password". OAuth: info "Akun terhubung dengan Google" |
| Data & Privasi | "Export Data (CSV)" + "Hapus Akun" (konfirmasi modal + hapus cascade) |
| Tentang Aplikasi | Versi app, link syarat & ketentuan, kebijakan privasi |

---

## BAB 5 — Spesifikasi API Lengkap

**Base URL:** `/api/v1` | **Content-Type:** `application/json` | **Auth:** JWT via Bearer token atau HttpOnly Cookie

```json
// Format Response Standar
{ "success": true, "data": {...}, "message": "OK" }
{ "success": false, "error": "Pesan error", "details": [...] }
```

### 5.1 Auth Endpoints

| Method | Path | Body / Query | Response | Auth |
|--------|------|-------------|---------|------|
| POST | `/auth/register` | `{ name, email, password, confirmPassword, university?, monthlyAllowance? }` | `{ user, accessToken }`, set cookie | Public |
| POST | `/auth/login` | `{ email, password }` | `{ user, accessToken }`, set cookie | Public |
| POST | `/auth/logout` | — | Clear cookie | Private |
| POST | `/auth/refresh` | cookie: refreshToken | New accessToken | Cookie |
| GET | `/auth/me` | — | `{ user }` | Private |
| POST | `/auth/forgot-password` | `{ email }` | `{ message }` | Public |
| POST | `/auth/reset-password` | `{ token, newPassword }` | `{ message }` | Public |
| GET | `/auth/google` | — | Redirect ke Google OAuth | Public |
| GET | `/auth/google/callback` | OAuth callback | Set cookie, redirect ke /dashboard | Public |

### 5.2 Transaction Endpoints

| Method | Path | Query Params / Body | Auth |
|--------|------|---------------------|------|
| GET | `/transactions` | `?month=, year=, type=, category=, paymentMethod=, search=, sort=, page=, limit=` | Private |
| GET | `/transactions/:id` | — | Private (owner) |
| POST | `/transactions` | `{ type, date, amount, category, paymentMethod, description, notes? }` | Private |
| PUT | `/transactions/:id` | Fields yang diubah | Private (owner) |
| DELETE | `/transactions/:id` | — | Private (owner) |
| GET | `/transactions/summary` | `?month=, year=` | Private |
| GET | `/transactions/monthly-trend` | `?months=6` | Private |
| GET | `/transactions/by-category` | `?month=, year=, type=` | Private |
| GET | `/transactions/export` | `?format=csv&from=&to=` | Private |

### 5.3 Budget Endpoints

| Method | Path | Body / Query | Auth |
|--------|------|-------------|------|
| GET | `/budget` | `?month=, year=` | Private |
| GET | `/budget/overview` | `?month=, year=` | Private |
| POST | `/budget` | `{ category, limitAmount, month, year }` | Private |
| PUT | `/budget/:id` | `{ limitAmount }` | Private (owner) |
| DELETE | `/budget/:id` | — | Private (owner) |

### 5.4 Savings Endpoints

| Method | Path | Body | Auth |
|--------|------|------|------|
| GET | `/savings` | — | Private |
| POST | `/savings` | `{ name, targetAmount, deadline?, icon? }` | Private |
| PUT | `/savings/:id` | `{ name?, targetAmount?, deadline?, icon? }` | Private (owner) |
| DELETE | `/savings/:id` | — | Private (owner) |
| POST | `/savings/:id/deposit` | `{ amount, note? }` | Private (owner) |
| POST | `/savings/:id/withdraw` | `{ amount, note? }` | Private (owner) |

### 5.5 Split Bill Endpoints

| Method | Path | Body | Auth |
|--------|------|------|------|
| GET | `/split-bill` | `?status=settled\|pending` | Private |
| POST | `/split-bill` | `{ title, totalAmount, date, participants: [{name, shareAmount}] }` | Private |
| DELETE | `/split-bill/:id` | — | Private (owner) |
| PATCH | `/split-bill/:id/participants/:participantId/pay` | — | Private (owner) |
| PATCH | `/split-bill/:id/settle` | — | Private (owner) |

### 5.6 Scheduled Payment Endpoints

| Method | Path | Body | Auth |
|--------|------|------|------|
| GET | `/scheduled-payments` | `?month=, year=` | Private |
| POST | `/scheduled-payments` | `{ name, amount, category, dueDay, frequency }` | Private |
| PUT | `/scheduled-payments/:id` | Fields yang diubah | Private (owner) |
| DELETE | `/scheduled-payments/:id` | — | Private (owner) |
| PATCH | `/scheduled-payments/:id/mark-paid` | — | Private |

### 5.7 Notification Endpoints

| Method | Path | Auth | Keterangan |
|--------|------|------|-----------|
| GET | `/notifications` | Private | List notifikasi user, terbaru di atas |
| PATCH | `/notifications/:id/read` | Private | Tandai satu notif sebagai dibaca |
| PATCH | `/notifications/read-all` | Private | Tandai semua notif sebagai dibaca |
| DELETE | `/notifications/:id` | Private | Hapus satu notifikasi |

### 5.8 Profile Endpoints

| Method | Path | Body | Auth |
|--------|------|------|------|
| GET | `/profile` | — | Private |
| PUT | `/profile` | `{ name?, university?, monthlyAllowance?, avatarUrl? }` | Private |
| PUT | `/profile/password` | `{ currentPassword, newPassword }` | Private (credentials only) |
| PUT | `/profile/notifications` | `{ notifBudgetAlert?, notifWeeklyReport? }` | Private |
| DELETE | `/profile` | `{ password? }` | Private (hapus akun + semua data) |

### 5.9 Investment Endpoints (Proxy + Cache)

| Method | Path | Auth | Keterangan |
|--------|------|------|-----------|
| GET | `/investment/prices` | Private | Return harga emas, USD/IDR, Bitcoin. Di-cache 60 detik. |
| GET | `/investment/history/:asset` | Private | `?days=7`, return data historis. Asset: `gold`, `usd`, `btc` |

### 5.10 AI Endpoints (Proxy ke ML Service)

Semua endpoint AI adalah proxy dari Express.js ke Flask/FastAPI. Express bertanggung jawab untuk autentikasi dan mengambil data user sebelum meneruskan ke ML service.

| Method | Path | Body | Auth | ML Endpoint |
|--------|------|------|------|------------|
| POST | `/ai/categorize` | `{ description: string }` | Private | POST `/categorize/auto` |
| POST | `/ai/insight` | `{ userId }` | Private | POST `/classify/spending-pattern` |
| GET | `/ai/insight` | — | Private | GET insight dari cache (1 jam) |
| POST | `/ai/health-score` | — | Private | POST `/health-score` |
| GET | `/ai/health-score` | — | Private | GET health score dari cache (1 jam) |
| POST | `/ai/forecast` | — | Private | POST `/forecast/next-month` |
| POST | `/ai/anomaly-check` | `{ transactionId }` | Private | POST `/anomaly/detect` |
| POST | `/ai/journal` | `{ month, year }` | Private | POST `/journal/monthly-summary` |
| POST | `/ai/chat` | `{ message, conversationHistory: [] }` | Private | POST `/chatbot/chat` |

---

## BAB 6 — Spesifikasi ML Service (Flask/FastAPI)

**Base URL ML Service:** `http://ml-service:8000` (internal, tidak exposed ke publik)
**Framework:** FastAPI | **Language:** Python 3.11+

### 6.1 Dataset & Fitur Model

Dataset pelatihan: `df_combined_clean.csv`

| Kolom Dataset | Tipe | Deskripsi | Digunakan untuk |
|--------------|------|----------|----------------|
| Date | DateTime | Tanggal transaksi | Feature engineering: month, day_of_week, week_of_month |
| Description | String | Nama/deskripsi transaksi | NLP auto-kategorisasi (TF-IDF features) |
| Amount | Float | Nominal transaksi (IDR) | Feature: avg_amount, total_per_category, z-score anomali |
| Transaction_Type | EXPENSE/INCOME | Tipe transaksi | Target variable, filter |
| Category | String | Kategori (15 kategori) | Target: auto-kategorisasi, feature: category distribution |
| Account_Name | String | Metode pembayaran | Feature: payment diversity |
| Month | Int | Bulan (1-12) | Feature: seasonality |
| Day_of_Week | String | Hari dalam seminggu | Feature: spending pattern per hari |

### 6.2 Modul ML: Klasifikasi Pola Belanja

**Endpoint:** `POST /classify/spending-pattern`

| Aspek | Detail |
|-------|--------|
| Tujuan | Mengklasifikasikan pola belanja user bulan ini: HEMAT, NORMAL, atau BOROS |
| Input | List transaksi user (amount, category, date, type) untuk periode tertentu |
| Features | total_expense, expense_to_income_ratio, category_distribution, avg_daily_expense, savings_rate |
| Algoritma | Random Forest Classifier (primary), XGBoost sebagai ensemble backup |
| Output | `{ label: "HEMAT"\|"NORMAL"\|"BOROS", confidence: float, factors: [string] }` |
| Training | Label di-generate: savings_rate > 30% = HEMAT, savings_rate < 0% = BOROS, else = NORMAL |

### 6.3 Modul ML: Prediksi Pengeluaran

**Endpoint:** `POST /forecast/next-month`

| Aspek | Detail |
|-------|--------|
| Tujuan | Memprediksi total pengeluaran bulan depan, per kategori dan total |
| Input | List transaksi 3–6 bulan terakhir, grouped by month and category |
| Features | historical_monthly_total, category_monthly_average, trend (linear regression slope), seasonality_factor |
| Algoritma | Linear Regression per kategori + Moving Average. Untuk data > 6 bulan: Prophet atau SARIMA |
| Output | `{ predicted_total: float, by_category: {category: {predicted, confidence_low, confidence_high}}, summary: string }` |
| Minimum Data | Minimal 2 bulan data |

### 6.4 Modul ML: Financial Health Score

**Endpoint:** `POST /health-score`

| Aspek | Detail |
|-------|--------|
| Tujuan | Skor 0–100 yang merepresentasikan kesehatan keuangan user secara holistik |
| Formula | Health Score = (savings_score × 35%) + (budget_adherence × 30%) + (consistency_score × 20%) + (diversity_score × 15%) |
| Komponen | savings_score: rasio tabungan. budget_adherence: % kategori tidak overbudget. consistency_score: konsistensi antar bulan. diversity_score: diversifikasi pengeluaran. |
| Output | `{ score: int (0-100), label: string, components: {...}, recommendations: [string] }` |

### 6.5 Modul ML: Deteksi Anomali

**Endpoint:** `POST /anomaly/detect`

| Aspek | Detail |
|-------|--------|
| Tujuan | Mendeteksi transaksi yang jumlahnya tidak wajar dibanding kebiasaan user |
| Algoritma | Isolation Forest + Z-score statistik. Anomali jika z-score > 2.5 ATAU Isolation Forest score > threshold |
| Input | Transaksi baru (amount, category) + histori transaksi kategori yang sama |
| Output | `{ is_anomaly: bool, confidence: float, reason: string, expected_range: {min, max} }` |
| Integrasi | Dipanggil async setelah setiap POST /transactions. Jika anomali: create notification + set `isAnomaly = true` |

### 6.6 Modul NLP: Auto-Kategorisasi

**Endpoint:** `POST /categorize/auto`

| Aspek | Detail |
|-------|--------|
| Tujuan | Memprediksi kategori transaksi dari teks deskripsi |
| Input | `{ description: string, amount?: float, transaction_type?: string }` |
| Pipeline | Preprocessing teks → TF-IDF vectorizer → Logistic Regression classifier |
| Output | `{ category: string, confidence: float, alternatives: [{category, confidence}] }` |
| Threshold | Confidence < 0.6 → return "Uncategorized", tidak auto-fill |
| Keyword Rules | Fallback: "kos"\|"kontrakan" → Tagihan, "gofood"\|"grabfood" → Makan & Minum, "spotify"\|"netflix" → Hiburan |

### 6.7 Modul AI: Chatbot Cuan AI

**Endpoint:** `POST /chatbot/chat`

| Aspek | Detail |
|-------|--------|
| Tujuan | Chatbot yang menjawab pertanyaan keuangan user dengan konteks data personalnya |
| LLM Backend | Google Gemini API (gemini-1.5-flash) atau OpenAI GPT-4o-mini sebagai fallback |
| Context Injection | System prompt berisi: total pengeluaran per kategori, health score, goals aktif, budget status |
| Input | `{ message: string, conversation_history: [{role, content}], user_context: {...} }` |
| Output | `{ reply: string, referenced_data?: {type: string, data: object} }` |
| Batasan | Max 10 pesan per sesi. Rate limit: 20 request/jam per user. |
| System Prompt | Berperan sebagai "Cuan AI", asisten keuangan friendly untuk mahasiswa. Jawab dalam Bahasa Indonesia. Tidak memberikan saran investasi spesifik. |

---

## BAB 7 — Alur Bisnis & Logic Kritis

### 7.1 Alur Autentikasi (OAuth 2.0 + Credentials)

**Via Credentials:**
1. User submit form login → NextAuth credentials provider dipanggil
2. NextAuth memanggil Express backend `POST /api/v1/auth/login`
3. Backend verifikasi email + bcrypt compare password → return user object
4. NextAuth generate JWT session → set HttpOnly cookie
5. Frontend redirect ke `/dashboard`

**Via Google OAuth 2.0:**
1. User klik "Lanjut dengan Google" → redirect ke Google OAuth consent
2. Google return code → NextAuth exchange untuk access token
3. NextAuth ambil profile Google (name, email, avatar)
4. Backend cek: email ada di DB? → update providerAccountId. Jika tidak: buat akun baru dengan `provider=GOOGLE`, `passwordHash=null`
5. NextAuth set session → redirect ke `/dashboard`

> **Catatan:** User yang signup via Google tidak memiliki `passwordHash`. Jika mencoba fitur "Ganti Password", tampilkan: "Akun ini terhubung dengan Google. Password tidak dapat diubah dari sini."

### 7.2 Logika Budget Tracking Real-time

- Setiap `POST /transactions` berhasil → backend memanggil `budget.service.ts#checkBudgetUsage()`
- Service hitung total expense kategori tersebut bulan ini
- Usage ≥ 80%: create notification `BUDGET_ALERT` severity MEDIUM
- Usage ≥ 100%: create notification `BUDGET_ALERT` severity HIGH
- Frontend polling `/notifications` setiap 30 detik atau Supabase Realtime

### 7.3 Logika Estimasi Savings Goal

```typescript
// Pseudo-code estimasi pencapaian goal
const remaining = goal.targetAmount - goal.currentAmount;
const transactions = await getSavingsTransactions(goal.id, last3Months);
const avgMonthlyDeposit = transactions
  .filter(t => t.type === 'DEPOSIT')
  .reduce((sum, t) => sum + t.amount, 0) / 3;

if (avgMonthlyDeposit <= 0) return null; // belum bisa estimasi

const monthsNeeded = Math.ceil(remaining / avgMonthlyDeposit);
const estimatedDate = addMonths(new Date(), monthsNeeded);
return estimatedDate;
```

### 7.4 Logika Auto-Kategorisasi AI

1. User ketik deskripsi transaksi di modal AddTransaction
2. Setelah user blur (atau delay 800ms), frontend call `POST /api/v1/ai/categorize`
3. Backend proxy ke ML service → return `{ category, confidence }`
4. Confidence ≥ 0.6: auto-fill dropdown + badge "AI". < 0.6: tidak auto-fill
5. User tetap bisa mengubah manual → `isAutoCateg = false`

### 7.5 Logika Deteksi Anomali Post-Transaction (Async)

1. `POST /transactions` berhasil → return response ke user
2. **Background:** `ai.service.ts#checkAnomaly(transaction, userId)` dipanggil async
3. Ambil histori 30 transaksi terakhir untuk kategori yang sama
4. Proxy ke ML service `POST /anomaly/detect`
5. Jika `is_anomaly = true`: `UPDATE transaction SET isAnomaly = true` + create notification `ANOMALY`
6. Frontend tampilkan badge "⚠️" pada transaksi anomali di list

### 7.6 Split Bill: Logika Pembagian

- **Equal:** `shareAmount = totalAmount / jumlah peserta`. Sisa rounding ditambahkan ke orang pertama (creator)
- **Custom:** validasi `sum(shareAmount) == totalAmount` dengan toleransi 1 rupiah
- `SplitBill.isSettled` otomatis `true` ketika semua `SplitBillParticipant.isPaid = true`

---

## BAB 8 — Strategi Performa

Target: **Lighthouse Performance Score ≥ 85** di halaman publik. Halaman terproteksi target ≥ 75.

### 8.1 Rendering Strategy per Halaman

| Halaman | Strategi | Revalidate | Alasan |
|---------|---------|-----------|-------|
| / (Landing) | SSG | — | Konten statis, SEO critical |
| /transactions | SSR | Per request | Data user-specific real-time |
| /dashboard | SSR | Per request | Ringkasan finansial harus fresh |
| /budgeting | SSR | Per request | Budget & kalender real-time |
| /savings | SSR | Per request | Progress goal real-time |
| /split-bill | SSR | Per request | Status pembayaran real-time |
| /financial-health | SSR | Per request | AI data di-cache di backend 1 jam |
| /forecast | CSR | — | Interaktif, ML call on demand |
| /chatbot | CSR | — | 100% interaktif, tidak butuh SEO |
| /investment | ISR | 60 detik | Data semi-real-time dari API publik |
| /profile | SSR | Per request | Data user terbaru |
| /auth/* | CSR | — | Form interaktif, tidak butuh SEO |

### 8.2 Caching Strategy

| Layer | Target | TTL | Implementasi |
|-------|--------|-----|-------------|
| ML AI Insight | Health score, insight harian | 1 jam per user | Cache di Express memory/Redis, invalidate saat ada transaksi baru |
| Investment Prices | Harga emas, kurs, crypto | 60 detik | Express in-memory cache, refresh background |
| Transaction Summary | Summary per bulan | 5 menit | TanStack Query `staleTime: 5 menit` |
| ML Forecast | Prediksi bulan depan | 24 jam | Cache di Express, invalidate saat ada 5+ transaksi baru |

### 8.3 Optimasi Frontend

| Aspek | Teknik | Implementasi |
|-------|--------|-------------|
| Gambar | Next/Image | Lazy loading otomatis, WebP conversion, blur placeholder |
| JavaScript Bundle | Dynamic Import | Chart components, komponen AI/modal: `next/dynamic({ ssr: false })` |
| CSS | Tailwind Purge | Hanya class yang dipakai di-bundle. Total CSS < 10KB |
| Fonts | next/font/google | Inter dengan subset latin, preload otomatis |
| Data Fetching | TanStack Query | `staleTime: 5 menit` untuk data transaksi |
| API Calls | Parallel fetching | Dashboard: `Promise.all` untuk summary, trend, dan category data |

---

## BAB 9 — Keamanan

| Aspek | Implementasi | File/Lokasi |
|-------|-------------|------------|
| Autentikasi | NextAuth.js: JWT access token (15 menit) + refresh token (7 hari) di HttpOnly, Secure, SameSite=Strict cookie | `auth.ts`, `authenticate.ts` |
| Otorisasi | Middleware `authorize.ts` cek `req.user.id`. Owner check di setiap resource. | `authorize.ts` |
| Password | bcrypt hash, `saltRounds = 12`. Null untuk OAuth users. Tidak pernah expose ke client. | `hash.helper.ts` |
| Input Validation | Zod schema di `validate.ts` middleware. Validasi setiap request body. | `validators/*.ts` |
| SQL Injection | Prisma parameterized queries. Tidak ada string concatenation untuk query DB. | Semua `*.service.ts` |
| XSS | React auto-escape. Content-Security-Policy header di `next.config.ts` | `next.config.ts` |
| CORS | Express CORS hanya allow origin dari `NEXT_PUBLIC_URL` dan ML service internal | `cors.ts` |
| Rate Limiting | 100 req/menit public, 30 req/menit auth, 20 req/jam AI endpoints | `rateLimiter.ts` |
| AI Context | User context ke ML/LLM hanya berisi data numerik/agregat, tidak pernah teks mentah sensitif | `ai.service.ts` |
| Data Privacy | Export hanya oleh owner. Hapus akun cascade delete semua data user. | `profile.service.ts` |
| Environment | Semua secret di `.env`. Validasi via Zod saat startup. `.env` tidak di-commit. | `config/env.ts` |
| Error Handling | `errorHandler.ts`: tidak expose stack trace di production. Log error di server. | `errorHandler.ts` |

---

## BAB 10 — Environment Variables

### 10.1 Backend (`.env`)

| Variable | Contoh Nilai | Keterangan |
|----------|-------------|-----------|
| `DATABASE_URL` | `postgresql://user:pass@host/kampuscuan?sslmode=require` | Supabase PostgreSQL connection string |
| `DIRECT_URL` | `postgresql://user:pass@host:5432/kampuscuan` | Prisma migrations (Supabase pooler bypass) |
| `JWT_SECRET` | `random-min-32-chars` | Secret untuk sign JWT access token |
| `JWT_REFRESH_SECRET` | `another-random-32` | Secret untuk refresh token |
| `JWT_EXPIRES_IN` | `15m` | Durasi access token |
| `JWT_REFRESH_EXPIRES_IN` | `7d` | Durasi refresh token |
| `PORT` | `5000` | Port Express server |
| `CLIENT_URL` | `http://localhost:3000` | Frontend URL untuk CORS |
| `ML_SERVICE_URL` | `http://localhost:8000` | URL ML/FastAPI service (internal) |
| `ML_SERVICE_API_KEY` | `secret-key` | API key untuk autentikasi ke ML service |
| `GOOGLE_CLIENT_ID` | `xxx.apps.googleusercontent.com` | Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-xxx` | Google OAuth Client Secret |
| `GEMINI_API_KEY` | `AIzaSy...` | Google Gemini API key untuk chatbot |
| `EXCHANGERATE_API_KEY` | `key` | API key exchangerate-api.com untuk kurs |
| `NODE_ENV` | `development` | `development` / `production` |

### 10.2 Frontend (`.env.local`)

| Variable | Contoh Nilai | Keterangan |
|----------|-------------|-----------|
| `NEXTAUTH_URL` | `http://localhost:3000` | Base URL aplikasi untuk NextAuth callbacks |
| `NEXTAUTH_SECRET` | `random-secret` | Secret NextAuth untuk encrypt JWT |
| `NEXT_PUBLIC_API_URL` | `http://localhost:5000/api/v1` | Base URL Express backend |
| `GOOGLE_CLIENT_ID` | `xxx.apps.googleusercontent.com` | Sama dengan backend |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-xxx` | Sama dengan backend |
| `NEXT_PUBLIC_APP_NAME` | `KampusCuan` | Nama aplikasi untuk meta tags |

### 10.3 ML Service (`.env`)

| Variable | Contoh Nilai | Keterangan |
|----------|-------------|-----------|
| `PORT` | `8000` | Port FastAPI server |
| `ML_API_KEY` | `secret-key` | API key untuk validasi request dari backend |
| `GEMINI_API_KEY` | `AIzaSy...` | Google Gemini untuk chatbot |
| `MODEL_PATH` | `./models/` | Path folder model `.pkl`/`.joblib` |
| `LOG_LEVEL` | `INFO` | Level logging |

---

## BAB 11 — Rencana Pengerjaan (Development Phases)

| Phase | Fokus | Tim | Estimasi | Output |
|-------|-------|-----|---------|--------|
| Phase 1 | Foundation & Setup | Semua | 2–3 hari | Monorepo setup, Prisma schema, seed data, auth (credentials + Google OAuth), komponen UI dasar Shadcn/ui, Sidebar layout |
| Phase 2 | Core Transactions & Dashboard | Fullstack | 3–4 hari | CRUD transaksi, modal input transaksi (semua field), halaman /transactions dengan filter, dashboard dengan metric cards dan grafik |
| Phase 3 | Budget, Savings, Split Bill | Fullstack | 3–4 hari | Budget CRUD + progress tracking, savings goals, split bill, scheduled payments + kalender |
| Phase 4 | ML Model Development | DS + AI | 4–5 hari | EDA dataset, training model klasifikasi, prediksi, health score, anomali detector, auto-kategorisasi NLP — semua ter-deploy di FastAPI |
| Phase 5 | Integrasi AI Features | Semua | 3–4 hari | Auto-kategorisasi live, /financial-health page, /forecast page, background anomaly check post-transaction |
| Phase 6 | Chatbot & Investment | AI + Fullstack | 2–3 hari | Chatbot Cuan AI dengan context injection, /chatbot page, /investment page dengan price cards dan sparklines |
| Phase 7 | Landing Page & Profile | Fullstack | 2–3 hari | Landing page SEO-optimized, /profile page, notification system, export CSV |
| Phase 8 | Polish, Testing & Deploy | Semua | 3–4 hari | Bug fixing, Lighthouse audit, responsive check, deployment ke Vercel + Railway, dokumentasi final |

---

## BAB 12 — Konvensi Kode & Best Practices

### 12.1 Naming Conventions

| Konteks | Convention | Contoh |
|---------|-----------|--------|
| Komponen React | PascalCase, file `.tsx` | `TransactionItem.tsx`, `AddTransactionModal.tsx` |
| Hooks | camelCase, prefix `use` | `useTransactions.ts`, `useBudget.ts` |
| Service | camelCase, suffix `.service.ts` | `transaction.service.ts`, `ai.service.ts` |
| Controller | camelCase, suffix `.controller.ts` | `transaction.controller.ts` |
| Routes | camelCase, suffix `.routes.ts` | `transaction.routes.ts` |
| TypeScript Interfaces | PascalCase | `interface Transaction`, `type TransactionType` |
| Zod Schema | camelCase, suffix `Schema` | `transactionSchema`, `budgetSchema` |
| Enum values (Prisma) | UPPER_SNAKE_CASE | `INCOME`, `EXPENSE`, `HEMAT`, `BOROS` |
| CSS Class (Tailwind) | Langsung di className | `className="flex items-center gap-4"` |
| API Response helper | `success()`, `error()` | `return success(res, data, 'Transaksi berhasil')` |
| Python (ML) | snake_case untuk semua | `spending_classifier.py`, `def predict_category(text):` |

### 12.2 Aturan Penting

- **Controller** TIDAK boleh berisi logika bisnis. Hanya: call service, handle error, return response.
- **Service** TIDAK boleh mengakses `req`/`res`. Terima parameter biasa, return data atau throw Error.
- Semua error dari service harus berupa instance `Error` dengan pesan yang jelas.
- Gunakan `async/await` konsisten. Jangan chain `.then()` panjang.
- Setiap komponen React idealnya < 150 baris. Jika lebih, pecah menjadi sub-komponen.
- Jangan fetch data langsung di `useEffect` jika bisa menggunakan TanStack Query.
- Semua string label UI, pesan error, status: definisikan di `constants.ts`.
- TypeScript strict mode. Hindari `any` kecuali benar-benar tidak bisa dihindari.
- Setiap endpoint yang mengubah data (POST/PUT/DELETE) harus melalui Zod validation middleware.
- **Owner check wajib:** setiap service yang mengakses resource by ID harus validasi `userId === resource.userId`.
- Jangan expose data user lain. `GET /transactions` harus filter by `userId` dari JWT.
- ML service tidak pernah menyimpan data user. Setiap request stateless.

### 12.3 Format Tanggal & Currency

- Semua date di database: **UTC**. Display di frontend: **WIB (UTC+7)**.
- Currency selalu dalam IDR (Rupiah). Format display: `"Rp 1.250.000"` menggunakan `Intl.NumberFormat`.
- Amount di database: **Decimal** (presisi 2 desimal). Jangan gunakan Float untuk currency.

### 12.4 Git Branching Strategy

| Branch | Penggunaan |
|--------|-----------|
| `main` | Production-ready code. Hanya merge dari `develop` setelah testing. |
| `develop` | Integration branch. Semua feature merge ke sini. |
| `feature/[nama-fitur]` | Pengembangan fitur baru. Contoh: `feature/transaction-crud` |
| `fix/[nama-bug]` | Bug fixes. Contoh: `fix/budget-calculation` |
| `ml/[nama-model]` | Pengembangan model ML. Contoh: `ml/spending-classifier` |

---

## BAB 13 — Decision Log & Catatan Arsitektur

| Keputusan | Pilihan | Alasan | Alternatif Ditolak |
|-----------|---------|--------|-------------------|
| Auth provider | NextAuth.js (Auth.js v5) | Built-in OAuth 2.0 + credentials, session management, TypeScript support | Supabase Auth (terlalu coupled), custom JWT (reinvent wheel) |
| ML Service terpisah | Flask/FastAPI microservice | Python ecosystem untuk ML lebih mature. ML engineer bisa develop independen. | Integrasi di Node.js (kurang mature untuk ML), Vertex AI (cost) |
| Database | PostgreSQL via Supabase | Managed PostgreSQL + Storage + Realtime gratis tier | MySQL, MongoDB (relational lebih cocok untuk financial data) |
| State management | Zustand + TanStack Query | Zustand untuk UI state (ringan), TanStack Query untuk server state (caching, refetch) | Redux Toolkit (terlalu verbose), Context API (tidak optimal untuk server state) |
| Auto-kategorisasi | TF-IDF + Logistic Regression + keyword fallback | Ringan, tidak butuh GPU, bisa di-deploy di free tier. Keyword rules sebagai fallback. | BERT/IndoBERT (terlalu berat), rule-only (kurang flexible) |
| Chatbot LLM | Gemini API (flash model) | Cost rendah, performance cukup, Google ecosystem. Flash model sangat cepat untuk chat. | GPT-4o (lebih mahal), fine-tuned model sendiri (butuh data banyak) |
| Split bill participants | Input nama manual (bukan FK user) | Tidak semua peserta adalah user KampusCuan. Input manual lebih fleksibel untuk MVP. | FK ke User (membatasi hanya sesama pengguna app) |

---

---

*Dokumen ini adalah sumber kebenaran tunggal proyek KampusCuan.*
*Setiap keputusan arsitektur, naming, skema database, dan alur bisnis merujuk ke dokumen ini.*
*Update dokumen ini setiap kali ada perubahan signifikan sebelum melanjutkan development.*