from email.policy import default
from tortoise import Model, fields


class Quote(Model):
    id = fields.IntField(pk=True)
    symbol = fields.CharField(max_length=16)
    price = fields.BigIntField()
    timestamp = fields.DatetimeField()


class Event(Model):
    id = fields.IntField(pk=True)
    betsAgainstLiquidityPoolSum = fields.DecimalField(10, 6)
    betsCloseTime = fields.DatetimeField()
    betsForLiquidityPoolSum = fields.DecimalField(10, 6)
    closedDynamics = fields.BigIntField()
    closedOracleTime = fields.DatetimeField()
    closedRate = fields.BigIntField()
    createdTime = fields.DatetimeField()
    currencyPair = fields.TextField()
    expirationFee = fields.DecimalField(10, 6)
    firstProviderAgainstSharesSum = fields.DecimalField(10, 6)
    firstProviderForSharesSum = fields.DecimalField(10, 6)
    isBetsForWin = fields.BooleanField()
    isClosed = fields.BooleanField()
    isMeasurementStarted = fields.BooleanField()
    liquidityPercent = fields.BigIntField()
    liquidityPrecision = fields.BigIntField()
    measureOracleStartTime = fields.DatetimeField()
    measurePeriod = fields.BigIntField()
    measureStartFee = fields.DecimalField(10, 6)
    oracleAddress = fields.TextField()
    ratioPrecision = fields.BigIntField()
    rewardCallFee = fields.DecimalField(10, 6)
    sharePrecision = fields.BigIntField()
    startRate = fields.BigIntField()
    targetDynamics = fields.BigIntField()
    targetDynamicsPrecision = fields.BigIntField()
    totalLiquidityAgainstSharesSum = fields.DecimalField(10, 6)
    totalLiquidityForSharesSum = fields.DecimalField(10, 6)
    totalLiquidityProvided = fields.DecimalField(10, 6)
    winAgainstProfitLossPerShare = fields.BigIntField()
    winForProfitLossPerShare = fields.BigIntField()

    user = fields.ForeignKeyField('models.User')
    totalBetsFor = fields.IntField(default=0)
    totalBetsAgainst = fields.IntField(default=0)


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
    winAgainstProfitLossPerShareAtEntry = fields.BigIntField(default=0)
    winForProfitLossPerShareAtEntry = fields.BigIntField(default=0)

    betsAgainstWinningLedger = fields.DecimalField(10, 6, default=0)
    betsForWinningLedger = fields.DecimalField(10, 6, default=0)
    depositedBets = fields.DecimalField(10, 6, default=0)

    withdrawed = fields.BooleanField(default=False)

    event = fields.ForeignKeyField('models.Event')
    user = fields.ForeignKeyField('models.User')


class Bet(Model):
    id = fields.IntField(pk=True)

    isFor = fields.BooleanField()
    amount = fields.DecimalField(10, 6)
    reward = fields.DecimalField(10, 6)

    event = fields.ForeignKeyField('models.Event')
    user = fields.ForeignKeyField('models.User')
