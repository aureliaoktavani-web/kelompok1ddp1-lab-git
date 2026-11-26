"""
piko_engine.py
--------------
Modul penentu state visual, persentase baterai, warna tema kartu,
dan dialog suportif karakter Piko berdasarkan data check-in hari ini.
"""

from __future__ import annotations

from typing import Any


THEMES: dict[str, dict[str, str]] = {
    "super_charged": {
        "card_bg": "#FDF3DA",
        "card_border": "#E6B84C",
        "accent": "#B47610",
        "pill_bg": "#F7E2A8",
        "pill_text": "#7A4E08",
        "bar_color": "#E5A93B",
    },
    "steady": {
        "card_bg": "#EDF3EE",
        "card_border": "#90B49B",
        "accent": "#3D6B52",
        "pill_bg": "#D7E7DB",
        "pill_text": "#2A4D3A",
        "bar_color": "#5B8A72",
    },
    "low_battery": {
        "card_bg": "#FBECE7",
        "card_border": "#DF9B88",
        "accent": "#A64B38",
        "pill_bg": "#F5D7CD",
        "pill_text": "#7A3224",
        "bar_color": "#D4745E",
    },
    "waiting": {
        "card_bg": "#F4EFE6",
        "card_border": "#D5C8B5",
        "accent": "#766553",
        "pill_bg": "#E9DFD0",
        "pill_text": "#57493B",
        "bar_color": "#B8A690",
    },
}


def _pick_dialog(today_log: dict[str, Any], battery_percent: int) -> tuple[str, str]:
    """
    Memilih pesan dialog kontekstual dan tips kecil untuk Piko
    berdasarkan kombinasi energi, tidur, air, olahraga, dan kafein.
    """
    energy = int(today_log.get("energy", 3))
    focus = int(today_log.get("focus", 3))
    sleep_hours = float(today_log.get("sleep_hours", 7.0))
    water_glasses = int(today_log.get("water_glasses", 6))
    exercise = bool(today_log.get("exercise", False))
    caffeine = str(today_log.get("caffeine", "Tidak"))

    # Tips tambahan ramah (sub-tip)
    sub_tip = ""
    if water_glasses < 4:
        sub_tip = "Pengingat lembut: coba tambah 2 gelas air lagi hari ini ya."
    elif caffeine == "Sore-Malam":
        sub_tip = "Catatan kecil: kafein sore-malam kadang bikin tidur malam agak mundur."
    elif sleep_hours < 6:
        sub_tip = "Kalau sempat, power nap 15-20 menit bisa bantu recharge sedikit."
    elif exercise:
        sub_tip = "Mantap sudah sempat gerak hari ini—tubuhmu pasti berterima kasih!"

    # Kondisi 1: Low Battery (Energi 1 - 2)
    if energy <= 2:
        if sleep_hours < 6:
            msg = (
                f"Energi kita lagi di {battery_percent}% nih. Tidur {sleep_hours:g} jam memang "
                "berat buat badan—pelan-pelan aja hari ini, jangan lupa istirahat lebih awal ya."
            )
        elif water_glasses < 4:
            msg = (
                f"Baterai Piko baru {battery_percent}%. Baru minum {water_glasses} gelas air—"
                "yuk teguk segelas air dulu, kadang lemas itu cuma tanda butuh hidrasi."
            )
        elif caffeine == "Sore-Malam":
            msg = (
                f"Hari ini lagi agak redup ({battery_percent}%). Kafein sore-malam kadang bikin "
                "energi naik sebentar lalu drop—gak apa-apa, kita recharge pelan-pelan."
            )
        else:
            msg = (
                f"Energi hari ini di {battery_percent}%. Gak apa-apa kok kalau lagi low-bat, "
                "gak harus selalu 100% setiap hari. Ambil jeda sebentar ya."
            )
        return msg, sub_tip

    # Kondisi 2: Super Charged (Energi 4 - 5)
    if energy >= 4:
        if sleep_hours >= 7 and exercise:
            msg = (
                f"Energi kita hari ini {battery_percent}%! Kombinasi tidur {sleep_hours:g} jam "
                "dan olahraga bikin Piko bersinar terang banget hari ini!"
            )
        elif sleep_hours >= 7:
            msg = (
                f"Energi kita hari ini {battery_percent}%! Keren, tidur cukup ({sleep_hours:g} jam) "
                "beneran ngaruh banget ke mood dan tenagamu ya!"
            )
        elif water_glasses < 4:
            msg = (
                f"Wih, energi {battery_percent}%! Biar tetap awet sampai malam, "
                "jangan lupa tambah minum airnya ya—baru tercatat {water_glasses} gelas."
            )
        elif focus >= 4:
            msg = (
                f"Super charged di {battery_percent}% dengan fokus tajam! "
                "Waktu yang pas buat nyicil hal paling penting hari ini."
            )
        else:
            msg = (
                f"Energi kita hari ini {battery_percent}%! Piko ikut senang lihat ritmemu "
                "lagi enak banget hari ini."
            )
        return msg, sub_tip

    # Kondisi 3: Steady / Normal (Energi 3)
    if water_glasses < 4:
        msg = (
            f"Ritme kita cukup stabil di {battery_percent}%. Cuma air putihnya baru "
            f"{water_glasses} gelas—yuk minum sedikit biar fokus tetap aman!"
        )
    elif sleep_hours < 6.5:
        msg = (
            f"Energi stabil di {battery_percent}% walau tidur cuma {sleep_hours:g} jam. "
            "Lumayan tangguh, tapi malam ini coba tidur lebih awal ya."
        )
    else:
        msg = (
            f"Kondisi kita tenang dan stabil di {battery_percent}%. "
            "Ritme santai kayak gini justru paling enak dijaga konsisten."
        )
    return msg, sub_tip


def get_piko_state(today_log: dict[str, Any] | None) -> dict[str, Any]:
    """
    Menentukan state visual dan dialog Piko berdasarkan check-in hari ini.

    Args:
        today_log: dict entri check-in hari ini, atau None jika belum check-in.

    Returns:
        Dictionary berisi state, label, asset_name, battery_percent, theme, message, sub_tip.
    """
    if not today_log:
        return {
            "state": "waiting",
            "label": "Menunggu Check-in",
            "asset_name": "piko_waiting.png",
            "battery_percent": None,
            "theme": THEMES["waiting"],
            "message": "Hey, gimana kondisimu hari ini? Yuk check-in 30 detik biar kita cek level bateraimu!",
            "sub_tip": "Catat singkat aja—tidur, air, gerak, dan rasamu hari ini.",
        }

    energy = int(today_log.get("energy", 3))
    battery_percent = max(20, min(100, energy * 20))

    if energy >= 4:
        state = "super_charged"
        label = "Super Charged"
        asset_name = "piko_charged.png"
    elif energy == 3:
        state = "steady"
        label = "Steady"
        asset_name = "piko_steady.png"
    else:
        state = "low_battery"
        label = "Low Battery"
        asset_name = "piko_sleepy.png"

    message, sub_tip = _pick_dialog(today_log, battery_percent)

    return {
        "state": state,
        "label": label,
        "asset_name": asset_name,
        "battery_percent": battery_percent,
        "theme": THEMES[state],
        "message": message,
        "sub_tip": sub_tip,
    }
