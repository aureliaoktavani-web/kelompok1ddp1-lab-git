"""
analytics.py
------------
Modul analitik inti HeyPiko:
1. Pattern & Correlation Insight (conditional average kebiasaan vs energi & fokus)
2. Flexible Streak & Weekly Consistency Score (7 hari terakhir)
3. Weekly Actionable Suggestion ("Misi Piko Minggu Ini")
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

MIN_DAYS_FOR_INSIGHT = 3

INDONESIAN_DAYS_SHORT = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]


def _mean(values: list[float]) -> float | None:
    """Menghitung rata-rata sederhana; mengembalikan None jika list kosong."""
    if not values:
        return None
    return sum(values) / len(values)


def _pct_diff(high_val: float, base_val: float) -> float:
    """Menghitung selisih persentase relatif terhadap nilai pembanding."""
    if base_val == 0:
        return 0.0
    return ((high_val - base_val) / base_val) * 100.0


def _filter_recent_logs(
    logs: list[dict[str, Any]], days: int = 7, reference_date: date | None = None
) -> list[dict[str, Any]]:
    """Memfilter log dalam rentang N hari terakhir (termasuk reference_date)."""
    today = reference_date or date.today()
    start_date = today - timedelta(days=days - 1)
    result = []
    for log in logs:
        try:
            d = datetime.strptime(log["date"], "%Y-%m-%d").date()
            if start_date <= d <= today:
                result.append(log)
        except (KeyError, ValueError):
            continue
    return sorted(result, key=lambda x: x["date"])


def analyze_patterns(logs: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Menganalisis pola korelasi antara kebiasaan (tidur, olahraga, air, kafein)
    dengan energi dan fokus menggunakan rata-rata bersyarat (conditional average).
    """
    total_days = len(logs)
    if total_days < MIN_DAYS_FOR_INSIGHT:
        return {
            "ready": False,
            "current_days": total_days,
            "required_days": MIN_DAYS_FOR_INSIGHT,
            "days_needed": MIN_DAYS_FOR_INSIGHT - total_days,
            "insights": [],
            "factors": [],
        }

    factors: list[dict[str, Any]] = []

    # 1. Durasi Tidur >= 7 jam vs < 7 jam (terhadap Energi)
    sleep_good = [float(x["energy"]) for x in logs if float(x.get("sleep_hours", 0)) >= 7.0]
    sleep_low = [float(x["energy"]) for x in logs if float(x.get("sleep_hours", 0)) < 7.0]
    if sleep_good and sleep_low:
        avg_g, avg_l = _mean(sleep_good), _mean(sleep_low)
        assert avg_g is not None and avg_l is not None
        pct = _pct_diff(avg_g, avg_l)
        if pct >= 0:
            sentence = (
                f"Energimu rata-rata {abs(pct):.0f}% lebih tinggi di hari kamu tidur minimal 7 jam "
                f"(skor {avg_g:.1f} vs {avg_l:.1f})."
            )
        else:
            sentence = (
                f"Rata-rata energimu saat tidur >= 7 jam ({avg_g:.1f}) cukup dekat dengan "
                f"saat tidur < 7 jam ({avg_l:.1f})."
            )
        factors.append(
            {
                "habit": "sleep",
                "label": "Tidur Cukup (>= 7 jam)",
                "metric": "Energi",
                "avg_good": round(avg_g, 2),
                "avg_other": round(avg_l, 2),
                "pct_impact": round(pct, 1),
                "abs_impact": round(abs(pct), 1),
                "sentence": sentence,
            }
        )

    # 2. Olahraga Ya vs Tidak (terhadap Energi & Fokus)
    ex_yes_e = [float(x["energy"]) for x in logs if bool(x.get("exercise", False))]
    ex_no_e = [float(x["energy"]) for x in logs if not bool(x.get("exercise", False))]
    ex_yes_f = [float(x["focus"]) for x in logs if bool(x.get("exercise", False))]
    ex_no_f = [float(x["focus"]) for x in logs if not bool(x.get("exercise", False))]
    if ex_yes_e and ex_no_e:
        avg_ye, avg_ne = _mean(ex_yes_e), _mean(ex_no_e)
        avg_yf, avg_nf = _mean(ex_yes_f), _mean(ex_no_f)
        assert avg_ye is not None and avg_ne is not None
        assert avg_yf is not None and avg_nf is not None
        pct_e = _pct_diff(avg_ye, avg_ne)
        pct_f = _pct_diff(avg_yf, avg_nf)
        if pct_f >= pct_e and pct_f > 0:
            sentence = (
                f"Di hari kamu berolahraga, skor fokusmu naik dari rata-rata {avg_nf:.1f} "
                f"menjadi {avg_yf:.1f} (+{pct_f:.0f}%)."
            )
            best_pct = pct_f
            metric_used = "Fokus"
            g_val, o_val = avg_yf, avg_nf
        else:
            direction = "lebih tinggi" if pct_e >= 0 else "lebih rendah"
            sentence = (
                f"Di hari kamu berolahraga, energimu rata-rata {abs(pct_e):.0f}% {direction} "
                f"(skor {avg_ye:.1f} vs {avg_ne:.1f})."
            )
            best_pct = pct_e
            metric_used = "Energi"
            g_val, o_val = avg_ye, avg_ne

        factors.append(
            {
                "habit": "exercise",
                "label": "Olahraga",
                "metric": metric_used,
                "avg_good": round(g_val, 2),
                "avg_other": round(o_val, 2),
                "pct_impact": round(best_pct, 1),
                "abs_impact": round(abs(best_pct), 1),
                "sentence": sentence,
            }
        )

    # 3. Minum Air >= 6 gelas vs < 6 gelas (terhadap Energi)
    water_good = [float(x["energy"]) for x in logs if int(x.get("water_glasses", 0)) >= 6]
    water_low = [float(x["energy"]) for x in logs if int(x.get("water_glasses", 0)) < 6]
    if water_good and water_low:
        avg_g, avg_l = _mean(water_good), _mean(water_low)
        assert avg_g is not None and avg_l is not None
        pct = _pct_diff(avg_g, avg_l)
        if pct >= 0:
            sentence = (
                f"Saat minum minimal 6 gelas air, energimu rata-rata {pct:.0f}% lebih baik "
                f"(skor {avg_g:.1f} vs {avg_l:.1f})."
            )
        else:
            sentence = (
                f"Rata-rata energimu saat minum >= 6 gelas ({avg_g:.1f}) relatif mirip dengan "
                f"saat < 6 gelas ({avg_l:.1f})."
            )
        factors.append(
            {
                "habit": "water",
                "label": "Hidrasi (>= 6 gelas)",
                "metric": "Energi",
                "avg_good": round(avg_g, 2),
                "avg_other": round(avg_l, 2),
                "pct_impact": round(pct, 1),
                "abs_impact": round(abs(pct), 1),
                "sentence": sentence,
            }
        )

    # 4. Kafein Sore-Malam vs Tidak/Pagi (terhadap Fokus)
    caff_late = [float(x["focus"]) for x in logs if x.get("caffeine") == "Sore-Malam"]
    caff_safe = [float(x["focus"]) for x in logs if x.get("caffeine") in ("Tidak", "Pagi")]
    if caff_late and caff_safe:
        avg_late, avg_safe = _mean(caff_late), _mean(caff_safe)
        assert avg_late is not None and avg_safe is not None
        pct = _pct_diff(avg_safe, avg_late)
        if avg_safe > avg_late:
            sentence = (
                f"Di hari tanpa kafein sore-malam, fokusmu rata-rata {pct:.0f}% lebih tinggi "
                f"(skor {avg_safe:.1f} vs {avg_late:.1f})."
            )
        else:
            sentence = (
                f"Skor fokus saat minum kafein sore-malam ({avg_late:.1f}) tidak lebih rendah "
                f"dari hari tanpa kafein sore ({avg_safe:.1f})."
            )
        factors.append(
            {
                "habit": "caffeine",
                "label": "Hindari Kafein Sore-Malam",
                "metric": "Fokus",
                "avg_good": round(avg_safe, 2),
                "avg_other": round(avg_late, 2),
                "pct_impact": round(pct, 1),
                "abs_impact": round(abs(pct), 1),
                "sentence": sentence,
            }
        )

    # Urutkan dari dampak absolut terbesar
    factors.sort(key=lambda item: item["abs_impact"], reverse=True)
    top_insights = [f["sentence"] for f in factors[:3]]

    if not top_insights:
        top_insights = [
            "Datamu sudah mulai terkumpul, tapi variasinya masih seragam. Terus check-in biar Piko bisa membandingkan pola harianmu!"
        ]

    return {
        "ready": True,
        "current_days": total_days,
        "required_days": MIN_DAYS_FOR_INSIGHT,
        "days_needed": 0,
        "insights": top_insights,
        "factors": factors,
    }


def calculate_weekly_consistency(
    logs: list[dict[str, Any]], reference_date: date | None = None
) -> dict[str, Any]:
    """
    Menghitung skor konsistensi mingguan (Flexible Streak) selama 7 hari terakhir
    beserta badge dan indikator 7 hari.
    """
    today = reference_date or date.today()
    filled_dates = {log.get("date") for log in logs}

    days_list: list[dict[str, Any]] = []
    filled_count = 0

    for offset in range(6, -1, -1):
        d = today - timedelta(days=offset)
        d_str = d.strftime("%Y-%m-%d")
        is_filled = d_str in filled_dates
        if is_filled:
            filled_count += 1
        days_list.append(
            {
                "date": d_str,
                "day_short": INDONESIAN_DAYS_SHORT[d.weekday()],
                "day_num": d.day,
                "filled": is_filled,
                "is_today": offset == 0,
            }
        )

    pct = round((filled_count / 7) * 100)

    if filled_count >= 6:
        badge = "Super Konsisten"
        note = "Ritmemu luar biasa terjaga minggu ini—pertahankan santai aja!"
    elif filled_count >= 4:
        badge = "Ritme Stabil"
        note = "Bolong 1-2 hari gak masalah, yang penting lanjut lagi."
    elif filled_count >= 1:
        badge = "Baru Memulai"
        note = "Langkah awal yang bagus! Cukup 30 detik sehari untuk jaga ritme."
    else:
        badge = "Yuk Mulai Lagi"
        note = "Gak pernah telat buat mulai lagi hari ini—Piko siap nemenin."

    return {
        "filled_days": filled_count,
        "total_days": 7,
        "percentage": pct,
        "badge": badge,
        "note": note,
        "days": days_list,
    }


def generate_weekly_suggestion(
    logs: list[dict[str, Any]], reference_date: date | None = None
) -> dict[str, str]:
    """
    Menghasilkan 1 rekomendasi target kecil yang realistis ("Misi Piko Minggu Ini")
    berdasarkan metrik terlemah dalam 7 hari terakhir dan korelasi dampak tertinggi.
    """
    recent = _filter_recent_logs(logs, days=7, reference_date=reference_date)
    if len(recent) < 2:
        return {
            "title": "Misi Piko Minggu Ini",
            "focus_habit": "consistency",
            "mission": "Coba lakukan Quick Check-in minimal 4 hari minggu ini supaya Piko bisa memetakan pola energimu.",
            "reason": "Data 7 hari terakhir masih baru dimulai—dengan 4 check-in, rekomendasi personalmu akan jauh lebih akurat.",
        }

    pattern = analyze_patterns(logs)
    impact_rank = {f["habit"]: f["abs_impact"] for f in pattern.get("factors", [])}

    avg_sleep = _mean([float(x.get("sleep_hours", 0)) for x in recent]) or 0.0
    avg_water = _mean([float(x.get("water_glasses", 0)) for x in recent]) or 0.0
    exercise_days = sum(1 for x in recent if bool(x.get("exercise", False)))
    late_caff_days = sum(1 for x in recent if x.get("caffeine") == "Sore-Malam")

    candidates: list[tuple[float, dict[str, str]]] = []

    if avg_sleep < 6.8:
        candidates.append(
            (
                impact_rank.get("sleep", 25.0) + 10.0,
                {
                    "title": "Misi Piko Minggu Ini",
                    "focus_habit": "sleep",
                    "mission": "Coba tidur sebelum jam 23.30 (minimal 7 jam) sebanyak 4 kali minggu ini.",
                    "reason": f"Rata-rata tidurmu 7 hari terakhir baru {avg_sleep:.1f} jam, dan tidur cukup punya pengaruh besar ke energimu.",
                },
            )
        )

    if avg_water < 6.0:
        candidates.append(
            (
                impact_rank.get("water", 15.0) + 5.0,
                {
                    "title": "Misi Piko Minggu Ini",
                    "focus_habit": "water",
                    "mission": "Siapkan botol minum di meja belajar dan capai minimal 6 gelas air selama 5 hari minggu ini.",
                    "reason": f"Rata-rata minummu minggu ini baru {avg_water:.1f} gelas per hari—hidrasi stabil bantu cegah ngantuk siang.",
                },
            )
        )

    if exercise_days < 2:
        candidates.append(
            (
                impact_rank.get("exercise", 20.0) + 5.0,
                {
                    "title": "Misi Piko Minggu Ini",
                    "focus_habit": "exercise",
                    "mission": "Jadwalkan gerak ringan 20 menit (jalan cepat atau stretching) minimal 2 kali minggu ini.",
                    "reason": f"Minggu ini kamu baru sempat olahraga {exercise_days} kali—sedikit gerak terbukti bantu dongkrak fokus harian.",
                },
            )
        )

    if late_caff_days >= 2:
        candidates.append(
            (
                impact_rank.get("caffeine", 18.0) + 5.0,
                {
                    "title": "Misi Piko Minggu Ini",
                    "focus_habit": "caffeine",
                    "mission": "Coba batasi konsumsi kafein hanya sampai siang hari (sebelum jam 14.00) minggu ini.",
                    "reason": f"Kamu tercatat minum kafein sore-malam {late_caff_days} kali minggu ini, yang bisa mengganggu kualitas fokus & tidur.",
                },
            )
        )

    if candidates:
        # Prioritaskan kebiasaan terlemah yang korelasinya paling tinggi terhadap energi
        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    return {
        "title": "Misi Piko Minggu Ini",
        "focus_habit": "maintain",
        "mission": "Pertahankan ritme tidur >= 7 jam dan hidrasi 6+ gelas minimal 5 hari minggu ini!",
        "reason": "Semua metrik utamamu minggu ini sudah di zona sehat—tinggal jaga konsistensinya tanpa tekanan.",
    }
