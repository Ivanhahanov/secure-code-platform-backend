from fastapi import APIRouter
from . import *

router = APIRouter()
sponsors = db.sponsors


class Sponsor(BaseModel):
    _id: str = None
    title: str
    description: str
    img: str

    @property
    def id(self):
        return self._id


@router.get('/list')
def list_sponsor(current_user: User = Depends(get_current_active_user)):
    sponsors_list = list()
    for sponsor in sponsors.find():
        sponsor['_id'] = str(sponsor['_id'])
        sponsors_list.append(sponsor)

    return sponsors_list


@router.put('/add')
def add_sponsor(sponsor: Sponsor, current_user: User = Depends(get_current_active_user)):
    _id = sponsors.insert_one(sponsor.dict(by_alias=True))
    sponsor = sponsor.dict(by_alias=True)
    sponsor["_id"] = str(_id.inserted_id)
    return sponsor


@router.post('/update')
def update_sponsor(sponsor: Sponsor, current_user: User = Depends(get_current_active_user)):
    _id = ObjectId(sponsor.id)
    sponsor = sponsor.dict(by_alias=True)
    sponsors.update_one({"_id": _id}, {'$set': sponsor})
    return sponsor


@router.delete('/del')
def del_sponsor(_id: Optional[str], current_user: User = Depends(get_current_active_user)):
    sponsors.delete_one({"_id": ObjectId(_id)})
    return _id
