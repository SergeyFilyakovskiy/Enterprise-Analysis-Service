from fastapi import FastAPI
from .database import Base

app = FastAPI()

@app.get("/healthy")
async def health_check():
    return {'status':'Healthy'}


