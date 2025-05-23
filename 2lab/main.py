from fastapi import FastAPI
from app.api import auth, encryption

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}

app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(encryption.router, prefix="", tags=["encryption"])
