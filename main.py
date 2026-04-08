from fastapi import FastAPI
from routers import auth, roles, documents, rag

app = FastAPI()

app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(documents.router)
app.include_router(rag.router)

@app.get("/")
def home():
    return {"message": "hello,Financial api is running"}
