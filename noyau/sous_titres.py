from __future__ import annotations

from pathlib import Path
import math
import re
from typing import Any, Iterable


STYLE_PRESETS = {
    "shorts_clean": {
        "font": "Arial",
        "font_size": 70,
        "primary": "&H00FFFFFF",
        "outline": "&H00000000",
        "shadow": "&HAA000000",
        "outline_size": 4,
        "shadow_size": 1,
        "margin_v": 250,
        "words_per_caption": 6,
        "words_per_line": 3,
    },
    "shorts_gold": {
        "font": "Arial",
        "font_size": 70,
        "primary": "&H0018B2D6",
        "outline": "&H00000000",
        "shadow": "&HAA000000",
        "outline_size": 4,
        "shadow_size": 1,
        "margin_v": 250,
        "words_per_caption": 6,
        "words_per_line": 3,
    },
    "shorts_big": {
        "font": "Arial",
        "font_size": 82,
        "primary": "&H00FFFFFF",
        "outline": "&H00000000",
        "shadow": "&HAA000000",
        "outline_size": 5,
        "shadow_size": 1,
        "margin_v": 235,
        "words_per_caption": 5,
        "words_per_line": 3,
    },
    "shorts_red": {
        "font": "Arial",
        "font_size": 68,
        "primary": "&H002222FF",
        "outline": "&H00FFFFFF",
        "shadow": "&HAA000000",
        "outline_size": 3,
        "shadow_size": 1,
        "margin_v": 245,
        "words_per_caption": 5,
        "words_per_line": 3,
    },
    "imperial": {
        "font": "Arial",
        "font_size": 70,
        "primary": "&H0018B2D6",
        "outline": "&H00000000",
        "shadow": "&HAA000000",
        "outline_size": 4,
        "shadow_size": 1,
        "margin_v": 250,
        "words_per_caption": 6,
        "words_per_line": 3,
    },
}


def _valeur(segment: Any, nom: str, defaut: Any = None) -> Any:
    if isinstance(segment, dict):
        return segment.get(nom, defaut)

    return getattr(segment, nom, defaut)


def _nettoyer_texte(texte: str) -> str:
    texte = re.sub(r"\s+", " ", str(texte or "")).strip()
    return texte


def _srt_temps(secondes: float) -> str:
    secondes = max(0.0, float(secondes or 0.0))
    millisecondes_total = int(round(secondes * 1000))
    heures = millisecondes_total // 3_600_000
    millisecondes_total %= 3_600_000
    minutes = millisecondes_total // 60_000
    millisecondes_total %= 60_000
    secondes_entieres = millisecondes_total // 1000
    millisecondes = millisecondes_total % 1000

    return f"{heures:02}:{minutes:02}:{secondes_entieres:02},{millisecondes:03}"


def _ass_temps(secondes: float) -> str:
    secondes = max(0.0, float(secondes or 0.0))
    centisecondes_total = int(round(secondes * 100))
    heures = centisecondes_total // 360_000
    centisecondes_total %= 360_000
    minutes = centisecondes_total // 6_000
    centisecondes_total %= 6_000
    secondes_entieres = centisecondes_total // 100
    centisecondes = centisecondes_total % 100

    return f"{heures:d}:{minutes:02}:{secondes_entieres:02}.{centisecondes:02}"


def _echapper_ass(texte: str) -> str:
    return (
        texte.replace("\\", "\\\\")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def _lignes_courtes(texte: str, mots_par_ligne: int = 3) -> str:
    mots = _nettoyer_texte(texte).split()

    if not mots:
        return ""

    if len(mots) <= mots_par_ligne:
        return " ".join(mots)

    milieu = math.ceil(len(mots) / 2)

    if len(mots) <= mots_par_ligne * 2:
        return " ".join(mots[:milieu]) + "\n" + " ".join(mots[milieu:])

    premiere = " ".join(mots[:mots_par_ligne])
    seconde = " ".join(mots[mots_par_ligne:mots_par_ligne * 2])

    return premiere + "\n" + seconde


def _fragmenter_segment(segment: Any, mots_max: int = 6) -> list[dict[str, Any]]:
    debut = float(_valeur(segment, "start", _valeur(segment, "debut", 0.0)) or 0.0)
    fin = float(_valeur(segment, "end", _valeur(segment, "fin", debut + 1.0)) or debut + 1.0)
    texte = _nettoyer_texte(_valeur(segment, "text", _valeur(segment, "texte", "")))

    if not texte:
        return []

    mots = texte.split()

    if len(mots) <= mots_max:
        return [{"start": debut, "end": max(fin, debut + 0.55), "text": texte}]

    duree = max(fin - debut, 0.9)
    morceaux = [" ".join(mots[index:index + mots_max]) for index in range(0, len(mots), mots_max)]
    total_mots = max(len(mots), 1)
    curseur = debut
    resultat = []

    for index, morceau in enumerate(morceaux):
        nombre_mots = len(morceau.split())
        if index == len(morceaux) - 1:
            fin_morceau = fin
        else:
            fin_morceau = curseur + duree * (nombre_mots / total_mots)

        fin_morceau = max(fin_morceau, curseur + 0.55)

        resultat.append(
            {
                "start": curseur,
                "end": fin_morceau,
                "text": morceau,
            }
        )

        curseur = fin_morceau

    return resultat


def _segments_affichage(segments: Iterable[Any], style: str = "shorts_clean") -> list[dict[str, Any]]:
    preset = STYLE_PRESETS.get(style, STYLE_PRESETS["shorts_clean"])
    mots_max = int(preset.get("words_per_caption", 6))
    resultat = []

    for segment in segments:
        resultat.extend(_fragmenter_segment(segment, mots_max=mots_max))

    return resultat


def ecrire_srt(segments: Iterable[Any], chemin_sortie: str | Path, style: str = "shorts_clean") -> Path:
    chemin = Path(chemin_sortie)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    lignes = []

    for index, segment in enumerate(_segments_affichage(segments, style=style), start=1):
        texte = _lignes_courtes(segment["text"], mots_par_ligne=4)
        lignes.append(str(index))
        lignes.append(f"{_srt_temps(segment['start'])} --> {_srt_temps(segment['end'])}")
        lignes.append(texte)
        lignes.append("")

    chemin.write_text("\n".join(lignes), encoding="utf-8")
    return chemin


def ecrire_ass(segments: Iterable[Any], chemin_sortie: str | Path, style: str = "shorts_clean") -> Path:
    chemin = Path(chemin_sortie)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    preset = STYLE_PRESETS.get(style, STYLE_PRESETS["shorts_clean"])
    mots_par_ligne = int(preset.get("words_per_line", 3))

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2
Collisions: Normal

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Shorts,{preset["font"]},{preset["font_size"]},{preset["primary"]},&H00FFFFFF,{preset["outline"]},{preset["shadow"]},-1,0,0,0,100,100,0,0,1,{preset["outline_size"]},{preset["shadow_size"]},2,70,70,{preset["margin_v"]},1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""

    lignes = [header.rstrip()]

    for segment in _segments_affichage(segments, style=style):
        texte = _lignes_courtes(segment["text"], mots_par_ligne=mots_par_ligne)
        texte = _echapper_ass(texte).replace("\n", r"\N")
        lignes.append(
            f"Dialogue: 0,{_ass_temps(segment['start'])},{_ass_temps(segment['end'])},Shorts,,0,0,0,,{texte}"
        )

    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return chemin


# Compatibility aliases for older imports.
def generer_srt(*args: Any, **kwargs: Any) -> Path:
    return ecrire_srt(*args, **kwargs)


def generer_ass(*args: Any, **kwargs: Any) -> Path:
    return ecrire_ass(*args, **kwargs)


def sauvegarder_srt(*args: Any, **kwargs: Any) -> Path:
    return ecrire_srt(*args, **kwargs)


def sauvegarder_ass(*args: Any, **kwargs: Any) -> Path:
    return ecrire_ass(*args, **kwargs)


def creer_srt(*args: Any, **kwargs: Any) -> Path:
    return ecrire_srt(*args, **kwargs)


def creer_ass(*args: Any, **kwargs: Any) -> Path:
    return ecrire_ass(*args, **kwargs)
