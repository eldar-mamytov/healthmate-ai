from fastapi import FastAPI

app = FastAPI(title="HealthMate-AI Backend")

@app.get("/")
async def read_root():
    return {"message": "Welcome to HealthMate-AI Backend"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}