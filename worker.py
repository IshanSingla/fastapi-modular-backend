from core.config import settings
import uvicorn

if __name__ == "__main__":  # Protect the main entry point
    uvicorn.run("app:app", host="0.0.0.0", port=settings.PORT, reload=True if settings.ENV != "production" else False,
        workers=1,)
