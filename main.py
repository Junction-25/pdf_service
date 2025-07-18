from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import router
from app.services import test_llm_connection

# --- APPLICATION SETUP ---
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Include the API routes
app.include_router(router)

# --- HEALTH CHECK ---
@app.get("/", tags=["Health"])
def health_check():
    """
    Basic health check endpoint.
    """
    return {"status": "healthy", "service": "Dar.ai PDF Service"}

@app.get("/health", tags=["Health"])
def health_check_detailed():
    """
    Detailed health check including LLM connectivity.
    """
    llm_status = test_llm_connection()
    return {
        "status": "healthy",
        "service": "Dar.ai PDF Service",
        "llm_connection": "working" if llm_status else "failed"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
