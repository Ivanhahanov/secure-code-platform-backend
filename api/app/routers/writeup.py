from fastapi import APIRouter, UploadFile, File, HTTPException
from . import *
from datetime import datetime
from .challenges import challenges

router = APIRouter()
writeup = db.writeup
writeup_score = db.writeup_score


class WriteUp(BaseModel):
    challenge_shortname: str
    author: str = None
    score: int = 0
    text: str
    writeup_created: datetime = None


class WriteUpScore(BaseModel):
    challenge_shortname: str
    author: str
    user: str = None
    value: int


@router.get('/')
def get_writeup(shortname: str, _: User = Depends(get_current_active_user)):
    writeups = [WriteUp(**db_writeup) for db_writeup in writeup.find({'challenge_shortname': shortname})]
    for data in writeups:
        data.text = markdown_to_html(data.text)
    return writeups


@router.put('/new')
def get_writeup(new_writeup: WriteUp, current_user: User = Depends(get_current_active_user)):
    new_writeup.writeup_created = datetime.now(timezone.utc).isoformat()
    new_writeup.author = current_user.username
    check_writeup(new_writeup)
    writeup.insert_one(new_writeup.dict())
    return {"status": True, **new_writeup.dict()}


@router.post('/score')
def writeup_users_score(score: WriteUpScore, current_user: User = Depends(get_current_active_user)):
    writeup_id = writeup.find_one({"challenge_shortname": score.challenge_shortname, "author": score.author}).get('_id')
    print(writeup_id)
    if writeup_id:
        if not writeup_score.find_one({"writeup_id": writeup_id, "user": current_user.username}):
            print(score.value)
            writeup_score.insert_one({"writeup_id": writeup_id, "user": current_user.username, "value": score.value})
            count = count_writeup_score(writeup_id)
            writeup.update_one({"challenge_shortname": score.challenge_shortname, "author": score.author},
                               {"$set": {"score": count}})
            return {"status": True, "score": count}
    raise HTTPException(status_code=400, detail="user has already rated")


def count_writeup_score(writeup_id):
    count = writeup_score.aggregate([
        {'$match': {
            "writeup_id": writeup_id
        }},
        {'$group': {
            "_id": "$writeup_id",
            "score": {"$sum": "$value"}
        }}]).next()['score']
    print(count)
    return count


@router.get('/get')
def get_writeups(challenge_shortname: str):
    return {'writeups': [WriteUp(**data) for data in writeup.find({"challenge_shortname": challenge_shortname})]}


def check_writeup(new_writeup):
    shortname = new_writeup.challenge_shortname
    if not challenges.find_one({"shortname": shortname}):
        raise HTTPException(status_code=400, detail="wrong shortname")
    if writeup.find_one({"challenge_shortname": new_writeup.challenge_shortname, "author": new_writeup.author}):
        raise HTTPException(status_code=400, detail="you already write writeup")
    return True
