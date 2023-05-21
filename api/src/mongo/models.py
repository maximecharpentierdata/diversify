from pydantic import BaseModel, validator
from typing import Optional, Literal
import yaml

# Assets

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


# Allocation


class AllocationStatement(BaseModel):
    object_type: Literal["asset", "asset_class"]
    object_name: str
    rate: Optional[float] = None


class Allocation(BaseModel):
    allocation: list[AllocationStatement]


# Constraints


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
