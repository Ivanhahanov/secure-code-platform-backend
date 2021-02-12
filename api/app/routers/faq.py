from fastapi import APIRouter
from . import *

router = APIRouter()
questions = db.questions


class FAQ(BaseModel):
    _id: str = None
    question: str
    answer: str

    @property
    def id(self):
        return self._id


@router.get('/list')
def list_questions(_: User = Depends(get_current_active_user)):
    faq = list()
    for question in questions.find():
        question['_id'] = str(question['_id'])
        faq.append(question)
    return faq


@router.put('/add')
def add_question(question: FAQ, _: User = Depends(get_current_user_if_admin)):
    _id = questions.insert_one(question.dict(by_alias=True))
    question = question.dict(by_alias=True)
    question["_id"] = str(_id.inserted_id)
    return question


@router.post('/update')
def update_faq(question: FAQ, _: User = Depends(get_current_user_if_admin)):
    _id = ObjectId(question.id)
    question = question.dict(by_alias=True)
    questions.update_one({"_id": _id}, {'$set': question})
    return question


@router.delete('/del')
def del_faq(_id: Optional[str], _: User = Depends(get_current_user_if_admin)):
    questions.delete_one({"_id": ObjectId(_id)})
    return _id
