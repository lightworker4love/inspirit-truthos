from typing import List
from pydantic import BaseModel


class AllowedMode(BaseModel):
    key: str
    label: str
    default: bool


class AllowedModesResponse(BaseModel):
    modes: List[AllowedMode]
