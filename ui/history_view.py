"""
ui/history_view.py
------------------
Halaman Riwayat Log (CRUD).
Menampilkan daftar catatan harian dalam format kartu yang ramah layar HP,
lengkap dengan tombol Edit, Hapus, dan opsi reset dummy data untuk demo.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from data_manager import delete_log, generate_dummy_data
from ui.styles import format_date_id


def render_history(logs: list[dict[str, Any]]) -> None:
    """Merender halaman Riwayat Log harian."""
    st.markdown(
        f"""
        <div style="margin-bottom:0.75rem;">
            <h2 style="margin:0; font-size:1.45rem;">Riwayat Check-in</h2>
            <div style="font-size:0.86rem; color:#756B62; margin-top:0.2rem;">
                Total {len(logs)} hari tercatat. Kamu bisa ubah atau hapus catatan kapan saja.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not logs:
        st.markdown(
            """
            <div class="paper-card" style="text-align:center; padding:1.6rem 1rem;">
                <div style="font-weight:600; margin-bottom:0.35rem;">Belum ada riwayat check-in</div>
                <div style="font-size:0.84rem; color:#756B62;">
                    Yuk mulai catat hari pertamamu atau muat data contoh di bawah untuk mencoba grafik!
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Tampilkan dari tanggal terbaru ke terlama
        for log in reversed(logs):
            d_str = log["date"]
            d_obj = datetime.strptime(d_str, "%Y-%m-%d").date()
            pretty_date = format_date_id(d_obj)

            ex_text = f"Olahraga {log['exercise_minutes']}m" if log.get("exercise") else "Tanpa olahraga"
            note_html = (
                f'<div class="log-note">“{log["note"]}”</div>' if log.get("note") else ""
            )

            st.markdown(
                f"""
                <div class="log-card">
                    <div class="log-header">
                        <span class="log-date">{pretty_date}</span>
                        <div class="log-scores">
                            <span class="score-chip">Energi {log['energy']}/5</span>
                            <span class="score-chip focus">Fokus {log['focus']}/5</span>
                        </div>
                    </div>
                    <div class="log-pills">
                        <span class="habit-pill">Tidur {log['sleep_hours']:g}j ({log['bedtime']})</span>
                        <span class="habit-pill">Air {log['water_glasses']} gls</span>
                        <span class="habit-pill">{ex_text}</span>
                        <span class="habit-pill">Kafein: {log['caffeine']}</span>
                    </div>
                    {note_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_edit, col_del, _ = st.columns([1, 1, 2.2])
            with col_edit:
                if st.button("Edit", key=f"edit_{d_str}", type="secondary", use_container_width=True):
                    st.session_state["edit_date"] = d_str
                    st.session_state["page"] = "checkin"
                    st.rerun()
            with col_del:
                confirm_key = f"confirm_del_{d_str}"
                if st.session_state.get(confirm_key):
                    if st.button("Yakin Hapus?", key=f"do_del_{d_str}", type="primary", use_container_width=True):
                        ok, msg = delete_log(d_str)
                        st.session_state[confirm_key] = False
                        if ok:
                            st.session_state["flash_message"] = msg
                        st.rerun()
                else:
                    if st.button("Hapus", key=f"ask_del_{d_str}", type="secondary", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()

            st.markdown("<div style='height:0.35rem;'></div>", unsafe_allow_html=True)

    # Utilitas demo di bagian bawah
    with st.expander("Pengaturan Data Demo"):
        st.caption(
            "Gunakan tombol ini saat presentasi/demo jika ingin mengembalikan 10 hari data contoh."
        )
        if st.button("Muat Ulang Data Contoh (10 Hari)", type="secondary", use_container_width=True):
            generate_dummy_data(overwrite=True)
            st.session_state["flash_message"] = "Data contoh 10 hari berhasil dimuat ulang!"
            st.rerun()
