from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from openai import OpenAI
import httpx
from typing import List, Dict, Any

from .. import schemas, models, auth
from ..database import get_db

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
import numpy as np

load_dotenv()

router = APIRouter(
    prefix="/ai",
    tags=["AI Models"],
)

# --- OpenAI Initialization (unchanged) ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not found. OpenAI functionality will be disabled.")
    openai_client = None
else:
    custom_http_client = httpx.Client(proxies={})
    openai_client = OpenAI(api_key=openai_api_key, http_client=custom_http_client)

# --- FLAN-T5-small setup (loads ONCE at container startup) ---
flan_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
flan_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
flan_pipeline = pipeline("text2text-generation", model=flan_model, tokenizer=flan_tokenizer, max_new_tokens=100)

embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Example knowledge base (replace with DB rows later!)
knowledge_base = [
    "Headaches can be caused by dehydration, stress, or illness.",
    "A sore throat may be a symptom of a cold, flu, or strep throat.",
    "If you have a fever over 102°F, seek medical advice.",
    "Rest and hydration are important when you feel unwell."
]
kb_vectors = embedder.encode(knowledge_base)

@router.post("/chat/", response_model=schemas.ChatMessageResponse)
async def chat_with_llm(
    request: schemas.ChatRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_user_message = models.ChatMessage(
        user_id=current_user.id,
        role="user",
        content=request.message,
        extracted_symptoms={},
        recommendations={}
    )
    db.add(db_user_message)
    db.commit()
    db.refresh(db_user_message)

    bot_response_content = ""
    extracted_symptoms: Dict[str, Any] = {}
    recommendations: Dict[str, Any] = {}

    if request.model_choice == "openai":
        if not openai_client:
            raise HTTPException(status_code=503, detail="OpenAI API not configured (OPENAI_API_KEY missing).")
        try:
            chat_completion = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": request.message}]
            )
            bot_response_content = chat_completion.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    elif request.model_choice == "flan-t5":
        # Find the most relevant knowledge base entry
        q_vector = embedder.encode([request.message])
        scores = np.inner(q_vector, kb_vectors)
        best_index = np.argmax(scores)
        context = knowledge_base[best_index]
        # Prompt for the generator
        prompt = f"Answer the question using this information:\n{context}\nQuestion: {request.message}"
        response = flan_pipeline(prompt)[0]['generated_text']
        bot_response_content = response.strip()
    else:
        raise HTTPException(status_code=400, detail="Invalid model_choice. Must be 'openai' or 'flan-t5'.")

    db_bot_message = models.ChatMessage(
        user_id=current_user.id,
        role="assistant",
        content=bot_response_content,
        extracted_symptoms=extracted_symptoms,
        recommendations=recommendations
    )
    db.add(db_bot_message)
    db.commit()
    db.refresh(db_bot_message)

    return db_bot_message

# --- Embedding Endpoint (leave as is for now, we’ll wire up MiniLM later) ---
@router.post("/embed/", response_model=schemas.EmbeddingResponse)
async def get_embedding(
    request: schemas.EmbedRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    # Placeholder for now
    return {"embedding": []}

@router.get("/chat/history/", response_model=List[schemas.ChatMessageResponse])
async def chat_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    messages = db.query(models.ChatMessage).filter_by(user_id=current_user.id).order_by(models.ChatMessage.timestamp).all()
    return messages