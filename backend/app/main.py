from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Pharmacy-api",
    description="Pharmacy management system for tracking sales, drugs ...",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="redocs",
)

# app.add_middleware(
    
# )

@app.get('/')
def root():
    return { "message" : "Pharmacy API is up" }