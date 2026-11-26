"""
data_manager.py
---------------
Modul manajemen data untuk HeyPiko.
Menangani operasi CRUD (Create, Read, Update, Delete), validasi input,
serta pembuatan dummy data realistis ke file lokal `data/logs.json`.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

# Path default penyimpanan data relatif terhadap file ini
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = BASE_DIR / "data" / "logs.json"

VALID_CAFFEINE_OPTIONS = ("Tidak", "Pagi", "Siang", "Sore-Malam")


def validate_log_entry(entry: dict[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    """
    Memvalidasi dan menormalisasi satu entri check-in harian.

    Returns:
        (is_valid, error_message, cleaned_entry)
    """
    try:
        # 1. Validasi tanggal (format YYYY-MM-DD)
        raw_date = str(entry.get("date", "")).strip()
        datetime.strptime(raw_date, "%Y-%m-%d")

        # 2. Validasi durasi tidur (0 - 12 jam)
        sleep_hours = round(float(entry.get("sleep_hours", 0)), 1)
        if not (0.0 <= sleep_hours <= 12.0):
            return False, "Durasi tidur harus berada di rentang 0 sampai 12 jam.", {}

        # 3. Validasi jam mulai tidur (format HH:MM)
        raw_bedtime = str(entry.get("bedtime", "23:00")).strip()
        datetime.strptime(raw_bedtime, "%H:%M")

        # 4. Validasi jumlah gelas air (0 - 15 gelas)
        water_glasses = int(entry.get("water_glasses", 0))
        if not (0 <= water_glasses <= 15):
            return False, "Jumlah gelas air harus berada di rentang 0 sampai 15 gelas.", {}

        # 5. Validasi olahraga & durasi menit
        exercise = bool(entry.get("exercise", False))
        exercise_minutes = int(entry.get("exercise_minutes", 0)) if exercise else 0
        if not (0 <= exercise_minutes <= 300):
            return False, "Durasi olahraga harus berada di rentang 0 sampai 300 menit.", {}

        # 6. Validasi konsumsi kafein
        caffeine = str(entry.get("caffeine", "Tidak")).strip()
        if caffeine not in VALID_CAFFEINE_OPTIONS:
            return (
                False,
                f"Pilihan kafein tidak valid. Gunakan salah satu dari: {', '.join(VALID_CAFFEINE_OPTIONS)}.",
                {},
            )

        # 7. Validasi energi & fokus (skala 1 - 5)
        energy = int(entry.get("energy", 3))
        if not (1 <= energy <= 5):
            return False, "Level energi harus berada di rentang 1 sampai 5.", {}

        focus = int(entry.get("focus", 3))
        if not (1 <= focus <= 5):
            return False, "Level fokus harus berada di rentang 1 sampai 5.", {}

        # 8. Catatan singkat (opsional)
        note = str(entry.get("note", "")).strip()

        cleaned = {
            "date": raw_date,
            "sleep_hours": sleep_hours,
            "bedtime": raw_bedtime,
            "water_glasses": water_glasses,
            "exercise": exercise,
            "exercise_minutes": exercise_minutes,
            "caffeine": caffeine,
            "energy": energy,
            "focus": focus,
            "note": note,
        }
        return True, "", cleaned

    except (ValueError, TypeError) as exc:
        return False, f"Format data tidak valid: {exc}", {}


def _write_logs(logs: list[dict[str, Any]], data_path: Path = DEFAULT_DATA_PATH) -> None:
    """Menulis list log terurut berdasarkan tanggal ke file JSON."""
    data_path.parent.mkdir(parents=True, exist_ok=True)
    sorted_logs = sorted(logs, key=lambda item: item["date"])
    with data_path.open("w", encoding="utf-8") as f:
        json.dump(sorted_logs, f, indent=2, ensure_ascii=False)


def load_logs(data_path: Path = DEFAULT_DATA_PATH) -> list[dict[str, Any]]:
    """
    Membaca seluruh riwayat check-in dari file JSON.
    Mengembalikan list kosong jika file belum ada atau rusak.
    """
    if not data_path.exists():
        return []
    try:
        with data_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return sorted(data, key=lambda item: item.get("date", ""))
    except (json.JSONDecodeError, OSError):
        return []


def get_log_by_date(
    target_date: str, data_path: Path = DEFAULT_DATA_PATH
) -> dict[str, Any] | None:
    """Mengambil satu entri log berdasarkan tanggal (YYYY-MM-DD), atau None jika tidak ada."""
    for log in load_logs(data_path):
        if log.get("date") == target_date:
            return log
    return None


def save_log(
    entry: dict[str, Any], data_path: Path = DEFAULT_DATA_PATH
) -> tuple[bool, str]:
    """
    Menyimpan entri check-in baru ke file JSON.
    Jika tanggal sudah ada, data tanggal tersebut otomatis diperbarui (mencegah duplikasi).
    """
    is_valid, error_msg, cleaned = validate_log_entry(entry)
    if not is_valid:
        return False, error_msg

    logs = load_logs(data_path)
    updated = False

    for i, existing in enumerate(logs):
        if existing.get("date") == cleaned["date"]:
            logs[i] = cleaned
            updated = True
            break

    if not updated:
        logs.append(cleaned)

    _write_logs(logs, data_path)
    action_msg = "Data hari tersebut berhasil diperbarui!" if updated else "Check-in berhasil disimpan!"
    return True, action_msg


def update_log(
    target_date: str, updated_entry: dict[str, Any], data_path: Path = DEFAULT_DATA_PATH
) -> tuple[bool, str]:
    """Memperbarui entri log yang sudah ada pada tanggal tertentu."""
    entry_copy = dict(updated_entry)
    entry_copy["date"] = target_date

    is_valid, error_msg, cleaned = validate_log_entry(entry_copy)
    if not is_valid:
        return False, error_msg

    logs = load_logs(data_path)
    for i, existing in enumerate(logs):
        if existing.get("date") == target_date:
            logs[i] = cleaned
            _write_logs(logs, data_path)
            return True, f"Data tanggal {target_date} berhasil diperbarui!"

    return False, f"Data untuk tanggal {target_date} tidak ditemukan."


def delete_log(target_date: str, data_path: Path = DEFAULT_DATA_PATH) -> tuple[bool, str]:
    """Menghapus entri log berdasarkan tanggal (YYYY-MM-DD)."""
    logs = load_logs(data_path)
    new_logs = [log for log in logs if log.get("date") != target_date]

    if len(new_logs) == len(logs):
        return False, f"Data untuk tanggal {target_date} tidak ditemukan."

    _write_logs(new_logs, data_path)
    return True, f"Data tanggal {target_date} berhasil dihapus."


def generate_dummy_data(
    reference_date: date | None = None,
    data_path: Path = DEFAULT_DATA_PATH,
    overwrite: bool = False,
) -> list[dict[str, Any]]:
    """
    Membuat 10 hari data contoh yang realistis (berakhir kemarin)
    agar grafik, analisis pola, dan flexible streak langsung terlihat saat demo,
    sementara hari ini tetap terbuka untuk dicoba check-in langsung.
    """
    if data_path.exists() and not overwrite and load_logs(data_path):
        return load_logs(data_path)

    today = reference_date or date.today()

    # Offset hari mundur dari hari ini (sengaja ada 1-2 hari bolong agar Flexible Streak realistis)
    templates = [
        (-12, 7.5, "22:45", 8, True, 35, "Pagi", 5, 4, "Tidur nyenyak, pagi langsung seger."),
        (-11, 6.0, "00:30", 5, False, 0, "Siang", 3, 3, "Nugas sampai larut, siang agak berat."),
        (-10, 5.5, "01:15", 4, False, 0, "Sore-Malam", 2, 2, "Ngopi sore bikin susah tidur malamnya."),
        (-9, 7.0, "23:10", 7, True, 25, "Pagi", 4, 4, "Jalan cepat pagi, fokus kuliah aman."),
        (-7, 8.0, "22:30", 8, True, 40, "Tidak", 5, 5, "Hari paling produktif minggu lalu!"),
        (-6, 6.5, "23:45", 6, False, 0, "Pagi", 3, 3, "Lumayan stabil meski gak sempat olahraga."),
        (-5, 5.0, "01:30", 4, False, 0, "Sore-Malam", 2, 2, "Brain fog di kelas siang, kurang tidur banget."),
        (-4, 7.5, "23:00", 7, True, 30, "Pagi", 4, 5, "Tidur cukup + stretching pagi kerasa banget bedanya."),
        (-2, 7.0, "23:20", 6, True, 20, "Pagi", 4, 4, "Habis lari santai, siang gak ngantuk."),
        (-1, 6.0, "00:20", 5, False, 0, "Siang", 3, 3, "Agak begadang beresin slide presentasi."),
    ]

    dummy_logs: list[dict[str, Any]] = []
    for offset, sleep, bedtime, water, ex, ex_min, caff, energy, focus, note in templates:
        log_date = (today + timedelta(days=offset)).strftime("%Y-%m-%d")
        dummy_logs.append(
            {
                "date": log_date,
                "sleep_hours": sleep,
                "bedtime": bedtime,
                "water_glasses": water,
                "exercise": ex,
                "exercise_minutes": ex_min,
                "caffeine": caff,
                "energy": energy,
                "focus": focus,
                "note": note,
            }
        )

    _write_logs(dummy_logs, data_path)
    return dummy_logs


def ensure_data_initialized(data_path: Path = DEFAULT_DATA_PATH) -> list[dict[str, Any]]:
    """Memastikan file data tersedia; jika belum ada, isi dengan dummy data."""
    logs = load_logs(data_path)
    if not logs:
        return generate_dummy_data(data_path=data_path)
    return logs
