from pathlib import Path
import json
import shutil
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


RACINE = Path(__file__).resolve().parent
DONNEES = RACINE / "donnees"
ENTREES = DONNEES / "entrees"
SORTIES = DONNEES / "sorties"
TACHES = DONNEES / "taches"

EXTENSIONS_AUTORISEES = {
    ".mp4",
    ".mov",
    ".mkv",
    ".webm",
    ".m4v",
    ".mp3",
    ".wav",
    ".m4a",
}

for dossier in (DONNEES, ENTREES, SORTIES, TACHES):
    dossier.mkdir(parents=True, exist_ok=True)


class DemandeTache(BaseModel):
    nom_stocke: str
    langue: str = "auto"
    modele: str = "base"
    style: str = "imperial"


application = FastAPI(title="Forge Souveraine")

application.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@application.get("/api/sante")
def lire_sante() -> dict:
    return {
        "ok": True,
        "nom": "Forge Souveraine",
        "etat": "pret",
        "dossiers": {
            "entrees": str(ENTREES),
            "sorties": str(SORTIES),
            "taches": str(TACHES),
        },
    }


@application.post("/api/televerser")
async def televerser_video(fichier: UploadFile = File(...)) -> dict:
    nom_original = fichier.filename or "video"
    suffixe = Path(nom_original).suffix.lower()

    if suffixe not in EXTENSIONS_AUTORISEES:
        raise HTTPException(
            status_code=400,
            detail=f"Extension non autorisee: {suffixe}",
        )

    identifiant = uuid.uuid4().hex
    nom_stocke = f"{identifiant}{suffixe}"
    chemin_destination = ENTREES / nom_stocke

    with chemin_destination.open("wb") as sortie:
        shutil.copyfileobj(fichier.file, sortie)

    return {
        "ok": True,
        "identifiant": identifiant,
        "nom_original": nom_original,
        "nom_stocke": nom_stocke,
        "taille_octets": chemin_destination.stat().st_size,
    }



@application.post("/api/taches/creer")
def creer_tache(demande: DemandeTache) -> dict:
    nom_stocke = Path(demande.nom_stocke).name
    chemin_entree = ENTREES / nom_stocke

    if not chemin_entree.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Fichier source introuvable: {nom_stocke}",
        )

    identifiant_tache = uuid.uuid4().hex
    maintenant = datetime.now(timezone.utc).isoformat()

    tache = {
        "ok": True,
        "identifiant_tache": identifiant_tache,
        "etat": "en_attente",
        "etape": "pret_pour_transcription",
        "nom_stocke": nom_stocke,
        "langue": demande.langue,
        "modele": demande.modele,
        "style": demande.style,
        "cree_a": maintenant,
        "mis_a_jour_a": maintenant,
    }

    chemin_tache = TACHES / f"{identifiant_tache}.json"
    chemin_tache.write_text(
        json.dumps(tache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return tache


@application.get("/api/taches/{identifiant_tache}")
def lire_tache(identifiant_tache: str) -> dict:
    identifiant_sur = Path(identifiant_tache).stem
    chemin_tache = TACHES / f"{identifiant_sur}.json"

    if not chemin_tache.exists():
        raise HTTPException(status_code=404, detail="Tache introuvable")

    return json.loads(chemin_tache.read_text(encoding="utf-8"))
