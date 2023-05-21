import logging

from json import loads

import yaml

from bson.json_util import dumps
from fastapi import APIRouter, Cookie
from pymongo.collection import Collection

from .database import get_mongo_db
from .models import Allocation

allocation_router = APIRouter(prefix="/allocation", tags=["allocation"])


with open("/conf/project_config.yml", "r") as f:
    PROJECT_CONFIG = yaml.safe_load(f)


def get_allocation_collection(session_id: str) -> Collection:
    db = get_mongo_db(session_id)
    allocation = PROJECT_CONFIG.get("mongodb", {}).get("allocation")
    return db[allocation]


def existing_allocation_statement(
    allocation_statement: dict, session_id: str
) -> bool:
    allocation_collection = get_allocation_collection(session_id)
    existing_asset = allocation_collection.find_one(
        {"object_name": allocation_statement.get("object_name")}
    )
    if existing_asset:
        return True
    return False


def create_allocation_statement(
    allocation_statement: dict, session_id: str
) -> str:
    allocation_collection = get_allocation_collection(session_id)
    allocation_statement_id = allocation_collection.insert_one(
        allocation_statement
    ).inserted_id
    logging.info(f"Created allocation statement {allocation_statement_id}")
    return allocation_statement_id


def update_allocation_statement(
    allocation_statement: dict, session_id: str
) -> str:
    allocation_collection = get_allocation_collection(session_id)
    asset_id = allocation_collection.find_one_and_update(
        {"object_name": allocation_statement.get("object_name")},
        {"$set": {"rate": allocation_statement.get("rate")}},
    )
    return asset_id


def delete_asset(allocation_statement: dict, session_id: str) -> str:
    allocation_collection = get_allocation_collection(session_id)
    asset_id = allocation_collection.find_one_and_delete(
        {"object_name": allocation_statement.get("object_name")}
    )
    return asset_id


def find_allocation_statement(object_name: str, session_id: str) -> dict:
    allocation_collection = get_allocation_collection(session_id)
    query = {"object_name": object_name}
    allocation_statement = allocation_collection.find_one(query)
    return allocation_statement


@allocation_router.get("/")
def route_get_allocation(session_id: str = Cookie()) -> dict:
    allocation_collection = get_allocation_collection(session_id)
    allocation = list(allocation_collection.find())
    allocation = [loads(dumps(statement)) for statement in allocation]
    return {"allocation": allocation}


@allocation_router.get("/find/{object_name}")
def search_allocation_statement(
    object_name: str, session_id: str = Cookie()
) -> dict:
    allocation_statement = find_allocation_statement(object_name, session_id)
    allocation_statement = loads(dumps(allocation_statement))
    return allocation_statement


@allocation_router.post("/")
def route_set_allocation(
    allocation: Allocation, session_id: str = Cookie()
) -> dict:
    allocation = allocation.dict()["allocation"]

    for statement in allocation:
        if existing_allocation_statement(statement, session_id):
            update_allocation_statement(statement, session_id)
        else:
            create_allocation_statement(statement, session_id)
    return {"message": "Allocation statements finished."}
