# generated by datamodel-codegen:
#   filename:  newEvent.json

from __future__ import annotations

from pydantic import BaseModel, Extra


class NewEventParameter(BaseModel):
    class Config:
        extra = Extra.forbid

    betsCloseTime: str
    currencyPair: str
    liquidityPercent: str
    measurePeriod: str
    targetDynamics: str
