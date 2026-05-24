from __future__ import annotations

from pathlib import Path
import csv
import json
import re
import unicodedata
from typing import Any


RISQUE_MOTS = {
    "mat": [
        "бляд", "блять", "сука", "хуй", "хуя", "пизд", "еба", "ёба", "ебл", "долбо",
        "нахуй", "похуй",
    ],
    "intime": [
        "секс", "эрот", "интим", "голая", "голый", "возбуд", "трах", "порно",
    ],
    "argent": [
        "деньги", "кредит", "долг", "банк", "зарплата", "займ", "оплата", "штраф",
    ],
    "personnel": [
        "адрес", "телефон", "паспорт", "карта", "номер", "фамилия", "имя", "почта",
    ],
    "conflit": [
        "убить", "ненавижу", "угрож", "драка", "насили", "разъеб", "сломать",
    ],
    "politique_risque": [
        "война", "полит", "государство", "власть", "митинг", "закон", "цензура",
    ],
}


def nettoyer_nom_fichier(valeur: str, defaut: str = "video") -> str:
    brut = Path(str(valeur or "")).stem
    brut = unicodedata.normalize("NFKC", brut)
    brut = re.sub(r"[^\wа-яА-ЯёЁ.-]+", "_", brut, flags=re.UNICODE)
    brut = re.sub(r"_+", "_", brut).strip("._-")

    if not brut:
        brut = defaut

    return brut[:72]


def format_temps(secondes: float) -> str:
    secondes = max(0.0, float(secondes or 0.0))
    total_ms = int(round(secondes * 1000))

    heures = total_ms // 3_600_000
    total_ms %= 3_600_000

    minutes = total_ms // 60_000
    total_ms %= 60_000

    sec = total_ms // 1000
    ms = total_ms % 1000

    if heures:
        return f"{heures:02}:{minutes:02}:{sec:02}.{ms:03}"

    return f"{minutes:02}:{sec:02}.{ms:03}"


def normaliser_texte(texte: str) -> str:
    return re.sub(r"\s+", " ", str(texte or "")).strip()


def trouver_segments(objet: Any) -> list[dict[str, Any]]:
    if isinstance(objet, list):
        candidats = []

        for item in objet:
            if isinstance(item, dict) and ("text" in item or "texte" in item) and ("start" in item or "debut" in item):
                candidats.append(item)

        if candidats:
            return candidats

        for item in objet:
            resultat = trouver_segments(item)
            if resultat:
                return resultat

    if isinstance(objet, dict):
        for cle in ["segments", "items", "transcription", "resultat", "data"]:
            if cle in objet:
                resultat = trouver_segments(objet[cle])
                if resultat:
                    return resultat

        for valeur in objet.values():
            resultat = trouver_segments(valeur)
            if resultat:
                return resultat

    return []


def extraire_segment(segment: dict[str, Any]) -> dict[str, Any]:
    debut = float(segment.get("start", segment.get("debut", 0.0)) or 0.0)
    fin = float(segment.get("end", segment.get("fin", debut)) or debut)
    texte = normaliser_texte(segment.get("text", segment.get("texte", "")))

    return {
        "start": debut,
        "end": max(fin, debut),
        "duration": max(fin - debut, 0.0),
        "text": texte,
        "flags": detecter_risques(texte),
    }


def detecter_risques(texte: str) -> list[str]:
    bas = texte.lower()
    flags = []

    for etiquette, mots in RISQUE_MOTS.items():
        if any(mot in bas for mot in mots):
            flags.append(etiquette)

    return flags


def lire_segments_json(chemin_json: str | Path) -> list[dict[str, Any]]:
    chemin = Path(chemin_json)
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    segments_bruts = trouver_segments(donnees)

    return [
        extrait
        for extrait in (extraire_segment(segment) for segment in segments_bruts)
        if extrait["text"]
    ]


def ecrire_timeline_csv(segments: list[dict[str, Any]], chemin: Path) -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)

    with chemin.open("w", encoding="utf-8-sig", newline="") as fichier:
        writer = csv.DictWriter(
            fichier,
            fieldnames=[
                "start",
                "end",
                "duration",
                "start_seconds",
                "end_seconds",
                "flags",
                "text",
            ],
            delimiter=";",
        )

        writer.writeheader()

        for segment in segments:
            writer.writerow(
                {
                    "start": format_temps(segment["start"]),
                    "end": format_temps(segment["end"]),
                    "duration": round(segment["duration"], 3),
                    "start_seconds": round(segment["start"], 3),
                    "end_seconds": round(segment["end"], 3),
                    "flags": ",".join(segment["flags"]),
                    "text": segment["text"],
                }
            )

    return chemin


def ecrire_transcript_txt(segments: list[dict[str, Any]], chemin: Path) -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    lignes = []

    for segment in segments:
        flags = f" [{', '.join(segment['flags'])}]" if segment["flags"] else ""
        lignes.append(f"[{format_temps(segment['start'])} - {format_temps(segment['end'])}]{flags} {segment['text']}")

    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return chemin


def ecrire_montage_md(segments: list[dict[str, Any]], chemin: Path, titre: str = "Монтажная карта") -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)

    lignes = [
        f"# {titre}",
        "",
        "| Старт | Конец | Длительность | Флаги | Текст |",
        "|---:|---:|---:|---|---|",
    ]

    for segment in segments:
        texte = segment["text"].replace("|", "\\|")
        flags = ", ".join(segment["flags"]) if segment["flags"] else ""
        lignes.append(
            f"| {format_temps(segment['start'])} | {format_temps(segment['end'])} | "
            f"{segment['duration']:.1f} | {flags} | {texte} |"
        )

    lignes.append("")
    chemin.write_text("\n".join(lignes), encoding="utf-8")
    return chemin


def exporter_timeline_depuis_json(
    chemin_json: str | Path,
    dossier_sorties: str | Path,
    nom_original: str = "video",
) -> dict[str, str]:
    dossier = Path(dossier_sorties)
    dossier.mkdir(parents=True, exist_ok=True)

    segments = lire_segments_json(chemin_json)
    base = nettoyer_nom_fichier(nom_original)

    chemins = {
        "transcript_txt": dossier / f"{base}_transcript.txt",
        "timeline_csv": dossier / f"{base}_timeline.csv",
        "montage_md": dossier / f"{base}_montage.md",
    }

    ecrire_transcript_txt(segments, chemins["transcript_txt"])
    ecrire_timeline_csv(segments, chemins["timeline_csv"])
    ecrire_montage_md(segments, chemins["montage_md"], titre=f"Монтажная карта: {base}")

    return {cle: chemin.name for cle, chemin in chemins.items()}
