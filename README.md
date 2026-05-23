# MyFinance Dashboard

Dashboard analitik untuk proyek **MyFinance - AI Powered Money Manager**.  
Repository ini berisi aplikasi dashboard berbasis **Streamlit** yang digunakan untuk menampilkan insight keuangan pengguna, seperti financial overview, financial health score, budget risk, money leak detection, dan weekly rewind.

Dashboard ini menjadi bagian dari output **Data Science** pada proyek capstone **CC26-PSU154 - Coding Camp 2026 powered by DBS Foundation**.

---

## Project Overview

**MyFinance** adalah aplikasi pencatatan keuangan berbasis AI yang membantu pengguna mencatat transaksi, memantau kondisi finansial, dan mengevaluasi kebiasaan pengeluaran secara lebih objektif.

Dashboard ini dibuat untuk membantu pengguna memahami data keuangan melalui visualisasi dan insight yang mudah dibaca. Fokus dashboard tidak hanya pada pencatatan transaksi, tetapi juga pada evaluasi kondisi finansial pengguna.

---

## Key Features

Dashboard MyFinance memiliki beberapa fitur utama:

### 1. Financial Overview

Menampilkan ringkasan kondisi keuangan pengguna, seperti:

- Total income
- Total expense
- Net cashflow
- Savings rate
- Spending breakdown

### 2. Financial Health Score

Menampilkan skor kesehatan finansial pengguna berdasarkan indikator seperti:

- Net cashflow
- Savings rate
- Budget usage
- Needs vs wants ratio
- Money leak indicator

### 3. Leak Detection

Mendeteksi potensi **money leak**, yaitu pengeluaran kecil yang berulang dan dapat membesar secara kumulatif.

Contoh money leak:

- Kopi atau minuman harian
- Snack
- Jajan dan nongkrong
- Pengeluaran lifestyle kecil namun berulang

### 4. Budget & Risk

Menampilkan analisis penggunaan budget dan risiko overbudget berdasarkan kategori pengeluaran.

Output yang ditampilkan dapat berupa:

- Budget usage ratio
- Risk level
- Daily spending trend
- Recent transactions

### 5. Weekly Rewind

Menampilkan ringkasan mingguan, seperti:

- Total income
- Total expense
- Net cashflow
- Top spending category
- Top leak item
- Weekly financial insight

---

## Tech Stack

| Technology | Usage |
|---|---|
| Python | Bahasa utama dashboard dan data processing |
| Streamlit | Framework dashboard interaktif |
| Pandas | Data manipulation dan preprocessing |
| Plotly / Matplotlib | Visualisasi data |
| JSON | Mock data dashboard |
| GitHub | Version control dan dokumentasi |

---

## Repository Structure

Struktur repository yang disarankan:

```text
MyFinance-Dashboard/
├── app.py
├── utils.py
├── requirements.txt
├── README.md
└── data/
    └── mockDashboardAnalysis.json
```

Penjelasan file:

| File / Folder | Description |
|---|---|
| `app.py` | File utama untuk menjalankan dashboard Streamlit |
| `utils.py` | Helper function untuk data processing dan analytical logic |
| `requirements.txt` | Daftar dependency Python |
| `data/mockDashboardAnalysis.json` | Mock data untuk simulasi dashboard |
| `README.md` | Dokumentasi penggunaan dashboard |

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/MyFinance-AI-Powered-Money-Manager/MyFinance-Dashboard.git
cd MyFinance-Dashboard
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Aktifkan virtual environment:

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Jika `requirements.txt` belum tersedia, dependency minimal yang dibutuhkan:

```bash
pip install streamlit pandas plotly matplotlib
```

---

## How to Run

Jalankan dashboard menggunakan command berikut:

```bash
streamlit run app.py
```

Setelah dijalankan, Streamlit akan membuka dashboard melalui browser lokal, biasanya pada:

```text
http://localhost:8501
```

---

## Data Source

Dashboard saat ini menggunakan mock data pada file:

```text
data/mockDashboardAnalysis.json
```

Mock data digunakan untuk mendemonstrasikan tampilan dashboard dan logic analitik sebelum dashboard terhubung langsung dengan backend production.

Pada tahap production, dashboard dapat diintegrasikan dengan backend/API agar data yang ditampilkan berasal dari transaksi pengguna aktual.

---

## Data Science Output

Dashboard ini dirancang untuk menampilkan beberapa output Data Science:

| Output | Description |
|---|---|
| `financial_health_score` | Skor kesehatan finansial pengguna |
| `budget_usage` | Rasio penggunaan budget |
| `overbudget_risk` | Risiko pengeluaran melebihi budget |
| `money_leak_detection` | Deteksi pengeluaran kecil yang berulang |
| `weekly_rewind` | Ringkasan kondisi keuangan mingguan |
| `spending_breakdown` | Distribusi pengeluaran berdasarkan kategori |

---

## Dashboard Flow

Alur dashboard secara umum:

```text
Mock / API Data
      ↓
Data Processing
      ↓
Financial Metrics Calculation
      ↓
Money Leak Detection
      ↓
Budget & Risk Analysis
      ↓
Dashboard Visualization
```

---

## Integration Plan

Untuk integrasi dengan aplikasi utama MyFinance, dashboard dapat menerima data dari backend melalui endpoint API.

Contoh endpoint yang dapat digunakan:

```text
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/budget-risk
GET /api/v1/dashboard/money-leak
GET /api/v1/dashboard/weekly-rewind
```

Atau menggunakan endpoint Data Science:

```text
POST /api/v1/ds/predict
```

Contoh response yang diharapkan:

```json
{
  "health_score": 78,
  "predicted_cashflow": 1500000,
  "overbudget_risk": "medium",
  "money_leak": "Pengeluaran kecil berulang terdeteksi pada kategori jajan dan nongkrong.",
  "total_spent": 1230000,
  "total_budget": 2000000,
  "categories": [
    {
      "name": "NEEDS",
      "amount": 900000
    },
    {
      "name": "WANTS",
      "amount": 330000
    }
  ]
}
```

---

## Deployment

Dashboard dapat dideploy menggunakan **Streamlit Cloud**.

Langkah umum deployment:

1. Push repository ke GitHub.
2. Login ke Streamlit Cloud.
3. Pilih repository `MyFinance-Dashboard`.
4. Pilih file utama `app.py`.
5. Deploy aplikasi.
6. Salin link deployment ke Project Brief.

Setelah deployment berhasil, tambahkan link dashboard pada bagian berikut:

- Project Brief
- README repository utama Data Science
- Dokumentasi final capstone

---

## Current Limitation

Beberapa limitasi dashboard saat ini:

- Dashboard masih menggunakan mock JSON untuk simulasi data.
- Data belum sepenuhnya terhubung dengan backend production.
- Financial Health Score masih dapat dikembangkan menjadi weighted score multi-indikator.
- Money leak detection masih dapat diperkuat menggunakan histori transaksi pengguna aktual.
- Dashboard perlu diuji lebih lanjut menggunakan data real user.

---

## Future Improvement

Pengembangan selanjutnya yang direkomendasikan:

- Integrasi langsung dengan backend MyFinance.
- Menampilkan data transaksi real-time.
- Menambahkan filter berdasarkan bulan, wallet, dan kategori.
- Memperkuat Financial Health Score dengan indikator tambahan.
- Mengembangkan money leak detection berbasis histori transaksi pengguna.
- Menambahkan export report untuk ringkasan mingguan/bulanan.
- Deploy dashboard ke Streamlit Cloud agar dapat diakses publik.

---

## Relation to Capstone Checklist

Dashboard ini mendukung checklist **Data Science** pada Project Brief, terutama:

- Melakukan Exploratory Data Analysis (EDA).
- Membuat visualisasi data dan explanatory analysis.
- Mengembangkan dashboard interaktif menggunakan Streamlit.
- Menampilkan insight dan kesimpulan dari data.
- Mendukung dokumentasi hasil pekerjaan Data Science.

---

## Contributors

Tim Capstone **CC26-PSU154**

| Name | Role |
|---|---|
| Nabiel Alfallah Herdiana | Data Scientist |
| Pascal Zufar Hanif | Data Scientist |
| Aditya Beckham Firmansyah | Full-Stack Web Developer |
| Robby Riandi | Full-Stack Web Developer |
| Fikri Fauzi | AI Engineer |
| Hafizh Kamaluddin Abdillah | AI Engineer |

---

## Repository Links

| Component | Repository |
|---|---|
| Full Stack Web | `https://github.com/MyFinance-AI-Powered-Money-Manager/MyFinance` |
| AI Backend | `https://github.com/MyFinance-AI-Powered-Money-Manager/my-finance-AI-backend` |
| Data Science | `https://github.com/MyFinance-AI-Powered-Money-Manager/MyFinance-Data` |
| Dashboard | `https://github.com/MyFinance-AI-Powered-Money-Manager/MyFinance-Dashboard` |

---

## Notes

Dashboard ini merupakan prototype analitik yang menunjukkan bagaimana output Data Science dapat ditampilkan secara visual kepada pengguna. Untuk penggunaan production, data dashboard perlu dihubungkan dengan backend utama agar insight yang muncul selalu sinkron dengan transaksi pengguna aktual.
