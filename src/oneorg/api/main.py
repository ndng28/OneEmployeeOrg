from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(
    title="OneEmployeeOrg API",
    description="Edu-tainment platform for K-12 students",
    version="2.0.0",
)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}
