# HeyPiko — Habit & Energy Pattern Tracker

**Kelompok 1 DDP 1 (`kelompok1ddp1-lab-git`) — Asdos Kalfin**
- Anyakarina
- Aurelia Oktavani Wijayanto
- Grivinie Gwynneth Agustin

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
# Jalankan langsung dari folder Project
.\.venv\Scripts\streamlit.exe run heypiko\main.py
```

Atau jika berada di dalam folder `heypiko`:

```powershell
pip install -r requirements.txt
streamlit run main.py
```
