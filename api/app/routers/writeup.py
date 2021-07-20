from fastapi import APIRouter, UploadFile, File, HTTPException
from . import *
from datetime import datetime
from .challenges import challenges

router = APIRouter()
writeup = db.writeup
writeup_score = db.writeup_score


class WriteUp(BaseModel):
    challenge_shortname: str
    text: str


class DBWriteUp(WriteUp):
    challenge_shortname: str
    author: str = None
    score: int = 0
    writeup_created: datetime = None


class ShowWriteup(DBWriteUp):
    is_owner: bool = False


class WriteUpScore(BaseModel):
    challenge_shortname: str
    author: str
    user: str = None
    value: int


@router.get('/')
def get_writeup(shortname: str, current_user: User = Depends(get_current_active_user)):
    writeups = [ShowWriteup(**db_writeup) for db_writeup in writeup.find({'challenge_shortname': shortname})]
    for data in writeups:
        data.text = markdown_to_html(data.text)
        if data.author == current_user.username:
            data.is_owner = True
    return {'writeups': writeups}


@router.put('/new')
def get_writeup(new_writeup: WriteUp, current_user: User = Depends(get_current_active_user)):
    new_writeup = DBWriteUp(**new_writeup.dict(),
                            writeup_created=datetime.now(timezone.utc).isoformat(),
                            author=current_user.username,
                            score=0,
                            )
    check_writeup(new_writeup)
    writeup.insert_one(new_writeup.dict())
    return {"status": True, **new_writeup.dict()}


@router.post('/score')
def writeup_users_score(score: WriteUpScore, current_user: User = Depends(get_current_active_user)):
    writeup_id = writeup.find_one({"challenge_shortname": score.challenge_shortname, "author": score.author})
    if writeup_id:
        writeup_id = writeup_id.get('_id')
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


@router.post('/update')
def update_writeup(updated_writeup: WriteUp, current_user: User = Depends(get_current_active_user)):
    db_writeup = DBWriteUp(**writeup.find_one({'challenge_shortname': updated_writeup.challenge_shortname,
                                               'author': current_user.username}))
    db_writeup.writeup_modified = datetime.now(timezone.utc).isoformat()
    db_writeup.text = updated_writeup.text
    writeup.update_one({'challenge_shortname': updated_writeup.challenge_shortname,
                        'author': current_user.username}, {"$set": db_writeup.dict()})
    return db_writeup


@router.delete('/delete')
def delete_writeup(challenge_shortname: str, current_user: User = Depends(get_current_active_user)):
    result = writeup.delete_one({'challenge_shortname': challenge_shortname,
                                 'author': current_user.username})
    if result.raw_result['n'] == 1:
        return {'status': result.acknowledged}
    return {'status': False}


def check_writeup(new_writeup):
    shortname = new_writeup.challenge_shortname
    if not challenges.find_one({"shortname": shortname}):
        raise HTTPException(status_code=400, detail="wrong shortname")
    if writeup.find_one({"challenge_shortname": new_writeup.challenge_shortname, "author": new_writeup.author}):
        raise HTTPException(status_code=400, detail="you already write writeup")
    return True
