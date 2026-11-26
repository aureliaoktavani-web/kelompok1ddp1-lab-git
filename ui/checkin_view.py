"""
ui/checkin_view.py
------------------
Halaman Quick Daily Check-in (< 30 detik).
Mendukung pencatatan hari ini, pencegahan duplikasi tanggal,
dan mode edit ketika dipanggil dari halaman Riwayat.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

import streamlit as st

from data_manager import VALID_CAFFEINE_OPTIONS, get_log_by_date, save_log


def _parse_time_str(value: str, fallback: time = time(23, 0)) -> time:
    try:
        dt = datetime.strptime(value, "%H:%M")
        return time(dt.hour, dt.minute)
    except (ValueError, TypeError):
        return fallback


def render_checkin(logs: list[dict[str, Any]]) -> None:
    """Merender halaman form Quick Daily Check-in."""
    edit_date_str = st.session_state.get("edit_date")

    if edit_date_str:
        st.markdown(
            f"""
            <div class="paper-card" style="background:#FDF3DA; border-color:#E6B84C; padding:0.75rem 1rem;">
                <div style="font-size:0.85rem; font-weight:600; color:#7A4E08;">
                    Mode Edit — Mengubah catatan tanggal <strong>{edit_date_str}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Batal Edit & Kembali ke Hari Ini", type="secondary", use_container_width=True):
            st.session_state["edit_date"] = None
            st.rerun()
        default_date = datetime.strptime(edit_date_str, "%Y-%m-%d").date()
    else:
        default_date = date.today()

    st.markdown(
        """
        <div style="margin-bottom:0.65rem;">
            <h2 style="margin:0; font-size:1.45rem;">Quick Check-in</h2>
            <div style="font-size:0.86rem; color:#756B62; margin-top:0.2rem;">
                Geser singkat kurang dari 30 detik. Kalau tanggal sudah pernah diisi, datanya otomatis diperbarui.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_date = st.date_input(
        "Tanggal Check-in",
        value=default_date,
        max_value=date.today(),
        format="YYYY-MM-DD",
    )
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    existing = get_log_by_date(selected_date_str)

    # Nilai awal otomatis terisi jika tanggal sudah memiliki data
    init_sleep = float(existing["sleep_hours"]) if existing else 7.0
    init_bedtime = _parse_time_str(existing["bedtime"]) if existing else time(23, 0)
    init_water = int(existing["water_glasses"]) if existing else 6
    init_exercise = bool(existing["exercise"]) if existing else False
    init_ex_min = int(existing["exercise_minutes"]) if existing and existing["exercise"] else 30
    init_caffeine = existing["caffeine"] if existing else "Pagi"
    init_energy = int(existing["energy"]) if existing else 4
    init_focus = int(existing["focus"]) if existing else 4
    init_note = existing["note"] if existing else ""

    if existing and not edit_date_str:
        st.caption(f"Sudah ada catatan untuk {selected_date_str}. Menyimpan akan memperbarui data hari ini.")

    # Bagian 1: Tidur
    st.markdown('<div class="section-label">1. Pola Tidur</div>', unsafe_allow_html=True)
    col_sleep1, col_sleep2 = st.columns([2, 1])
    with col_sleep1:
        sleep_hours = st.slider(
            "Durasi Tidur (jam)",
            min_value=0.0,
            max_value=12.0,
            value=min(12.0, max(0.0, init_sleep)),
            step=0.5,
            key=f"sleep_{selected_date_str}",
        )
    with col_sleep2:
        bedtime_val = st.time_input(
            "Jam Tidur",
            value=init_bedtime,
            step=900,
            key=f"bedtime_{selected_date_str}",
        )

    # Bagian 2: Kebiasaan Harian
    st.markdown('<div class="section-label">2. Kebiasaan Harian</div>', unsafe_allow_html=True)
    water_glasses = st.slider(
        "Jumlah Gelas Air",
        min_value=0,
        max_value=15,
        value=min(15, max(0, init_water)),
        step=1,
        key=f"water_{selected_date_str}",
    )

    col_ex1, col_ex2 = st.columns([1, 1])
    with col_ex1:
        exercise = st.toggle(
            "Olahraga / Gerak Aktif",
            value=init_exercise,
            key=f"ex_{selected_date_str}",
        )
    with col_ex2:
        if exercise:
            exercise_minutes = st.number_input(
                "Durasi (menit)",
                min_value=5,
                max_value=300,
                value=max(5, init_ex_min),
                step=5,
                key=f"ex_min_{selected_date_str}",
            )
        else:
            exercise_minutes = 0
            st.caption("Tidak olahraga hari ini")

    caff_index = (
        VALID_CAFFEINE_OPTIONS.index(init_caffeine)
        if init_caffeine in VALID_CAFFEINE_OPTIONS
        else 0
    )
    caffeine = st.radio(
        "Konsumsi Kafein",
        options=list(VALID_CAFFEINE_OPTIONS),
        index=caff_index,
        horizontal=True,
        key=f"caff_{selected_date_str}",
    )

    # Bagian 3: Energi & Fokus
    st.markdown('<div class="section-label">3. Kondisi Energi & Fokus</div>', unsafe_allow_html=True)
    energy_labels = {1: "1 · Sangat Lemas", 2: "2 · Low-bat", 3: "3 · Cukup Stabil", 4: "4 · Segar", 5: "5 · Penuh!"}
    focus_labels = {1: "1 · Buyar", 2: "2 · Mudah Terdistraksi", 3: "3 · Lumayan", 4: "4 · Tajam", 5: "5 · Sangat Fokus!"}

    energy = st.select_slider(
        "Level Energi",
        options=[1, 2, 3, 4, 5],
        value=init_energy,
        format_func=lambda v: energy_labels[v],
        key=f"energy_{selected_date_str}",
    )
    focus = st.select_slider(
        "Level Fokus",
        options=[1, 2, 3, 4, 5],
        value=init_focus,
        format_func=lambda v: focus_labels[v],
        key=f"focus_{selected_date_str}",
    )

    # Bagian 4: Catatan Singkat
    st.markdown('<div class="section-label">4. Catatan Singkat (Opsional)</div>', unsafe_allow_html=True)
    note = st.text_input(
        "Ada hal menarik hari ini?",
        value=init_note,
        placeholder="Misal: Habis lari pagi, siang gak ngantuk...",
        label_visibility="collapsed",
        key=f"note_{selected_date_str}",
    )

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    if st.button("Simpan Check-in", type="primary", use_container_width=True, key="btn_save_checkin"):
        entry = {
            "date": selected_date_str,
            "sleep_hours": float(sleep_hours),
            "bedtime": bedtime_val.strftime("%H:%M"),
            "water_glasses": int(water_glasses),
            "exercise": bool(exercise),
            "exercise_minutes": int(exercise_minutes) if exercise else 0,
            "caffeine": str(caffeine),
            "energy": int(energy),
            "focus": int(focus),
            "note": note,
        }
        ok, msg = save_log(entry)
        if ok:
            st.session_state["edit_date"] = None
            st.session_state["flash_message"] = msg
            st.session_state["page"] = "dashboard"
            st.rerun()
        else:
            st.error(msg)
