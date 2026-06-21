from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, is_db_connected
from app.routers import auth, grade, student, lesson
from app import models

# Meta-tag configurations for clean OpenAPI/Swagger documentation categorization
openapi_tags = [
    {"name": "Entry Operations"},
    {"name": "Student Operations"},
    {"name": "Lesson Operations"},
    {"name": "Grade Operations"},
]

app = FastAPI(title="Mini LMS Backend API", openapi_tags=openapi_tags)

# Cross-Origin Resource Sharing (CORS) security middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits comprehensive origins access framework during active development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Application state container variable to track baseline infrastructure status
app.state.db_ready = False


@app.on_event("startup")
def on_startup():
    """
    Triggers on application startup lifecycle to automatically provision database schemas.
    If the database server is offline, the API remains functional rather than crashing out.
    """
    app.state.db_ready = init_db(models.Base.metadata)

# Register functional feature routers into the primary core application context
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(grade.router)
app.include_router(lesson.router) 

@app.get("/")
def root():
    """
    Root endpoint serving as a basic entry point ping verification route.
    """
    return {"message": "Welcome to the Mini LMS System"}


@app.get("/health/db")
def db_health():
    """
    Exposes an operational health-check gateway monitoring live connection states to SQL Server.
    """
    connected = is_db_connected()
    return {
        "db_connected": connected,
        "db_initialized_on_startup": bool(app.state.db_ready),
    }