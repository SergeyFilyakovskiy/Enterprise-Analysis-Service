from fastapi import FastAPI
from .api import auth, analysis

app = FastAPI()

@app.get("/healthy")
async def health_check():
    return {'status':'Healthy'}

app.include_router(auth.router)
app.include_router(analysis.router)
