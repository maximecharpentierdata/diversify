import logging

from json import loads
from typing import Literal, Optional

import yaml

from bson import ObjectId
from bson.json_util import dumps
from fastapi import APIRouter, Cookie, HTTPException
from pydantic import BaseModel, validator
from pymongo.collection import Collection

from .database import get_mongo_db


constraints_router = APIRouter(prefix="/constraints", tags=["constraints"])


class ConstraintedAsset(BaseModel):
    asset_name: str
    coef: float

    @validator("coef")
    def check_coef(cls, v):
        assert v != 0, "Coefficient cannot be 0"
        return v


class Constraint(BaseModel):
    assets: list[ConstraintedAsset]
    operator: Literal["leq", "geq", "eq"]
    value: float


def get_constraints_collection(session_id: str) -> Collection:
    db = get_mongo_db(session_id)
    return db["constraints"]


def insert_constraint(constraint: dict, session_id: str) -> Optional[str]:
    constraints_collection = get_constraints_collection(session_id)
    result = constraints_collection.insert_one(constraint)
    return result.inserted_id


@constraints_router.get("/")
def route_get_constraints(session_id: str = Cookie()) -> dict:
    constraints_collection = get_constraints_collection(session_id)
    constraints = constraints_collection.find()
    return loads(dumps(constraints))


@constraints_router.put("/")
def route_insert_constraint(
    constraint: Constraint, session_id: str = Cookie()
) -> dict:
    constraint = constraint.dict()
    constraint_id = insert_constraint(constraint, session_id)
    logging.info(f"Created constraint {constraint_id}")
    return {"inserted_id": str(constraint_id)}


@constraints_router.get("/{constraint_id}")
def route_get_constraint(
    constraint_id: str, session_id: str = Cookie()
) -> dict:
    constraints_collection = get_constraints_collection(session_id)
    constraint = constraints_collection.find_one(
        {"_id": ObjectId(constraint_id)}
    )
    if not constraint:
        raise HTTPException(status_code=404, detail="Constraint not found")
    return loads(dumps(constraint))


@constraints_router.post("/")
def route_update_constraint(
    constraint: Constraint, session_id: str = Cookie()
) -> dict:
    constraint = constraint.dict()
    constraints_collection = get_constraints_collection(session_id)
    constraint_id = constraint["_id"]
    constraints_collection.find_one_and_update(
        {"_id": ObjectId(constraint_id)},
        {"$set": constraint},
    )
    logging.info(f"Updated constraint {constraint_id}")
    return {"updated_id": str(constraint_id)}


@constraints_router.delete("/{constraint_id}")
def route_delete_constraint(
    constraint_id: str, session_id: str = Cookie()
) -> dict:
    constraints_collection = get_constraints_collection(session_id)
    constraints_collection.delete_one({"_id": ObjectId(constraint_id)})
    logging.info(f"Deleted constraint {constraint_id}")
    return {"deleted_id": str(constraint_id)}
