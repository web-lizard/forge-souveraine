from pathlib import Path
from typing import Optional

from faster_whisper import WhisperModel


INVITE_TRANSCRIPTION_RU = (
    "Это расшифровка русской разговорной речи для короткого видео. "
    "Сохраняй смысл фразы, не заменяй редкие слова похожими бытовыми словами. "
    "Возможные термины: эзотерическом, эзотерический, эзотерика, эзотерические, "
    "символические системы, символическая система, саламандра, саламандру, "
    "магазин, магазинчик, цветы, растения. "
    "Если слышится слово эзотерическом, пиши именно эзотерическом, а не италлическом."
)


def construire_invite_transcription(langue: str | None) -> str | None:
    if not langue or str(langue).lower() in {"auto", "ru", "russian", "rus"}:
        return INVITE_TRANSCRIPTION_RU

    return None

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
        beam_size=7,
        best_of=7,
        patience=1.15,
        temperature=0.0,
        compression_ratio_threshold=2.4,
        log_prob_threshold=-1.0,
        no_speech_threshold=0.55,
        condition_on_previous_text=True,
        initial_prompt=construire_invite_transcription(locals().get('langue')),
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 450, "speech_pad_ms": 250},
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
