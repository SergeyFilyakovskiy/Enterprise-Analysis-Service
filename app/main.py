from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from .database import async_engine
from .models import Base, User, FinancialReport, ReportAssets, ReportLiabilities, ReportProfitLoss
from .api import auth, analysis,reports, user


@asynccontextmanager
async def lifespan(app: FastAPI):


    async with async_engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)
        print("--- TABLES CREATED SUCCESSFULLY ---")
    
    yield
    
    print("--- SHUTDOWN ---")

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(reports.router)
app.include_router(user.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Главная"})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Вход"})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Регистрация"})

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("report_upload.html", {"request": request, "title": "Загрузка отчета"})

@app.get("/analysis/{report_id}", response_class=HTMLResponse)
async def analysis_page(request: Request, report_id: int):
    return templates.TemplateResponse("analysis_result.html", {"request": request, "title": "Результаты анализа", "report_id": report_id})

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("report_upload.html", {"request": request, "title": "Загрузка"})

