from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import shutil

from fastapi.middleware.cors import CORSMiddleware
from src.rag import generate_answer
from src.vector_store import build_vector_store

app = FastAPI(title="DocSense API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = "data/raw"


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


def clear_previous_uploaded_files():
    """
    Remove old uploaded PDFs only.
    Do NOT delete Chroma DB folder; vector_store will replace the collection safely.
    """
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "DocSense backend is running"
    }


@app.get("/files")
def list_current_files():
    try:
        if not os.path.exists(UPLOAD_DIR):
            return {"files": []}

        files = [
            f for f in os.listdir(UPLOAD_DIR)
            if os.path.isfile(os.path.join(UPLOAD_DIR, f))
        ]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rebuild")
def rebuild_index():
    try:
        build_vector_store()
        return {
            "status": "success",
            "message": "Vector database rebuilt successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask_question(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        answer = generate_answer(request.question, k=request.top_k)
        return {
            "status": "success",
            "question": request.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Clear old uploaded PDFs only
        clear_previous_uploaded_files()

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Rebuild vector store for the new single uploaded file
        build_vector_store()

        return {
            "status": "success",
            "filename": file.filename,
            "message": "File uploaded and vector database rebuilt successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))