from decimal import Decimal
from email.policy import default
from enum import Enum

from tortoise import Model, fields

liquidityPrecision = 6
ratioPrecision = 8
sharePrecision = 8
targetDynamicsPrecision = 6


def to_liquidity(value):
    return int(value) / Decimal(10 ** liquidityPrecision)


def to_ratio(value):
    return int(value) / Decimal(10 ** ratioPrecision)


def to_share(value):
    return int(value) / Decimal(10 ** sharePrecision)


def to_dynamics(value):
    return int(value) / Decimal(10 ** targetDynamicsPrecision)


class EventStatus(Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class Symbol(Model):
    symbol = fields.CharField(max_length=16)


class Quote(Model):
    id = fields.IntField(pk=True)
    symbol = fields.ForeignKeyField("models.Symbol", "quotes")
    price = fields.BigIntField()
    timestamp = fields.DatetimeField()


class Event(Model):
    id = fields.IntField(pk=True)
    betsAgainstLiquidityPoolSum = fields.DecimalField(10, 6)
    betsCloseTime = fields.DatetimeField()
    betsForLiquidityPoolSum = fields.DecimalField(10, 6)
    closedDynamics = fields.DecimalField(10, targetDynamicsPrecision)
    closedOracleTime = fields.DatetimeField()
    closedRate = fields.DecimalField(10, ratioPrecision)
    createdTime = fields.DatetimeField()
    currencyPair = fields.ForeignKeyField("models.Symbol", "events")
    expirationFee = fields.DecimalField(10, 6)
    firstProviderAgainstSharesSum = fields.DecimalField(10, 6)
    firstProviderForSharesSum = fields.DecimalField(10, 6)
    isBetsForWin = fields.BooleanField()
    liquidityPercent = fields.DecimalField(10, liquidityPrecision)
    measureOracleStartTime = fields.DatetimeField()
    measurePeriod = fields.BigIntField()
    measureStartFee = fields.DecimalField(10, 6)
    oracleAddress = fields.TextField()
    rewardCallFee = fields.DecimalField(10, 6)
    startRate = fields.DecimalField(10, ratioPrecision)
    targetDynamics = fields.DecimalField(10, targetDynamicsPrecision)
    totalLiquidityAgainstSharesSum = fields.DecimalField(10, 6)
    totalLiquidityForSharesSum = fields.DecimalField(10, 6)
    totalLiquidityProvided = fields.DecimalField(10, 6)
    winAgainstProfitLossPerShare = fields.DecimalField(10, sharePrecision, default=0)
    winForProfitLossPerShare = fields.DecimalField(10, sharePrecision, default=0)

    user = fields.ForeignKeyField('models.User', 'events')
    totalBetsFor = fields.IntField(default=0)
    totalBetsAgainst = fields.IntField(default=0)
    status = fields.CharEnumField(EventStatus)


class User(Model):
    address = fields.TextField(pk=True)
    totalLiquidityProvided = fields.DecimalField(10, 6, default=0)
    totalEventsCreated = fields.IntField(default=0)
    totalBets = fields.IntField(default=0)
    totalDepositedBets = fields.DecimalField(10, 6, default=0)
    totalFeesCollected = fields.DecimalField(10, 6, default=0)
    totalWithdrawed = fields.DecimalField(10, 6, default=0)


class Ledger(Model):
    id = fields.IntField(pk=True)

    liquidityAgainstSharesLedger = fields.DecimalField(10, 6, default=0)
    liquidityForSharesLedger = fields.DecimalField(10, 6, default=0)
    providedLiquidityLedger = fields.DecimalField(10, 6, default=0)
    winAgainstProfitLossPerShareAtEntry = fields.DecimalField(10, sharePrecision, default=0)
    winForProfitLossPerShareAtEntry = fields.DecimalField(10, sharePrecision, default=0)

    betsAgainstWinningLedger = fields.DecimalField(10, 6, default=0)
    betsForWinningLedger = fields.DecimalField(10, 6, default=0)
    depositedBets = fields.DecimalField(10, 6, default=0)

    withdrawed = fields.BooleanField(default=False)

    event = fields.ForeignKeyField('models.Event', 'positions')
    user = fields.ForeignKeyField('models.User', 'positions')


class Bet(Model):
    id = fields.IntField(pk=True)

    isFor = fields.BooleanField()
    amount = fields.DecimalField(10, 6)
    reward = fields.DecimalField(10, 6)

    event = fields.ForeignKeyField('models.Event', 'bets')
    user = fields.ForeignKeyField('models.User', 'bets')
