from pathlib import Path
import subprocess

from imageio_ffmpeg import get_ffmpeg_exe


def rendre_video(
    chemin_video: str | Path,
    chemin_ass: str | Path,
    chemin_sortie: str | Path,
) -> Path:
    chemin_video = Path(chemin_video)
    chemin_ass = Path(chemin_ass)
    chemin_sortie = Path(chemin_sortie)

    if not chemin_video.exists():
        raise FileNotFoundError(f"Video introuvable: {chemin_video}")

    if not chemin_ass.exists():
        raise FileNotFoundError(f"Sous-titres ASS introuvables: {chemin_ass}")

    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg = get_ffmpeg_exe()

    commande = [
        ffmpeg,
        "-y",
        "-i",
        str(chemin_video),
        "-vf",
        f"ass={chemin_ass.name}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
        str(chemin_sortie),
    ]

    resultat = subprocess.run(
        commande,
        cwd=str(chemin_ass.parent),
        capture_output=True,
        text=True,
    )

    if resultat.returncode != 0:
        message = (resultat.stderr or resultat.stdout or "Erreur ffmpeg inconnue").strip()
        raise RuntimeError(message[-4000:])

    return chemin_sortie
