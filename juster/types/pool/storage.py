# generated by datamodel-codegen:
#   filename:  storage.json

from __future__ import annotations

from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Extra


class Key(BaseModel):
    class Config:
        extra = Extra.forbid

    eventId: str
    positionId: str


class Value(BaseModel):
    class Config:
        extra = Extra.forbid

    provider: str
    shares: str


class Claim(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: Value


class Entries(BaseModel):
    class Config:
        extra = Extra.forbid

    acceptAfter: str
    amount: str
    provider: str


class Events(BaseModel):
    class Config:
        extra = Extra.forbid

    createdCounter: str
    lockedShares: str
    provided: str
    result: Optional[str]
    totalShares: str


class Lines(BaseModel):
    class Config:
        extra = Extra.forbid

    advanceTime: str
    betsPeriod: str
    currencyPair: str
    isPaused: bool
    juster: str
    lastBetsCloseTime: str
    liquidityPercent: str
    maxEvents: str
    measurePeriod: str
    minBettingPeriod: str
    rateAboveEq: str
    rateBelow: str
    targetDynamics: str


class Positions(BaseModel):
    class Config:
        extra = Extra.forbid

    addedCounter: str
    entryLiquidityUnits: str
    provider: str
    shares: str


class Withdrawals(BaseModel):
    class Config:
        extra = Extra.forbid

    liquidityUnits: str
    positionId: str
    shares: str


class PoolStorage(BaseModel):
    class Config:
        extra = Extra.forbid

    activeEvents: Dict[str, str]
    activeLiquidity: str
    claims: List[Claim]
    counter: str
    entries: Dict[str, Entries]
    entryLiquidity: str
    entryLockPeriod: str
    events: Dict[str, Events]
    isDepositPaused: bool
    lines: Dict[str, Lines]
    liquidityUnits: str
    manager: str
    maxEvents: str
    metadata: Dict[str, str]
    nextEntryId: str
    nextLineId: str
    nextLiquidity: str
    nextPositionId: str
    nextWithdrawalId: str
    positions: Dict[str, Positions]
    precision: str
    proposedManager: str
    totalShares: str
    withdrawableLiquidity: str
    withdrawals: Dict[str, Withdrawals]
