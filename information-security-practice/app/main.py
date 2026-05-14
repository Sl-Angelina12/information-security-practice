from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware #Додала
from app.database import Base, engine
from app import models

from app.middleware.security_headers import SecurityHeadersMiddleware #Додала
from app.middleware.rate_limiter import limiter #Додала

from app.routers.auth import router as auth_router
from app.routers.students import router as students_router
from app.routers.teachers import router as teachers_router
from app.routers.admin import router as admin_router

app = FastAPI(
	title="Електронний деканат",
	description="API для управління академічними даними",
	version="0.6.0" #Оновила версію
)

app.state.limiter = limiter
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
    	"http://localhost:3000",
    	"http://localhost:8000",
		"http://localhost:3010", #Додала порт
	],
	allow_credentials=True,
	allow_methods=["GET", "POST", "PUT", "DELETE"],
	allow_headers=["Authorization", "Content-Type"],
)

# Підключення роутерів
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(admin_router)

@app.get("/")
def root():
	return {"message": "Електронний деканат API v0.6.0"}

@app.get("/health")
def health_check():
	return {
    	"status": "healthy",
    	"database": "SQLite",
    	"tables": len(Base.metadata.tables)
	}
