from . import *
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

db = mongo.secure_code_platform
users = db.users
router = APIRouter()


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
    if user.user_role not in roles[1:]:
        raise HTTPException(status_code=400, detail="Invalid Role")
    user.password = get_password_hash(user.password)
    users.insert(user.dict(by_alias=True))
    return {'user': user}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return {"item_id": "Foo", "owner": current_user.username}
