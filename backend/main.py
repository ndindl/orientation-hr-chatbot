from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from retriever import retrieve
from chat import chat as chat_fn

app = FastAPI(title="ABC Widgets HR Chatbot")

# Dev-only: tighten allow_origins to the intranet hostname before production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    language: Literal["en", "es"] = "en"
    history: list[Message] = []


class Citation(BaseModel):
    source_file: str
    page_number: int


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    chunks = retrieve(req.message)
    history = [{"role": m.role, "content": m.content} for m in req.history]
    answer = chat_fn(req.message, chunks, req.language, history)
    citations = [
        Citation(source_file=c["source_file"], page_number=c["page_number"])
        for c in chunks
    ]
    return ChatResponse(answer=answer, citations=citations)
