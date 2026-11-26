"""
ui/insight_view.py
------------------
Halaman Insight & Grafik:
- Misi Piko Minggu Ini (Weekly Actionable Suggestion)
- Pattern & Correlation Insight (Analisis Pola Otomatis)
- Grafik Tren Interaktif 7-14 Hari (Altair)
"""

from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from analytics import analyze_patterns, generate_weekly_suggestion


def _build_trend_chart(df: pd.DataFrame, mode: str) -> alt.Chart:
    """Membuat grafik garis interaktif Altair bergaya Warm Paper & Sunlight."""
    base = alt.Chart(df).encode(
        x=alt.X(
            "date_label:N",
            sort=list(df["date_label"]),
            title=None,
            axis=alt.Axis(labelColor="#756B62", tickColor="#E7DDD0", domainColor="#E7DDD0", labelAngle=0),
        )
    )

    if mode == "Energi & Fokus":
        melted = df.melt(
            id_vars=["date_label"],
            value_vars=["energy", "focus"],
            var_name="Metrik",
            value_name="Skor",
        )
        melted["Metrik"] = melted["Metrik"].map({"energy": "Energi", "focus": "Fokus"})
        chart = (
            alt.Chart(melted)
            .mark_line(point=alt.OverlayMarkDef(filled=True, size=70), strokeWidth=2.8)
            .encode(
                x=alt.X(
                    "date_label:N",
                    sort=list(df["date_label"]),
                    title=None,
                    axis=alt.Axis(labelColor="#756B62", tickColor="#E7DDD0", domainColor="#E7DDD0", labelAngle=0),
                ),
                y=alt.Y(
                    "Skor:Q",
                    scale=alt.Scale(domain=[0.5, 5.5]),
                    title="Skor (1-5)",
                    axis=alt.Axis(labelColor="#756B62", gridColor="#EFE8DC", titleColor="#756B62"),
                ),
                color=alt.Color(
                    "Metrik:N",
                    scale=alt.Scale(domain=["Energi", "Fokus"], range=["#D99B26", "#5B8A72"]),
                    legend=alt.Legend(orient="top", title=None, labelColor="#2B2623"),
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Tanggal"),
                    alt.Tooltip("Metrik:N", title="Metrik"),
                    alt.Tooltip("Skor:Q", title="Skor"),
                ],
            )
            .properties(height=240)
            .configure_view(strokeWidth=0, fill="transparent")
            .configure(background="transparent")
        )
        return chart

    # Mode pembanding: Jam Tidur vs Energi atau Gelas Air vs Energi (dual-axis clean)
    if mode == "Jam Tidur vs Energi":
        habit_col = "sleep_hours"
        habit_title = "Tidur (Jam)"
        bar_color = "#DCE7DE"
        bar_stroke = "#7FA68E"
    else:
        habit_col = "water_glasses"
        habit_title = "Air (Gelas)"
        bar_color = "#E3ECF0"
        bar_stroke = "#7BA4B8"

    bars = base.mark_bar(
        cornerRadiusTopLeft=6,
        cornerRadiusTopRight=6,
        color=bar_color,
        stroke=bar_stroke,
        strokeWidth=1,
        size=22,
    ).encode(
        y=alt.Y(
            f"{habit_col}:Q",
            title=habit_title,
            axis=alt.Axis(labelColor="#756B62", gridColor="#EFE8DC", titleColor="#756B62"),
        ),
        tooltip=[
            alt.Tooltip("date_label:N", title="Tanggal"),
            alt.Tooltip(f"{habit_col}:Q", title=habit_title),
            alt.Tooltip("energy:Q", title="Energi"),
        ],
    )

    line = base.mark_line(
        point=alt.OverlayMarkDef(filled=True, size=75, color="#D99B26"),
        color="#D99B26",
        strokeWidth=2.8,
    ).encode(
        y=alt.Y(
            "energy:Q",
            scale=alt.Scale(domain=[0.5, 5.5]),
            title="Energi (1-5)",
            axis=alt.Axis(labelColor="#B47610", titleColor="#B47610", grid=False),
        ),
        tooltip=[
            alt.Tooltip("date_label:N", title="Tanggal"),
            alt.Tooltip("energy:Q", title="Energi"),
            alt.Tooltip(f"{habit_col}:Q", title=habit_title),
        ],
    )

    return (
        alt.layer(bars, line)
        .resolve_scale(y="independent")
        .properties(height=250)
        .configure_view(strokeWidth=0, fill="transparent")
        .configure(background="transparent")
    )


def render_insight(logs: list[dict[str, Any]]) -> None:
    """Merender halaman Insight & Grafik."""
    st.markdown(
        """
        <div style="margin-bottom:0.75rem;">
            <h2 style="margin:0; font-size:1.45rem;">Insight & Pola Energi</h2>
            <div style="font-size:0.86rem; color:#756B62; margin-top:0.2rem;">
                Temukan kebiasaan kecil yang paling memengaruhi energi dan fokus harianmu.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Kartu Misi Piko Minggu Ini (Fitur 5)
    mission = generate_weekly_suggestion(logs)
    st.markdown(
        f"""
        <div class="mission-card">
            <div class="mission-kicker">✦ {mission['title']}</div>
            <div class="mission-text">{mission['mission']}</div>
            <div class="mission-reason">{mission['reason']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Analisis Pola Otomatis (Fitur 3)
    st.markdown('<div class="section-label">Analisis Korelasi Kebiasaan</div>', unsafe_allow_html=True)
    pattern = analyze_patterns(logs)

    if not pattern["ready"]:
        progress = pattern["current_days"] / pattern["required_days"]
        st.markdown(
            f"""
            <div class="paper-card">
                <div style="font-weight:600; font-size:0.95rem; margin-bottom:0.35rem;">
                    Butuh {pattern['days_needed']} hari check-in lagi untuk membuka analisis pola
                </div>
                <div style="font-size:0.82rem; color:#756B62; margin-bottom:0.6rem;">
                    Terkumpul {pattern['current_days']} dari {pattern['required_days']} hari minimal.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(progress)
    else:
        factors = pattern["factors"][:3]
        if factors:
            for item in factors:
                sign = "+" if item["pct_impact"] >= 0 else ""
                st.markdown(
                    f"""
                    <div class="insight-item">
                        <div class="insight-badge">{sign}{item['pct_impact']:.0f}%</div>
                        <div>
                            <div style="font-size:0.75rem; font-weight:700; color:#756B62; margin-bottom:0.15rem;">
                                {item['label']} → {item['metric']}
                            </div>
                            <div class="insight-text">{item['sentence']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            for text in pattern["insights"]:
                st.markdown(
                    f'<div class="paper-card"><div class="insight-text">{text}</div></div>',
                    unsafe_allow_html=True,
                )

    # 3. Grafik Tren Mingguan (Fitur 6)
    st.markdown('<div class="section-label">Grafik Tren Harian</div>', unsafe_allow_html=True)
    if not logs:
        st.info("Belum ada data check-in untuk ditampilkan pada grafik.")
        return

    col_f1, col_f2 = st.columns([1.4, 1])
    with col_f1:
        chart_mode = st.selectbox(
            "Metrik Pembanding",
            options=["Energi & Fokus", "Jam Tidur vs Energi", "Gelas Air vs Energi"],
            label_visibility="collapsed",
        )
    with col_f2:
        range_opt = st.selectbox(
            "Rentang",
            options=["7 Hari Terakhir", "14 Hari Terakhir"],
            label_visibility="collapsed",
        )

    limit_n = 7 if range_opt == "7 Hari Terakhir" else 14
    recent_slice = logs[-limit_n:]
    df = pd.DataFrame(recent_slice)
    df["date_label"] = pd.to_datetime(df["date"]).dt.strftime("%d/%m")

    chart = _build_trend_chart(df, chart_mode)
    st.altair_chart(chart, use_container_width=True)
