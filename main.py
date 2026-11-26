"""
main.py
-------
Entry point utama aplikasi HeyPiko — Habit & Energy Pattern Tracker.
Mengatur konfigurasi halaman, navigasi mobile-first, dan pemuatan modul UI.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from data_manager import ensure_data_initialized
from ui.checkin_view import render_checkin
from ui.dashboard_view import render_dashboard
from ui.history_view import render_history
from ui.insight_view import render_insight
from ui.styles import format_date_id, inject_custom_css

st.set_page_config(
    page_title="HeyPiko — Habit & Energy Tracker",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def main() -> None:
    inject_custom_css()

    # Inisialisasi state navigasi
    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"
    if "edit_date" not in st.session_state:
        st.session_state["edit_date"] = None

    # Header brand mobile-first
    today_label = format_date_id(date.today())
    st.markdown(
        f"""
        <div class="brand-bar">
            <div class="brand-title">
                <span class="brand-dot"></span>
                HeyPiko
            </div>
            <div class="brand-date">{today_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigasi 4 tab ramah ibu jari di layar HP
    nav_items = [
        ("dashboard", "Beranda"),
        ("checkin", "Check-in"),
        ("insight", "Insight"),
        ("history", "Riwayat"),
    ]
    nav_cols = st.columns(4, gap="small")
    for col, (page_id, label) in zip(nav_cols, nav_items):
        is_active = st.session_state["page"] == page_id
        with col:
            if st.button(
                label,
                key=f"nav_{page_id}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                if page_id != "checkin":
                    st.session_state["edit_date"] = None
                st.session_state["page"] = page_id
                st.rerun()

    # Tampilkan notifikasi singkat jika baru saja simpan/hapus data
    flash_msg = st.session_state.pop("flash_message", None)
    if flash_msg:
        st.toast(flash_msg)

    # Muat data check-in (otomatis buat dummy data jika kosong)
    logs = ensure_data_initialized()

    # Render halaman aktif
    current_page = st.session_state["page"]
    if current_page == "dashboard":
        render_dashboard(logs)
    elif current_page == "checkin":
        render_checkin(logs)
    elif current_page == "insight":
        render_insight(logs)
    elif current_page == "history":
        render_history(logs)


if __name__ == "__main__":
    main()
