# generated by datamodel-codegen:
#   filename:  withdrawClaims.json

from __future__ import annotations

from typing import List

from pydantic import BaseModel
from pydantic import Extra


class WithdrawClaimsParameterItem(BaseModel):
    class Config:
        extra = Extra.forbid

    eventId: str
    provider: str


class WithdrawClaimsParameter(BaseModel):
    __root__: List[WithdrawClaimsParameterItem]
