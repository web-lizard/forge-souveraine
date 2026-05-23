from pathlib import Path


def nettoyer_texte(texte: str) -> str:
    return " ".join((texte or "").replace("\n", " ").split()).strip()


def horodatage_srt(secondes: float) -> str:
    millisecondes = int(round(secondes * 1000))
    heures, millisecondes = divmod(millisecondes, 3600_000)
    minutes, millisecondes = divmod(millisecondes, 60_000)
    secondes_entieres, millisecondes = divmod(millisecondes, 1000)
    return f"{heures:02}:{minutes:02}:{secondes_entieres:02},{millisecondes:03}"


def horodatage_ass(secondes: float) -> str:
    centiemes = int(round(secondes * 100))
    heures, centiemes = divmod(centiemes, 3600 * 100)
    minutes, centiemes = divmod(centiemes, 60 * 100)
    secondes_entieres, centiemes = divmod(centiemes, 100)
    return f"{heures}:{minutes:02}:{secondes_entieres:02}.{centiemes:02}"


def proteger_ass(texte: str) -> str:
    return (
        nettoyer_texte(texte)
        .replace("\\", "\\\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
    )


def ecrire_srt(segments: list[dict], chemin_sortie: str | Path) -> Path:
    chemin_sortie = Path(chemin_sortie)
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    blocs = []

    for index, segment in enumerate(segments, start=1):
        debut = horodatage_srt(float(segment["debut"]))
        fin = horodatage_srt(float(segment["fin"]))
        texte = nettoyer_texte(str(segment["texte"]))
        blocs.append(f"{index}\n{debut} --> {fin}\n{texte}")

    chemin_sortie.write_text("\n\n".join(blocs) + "\n", encoding="utf-8")
    return chemin_sortie


def ecrire_ass(segments: list[dict], chemin_sortie: str | Path) -> Path:
    chemin_sortie = Path(chemin_sortie)
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    entete = """[Script Info]
Title: Forge Souveraine
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Imperial,Arial,76,&H00FFFFFF,&H000000FF,&H000018D6,&HAA000000,-1,0,0,0,100,100,0,0,1,5,2,2,80,80,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""

    lignes = [entete]

    for segment in segments:
        debut = horodatage_ass(float(segment["debut"]))
        fin = horodatage_ass(float(segment["fin"]))
        texte = proteger_ass(str(segment["texte"]))
        lignes.append(f"Dialogue: 0,{debut},{fin},Imperial,,0,0,0,,{texte}")

    chemin_sortie.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return chemin_sortie
