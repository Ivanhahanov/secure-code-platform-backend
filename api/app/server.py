import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from api.app.routers import challenges, scoreboard, auth, admin

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(level=logging.DEBUG)
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
mqtt_answer = ''


app.include_router(auth.router, prefix="/auth", tags=['Auth'])
app.include_router(challenges.router, prefix="/challenges", tags=['Challenges'])
app.include_router(scoreboard.router, prefix="/scoreboard", tags=['Scoreboard'])
app.include_router(admin.router, prefix='/admin', tags=['Admin'])


@app.get("/")
def index(token: str = Depends(oauth2_scheme)):
    return {"data": "Hello, World!", "token": token}


