from . import *
from fastapi import APIRouter
import requests
from fastapi.responses import StreamingResponse

file_path = "/openvpn/users/ivanh.ovpn"
router = APIRouter()


@router.get('/get')
def get_openvpn_config(current_user: User = Depends(get_current_active_user)):
    config = requests.post("http://openvpn:8080/api/user/config/show",
                           data={"username": current_user.username})
    response = StreamingResponse(iter([config.content]), media_type="text/plain")
    response.headers["Content-Disposition"] = f"attachment; filename={current_user.username}.ovpn"
    return response


@router.get('/generate')
def generate_openvpn_config(current_user: User = Depends(get_current_active_user)):
    config = generate_config(current_user.username)
    response = StreamingResponse(iter([config]), media_type="text/plain")
    response.headers["Content-Disposition"] = f"attachment; filename={current_user.username}.ovpn"
    return response


def generate_config(username):
    response = requests.post("http://openvpn:8080/api/user/create",
                             data={"username": username,
                                   "password": "nopass"})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.content
