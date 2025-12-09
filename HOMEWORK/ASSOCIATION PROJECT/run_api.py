"""
Script pour lancer l'API FastAPI
Usage: uvicorn api:app --reload
ou: python run_api.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

