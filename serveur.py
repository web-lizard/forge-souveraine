from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


RACINE = Path(__file__).resolve().parent
DONNEES = RACINE / "donnees"
ENTREES = DONNEES / "entrees"
SORTIES = DONNEES / "sorties"
TACHES = DONNEES / "taches"

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
