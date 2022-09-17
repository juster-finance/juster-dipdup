# generated by datamodel-codegen:
#   filename:  bet.json

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Union

from pydantic import BaseModel
from pydantic import Extra


class BetItem(BaseModel):
    class Config:
        extra = Extra.forbid

    aboveEq: Dict[str, Any]


class BetItem1(BaseModel):
    class Config:
        extra = Extra.forbid

    below: Dict[str, Any]


class BetParameter(BaseModel):
    class Config:
        extra = Extra.forbid

    bet: Union[BetItem, BetItem1]
    eventId: str
    minimalWinAmount: str