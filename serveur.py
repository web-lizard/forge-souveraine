from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware


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
