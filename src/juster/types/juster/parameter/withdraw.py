# generated by datamodel-codegen:
#   filename:  withdraw.json

from __future__ import annotations

from pydantic import BaseModel
from pydantic import Extra


class WithdrawParameter(BaseModel):
    class Config:
        extra = Extra.forbid

    eventId: str
    participantAddress: str