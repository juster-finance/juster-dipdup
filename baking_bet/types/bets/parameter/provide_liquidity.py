# generated by datamodel-codegen:
#   filename:  provideLiquidity.json

from __future__ import annotations

from pydantic import BaseModel


class ProvideLiquidityParameter(BaseModel):
    eventId: str
    expectedRatioAboveEq: str
    expectedRatioBelow: str
    maxSlippage: str
