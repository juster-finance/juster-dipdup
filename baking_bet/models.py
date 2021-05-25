from decimal import Decimal
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
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    CANCELED = "CANCELED"


class BetSide(Enum):
    FOR = "FOR"
    AGAINST = "AGAINST"


class CurrencyPair(Model):
    symbol = fields.CharField(max_length=16)


class Quote(Model):
    id = fields.IntField(pk=True)
    price = fields.BigIntField()
    timestamp = fields.DatetimeField()
    currencyPair = fields.ForeignKeyField("models.CurrencyPair", "quotes")


class Event(Model):
    id = fields.IntField(pk=True)
    currencyPair = fields.ForeignKeyField("models.CurrencyPair", "events")
    status = fields.CharEnumField(EventStatus)

    targetDynamics = fields.DecimalField(10, targetDynamicsPrecision)  # 1.1 == +10%, 0.8 == -20%
    measurePeriod = fields.BigIntField()  # interval in seconds
    betsCloseTime = fields.DatetimeField()  # countdown

    startRate = fields.DecimalField(10, ratioPrecision)
    closedRate = fields.DecimalField(10, ratioPrecision, null=True)

    measureOracleStartTime = fields.DatetimeField(null=True)  # actual start time
    closedOracleTime = fields.DatetimeField(null=True)  # actual stop time

    createdTime = fields.DatetimeField(auto_now_add=True)
    poolFor = fields.DecimalField(10, 6, default=Decimal('0'))  # available liquidity
    poolAgainst = fields.DecimalField(10, 6, default=Decimal('0'))  # and current ratio
    liquidityPercent = fields.DecimalField(10, liquidityPrecision)  # used to calculate potential reward
    # Calculate: potentialReward(for) =
    # [1 - liquidityPercent * (now - createdTime) / (betsCloseTime - createdTime)] * (poolAgainst / (poolFor + amount))

    totalLiquidityShares = fields.DecimalField(10, sharePrecision, default=Decimal('0'))
    # Calculate: incomingShare = amount / (poolFor + poolAgainst)
    # Calculate: finalReward(for) = poolAgainst * (shares[own] / totalLiquidityShares) + providedLiquidityFor[own]
    
    totalBetsAmount = fields.DecimalField(10, 6, default=Decimal('0'))
    totalLiquidityProvided = fields.DecimalField(10, 6, default=Decimal('0'))


class Bet(Model):
    id = fields.IntField(pk=True)
    side = fields.CharEnumField(BetSide)
    amount = fields.DecimalField(10, 6)
    reward = fields.DecimalField(10, 6)
    event = fields.ForeignKeyField('models.Event', 'bets')
    user = fields.ForeignKeyField('models.User', 'bets')


class Deposit(Model):
    id = fields.IntField(pk=True)
    amount = fields.DecimalField(10, 6)
    shares = fields.DecimalField(10, sharePrecision)
    event = fields.ForeignKeyField('models.Event', 'deposits')
    user = fields.ForeignKeyField('models.User', 'deposits')


class Withdrawal(Model):
    id = fields.IntField(pk=True)
    amount = fields.DecimalField(10, 6)
    event = fields.ForeignKeyField('models.Event', 'withdrawals')
    user = fields.ForeignKeyField('models.User', 'withdrawals')


class Position(Model):
    id = fields.IntField(pk=True)
    rewardFor = fields.DecimalField(10, 6, default=Decimal('0'))
    rewardAgainst = fields.DecimalField(10, 6, default=Decimal('0'))
    shares = fields.DecimalField(10, sharePrecision, default=Decimal('0'))
    withdrawn = fields.BooleanField(default=False)
    event = fields.ForeignKeyField('models.Event', 'positions')
    user = fields.ForeignKeyField('models.User', 'positions')


class User(Model):
    address = fields.TextField(pk=True)
    totalBetsCount = fields.IntField(default=0)
    totalBetsAmount = fields.DecimalField(10, 6, default=Decimal('0'))
    totalLiquidityProvided = fields.DecimalField(10, 6, default=Decimal('0'))
    totalReward = fields.DecimalField(10, 6, default=Decimal('0'))
    totalWithdrawn = fields.DecimalField(10, 6, default=Decimal('0'))
