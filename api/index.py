# api/index.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from embeddings import search_answers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for testing frontend or Promptfoo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def answer_question(req: Request):
    data = await req.json()
    question = data.get("question", "")
    extra_note = data.get("extra_note", "")
    return JSONResponse(content=search_answers(question, extra_note))
