import os
import httpx
from openai import OpenAI
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer

# OpenAI Setup
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    custom_http_client = httpx.Client(proxies={})
    openai_client = OpenAI(api_key=openai_api_key, http_client=custom_http_client)
else:
    openai_client = None

# Function to get expert doctor response
def get_doctor_response(user_input, chat_history=[]):
    if not openai_client:
        return "OpenAI API key not set."

    system_prompt = (
        "You are HealthMate AI, a highly experienced medical doctor. "
        "Your job is to conduct a medical consultation. Start by asking the patient what brings them in. "
        "If the user mentions symptoms (e.g., pain, cough, nausea), ask relevant follow-up questions: "
        "location, severity (1-10), when it started, any triggers, and other symptoms. "
        "Then suggest a likely condition and classify it into one of three categories:\n"
        "1. Critical: Advise to consult a doctor or go to ER immediately.\n"
        "2. Moderate: Explain home treatment (rest, hydration, pain relievers) and when to seek help.\n"
        "3. Mild: Suggest simple remedies or over-the-counter meds.\n"
        "Be professional, friendly, and never make a definitive diagnosis."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for message in chat_history:
        messages.append({"role": message['role'], "content": message['content']})
    messages.append({"role": "user", "content": user_input})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        return f"OpenAI API error: {str(e)}"

# FLAN-T5 Setup
flan_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
flan_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
flan_pipeline = pipeline(
    "text2text-generation", 
    model=flan_model, 
    tokenizer=flan_tokenizer, 
    max_new_tokens=150,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.2
)

# Embedding Model
embedder = SentenceTransformer('all-MiniLM-L6-v2')