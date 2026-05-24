import unicodedata
﻿from pathlib import Path
import os
import subprocess
import sys
import json
import shutil
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from noyau.transcription import transcrire_fichier
from noyau.sous_titres import ecrire_ass, ecrire_srt
from noyau.rendu import rendre_video


RACINE = Path(__file__).resolve().parent
DONNEES = RACINE / "donnees"
ENTREES = DONNEES / "entrees"
CONFIGURATION = DONNEES / "configuration.json"


def lire_configuration() -> dict:
    if not CONFIGURATION.exists():
        return {}

    try:
        return json.loads(CONFIGURATION.read_text(encoding="utf-8"))
    except Exception:
        return {}


def ecrire_configuration(configuration: dict) -> None:
    CONFIGURATION.parent.mkdir(parents=True, exist_ok=True)
    CONFIGURATION.write_text(
        json.dumps(configuration, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def obtenir_dossier_sorties() -> Path:
    configuration = lire_configuration()
    valeur = (
        os.environ.get("FORGE_SORTIES_DIR")
        or configuration.get("dossier_sorties")
        or r"D:\ForgeSouveraine\sorties"
    )

    return Path(valeur)

SORTIES = obtenir_dossier_sorties()
TACHES = DONNEES / "taches"

EXTENSIONS_VIDEO = {'.mp4', '.mov', '.mkv', '.webm', '.m4v'}


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
    style: str = "shorts_clean"


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



class DemandeFinaliserSorties(BaseModel):
    sorties: dict = {}
    nom_original: str = ""
    exporter_techniques: bool = False


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



@application.post("/api/taches/{identifiant_tache}/executer")
def executer_tache(identifiant_tache: str) -> dict:
    identifiant_sur = Path(identifiant_tache).stem
    chemin_tache = TACHES / f"{identifiant_sur}.json"

    if not chemin_tache.exists():
        raise HTTPException(status_code=404, detail="Tache introuvable")

    tache = json.loads(chemin_tache.read_text(encoding="utf-8"))
    tache["etat"] = "en_cours"
    tache["etape"] = "transcription"
    tache["mis_a_jour_a"] = datetime.now(timezone.utc).isoformat()
    chemin_tache.write_text(json.dumps(tache, ensure_ascii=False, indent=2), encoding="utf-8")

    chemin_entree = ENTREES / Path(tache["nom_stocke"]).name

    try:
        resultat = transcrire_fichier(
            chemin_entree=chemin_entree,
            langue=tache.get("langue", "auto"),
            modele=tache.get("modele", "base"),
        )

        base_sortie = f"{identifiant_sur}_{chemin_entree.stem}"
        chemin_json = SORTIES / f"{base_sortie}.json"
        chemin_srt = SORTIES / f"{base_sortie}.srt"
        chemin_ass = SORTIES / f"{base_sortie}.ass"

        chemin_json.write_text(
            json.dumps(resultat, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        ecrire_srt(resultat["segments"], chemin_srt, (locals().get('tache') or locals().get('donnees_tache') or locals().get('tache_donnees') or {}).get('style', 'shorts_clean'))
        ecrire_ass(resultat["segments"], chemin_ass, (locals().get('tache') or locals().get('donnees_tache') or locals().get('tache_donnees') or {}).get('style', 'shorts_clean'))

        tache["etat"] = "terminee"
        tache["etape"] = "sorties_pretes"
        tache["langue_detectee"] = resultat.get("langue")
        tache["duree"] = resultat.get("duree")
        tache["segments"] = len(resultat.get("segments", []))
        tache["sorties"] = {
            "json": chemin_json.name,
            "srt": chemin_srt.name,
            "ass": chemin_ass.name,
        }
        tache["mis_a_jour_a"] = datetime.now(timezone.utc).isoformat()

    except Exception as erreur:
        tache["etat"] = "erreur"
        tache["etape"] = "transcription_erreur"
        tache["erreur"] = str(erreur)
        tache["mis_a_jour_a"] = datetime.now(timezone.utc).isoformat()

    chemin_tache.write_text(
        json.dumps(tache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return tache



@application.get("/api/sorties/{nom_fichier}")
def telecharger_sortie(nom_fichier: str) -> FileResponse:
    nom_sur = Path(nom_fichier).name
    chemin_sortie = SORTIES / nom_sur

    if not chemin_sortie.exists():
        raise HTTPException(status_code=404, detail="Sortie introuvable")

    return FileResponse(
        chemin_sortie,
        filename=nom_sur,
    )



@application.post("/api/taches/{identifiant_tache}/rendre")
def rendre_tache(identifiant_tache: str) -> dict:
    identifiant_sur = Path(identifiant_tache).stem
    chemin_tache = TACHES / f"{identifiant_sur}.json"

    if not chemin_tache.exists():
        raise HTTPException(status_code=404, detail="Tache introuvable")

    tache = json.loads(chemin_tache.read_text(encoding="utf-8"))

    nom_stocke = Path(tache.get("nom_stocke", "")).name
    chemin_entree = ENTREES / nom_stocke

    if chemin_entree.suffix.lower() not in EXTENSIONS_VIDEO:
        raise HTTPException(
            status_code=400,
            detail="Le rendu MP4 demande une video en entree",
        )

    sorties = tache.get("sorties") or {}
    nom_ass = sorties.get("ass")

    if not nom_ass:
        raise HTTPException(
            status_code=400,
            detail="Sous-titres ASS absents. Execute la transcription avant le rendu.",
        )

    chemin_ass = SORTIES / Path(nom_ass).name

    if not chemin_ass.exists():
        raise HTTPException(status_code=404, detail="Fichier ASS introuvable")

    base_sortie = f"{identifiant_sur}_{chemin_entree.stem}"
    chemin_mp4 = SORTIES / f"{base_sortie}_sous_titres.mp4"

    tache["etat"] = "en_cours"
    tache["etape"] = "rendu_video"
    tache["mis_a_jour_a"] = datetime.now(timezone.utc).isoformat()
    chemin_tache.write_text(
        json.dumps(tache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    try:
        rendre_video(
            chemin_video=chemin_entree,
            chemin_ass=chemin_ass,
            chemin_sortie=chemin_mp4,
        )

        sorties["mp4"] = chemin_mp4.name
        tache["sorties"] = sorties
        tache["etat"] = "terminee"
        tache["etape"] = "video_prete"
        tache["mis_a_jour_a"] = datetime.now(timezone.utc).isoformat()

    except Exception as erreur:
        tache["etat"] = "erreur"
        tache["etape"] = "rendu_erreur"
        tache["erreur"] = str(erreur)
        tache["mis_a_jour_a"] = datetime.now(timezone.utc).isoformat()

    chemin_tache.write_text(
        json.dumps(tache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return tache




def nettoyer_nom_lisible(valeur: str, defaut: str = "video") -> str:
    brut = Path(str(valeur or "")).stem
    brut = unicodedata.normalize("NFKC", brut)
    brut = re.sub(r"[^\wа-яА-ЯёЁ.-]+", "_", brut, flags=re.UNICODE)
    brut = re.sub(r"_+", "_", brut).strip("._-")

    if not brut:
        brut = defaut

    return brut[:72]


def chemin_unique(dossier: Path, nom: str) -> Path:
    candidat = dossier / nom

    if not candidat.exists():
        return candidat

    base = candidat.stem
    suffixe = candidat.suffix

    for index in range(2, 1000):
        candidat_indexe = dossier / f"{base}_{index}{suffixe}"

        if not candidat_indexe.exists():
            return candidat_indexe

    return dossier / f"{base}_{datetime.now().strftime('%H%M%S')}{suffixe}"


def finaliser_sorties_apres_rendu(sorties: dict, nom_original: str, exporter_techniques: bool = False) -> dict:
    global SORTIES

    SORTIES = obtenir_dossier_sorties()
    SORTIES.mkdir(parents=True, exist_ok=True)

    if not isinstance(sorties, dict):
        return {}

    base = nettoyer_nom_lisible(nom_original)
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_finale = f"{horodatage}_{base}"

    resultat = {}

    for cle, nom in list(sorties.items()):
        if not nom:
            continue

        chemin = SORTIES / str(nom)

        if not chemin.exists() or not chemin.is_file():
            continue

        extension = chemin.suffix.lower()

        if extension == ".mp4" or cle == "mp4":
            destination = chemin_unique(SORTIES, f"{base_finale}.mp4")
            chemin.replace(destination)
            resultat["mp4"] = destination.name
            continue

        if exporter_techniques:
            destination = chemin_unique(SORTIES, f"{base_finale}{extension}")
            chemin.replace(destination)
            resultat[cle] = destination.name
        else:
            try:
                chemin.unlink()
            except Exception:
                pass

    return resultat


@application.get("/api/sorties")
def lister_sorties(inclure_techniques: bool = False) -> dict:
    global SORTIES
    SORTIES = obtenir_dossier_sorties()
    fichiers = []

    SORTIES.mkdir(parents=True, exist_ok=True)

    for chemin in sorted(SORTIES.glob("*"), key=lambda item: item.stat().st_mtime, reverse=True):
        if not chemin.is_file():
            continue

        extension = chemin.suffix.lower().lstrip(".")

        if not inclure_techniques and extension != "mp4":
            continue

        stat = chemin.stat()

        fichiers.append(
            {
                "nom": chemin.name,
                "extension": extension,
                "taille_octets": stat.st_size,
                "modifie_a": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            }
        )

    return {
        "ok": True,
        "dossier": str(SORTIES),
        "fichiers": fichiers[:300],
    }


@application.post("/api/sorties/ouvrir")
def ouvrir_dossier_sorties() -> dict:
    SORTIES.mkdir(parents=True, exist_ok=True)

    if sys.platform.startswith("win"):
        os.startfile(str(SORTIES))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(SORTIES)])
    else:
        subprocess.Popen(["xdg-open", str(SORTIES)])

    return {
        "ok": True,
        "dossier": str(SORTIES),
    }



@application.post("/api/sorties/choisir")
def choisir_dossier_sorties() -> dict:
    global SORTIES

    try:
        import tkinter as tk
        from tkinter import filedialog

        racine = tk.Tk()
        racine.withdraw()
        racine.attributes("-topmost", True)

        dossier = filedialog.askdirectory(
            title="Выбрать папку результатов Forge Souveraine",
            initialdir=str(obtenir_dossier_sorties()),
        )

        racine.destroy()
    except Exception as erreur:
        raise HTTPException(status_code=500, detail=f"Folder picker failed: {erreur}")

    if not dossier:
        return lister_sorties()

    configuration = lire_configuration()
    configuration["dossier_sorties"] = dossier
    ecrire_configuration(configuration)

    SORTIES = Path(dossier)
    SORTIES.mkdir(parents=True, exist_ok=True)

    return lister_sorties()



@application.post("/api/sorties/finaliser")
def finaliser_sorties(demande: DemandeFinaliserSorties) -> dict:
    sorties = finaliser_sorties_apres_rendu(
        sorties=demande.sorties,
        nom_original=demande.nom_original,
        exporter_techniques=demande.exporter_techniques,
    )

    return {
        "ok": True,
        "dossier": str(obtenir_dossier_sorties()),
        "sorties": sorties,
        "fichiers": lister_sorties(inclure_techniques=demande.exporter_techniques)["fichiers"],
    }
