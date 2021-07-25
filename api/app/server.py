import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from api.app.routers import challenges, scoreboard, auth, admin, user, sponsors, faq, flags, openvpn, writeup, stats, info
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
import os

app = FastAPI()
logging.basicConfig(level=logging.INFO)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="api/static"), name="static")
dist = StaticFiles(directory="/frontend/dist")
app.include_router(auth.router, prefix="/auth", tags=['Auth'])
app.include_router(user.router, prefix="/users", tags=['Users'])
app.include_router(openvpn.router, prefix='/openvpn', tags=['OpenVpn'])
app.include_router(stats.router, prefix='/stats', tags=['Statistics'])
app.include_router(challenges.router, prefix="/challenges", tags=['Challenges'])
app.include_router(writeup.router, prefix="/writeup", tags=['Writeup'])
app.include_router(scoreboard.router, prefix="/scoreboard", tags=['Scoreboard'])
app.include_router(flags.router, prefix='/flag', tags=['Flags'])
app.include_router(admin.router, prefix='/admin', tags=['Admin'])
app.include_router(faq.router, prefix='/faq', tags=['FAQ'])
app.include_router(sponsors.router, prefix='/sponsors', tags=['Sponsors'])
app.include_router(info.router, prefix='/info', tags=['Info'])


@app.get("/{path:path}", name="catch-all")
async def frontend_catchall(path: str, request: Request):
    # Find static file for path
    path = path.lstrip("/")
    full_path, stat_path = await dist.lookup_path(path)

    # If file exists, serve it
    if os.path.isfile(full_path) and stat_path is not None:
        return await dist.get_response(path, request.scope)

    # Serve index.html
    return await dist.get_response("index.html", request.scope)
