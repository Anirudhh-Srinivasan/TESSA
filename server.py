import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel, Field

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"  # use whichever model worked for you

hotel_info = open("hotel_info.md").read()
SYSTEM_PROMPT = f"""You are the front desk assistant for the hotel below.
Answer only using this information. If the answer isn't here, say you don't know
and offer to connect them with a human.

{hotel_info}"""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list[Message] = []


class ChatResponse(BaseModel):
    reply: str


FAQS = {
    "checkin": {
        "question": "What are the check-in and check-out times?",
        "answer": "Check-in is from 3:00 PM and check-out is by 11:00 AM.",
    },
    "rooms": {
        "question": "What rooms and prices do you have?",
        "answer": "Standard $150/night (sleeps 2), Deluxe Ocean View $220/night (sleeps 3), Suite $350/night (sleeps 4).",
    },
    "breakfast": {
        "question": "When is breakfast served?",
        "answer": "Breakfast is 7:00 AM to 10:30 AM in the ground floor restaurant. Included with Deluxe and Suite, $15 for Standard.",
    },
    "amenities": {
        "question": "What amenities do you offer?",
        "answer": "Pool (7 AM to 10 PM), 24-hour gym, free wifi in all rooms, and parking at $25/night.",
    },
    "cancellation": {
        "question": "What is the cancellation policy?",
        "answer": "Free cancellation up to 48 hours before check-in.",
    },
}


def ask_llm(messages: list[dict]) -> str:
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [m.model_dump() for m in req.history]
    messages.append({"role": "user", "content": req.message})

    try:
        reply = ask_llm(messages)
    except Exception:
        raise HTTPException(status_code=502, detail="LLM call failed")

    return ChatResponse(reply=reply)


@app.get("/faqs")
def list_faqs():
    return [{"id": k, "question": v["question"]} for k, v in FAQS.items()]


@app.get("/faqs/{faq_id}")
def get_faq(faq_id: str):
    faq = FAQS.get(faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"answer": faq["answer"]}