import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path
from src.rag_engine import RAGEngine  # Absolute import
from fastapi import FastAPI  # Added missing import
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
engine = RAGEngine()

@app.get("/recommend")
async def recommend_assessments(query: str):
    logger.info(f"Received query: {query}")
    results = engine.recommend(query)
    logger.info(f"Returning {len(results)} recommendations")
    return {"recommendations": results}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)