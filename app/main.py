"""
FastAPIアプリ本体。

- GET  /             : アップロード画面
- POST /api/process  : 音声ファイルをアップロード→文字起こし→情報抽出→結果を返す
"""
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.extract import build_karte_draft
from app.transcribe import transcribe_audio

BASE_DIR = Path(__file__).parent

app = FastAPI(title="dental-chart-voice", version="0.1.0")
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR.parent / "static")),
    name="static",
)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".mp4", ".webm", ".ogg"}
MAX_FILE_SIZE_MB = 200


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/process")
async def process_audio(file: UploadFile = File(...)):
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "error": f"対応していないファイル形式です: {suffix}"
            },
        )

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    total_bytes = 0

    with tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False
    ) as tmp:
        tmp_path = tmp.name

        while True:
            chunk = await file.read(1024 * 1024)

            if not chunk:
                break

            total_bytes += len(chunk)

            if total_bytes > max_bytes:
                Path(tmp_path).unlink(missing_ok=True)

                return JSONResponse(
                    status_code=413,
                    content={
                        "error": (
                            f"ファイルサイズが上限の"
                            f"{MAX_FILE_SIZE_MB}MBを超えています。"
                        )
                    },
                )

            tmp.write(chunk)

    try:
        transcript = transcribe_audio(tmp_path)

        if not transcript:
            return JSONResponse(
                status_code=422,
                content={
                    "error": (
                        "音声から文字起こし結果が"
                        "得られませんでした。"
                    )
                },
            )

        karte_draft = build_karte_draft(transcript)

        return JSONResponse(
            content=karte_draft.model_dump(mode="json")
        )

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)},
        )

    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok"}
