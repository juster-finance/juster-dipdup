# generated by datamodel-codegen:
#   filename:  newEvent.json

from __future__ import annotations

from pydantic import BaseModel


class NewEventParameter(BaseModel):
    betsCloseTime: str
    currencyPair: str
    liquidityPercent: str
    measurePeriod: str
    targetDynamics: str