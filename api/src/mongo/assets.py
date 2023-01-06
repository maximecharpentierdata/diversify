import logging
from json import loads
from typing import Optional

import yaml
from bson.json_util import dumps
from fastapi import APIRouter, Cookie, HTTPException
from pydantic import BaseModel, validator
from pymongo.collection import Collection

from .database import get_mongo_db

assets_router = APIRouter(prefix="/assets", tags=["assets"])


with open("/conf/project_config.yml", "r") as f:
    PROJECT_CONFIG = yaml.safe_load(f)


class Asset(BaseModel):
    name: str
    class_name: str
    value: Optional[float] = 0.0

    @validator("class_name")
    def check_class_name(cls, v):
        assert v in PROJECT_CONFIG.get("config", {}).get(
            "asset_classes"
        ), f"Class {v} is not in the list of asset classes"
        return v

    @validator("name")
    def check_name(cls, v):
        assert v is not "", "Name cannot be empty"
        return v


def get_assets_collection(session_id) -> Collection:
    db = get_mongo_db(session_id)
    assets = PROJECT_CONFIG.get("mongodb", {}).get("assets")
    return db[assets]


def existing_asset(asset: dict, session_id: str) -> bool:
    assets_collection = get_assets_collection(session_id)
    existing_asset = assets_collection.find_one(
        {"name": asset.get("name"), "class_name": asset.get("class_name")}
    )
    if existing_asset:
        return True
    return False


def create_asset(asset: dict, session_id: str) -> str:
    assets_collection = get_assets_collection(session_id)
    asset_id = assets_collection.insert_one(asset).inserted_id
    logging.info(f"Created asset {asset_id}")
    return asset_id


def update_asset_value(asset: dict, session_id: str) -> str:
    assets_collection = get_assets_collection(session_id)
    asset_id = assets_collection.find_one_and_update(
        {"name": asset.get("name")},
        {"$set": {"value": asset.get("value")}},
    )
    return asset_id


def delete_asset(asset_name: str, session_id: str) -> str:
    assets_collection = get_assets_collection(session_id)
    asset_id = assets_collection.find_one_and_delete({"name": asset_name})
    return asset_id


def search_asset(
    name: Optional[str] = None,
    class_name: Optional[str] = None,
    session_id: str = None,
) -> list[dict]:
    assets_collection = get_assets_collection(session_id)
    query = {}
    if name:
        query["name"] = name
    if class_name:
        query["class_name"] = class_name

    assets = list(assets_collection.find(query))
    return assets


@assets_router.get("/")
def route_get_assets(session_id: str = Cookie()) -> dict:
    assets_collection = get_assets_collection(session_id)
    assets = list(assets_collection.find())
    assets = [loads(dumps(asset)) for asset in assets]
    return {"assets": assets}


@assets_router.get("/search")
def route_search_asset(
    name: Optional[str] = None,
    class_name: Optional[str] = None,
    session_id: str = Cookie(),
) -> dict:
    assets = search_asset(name, class_name, session_id)
    assets = [loads(dumps(asset)) for asset in assets]
    return {"assets": assets}


@assets_router.put("/")
def route_create_asset(
    asset: Asset, session_id: str = Cookie()
) -> dict | HTTPException:
    asset = asset.dict()
    if existing_asset(asset, session_id):
        raise HTTPException(
            status_code=400,
            detail=f"Asset {asset.get('name')} already exists",
        )
    try:
        asset_id = create_asset(asset, session_id)
    except AssertionError as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return {"asset_id": str(asset_id)}


@assets_router.post("/")
def route_update_asset_value(
    asset: dict, session_id: str = Cookie()
) -> dict | HTTPException:
    asset_id = update_asset_value(asset, session_id)
    if not asset_id:
        raise HTTPException(
            status_code=400,
            detail=f"Asset {asset.get('name')} does not exist",
        )
    logging.info(f"Updated asset {asset_id}")
    return {"asset_id": str(asset_id)}


@assets_router.delete("/{asset_name}")
def route_delete_asset(
    asset_name: str, session_id: str = Cookie()
) -> dict | HTTPException:
    asset_id = delete_asset(asset_name, session_id)
    if not asset_id:
        raise HTTPException(
            status_code=400,
            detail=f"Asset {asset_name} does not exist",
        )
    logging.info(f"Deleted asset {asset_id}")
    return {"asset_id": str(asset_id)}
