import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from api.app.routers import challenges, scoreboard, auth, admin, user, sponsors, faq

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=['Auth'])
app.include_router(user.router, prefix="/users", tags=['Users'])
app.include_router(challenges.router, prefix="/challenges", tags=['Challenges'])
app.include_router(scoreboard.router, prefix="/scoreboard", tags=['Scoreboard'])
app.include_router(admin.router, prefix='/admin', tags=['Admin'])
app.include_router(faq.router, prefix='/faq', tags=['FAQ'])
app.include_router(sponsors.router, prefix='/sponsors', tags=['Sponsors'])


@app.get("/")
def index(token: str):
    return {"data": "Hello, World!", "token": token}
