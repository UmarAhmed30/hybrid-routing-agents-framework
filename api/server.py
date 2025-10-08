from fastapi import FastAPI

app = FastAPI(title="HyRA API")

@app.get("/health_check")
def health_check():
    return {"status": "ok"}

@app.get("/")
def home():
    return {"message": "Hybrid Routing Agent Framework API is running!"}
