import datetime

from . import *
from fastapi import Depends, APIRouter, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from .scoreboard import get_users_without_admin
from .extensions.avatar_generator import create_avatar

db = mongo.secure_code_platform
users = db.users
router = APIRouter()


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    auth_user = authenticate_user(form_data.username, form_data.password)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": auth_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/register")
async def register_user(user: UserInDB):
    users_list = [user['username'] for user in db.users.find({})]
    if user.username in users_list:
        raise HTTPException(status_code=409, detail="Users exists")
    if user.user_role != "user":
        raise HTTPException(status_code=400, detail="Invalid Role")
    user.password = get_password_hash(user.password)
    user.avatar_path = save_avatar(user)
    user.created_at = datetime.now(timezone.utc).isoformat()
    user.modified_at = user.created_at
    users.insert(user.dict(by_alias=True))
    return {'user': user}


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    user = users.find_one({"username": current_user.username})
    num_of_solved_challenges = len(user.get("solved_challenges_id", []))
    user = UserScriptKiddy(**users.find_one({"username": current_user.username}, {'_id': False}),
                           num_of_solved_challenges=num_of_solved_challenges,
                           place_in_scoreboard=1
                           )
    user.place_in_scoreboard = get_place_in_scoreboard(current_user.username)
    return user


def get_place_in_scoreboard(username):
    all_users = get_users_without_admin()
    sorted_users = sorted(all_users, key=lambda scoreboard_user: scoreboard_user.users_score)
    for index, user in enumerate(sorted_users, start=1):
        if user.username == username:
            place_in_scoreboard = index
            return place_in_scoreboard
    return -1


@router.post("/change_password")
def change_password(passwords: ChangePassword, current_user: User = Depends(get_current_active_user)):
    user = authenticate_user(current_user.username, passwords.old_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    current_user.password = get_password_hash(passwords.new_password)
    current_user.modified_at = datetime.now(timezone.utc).isoformat()
    users.update_one({'username': current_user.username}, {'$set': {'password': current_user.password}})
    return User(**current_user.dict(by_alias=True))


@router.get("/change_avatar")
async def change_avatar(current_user: User = Depends(get_current_active_user)):
    user = User(**users.find_one({"username": current_user.username}))
    time_delta = datetime.now(timezone.utc) - user.modified_at
    if time_delta.days >= 0:
        save_avatar(current_user)
        user.modified_at = datetime.now(timezone.utc).isoformat()
        return {"result": True, "message": "Avatar changed successfully"}
    time_left = timedelta(days=10) - time_delta
    return {"result": False, "message": f"Time left: {time_left}"}


def save_avatar(current_user):
    avatar_path = f'/api/static/img/avatar/{current_user.username}.svg'
    create_avatar(avatar_path, current_user.sex)
    return "/".join(avatar_path.split("/")[2:])


@router.put("/upload_avatar")
def put_avatar(avatar_img: UploadFile = File(...),
               current_user: User = Depends(get_current_active_user)):
    avatar_path = upload_avatar(avatar_img, current_user.username)
    users.update_one({'username': current_user.username},
                     {'$set': {'avatar_path': avatar_path}})
    return {'status': True}


def upload_avatar(img, username):
    extension = os.path.splitext(img.filename)[1].lower()
    if extension not in ('.png', '.jpg', '.jpeg'):
        HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Wrong extension {extension}"
        )
    mime_type = img.content_type
    if mime_type not in ('image/png', 'image/jpeg'):
        HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Wrong Media type {extension}"
        )
    filename = f'api/static/img/avatar/{username}{extension}'
    with open(filename, 'wb') as f:
        [f.write(chunk) for chunk in iter(lambda: img.file.read(), b'')]
    return filename
