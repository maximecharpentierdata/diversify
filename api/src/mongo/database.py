import datetime

import yaml
from pymongo import MongoClient

with open("/conf/project_config.yml", "r") as f:
    PROJECT_CONFIG = yaml.safe_load(f)


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
