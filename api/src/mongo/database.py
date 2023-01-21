import datetime
from bson import json_util

import yaml
from pymongo import MongoClient
from fastapi import APIRouter, responses, Cookie

from io import StringIO

with open("/conf/project_config.yml", "r") as f:
    PROJECT_CONFIG = yaml.safe_load(f)

mongo_router = APIRouter(prefix="/mongo", tags=["mongo"])


@mongo_router.get("/export")
def export(session_id: str = Cookie()):
    db = get_mongo_db(session_id)
    assets = PROJECT_CONFIG.get("mongodb", {}).get("assets", "")
    json_export = list(db[assets].find({}))
    file = StringIO()
    file.write(json_util.dumps(json_export))
    return responses.StreamingResponse(
        content=iter(file.getvalue()),
        headers={
            "Content-Disposition": "attachment; filename=export.diversify"
        },
    )


def get_mongo_db(session_id) -> MongoClient:
    host = PROJECT_CONFIG.get("mongodb", {}).get("host")
    port = PROJECT_CONFIG.get("mongodb", {}).get("port")
    user = PROJECT_CONFIG.get("mongodb", {}).get("user")
    password = PROJECT_CONFIG.get("mongodb", {}).get("password")
    # db = PROJECT_CONFIG.get("mongodb", {}).get("db")

    client = MongoClient(
        host=host, port=port, username=user, password=password
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
