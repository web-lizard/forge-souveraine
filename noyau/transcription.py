from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel


CACHE_MODELES = {}


def charger_modele(nom_modele: str = "base") -> WhisperModel:
    nom_modele = (nom_modele or "base").strip().lower()

    if nom_modele not in CACHE_MODELES:
        CACHE_MODELES[nom_modele] = WhisperModel(
            nom_modele,
            device="cpu",
            compute_type="int8",
        )

    return CACHE_MODELES[nom_modele]


def transcrire_fichier(
    chemin_entree: str | Path,
    langue: Optional[str] = "auto",
    modele: str = "base",
) -> dict:
    chemin_entree = Path(chemin_entree)

    if not chemin_entree.exists():
        raise FileNotFoundError(f"Fichier introuvable: {chemin_entree}")

    langue_preparee = None
    if langue and langue.lower() != "auto":
        langue_preparee = langue.lower()

    moteur = charger_modele(modele)

    segments_bruts, info = moteur.transcribe(
        str(chemin_entree),
        language=langue_preparee,
        vad_filter=True,
        beam_size=5,
    )

    segments = []

    for segment in segments_bruts:
        texte = (segment.text or "").strip()
        if not texte:
            continue

        segments.append(
            {
                "debut": float(segment.start),
                "fin": float(segment.end),
                "texte": texte,
            }
        )

    return {
        "langue": getattr(info, "language", None),
        "duree": float(getattr(info, "duration", 0.0) or 0.0),
        "segments": segments,
    }
