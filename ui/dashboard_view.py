"""
ui/dashboard_view.py
--------------------
Halaman utama: Piko Companion Dashboard.
Menampilkan karakter Piko, dialog kontekstual, tombol cepat Check-in,
Flexible Streak mingguan, dan ringkasan skor 7 hari terakhir.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import streamlit as st

from analytics import calculate_weekly_consistency
from piko_engine import get_piko_state
from ui.styles import load_image_base64


def render_dashboard(logs: list[dict[str, Any]]) -> None:
    """Merender halaman Beranda / Piko Companion Dashboard."""
    today_str = date.today().strftime("%Y-%m-%d")
    today_log = next((log for log in logs if log.get("date") == today_str), None)

    piko = get_piko_state(today_log)
    theme = piko["theme"]
    battery = piko["battery_percent"]
    battery_label = f"{battery}%" if battery is not None else "--%"
    bar_width = battery if battery is not None else 12

    img_b64 = load_image_base64(piko["asset_name"])
    if img_b64:
        avatar_html = (
            f'<div class="piko-avatar-wrap">'
            f'<img src="data:image/png;base64,{img_b64}" class="piko-avatar" alt="Piko" />'
            f"</div>"
        )
    else:
        avatar_html = (
            '<div class="piko-avatar-wrap">'
            '<div style="width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,0.65);'
            'display:flex;align-items:center;justify-content:center;font-size:2.4rem;">✨</div>'
            "</div>"
        )

    subtip_html = (
        f'<div class="piko-subtip">{piko["sub_tip"]}</div>' if piko.get("sub_tip") else ""
    )

    # 1. Kartu Hero Piko
    st.markdown(
        f"""
        <div class="piko-hero" style="background:{theme['card_bg']}; border-color:{theme['card_border']};">
            <div class="piko-top-row">
                <span class="piko-pill" style="background:{theme['pill_bg']}; color:{theme['pill_text']};">
                    ● {piko['label']}
                </span>
                <span class="piko-battery-text" style="color:{theme['accent']};">
                    Baterai {battery_label}
                </span>
            </div>
            {avatar_html}
            <div class="piko-speech">
                “{piko['message']}”
            </div>
            <div class="battery-track">
                <div class="battery-fill" style="width:{bar_width}%; background:{theme['bar_color']};"></div>
            </div>
            {subtip_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Tombol Cepat Check-in Hari Ini
    cta_label = "Perbarui Check-in Hari Ini" if today_log else "Check-in Hari Ini (30 Detik)"
    if st.button(cta_label, type="primary", use_container_width=True, key="dash_cta_checkin"):
        st.session_state["edit_date"] = None
        st.session_state["page"] = "checkin"
        st.rerun()

    st.markdown("<div style='height: 0.45rem;'></div>", unsafe_allow_html=True)

    # 3. Kartu Flexible Streak & Weekly Consistency Score
    consistency = calculate_weekly_consistency(logs)
    dots_html_parts = []
    for d in consistency["days"]:
        classes = ["day-circle"]
        if d["filled"]:
            classes.append("filled")
        if d["is_today"]:
            classes.append("today")
        mark = "✓" if d["filled"] else str(d["day_num"])
        dots_html_parts.append(
            f'<div class="day-item">'
            f'<span class="day-label">{d["day_short"]}</span>'
            f'<div class="{" ".join(classes)}">{mark}</div>'
            f"</div>"
        )
    dots_html = "".join(dots_html_parts)

    st.markdown(
        f"""
        <div class="paper-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#756B62;">
                        Konsistensi 7 Hari Terakhir
                    </div>
                    <div class="font-serif" style="font-size:1.2rem; font-weight:700; margin-top:0.15rem;">
                        {consistency['filled_days']}/7 Hari ({consistency['percentage']}%)
                    </div>
                </div>
                <span class="piko-pill" style="background:#EDF3EE; color:#366049;">
                    {consistency['badge']}
                </span>
            </div>
            <div class="week-dots">{dots_html}</div>
            <div style="font-size:0.82rem; color:#756B62; line-height:1.4;">
                {consistency['note']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Ringkasan Cepat 7 Hari Terakhir
    cutoff = (date.today() - timedelta(days=6)).strftime("%Y-%m-%d")
    recent_logs = [log for log in logs if log.get("date", "") >= cutoff]

    if recent_logs:
        avg_sleep = sum(float(x["sleep_hours"]) for x in recent_logs) / len(recent_logs)
        avg_energy = sum(int(x["energy"]) for x in recent_logs) / len(recent_logs)
        avg_water = sum(int(x["water_glasses"]) for x in recent_logs) / len(recent_logs)
        sleep_str = f"{avg_sleep:.1f}j"
        energy_str = f"{avg_energy:.1f}/5"
        water_str = f"{avg_water:.1f} gls"
    else:
        sleep_str = "--"
        energy_str = "--"
        water_str = "--"

    st.markdown(
        f"""
        <div class="mini-grid">
            <div class="mini-tile">
                <div class="mini-val">{sleep_str}</div>
                <div class="mini-lbl">Rata-rata Tidur</div>
            </div>
            <div class="mini-tile">
                <div class="mini-val">{energy_str}</div>
                <div class="mini-lbl">Rata-rata Energi</div>
            </div>
            <div class="mini-tile">
                <div class="mini-val">{water_str}</div>
                <div class="mini-lbl">Air Harian</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
