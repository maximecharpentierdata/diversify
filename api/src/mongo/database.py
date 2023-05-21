import datetime

import yaml
from bson import json_util
import json

from fastapi import APIRouter, Cookie
from pymongo import MongoClient
from pymongo.database import Database

from pydantic import BaseModel

from .models import AllocationStatement, Asset, Constraint

with open("/conf/project_config.yml", "r") as f:
    PROJECT_CONFIG = yaml.safe_load(f)

mongo_router = APIRouter(prefix="/mongo", tags=["mongo"])


def get_mongo_db(session_id) -> Database:
    host = PROJECT_CONFIG.get("mongodb", {}).get("host")
    port = PROJECT_CONFIG.get("mongodb", {}).get("port")
    user = PROJECT_CONFIG.get("mongodb", {}).get("user")
    password = PROJECT_CONFIG.get("mongodb", {}).get("password")
    # db = PROJECT_CONFIG.get("mongodb", {}).get("db")

    client = MongoClient(
        host=f"mongodb://{host}/{session_id}",
        port=port,
        username=user,
        password=password,
    )

    db = client[session_id]

    # Keep track of the last modification date for the session
    meta_collection = db["meta"]
    if meta_collection.count_documents({}) == 0:
        meta_collection.insert_one(
            {"last_modif_date": datetime.datetime.now()}
        )
    else:
        meta_collection.update_one(
            {}, {"$set": {"last_modif_date": datetime.datetime.now()}}
        )

    return db


@mongo_router.get("/export")
def export_data(session_id: str = Cookie()) -> dict:
    mongo_db = get_mongo_db(session_id)
    collections = mongo_db.list_collection_names()
    export_data = {}
    for collection in collections:
        if collection not in ["meta"]:
            export_data[collection] = list(
                mongo_db[collection].find({}, {"_id": 0})
            )

    return json.loads(json_util.dumps(export_data))


class DataBase(BaseModel):
    assets: list[Asset]
    allocation: list[AllocationStatement]
    constraints: list[Constraint]


@mongo_router.post("/import")
def import_data(import_data: DataBase, session_id: str = Cookie()) -> dict:
    import_data = import_data.dict()

    mongo_db = get_mongo_db(session_id)

    for collection in import_data.keys():
        mongo_db.drop_collection(collection)
        mongo_db[collection].insert_many(import_data[collection])

    return {"status": "ok"}
