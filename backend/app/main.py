#FastAPI uygulamasini burada ayaga kaldirir ve
#hazirlanan routerları(yoneticileri) buraya kaydedersin.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, is_db_connected
from app.routers import auth, grade, student, lesson #lesson i ekledim
from app import models

openapi_tags = [
    {"name": "Entry Operations"},
    {"name": "Student Operations"},
    {"name": "Lesson Operations"},
    {"name": "Grade Operations"},
]

app = FastAPI(title="Mini LMS Backend API", openapi_tags=openapi_tags)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gelistirme asamasinda tum originlere izin veriyoruz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.state.db_ready = False


@app.on_event("startup")
def on_startup():
    # Uygulama ayaga kalkarken tablo olusturmayi dener,
    # DB baglantisi yoksa API yine de ayakta kalir.
    app.state.db_ready = init_db(models.Base.metadata)

app.include_router(auth.router)
app.include_router(student.router)
app.include_router(grade.router)

app.include_router(lesson.router) 

@app.get("/")
def root():
    return {"message": "Welcome to the Mini LMS System"}


@app.get("/health/db")
def db_health():
    connected = is_db_connected()
    return {
        "db_connected": connected,
        "db_initialized_on_startup": bool(app.state.db_ready),
    }

