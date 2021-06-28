import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from api.app.routers import challenges, scoreboard, auth, admin, user, sponsors, faq, flags, openvpn, writeup
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="api/static"), name="static")
app.include_router(auth.router, prefix="/auth", tags=['Auth'])
app.include_router(user.router, prefix="/users", tags=['Users'])
app.include_router(openvpn.router, prefix='/openvpn', tags=['OpenVpn'])
app.include_router(challenges.router, prefix="/challenges", tags=['Challenges'])
app.include_router(writeup.router, prefix="/writeup", tags=['Writeup'])
app.include_router(scoreboard.router, prefix="/scoreboard", tags=['Scoreboard'])
app.include_router(flags.router, prefix='/flag', tags=['Flags'])
app.include_router(admin.router, prefix='/admin', tags=['Admin'])
app.include_router(faq.router, prefix='/faq', tags=['FAQ'])
app.include_router(sponsors.router, prefix='/sponsors', tags=['Sponsors'])


@app.get("/")
def index(token: str):
    return {"data": "Hello, World!", "token": token}
