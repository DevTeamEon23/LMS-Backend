import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run("app:app",
                host="0.0.0.0",
                port=9092,
                reload=settings.SERVER_RELOAD)

