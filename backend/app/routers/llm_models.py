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

# FLAN-T5 Setup
flan_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
flan_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
flan_pipeline = pipeline("text2text-generation", model=flan_model, tokenizer=flan_tokenizer, max_new_tokens=150)

# Embedding Model
embedder = SentenceTransformer('all-MiniLM-L6-v2')