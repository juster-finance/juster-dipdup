# generated by datamodel-codegen:
#   filename:  storage.json

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Extra


class Key(BaseModel):
    class Config:
        extra = Extra.forbid

    address: str
    nat: str


class BetsAboveEqItem(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: str


class BetsBelowItem(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: str


class Config(BaseModel):
    class Config:
        extra = Extra.forbid

    expirationFee: str
    isEventCreationPaused: bool
    maxAllowedMeasureLag: str
    maxLiquidityPercent: str
    maxMeasurePeriod: str
    maxPeriodToBetsClose: str
    measureStartFee: str
    minLiquidityPercent: str
    minMeasurePeriod: str
    minPeriodToBetsClose: str
    oracleAddress: str
    providerProfitFee: str
    rewardCallFee: str
    rewardFeeSplitAfter: str


class DepositedBet(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: str


class DepositedLiquidityItem(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: str


class Events(BaseModel):
    class Config:
        extra = Extra.forbid

    betsCloseTime: str
    closedDynamics: Optional[str]
    closedOracleTime: Optional[str]
    closedRate: Optional[str]
    createdTime: str
    creator: str
    currencyPair: str
    expirationFee: str
    isBetsAboveEqWin: Optional[bool]
    isClosed: bool
    isForceMajeure: bool
    liquidityPercent: str
    maxAllowedMeasureLag: str
    measureOracleStartTime: Optional[str]
    measurePeriod: str
    measureStartFee: str
    oracleAddress: str
    poolAboveEq: str
    poolBelow: str
    rewardCallFee: str
    startRate: Optional[str]
    targetDynamics: str
    totalLiquidityShares: str


class IsWithdrawnItem(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: Dict[str, Any]


class LiquidityShare(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: str


class ProvidedLiquidityAboveEqItem(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: str


class ProvidedLiquidityBelowItem(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: str


class JusterStorage(BaseModel):
    class Config:
        extra = Extra.forbid

    bakingRewards: str
    betsAboveEq: List[BetsAboveEqItem]
    betsBelow: List[BetsBelowItem]
    closeCallId: Optional[str]
    config: Config
    depositedBets: List[DepositedBet]
    depositedLiquidity: List[DepositedLiquidityItem]
    events: Dict[str, Events]
    isWithdrawn: List[IsWithdrawnItem]
    liquidityPrecision: str
    liquidityShares: List[LiquidityShare]
    manager: str
    measurementStartCallId: Optional[str]
    metadata: Dict[str, str]
    nextEventId: str
    proposedManager: Optional[str]
    providedLiquidityAboveEq: List[ProvidedLiquidityAboveEqItem]
    providedLiquidityBelow: List[ProvidedLiquidityBelowItem]
    providerProfitFeePrecision: str
    ratioPrecision: str
    retainedProfits: str
    sharePrecision: str
    targetDynamicsPrecision: str
