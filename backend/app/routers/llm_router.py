from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from sqlalchemy import text 
import re
from .llm_models import openai_client, flan_pipeline, embedder
from .. import schemas, models, auth
from ..database import get_db
from .llm_models import get_doctor_response
import numpy as np

router = APIRouter(
    prefix="/ai",
    tags=["AI Models"],
)

def retrieve_disease_info(question: str, db: Session):
    # Debug
    print("DEBUG: Looking up disease info for question:", question)

    # Fetch all symptoms and their keywords from DB
    symptoms = db.execute(text("SELECT id, name, keywords FROM symptoms")).fetchall()
    print("DEBUG: Retrieved symptoms from DB:", symptoms)

    # Prepare a dict: {symptom_id: [keyword1, keyword2, ...]}
    symptom_kw_map = {}
    for row in symptoms:
        symptom_id, name, keywords = row
        keyword_list = [kw.strip().lower() for kw in keywords.split(',') if kw.strip()]
        # Also add the symptom name itself as a keyword
        keyword_list.append(name.lower())
        symptom_kw_map[symptom_id] = keyword_list

    # Find matching symptoms in question
    question_lower = question.lower()
    matching_symptom_ids = set()
    
    print("DEBUG: Question in lowercase:", question_lower)
    
    for symptom_id, kw_list in symptom_kw_map.items():
        for kw in kw_list:
            # Use word boundary matching to avoid partial matches
            if re.search(r'\b' + re.escape(kw) + r'\b', question_lower):
                matching_symptom_ids.add(symptom_id)
                print(f"DEBUG: Matched keyword '{kw}' for symptom_id {symptom_id}")
                break

    print("DEBUG: Matching symptom IDs:", matching_symptom_ids)

    if not matching_symptom_ids:
        print("DEBUG: No symptoms matched, using fallback")
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
        stmt = text("SELECT disease_id, weight FROM disease_symptoms WHERE symptom_id = :sid")
        links = db.execute(stmt, {"sid": symptom_id}).fetchall()
        print(f"DEBUG: Disease links for symptom {symptom_id}:", links)
        for disease_id, weight in links:
            disease_scores[disease_id] = disease_scores.get(disease_id, 0) + float(weight)

    print("DEBUG: Disease scores:", disease_scores)

    if not disease_scores:
        print("DEBUG: No linked diseases found, using fallback")
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
    print(f"DEBUG: Top disease ID: {top_disease_id} with score: {disease_scores[top_disease_id]}")
    
    disease_row = db.execute(
        text("SELECT id, name, description FROM diseases WHERE id = :did"),
        {"did": top_disease_id}
    ).fetchone()
    
    # Fetch specific suggestions for this disease + some general advice
    suggestions = db.execute(
        text("SELECT text FROM suggestions WHERE disease_id = :did OR is_general_advice = TRUE LIMIT 5"),
        {"did": top_disease_id}
    ).fetchall()
    
    print(f"DEBUG: Selected disease: {disease_row}")
    print(f"DEBUG: Found suggestions: {[s[0] for s in suggestions]}")
    
    return disease_row, [s[0] for s in suggestions]


def find_best_disease_by_embedding(question: str, db: Session, embedder):
    """
    Given a user's question, use embeddings to find the most relevant disease and suggestions.
    """
    try:
        print(f"DEBUG: Embedding search for question: {question}")
        
        # Fetch all diseases from DB
        diseases = db.execute(text("SELECT id, name, description FROM diseases")).fetchall()
        if not diseases:
            print("DEBUG: No diseases found in database")
            return None, []

        print(f"DEBUG: Found {len(diseases)} diseases in database")

        # Build disease texts for embedding
        disease_texts = [f"{d[1]}: {d[2]}" for d in diseases]
        disease_ids = [d[0] for d in diseases]

        # Compute embeddings
        print("DEBUG: Computing embeddings...")
        disease_vectors = embedder.encode(disease_texts)
        user_vec = embedder.encode([question])[0]
        print(f"DEBUG: Embeddings computed. Disease vectors shape: {disease_vectors.shape}, User vector shape: {user_vec.shape}")

        # Compute cosine similarity
        sims = np.dot(disease_vectors, user_vec) / (np.linalg.norm(disease_vectors, axis=1) * np.linalg.norm(user_vec) + 1e-9)
        best_idx = int(np.argmax(sims))
        best_disease = diseases[best_idx]
        
        print(f"DEBUG: Best disease match: {best_disease[1]} with similarity: {sims[best_idx]:.3f}")

        # Fetch suggestions for the best disease
        suggestions = db.execute(
            text("SELECT text FROM suggestions WHERE disease_id = :did OR is_general_advice = TRUE LIMIT 5"),
            {"did": best_disease[0]}
        ).fetchall()

        print(f"DEBUG: Found {len(suggestions)} suggestions for disease {best_disease[1]}")

        return best_disease, [s[0] for s in suggestions]
        
    except Exception as e:
        print(f"DEBUG: Error in find_best_disease_by_embedding: {e}")
        import traceback
        traceback.print_exc()
        return None, []


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
            chat_history = db.query(models.ChatMessage)\
                .filter_by(user_id=current_user.id)\
                .order_by(models.ChatMessage.timestamp).all()
            history_as_list = [{"role": m.role, "content": m.content} for m in chat_history[-5:]]  # last 5 messages

            bot_response_content = get_doctor_response(request.message, chat_history=history_as_list)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    elif request.model_choice == "flan-t5":
        user_text = request.message.lower().strip()

        # -- FOLLOW-UP HANDLER: If user says "yes" after being offered advice, show tips for last disease --
        last_bot_message = db.query(models.ChatMessage).filter_by(
            user_id=current_user.id, role="assistant"
        ).order_by(models.ChatMessage.timestamp.desc()).first()

        yes_triggers = ["yes", "sure", "okay", "please", "go ahead", "yep", "yeah"]
        if user_text.strip().lower() in yes_triggers and last_bot_message and (
            "want to hear what you can do next" in last_bot_message.content.lower() or
            "would you like some advice" in last_bot_message.content.lower()
        ):
            # Try to extract the disease name from last_bot_message
            import re
            disease_match = re.search(r"(?:like|have|is|consider\.|sometimes mean)\s+([A-Za-z\s\(\)\'\-]+)\.", last_bot_message.content)
            if disease_match:
                disease_name = disease_match.group(1).strip()
                # Fetch disease info
                disease_row = db.execute(
                    text("SELECT id, name, description FROM diseases WHERE LOWER(name) LIKE :dname"),
                    {"dname": f"%{disease_name.lower()}%"}
                ).fetchone()
                if disease_row:
                    # Fetch suggestions for the disease
                    suggestions = db.execute(
                        text("SELECT text FROM suggestions WHERE disease_id = :did OR is_general_advice = TRUE LIMIT 5"),
                        {"did": disease_row[0]}
                    ).fetchall()
                    # Filter suggestions
                    specific_suggestions = [
                        s[0] for s in suggestions
                        if not s[0].lower().startswith("please consult")
                        and not s[0].lower().startswith("it's always best")
                        and not s[0].lower().startswith("stay hydrated")
                        and len(s[0]) > 20
                    ]
                    advice = "\n".join(f"- {s}" for s in (specific_suggestions[:3] if specific_suggestions else [s[0] for s in suggestions[:3]]))
                    bot_response_content = f"Here are a few things you can try:\n{advice}"
                    db_bot_message = models.ChatMessage(
                        role="assistant",
                        content=bot_response_content,
                        user_id=current_user.id,
                    )
                    db.add(db_bot_message)
                    db.commit()
                    db.refresh(db_bot_message)
                    return db_bot_message
            # If disease not found, fallback
            bot_response_content = "Sorry, I couldn't find more details. Could you please rephrase your symptoms?"
            db_bot_message = models.ChatMessage(
                role="assistant",
                content=bot_response_content,
                user_id=current_user.id,
            )
            db.add(db_bot_message)
            db.commit()
            db.refresh(db_bot_message)
            return db_bot_message
        
        # Handle greetings
        if any(greet in user_text for greet in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            bot_response_content = "Hello! I'm your health assistant. How can I help you today?"
        else:
            # Get disease and suggestions from database
            disease_row, suggestions = retrieve_disease_info(request.message, db)
            
            print("DEBUG: disease_row =", disease_row)
            print("DEBUG: suggestions =", suggestions)
            
            if disease_row and suggestions:
                disease_name = disease_row[1]
                disease_desc = disease_row[2]
                
                # Filter out generic "consult doctor" suggestions
                specific_suggestions = [
                    s for s in suggestions 
                    if not s.lower().startswith("please consult") and 
                       not s.lower().startswith("it's always best") and
                       not s.lower().startswith("stay hydrated") and
                       len(s) > 20  # Avoid very short generic responses
                ]
                
                # If we have specific suggestions, use them
                if specific_suggestions:
                    # Take up to 2 specific suggestions
                    selected_suggestions = specific_suggestions[:2]
                    
                    # Create a natural response
                    if len(selected_suggestions) == 1:
                        bot_response_content = f"Based on your symptoms, you might be experiencing {disease_name.lower()}. {selected_suggestions[0]}"
                    else:
                        suggestions_text = f"{selected_suggestions[0]} Additionally, {selected_suggestions[1].lower()}"
                        bot_response_content = f"Based on your symptoms, you might be experiencing {disease_name.lower()}. {suggestions_text}"
                
                # If no specific suggestions, create a helpful response
                else:
                    # Get some general advice that's not too generic
                    general_advice = db.execute(text(
                        "SELECT text FROM suggestions WHERE is_general_advice=TRUE AND text NOT LIKE '%consult%' AND text NOT LIKE '%doctor%' ORDER BY random() LIMIT 1"
                    )).fetchone()
                    
                    if general_advice:
                        bot_response_content = f"Based on your symptoms, you might be experiencing {disease_name.lower()}. {disease_desc} {general_advice[0]}"
                    else:
                        bot_response_content = f"Based on your symptoms, you might be experiencing {disease_name.lower()}. {disease_desc} Remember to get plenty of rest and stay hydrated."
            
            # If no disease matched, provide helpful general advice
            else:
                # Get specific general advice
                general_advice = db.execute(text(
                    "SELECT text FROM suggestions WHERE is_general_advice=TRUE AND text NOT LIKE '%consult%' AND text NOT LIKE '%doctor%' ORDER BY random() LIMIT 2"
                )).fetchall()
                
                if general_advice:
                    if len(general_advice) == 1:
                        bot_response_content = f"I understand you're not feeling well. {general_advice[0][0]}"
                    else:
                        bot_response_content = f"I understand you're not feeling well. {general_advice[0][0]} Also, {general_advice[1][0].lower()}"
                else:
                    bot_response_content = "I understand you're not feeling well. Make sure to get plenty of rest, stay hydrated, and consider consulting a healthcare provider if your symptoms persist or worsen."
    elif request.model_choice == "embedding":
        import traceback
        try:
            user_text = request.message.lower().strip()
            import re

            # 1. Greeting
            try:
                greeting_tmpl = db.execute(text("SELECT text FROM templates WHERE template_type='greeting' AND is_active=TRUE LIMIT 1")).fetchone()
                if re.match(r"^(hi|hello|hey|good morning|good afternoon|good evening)[\s\!\.\?\,]*$", user_text):
                    bot_response_content = greeting_tmpl[0] if greeting_tmpl else "Hello! I'm your health assistant. How can I help you today?"
                    # Early return for greetings
                    db_bot_message = models.ChatMessage(
                        role="assistant",
                        content=bot_response_content,
                        user_id=current_user.id,
                    )
                    db.add(db_bot_message)
                    db.commit()
                    db.refresh(db_bot_message)
                    return db_bot_message
            except Exception as e:
                print(f"DEBUG: Error with greeting template: {e}")
                if re.match(r"^(hi|hello|hey|good morning|good afternoon|good evening)[\s\!\.\?\,]*$", user_text):
                    bot_response_content = "Hello! I'm your health assistant. How can I help you today?"
                    # Early return for greetings
                    db_bot_message = models.ChatMessage(
                        role="assistant",
                        content=bot_response_content,
                        user_id=current_user.id,
                    )
                    db.add(db_bot_message)
                    db.commit()
                    db.refresh(db_bot_message)
                    return db_bot_message

            # 2. No health keywords
            if not any(kw in user_text for kw in [
                "pain", "headache", "fever", "throat", "sick", "symptom", "cold", "cough", "runny", "temperature",
                "nausea", "stomach", "vomit", "ill", "tired", "fatigue", "diarrhea", "rash", "sore", "infection"
            ]):
                bot_response_content = "I'm here to help only with your health or wellness questions. Please describe your symptoms."
                # Early return for non-health messages
                db_bot_message = models.ChatMessage(
                    role="assistant",
                    content=bot_response_content,
                    user_id=current_user.id,
                )
                db.add(db_bot_message)
                db.commit()
                db.refresh(db_bot_message)
                return db_bot_message

            # 3. Try to match a disease
            try:
                disease_row, suggestions = find_best_disease_by_embedding(request.message, db, embedder)
                
                if disease_row is None:
                    # Fallback response without templates
                    try:
                        advice = "\n".join(f"- {s[0]}" for s in db.execute(text("SELECT text FROM suggestions WHERE is_general_advice=TRUE ORDER BY random() LIMIT 3")).fetchall())
                        bot_response_content = f"I understand you're not feeling well. Here are some general recommendations:\n{advice}"
                    except Exception as e:
                        print(f"DEBUG: Error with fallback suggestions: {e}")
                        bot_response_content = "I understand you're not feeling well. Please consult a healthcare provider if your symptoms persist or worsen."
                else:
                    # Try to use templates, fallback to simple response if templates fail
                    try:
                        tmpl = db.execute(
                            text("""
                                SELECT text FROM templates 
                                WHERE template_type='disease' 
                                AND is_active=TRUE 
                                AND (disease_id=:did OR disease_id IS NULL)
                                ORDER BY random() LIMIT 1
                            """),
                            {"did": disease_row[0]}
                        ).fetchone()
                        
                        # Try to pick a random, human-like template (disease-specific or general)
                        tmpl = db.execute(
                            text("""
                                SELECT text FROM templates 
                                WHERE template_type='disease' 
                                AND is_active=TRUE 
                                AND (disease_id=:did OR disease_id IS NULL)
                                ORDER BY random() LIMIT 1
                            """),
                            {"did": disease_row[0]}
                        ).fetchone()

                        if tmpl:
                            tmpl_text = tmpl[0]
                        else:
                            tmpl_text = "Based on your symptoms, the likely cause is {disease_name}: {disease_desc}.\nHere’s what you can try:\n{advice}"

                        tmpl_text = tmpl_text.replace("{disease_name}", disease_row[1]).replace("{disease_desc}", disease_row[2])

                        # Filter out generic suggestions and use specific ones
                        specific_suggestions = [
                            s for s in suggestions 
                            if not s.lower().startswith("please consult") and 
                            not s.lower().startswith("it's always best") and
                            not s.lower().startswith("stay hydrated") and
                            len(s) > 20  # Avoid very short generic responses
                        ]

                        # Use specific suggestions if available, otherwise use all suggestions
                        final_suggestions = specific_suggestions[:3] if specific_suggestions else suggestions[:3]

                        # If still empty, add some general advice (guaranteed to never be blank)
                        if not final_suggestions:
                            advice_rows = db.execute(text(
                                "SELECT text FROM suggestions WHERE is_general_advice=TRUE AND text NOT LIKE '%consult%' AND text NOT LIKE '%doctor%' ORDER BY random() LIMIT 2"
                            )).fetchall()
                            final_suggestions = [s[0] for s in advice_rows] if advice_rows else ["Try to get plenty of rest and stay hydrated."]

                        advice = "\n".join(f"- {s}" for s in final_suggestions)
                        tmpl_text = tmpl_text.replace("{advice}", advice)
                        bot_response_content = tmpl_text
                        
                    except Exception as e:
                        print(f"DEBUG: Error with disease templates: {e}")
                        # Simple fallback response with better suggestions
                        specific_suggestions = [
                            s for s in suggestions 
                            if not s.lower().startswith("please consult") and 
                               not s.lower().startswith("it's always best") and
                               not s.lower().startswith("stay hydrated") and
                               len(s) > 20
                        ]
                        final_suggestions = specific_suggestions[:2] if specific_suggestions else suggestions[:2]
                        advice = "\n".join(f"- {s}" for s in final_suggestions)
                        bot_response_content = f"Based on your symptoms, you might be experiencing {disease_row[1].lower()}. {disease_row[2]} Here are some recommendations:\n{advice}"
                        
            except Exception as e:
                print(f"DEBUG: Error in disease matching: {e}")
                bot_response_content = "I understand you're not feeling well. Please consult a healthcare provider if your symptoms persist or worsen."
                
        except Exception as e:
            print(f"DEBUG: General embedding model error: {e}")
            traceback.print_exc()
            bot_response_content = "I'm having trouble processing your request right now. Please try again or use a different model."
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

@router.get("/test-embed/")
def test_embed(prompt: str = "test"):
    try:
        print(f"Received prompt for embedding: {prompt}")
        try:
            print(f"Generating embedding...")
            vector = embedder.encode(prompt)
            print(f"Vector generated: {vector[:5]}...")  # preview only
            return {"message": "Embedding worked", "vector": vector}
        except Exception as e:
            print(f"Error during embedding: {e}")
            return {"message": "Embedding failed", "error": str(e)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}