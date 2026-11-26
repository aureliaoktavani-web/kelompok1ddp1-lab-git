"""
ui/styles.py
------------
Custom CSS & helper visual untuk tema "Warm Paper & Sunlight" HeyPiko.
Dirancang mobile-first agar nyaman di layar HP sekaligus rapi di desktop.
"""

from __future__ import annotations

import base64
from datetime import date
from pathlib import Path

import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

BULAN_ID = [
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Agu",
    "Sep",
    "Okt",
    "Nov",
    "Des",
]
HARI_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def format_date_id(d: date) -> str:
    """Format tanggal ke bahasa Indonesia ringkas, misal 'Kamis, 26 Nov 2026'."""
    return f"{HARI_ID[d.weekday()]}, {d.day} {BULAN_ID[d.month]} {d.year}"


def load_image_base64(asset_name: str) -> str | None:
    """Membaca file gambar dari folder assets/ sebagai string base64."""
    img_path = ASSETS_DIR / asset_name
    if not img_path.exists():
        return None
    data = img_path.read_bytes()
    return base64.b64encode(data).decode("utf-8")


def inject_custom_css() -> None:
    """Menyuntikkan Google Fonts & styling Warm Paper & Sunlight ke Streamlit."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        :root {
            --paper-bg: #FAF7F2;
            --card-bg: #FFFDF9;
            --soft-bg: #F2ECE1;
            --ink: #2B2623;
            --ink-muted: #756B62;
            --border-warm: #E7DDD0;
            --honey: #D99B26;
            --sage: #5B8A72;
            --terracotta: #D4745E;
        }

        /* Sembunyikan chrome bawaan Streamlit agar terasa seperti aplikasi mobile */
        #MainMenu, footer, header[data-testid="stHeader"] {
            visibility: hidden;
            height: 0px;
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--ink);
        }

        .stApp {
            background-color: var(--paper-bg);
        }

        /* Container mobile-first terpusat */
        .block-container {
            max-width: 540px !important;
            padding-top: 1.25rem !important;
            padding-bottom: 3.5rem !important;
            padding-left: 1.1rem !important;
            padding-right: 1.1rem !important;
        }

        /* Tipografi editorial untuk judul */
        h1, h2, h3, .font-serif {
            font-family: 'Fraunces', Georgia, serif !important;
            color: var(--ink) !important;
            letter-spacing: -0.02em;
        }

        /* Header Brand */
        .brand-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.85rem;
            padding: 0.2rem 0.1rem;
        }
        .brand-title {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            font-family: 'Fraunces', Georgia, serif;
            font-size: 1.55rem;
            font-weight: 700;
            color: var(--ink);
            line-height: 1;
        }
        .brand-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #F9D976, #D99B26);
            box-shadow: 0 0 0 4px rgba(217, 155, 38, 0.18);
            display: inline-block;
        }
        .brand-date {
            font-size: 0.82rem;
            font-weight: 500;
            color: var(--ink-muted);
            background: var(--soft-bg);
            padding: 0.32rem 0.72rem;
            border-radius: 999px;
        }

        /* Tombol navigasi & tombol utama */
        div.stButton > button {
            border-radius: 14px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            padding: 0.52rem 0.75rem !important;
            transition: all 0.18s ease !important;
            border: 1px solid var(--border-warm) !important;
        }
        div.stButton > button[kind="primary"] {
            background-color: var(--ink) !important;
            color: #FAF7F2 !important;
            border-color: var(--ink) !important;
            box-shadow: 0 4px 12px rgba(43, 38, 35, 0.12) !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #3E3631 !important;
            transform: translateY(-1px);
        }
        div.stButton > button[kind="secondary"] {
            background-color: var(--card-bg) !important;
            color: var(--ink-muted) !important;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: var(--soft-bg) !important;
            color: var(--ink) !important;
            border-color: #D5C8B5 !important;
        }

        /* Kartu umum */
        .paper-card {
            background: var(--card-bg);
            border: 1px solid var(--border-warm);
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 6px 20px rgba(43, 38, 35, 0.035);
        }

        /* Kartu Hero Piko */
        .piko-hero {
            border-radius: 26px;
            padding: 1.35rem 1.25rem 1.25rem 1.25rem;
            margin-bottom: 1rem;
            border: 1.5px solid;
            box-shadow: 0 10px 26px rgba(43, 38, 35, 0.05);
        }
        .piko-top-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }
        .piko-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
            letter-spacing: 0.01em;
        }
        .piko-battery-text {
            font-size: 0.85rem;
            font-weight: 700;
        }
        .piko-avatar-wrap {
            display: flex;
            justify-content: center;
            margin: 0.2rem 0 0.85rem 0;
        }
        .piko-avatar {
            width: 176px;
            height: 176px;
            object-fit: cover;
            border-radius: 24px;
        }
        .piko-speech {
            background: rgba(255, 253, 249, 0.88);
            border: 1px solid rgba(43, 38, 35, 0.07);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            font-size: 0.95rem;
            line-height: 1.5;
            color: var(--ink);
            margin-bottom: 0.75rem;
        }
        .piko-subtip {
            font-size: 0.8rem;
            color: var(--ink-muted);
            margin-top: 0.45rem;
            line-height: 1.4;
        }
        .battery-track {
            width: 100%;
            height: 8px;
            background: rgba(43, 38, 35, 0.09);
            border-radius: 999px;
            overflow: hidden;
        }
        .battery-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.35s ease;
        }

        /* Indikator 7 Hari (Flexible Streak) */
        .week-dots {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 0.4rem;
            margin: 0.85rem 0 0.65rem 0;
        }
        .day-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.3rem;
        }
        .day-label {
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--ink-muted);
        }
        .day-circle {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.78rem;
            font-weight: 700;
            border: 1.5px solid var(--border-warm);
            background: #FAF7F2;
            color: #ABA094;
        }
        .day-circle.filled {
            background: var(--sage);
            border-color: var(--sage);
            color: #FFFDF9;
        }
        .day-circle.today {
            box-shadow: 0 0 0 3px rgba(217, 155, 38, 0.28);
            border-color: var(--honey);
        }

        /* Mini stats grid */
        .mini-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.65rem;
            margin-bottom: 1rem;
        }
        .mini-tile {
            background: var(--card-bg);
            border: 1px solid var(--border-warm);
            border-radius: 18px;
            padding: 0.8rem 0.7rem;
            text-align: center;
        }
        .mini-val {
            font-family: 'Fraunces', Georgia, serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--ink);
            line-height: 1.2;
        }
        .mini-lbl {
            font-size: 0.72rem;
            color: var(--ink-muted);
            margin-top: 0.2rem;
            font-weight: 500;
        }

        /* Insight & Mission cards */
        .mission-card {
            background: #EDF3EE;
            border: 1.5px solid #9EBFA8;
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            margin-bottom: 1rem;
        }
        .mission-kicker {
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #3D6B52;
            margin-bottom: 0.35rem;
        }
        .mission-text {
            font-family: 'Fraunces', Georgia, serif;
            font-size: 1.08rem;
            font-weight: 600;
            color: var(--ink);
            line-height: 1.4;
            margin-bottom: 0.45rem;
        }
        .mission-reason {
            font-size: 0.83rem;
            color: #4D5E53;
            line-height: 1.45;
        }

        .insight-item {
            background: var(--card-bg);
            border: 1px solid var(--border-warm);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.65rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        .insight-badge {
            flex-shrink: 0;
            background: #FDF3DA;
            color: #9C640C;
            border: 1px solid #ECD08B;
            border-radius: 12px;
            padding: 0.28rem 0.55rem;
            font-size: 0.78rem;
            font-weight: 700;
        }
        .insight-text {
            font-size: 0.88rem;
            line-height: 1.45;
            color: var(--ink);
        }

        /* History card */
        .log-card {
            background: var(--card-bg);
            border: 1px solid var(--border-warm);
            border-radius: 18px;
            padding: 0.95rem 1.05rem;
            margin-bottom: 0.5rem;
        }
        .log-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.55rem;
        }
        .log-date {
            font-family: 'Fraunces', Georgia, serif;
            font-size: 1rem;
            font-weight: 600;
            color: var(--ink);
        }
        .log-scores {
            display: flex;
            gap: 0.35rem;
        }
        .score-chip {
            font-size: 0.74rem;
            font-weight: 700;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            background: #FDF3DA;
            color: #8F5B0B;
        }
        .score-chip.focus {
            background: #EDF3EE;
            color: #366049;
        }
        .log-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-bottom: 0.45rem;
        }
        .habit-pill {
            font-size: 0.75rem;
            color: var(--ink-muted);
            background: #F4EFE6;
            padding: 0.22rem 0.55rem;
            border-radius: 8px;
            font-weight: 500;
        }
        .log-note {
            font-size: 0.82rem;
            color: var(--ink-muted);
            font-style: italic;
            margin-top: 0.25rem;
        }

        /* Rapikan form & input */
        .section-label {
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--ink-muted);
            margin: 0.9rem 0 0.35rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
