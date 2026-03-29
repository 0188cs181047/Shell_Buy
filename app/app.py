from fastapi import FastAPI
import uvicorn
from app.routers import user, product, user_category, payment
from app.routers.auth import token_referesh, login, register, auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
app = FastAPI(title="My API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
@app.get("/")
def hello_word():
    return "hello word"

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(auth.router)
app.include_router(login.router)
app.include_router(register.router)
app.include_router(token_referesh.router)
app.include_router(product.router)
app.include_router(user_category.router)
app.include_router(payment.router)


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)