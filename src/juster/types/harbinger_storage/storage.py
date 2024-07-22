# generated by datamodel-codegen:
#   filename:  storage.json

from __future__ import annotations

from typing import Dict
from typing import Optional

from pydantic import BaseModel
from pydantic import Extra


class OracleData(BaseModel):
    class Config:
        extra = Extra.forbid

    timestamp_0: str
    timestamp_1: str
    nat_0: str
    nat_1: str
    nat_2: str
    nat_3: str
    nat_4: str


class HarbingerStorageStorage(BaseModel):
    class Config:
        extra = Extra.forbid

    oracleData: Dict[str, OracleData]
    publicKey: Optional[str]