# generated by datamodel-codegen:
#   filename:  withdrawLiquidity.json

from __future__ import annotations

from typing import List

from pydantic import BaseModel
from pydantic import Extra


class WithdrawLiquidityParameterItem(BaseModel):
    class Config:
        extra = Extra.forbid

    eventId: str
    positionId: str


class WithdrawLiquidityParameter(BaseModel):
    __root__: List[WithdrawLiquidityParameterItem]