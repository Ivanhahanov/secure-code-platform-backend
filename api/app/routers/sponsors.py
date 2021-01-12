import hashlib
from random import sample

from fastapi import APIRouter
from fastapi import File, UploadFile
from . import *

router = APIRouter()
sponsors = db.sponsors
upload_path = 'api/static/img/sponsors/'
sponsors_img_path = 'static/img/sponsors/'


class Sponsor(BaseModel):
    _id: str = None
    title: str
    description: str
    img: str = None

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
async def add_challenge_with_files(title: str,
                                   description: str,
                                   sponsor_img: UploadFile = File(...),
                                   current_user: User = Depends(get_current_user_if_admin)):
    img = shuffle_name(sponsor_img.filename)
    upload_file(img, sponsor_img)
    sponsor = Sponsor(title=title, description=description, img=sponsors_img_path + img)
    _id = sponsors.insert_one(sponsor.dict(by_alias=True))
    sponsor = sponsor.dict(by_alias=True)
    sponsor["_id"] = str(_id.inserted_id)
    return sponsor


def upload_file(filename, file):
    with open(upload_path + filename, 'wb') as f:
        [f.write(chunk) for chunk in iter(lambda: file.file.read(), b'')]
    return True


def shuffle_name(filename):
    extension = filename.split('.')[-1]
    timestamp = str(datetime.now().timestamp()).replace('.', '')
    filename = ''.join(filename.split('.')[:-1])
    filename = ''.join(sample(timestamp, len(timestamp))) + f'{filename}'
    return f'{hashlib.md5(filename.encode("utf-8")).hexdigest()}.{extension}'


@router.post('/update')
def update_sponsor(sponsor: Sponsor, current_user: User = Depends(get_current_user_if_admin)):
    _id = ObjectId(sponsor.id)
    sponsor = sponsor.dict(by_alias=True)
    sponsors.update_one({"_id": _id}, {'$set': sponsor})
    return sponsor


@router.delete('/del')
def del_sponsor(_id: Optional[str], current_user: User = Depends(get_current_user_if_admin)):
    sponsors.delete_one({"_id": ObjectId(_id)})
    return _id
