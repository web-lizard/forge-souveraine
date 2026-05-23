# Forge Souveraine

Local subtitle generator and renderer for Shorts videos.

## Idea

Forge Souveraine is a local-first tool for turning short videos into styled subtitle assets:

- upload video locally
- transcribe audio with faster-whisper
- export SRT
- export ASS for styled captions
- prepare the pipeline for final MP4 rendering with burned-in subtitles

## Local launch

Run:

```powershell
.\start_forge_souveraine.bat
```

Then open:

```text
http://127.0.0.1:8787
```

## Roadmap

- video upload
- local transcription
- SRT export
- ASS export
- style presets
- MP4 render with ffmpeg
- batch processing
- desktop wrapper
- PyInstaller build
