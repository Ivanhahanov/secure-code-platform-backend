from redis import Redis
from pymongo import MongoClient
r = Redis(host='redis', port=6379, db=0, password="sOmE_sEcUrE_pAsS")
mongo = MongoClient('mongodb', 27017)