from fastapi import APIRouter, responses
from . import *

router = APIRouter()
DOCUMENTS_PATH = '/api/documents/'


@router.get('/contacts')
def contacts():
    return {
        'telegram:': 't.me',
    }


@router.get('/terms_of_service')
def terms_of_service():
    return responses.FileResponse(os.path.join(DOCUMENTS_PATH, 'terms_of_service.pdf'),
                                  media_type='application/pdf')


@router.get('/privacy_policy')
def privacy_policy():
    return responses.FileResponse(os.path.join(DOCUMENTS_PATH, 'privacy_policy.pdf'),
                                  media_type='application/pdf')
