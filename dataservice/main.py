from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing any modules
load_dotenv()

from src.main import app

if __name__ == "__main__":
    import uvicorn
    import os

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8003))

    uvicorn.run(app, host=host, port=port, reload=True)
