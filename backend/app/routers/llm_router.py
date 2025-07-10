from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import re
from .llm_models import openai_client, flan_pipeline, embedder
from .. import schemas, models, auth
from ..database import get_db
import numpy as np

router = APIRouter(
    prefix="/ai",
    tags=["AI Models"],
)

def retrieve_disease_info(question: str, db: Session):
    """
    Given a user's question, returns the most relevant disease,
    its description, and relevant suggestions.
    """
    # Fetch all symptoms and their keywords from DB
    symptoms = db.execute(text("SELECT id, name, keywords FROM symptoms")).fetchall()
    # Prepare a dict: {symptom_id: [keyword1, keyword2, ...]}
    symptom_kw_map = {}
    for row in symptoms:
        symptom_id, name, keywords = row
        keyword_list = [kw.strip().lower() for kw in keywords.split(',') if kw.strip()]
        symptom_kw_map[symptom_id] = keyword_list

    # Find matching symptoms in question
    question_lower = question.lower()
    matching_symptom_ids = set()
    for symptom_id, kw_list in symptom_kw_map.items():
        for kw in kw_list:
            # Simple keyword presence check (word boundary so "run" not in "running")
            if re.search(r"\b" + re.escape(kw) + r"\b", question_lower):
                matching_symptom_ids.add(symptom_id)
                break

    if not matching_symptom_ids:
        # Fallback: just return "General Unwell Feeling" if no matches
        disease_row = db.execute(text(
            "SELECT id, name, description FROM diseases WHERE name = 'General Unwell Feeling'"
        )).fetchone()
        suggestions = db.execute(text(
            "SELECT text FROM suggestions WHERE is_general_advice = TRUE"
        )).fetchall()
        return disease_row, [s[0] for s in suggestions]

    # For each matched symptom, vote for linked diseases (sum weights)
    disease_scores = {}
    for symptom_id in matching_symptom_ids:
        links = db.execute(text(
            "SELECT disease_id, weight FROM disease_symptoms WHERE symptom_id = :sid",
            {"sid": symptom_id}
        )).fetchall()
        for disease_id, weight in links:
            disease_scores[disease_id] = disease_scores.get(disease_id, 0) + float(weight)

    if not disease_scores:
        # No linked diseases found
        disease_row = db.execute(text(
            "SELECT id, name, description FROM diseases WHERE name = 'General Unwell Feeling'"
        )).fetchone()
        suggestions = db.execute(text(
            "SELECT text FROM suggestions WHERE is_general_advice = TRUE"
        )).fetchall()
        return disease_row, [s[0] for s in suggestions]

    # Pick the highest scoring disease
    top_disease_id = max(disease_scores, key=lambda k: disease_scores[k])
    disease_row = db.execute(text(
        "SELECT id, name, description FROM diseases WHERE id = :did",
        {"did": top_disease_id}
    )).fetchone()
    # Fetch specific suggestions for this disease + some general advice
    suggestions = db.execute(text(
        "SELECT text FROM suggestions WHERE disease_id = :did OR is_general_advice = TRUE LIMIT 5",
        {"did": top_disease_id}
    )).fetchall()
    return disease_row, [s[0] for s in suggestions]


def find_best_disease_by_embedding(question: str, db: Session, embedder):
    """
    Given a user's question, use embeddings to find the most relevant disease and suggestions.
    """
    # Fetch all diseases from DB
    diseases = db.execute(text("SELECT id, name, description FROM diseases")).fetchall()
    if not diseases:
        return None, []

    # Build disease texts for embedding
    disease_texts = [f"{d[1]}: {d[2]}" for d in diseases]
    disease_ids = [d[0] for d in diseases]

    # Compute embeddings
    disease_vectors = embedder.encode(disease_texts)
    user_vec = embedder.encode([question])[0]

    # Compute cosine similarity
    sims = np.dot(disease_vectors, user_vec) / (np.linalg.norm(disease_vectors, axis=1) * np.linalg.norm(user_vec) + 1e-9)
    best_idx = int(np.argmax(sims))
    best_disease = diseases[best_idx]

    # Fetch suggestions for the best disease
    suggestions = db.execute(
        text("SELECT text FROM suggestions WHERE disease_id = :did OR is_general_advice = TRUE LIMIT 5"),
        {"did": best_disease[0]}
    ).fetchall()

    return best_disease, [s[0] for s in suggestions]


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
        disease_row, suggestions = retrieve_disease_info(request.message, db)
        if disease_row:
            advice = "\n".join(f"- {s}" for s in suggestions[:3]) if suggestions else ""
            flan_prompt = (
                "You are a health assistant. ONLY use the info below.\n"
                f"Disease: {disease_row[1]}\n"
                f"Description: {disease_row[2]}\n"
                f"Advice:\n{advice}\n"
                f"User's symptoms: '{request.message}'\n"
                "Answer in a friendly, simple way using the above information only. If you are unsure, say to see a doctor."
            )
        else:
            general_advice = "\n".join(f"- {s[0]}" for s in db.execute("SELECT text FROM suggestions WHERE is_general_advice=TRUE ORDER BY random() LIMIT 3").fetchall())
            flan_prompt = (
                "You are a health assistant. The user's symptoms did not match a known disease.\n"
                f"General advice:\n{general_advice}\n"
                "Politely recommend to see a doctor if they feel unwell or worried."
            )
        flan_response = flan_pipeline(flan_prompt)[0]['generated_text']
        bot_response_content = flan_response
    elif request.model_choice == "embedding":
        user_text = request.message.lower().strip()
        import re

        # 1. Greeting
        greeting_tmpl = db.execute("SELECT text FROM templates WHERE template_type='greeting' AND is_active=TRUE LIMIT 1").fetchone()
        if re.match(r"^(hi|hello|hey|good morning|good afternoon|good evening)[\s\!\.\?\,]*$", user_text):
            bot_response_content = greeting_tmpl[0] if greeting_tmpl else "Hello! Please describe your symptoms."

        # 2. No health keywords
        elif not any(kw in user_text for kw in [
            "pain", "headache", "fever", "throat", "sick", "symptom", "cold", "cough", "runny", "temperature",
            "nausea", "stomach", "vomit", "ill", "tired", "fatigue", "diarrhea", "rash", "sore", "infection"
        ]):
            bot_response_content = "I'm here to help only with your health or wellness questions. Please describe your symptoms."

        # 3. Try to match a disease
        else:
            disease_row, suggestions = find_best_disease_by_embedding(request.message, db, embedder)
            if disease_row is None:
                # Fallback
                fallback_tmpl = db.execute("SELECT text FROM templates WHERE template_type='fallback' AND is_active=TRUE LIMIT 1").fetchone()
                advice = "\n".join(f"- {s[0]}" for s in db.execute("SELECT text FROM suggestions WHERE is_general_advice=TRUE ORDER BY random() LIMIT 3").fetchall())
                bot_response_content = fallback_tmpl[0].replace("{advice}", advice) if fallback_tmpl else f"General advice:\n{advice}"
            else:
                # Disease template
                tmpl = db.execute("SELECT text FROM templates WHERE template_type='disease' AND disease_id=%s AND is_active=TRUE LIMIT 1", (disease_row[0],)).fetchone()
                if not tmpl:
                    tmpl_text = "Based on your symptoms, the likely cause is {disease_name}: {disease_desc}.\nRecommended steps:\n{advice}"
                else:
                    tmpl_text = tmpl[0]
                tmpl_text = tmpl_text.replace("{disease_name}", disease_row[1]).replace("{disease_desc}", disease_row[2])
                advice = "\n".join(f"- {s}" for s in suggestions[:3])
                tmpl_text = tmpl_text.replace("{advice}", advice)
                bot_response_content = tmpl_text
    else:
        raise HTTPException(status_code=400, detail="Invalid model_choice. Must be 'openai', 'flan-t5', or 'embedding'.")

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
    # Make sure input is not empty
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty.")
    # Compute embedding
    embedding = embedder.encode(request.text)
    # Convert to list for JSON response
    return {"embedding": embedding.tolist()}

@router.get("/chat/history/", response_model=List[schemas.ChatMessageResponse])
async def chat_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    messages = db.query(models.ChatMessage).filter_by(user_id=current_user.id).order_by(models.ChatMessage.timestamp).all()
    return messages