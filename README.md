# HeyPiko — Habit & Energy Pattern Tracker

Aplikasi pelacak kebiasaan dan pola energi harian berbasis Python + Streamlit dengan karakter pendamping **Piko**.

## Struktur Proyek (Modular untuk Kerja Kelompok)

```text
heypiko/
├── main.py              # Entry point aplikasi & navigasi halaman
├── data_manager.py      # Operasi CRUD & validasi data ke data/logs.json
├── piko_engine.py       # Logika state/ekspresi Piko, baterai (%), & pesan suportif
├── analytics.py         # Analisis korelasi kebiasaan vs energi, flexible streak, & misi mingguan
├── ui/
│   ├── __init__.py
│   ├── styles.py        # Custom CSS & komponen visual aesthetic (mobile-first)
│   ├── dashboard_view.py
│   ├── checkin_view.py
│   ├── insight_view.py
│   └── history_view.py
├── assets/              # Ilustrasi ekspresi Piko (charged, steady, sleepy, waiting)
├── data/
│   └── logs.json        # Penyimpanan data check-in harian
├── .streamlit/
│   └── config.toml      # Konfigurasi tema Streamlit
└── requirements.txt
```

## Cara Menjalankan di Laptop

```powershell
# 1. Aktifkan virtual environment (dari folder Project)
.\.venv\Scripts\Activate.ps1

# 2. Masuk ke folder heypiko
cd heypiko

# 3. Jalankan Streamlit
streamlit run main.py
```
