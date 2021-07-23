from decimal import Decimal
from enum import Enum

from tortoise import Model, fields

liquidity_precision = 6
ratio_precision = 8
share_precision = 8
target_dynamics_precision = 6


def to_liquidity(value):
    return int(value) / Decimal(10 ** liquidity_precision)


def to_ratio(value):
    return int(value) / Decimal(10 ** ratio_precision)


def to_share(value):
    return int(value) / Decimal(10 ** share_precision)


def to_dynamics(value):
    return int(value) / Decimal(10 ** target_dynamics_precision)


class EventStatus(Enum):
    NEW = "NEW"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    CANCELED = "CANCELED"


class BetSide(Enum):
    ABOVE_EQ = "ABOVE_EQ"
    BELOW = "BELOW"


class CurrencyPair(Model):
    symbol = fields.CharField(max_length=16)


class Quote(Model):
    id = fields.IntField(pk=True)
    price = fields.BigIntField()
    timestamp = fields.DatetimeField()
    currency_pair = fields.ForeignKeyField("models.CurrencyPair", "quotes")


class Event(Model):
    id = fields.IntField(pk=True)
    currency_pair = fields.ForeignKeyField("models.CurrencyPair", "events")
    creator = fields.ForeignKeyField('models.User', 'events')
    status = fields.CharEnumField(EventStatus)
    winner_bets = fields.CharEnumField(BetSide, null=True)

    target_dynamics = fields.DecimalField(10, target_dynamics_precision)  # 1.1 == +10%, 0.8 == -20%
    measure_period = fields.BigIntField()  # interval in seconds
    bets_close_time = fields.DatetimeField()  # countdown

    start_rate = fields.DecimalField(10, ratio_precision, null=True)
    closed_rate = fields.DecimalField(10, ratio_precision, null=True)
    closed_dynamics = fields.DecimalField(10, target_dynamics_precision, null=True)

    measure_oracle_start_time = fields.DatetimeField(null=True)  # actual start time
    closed_oracle_time = fields.DatetimeField(null=True)  # actual stop time

    created_time = fields.DatetimeField(auto_now_add=True)
    pool_above_eq = fields.DecimalField(10, 6, default=Decimal('0'))  # available liquidity
    pool_below = fields.DecimalField(10, 6, default=Decimal('0'))  # and current ratio
    liquidity_percent = fields.DecimalField(10, liquidity_precision)  # used to calculate potential reward
    # Calculate: potentialReward(for) =
    # [1 - liquidityPercent * (now - createdTime) / (betsCloseTime - createdTime)] * (poolAgainst / (poolFor + amount))

    total_liquidity_shares = fields.DecimalField(16, share_precision, default=Decimal('0'))
    # Calculate: incomingShare = amount / (poolFor + poolAgainst)
    # Calculate: finalReward(for) = poolAgainst * (shares[own] / totalLiquidityShares) + providedLiquidityFor[own]
    
    total_bets_amount = fields.DecimalField(10, 6, default=Decimal('0'))
    total_liquidity_provided = fields.DecimalField(10, 6, default=Decimal('0'))

    positions: fields.ReverseRelation['Position']

    @property
    def winning_pool(self):
        return {
            BetSide.ABOVE_EQ: self.pool_above_eq,
            BetSide.BELOW: self.pool_below,
        }[self.winner_bets]

    @property
    def losing_pool(self):
        return {
            BetSide.BELOW: self.pool_above_eq,
            BetSide.ABOVE_EQ: self.pool_below,
        }[self.winner_bets]

    def set_winner_bets(self):
        assert self.closed_rate
        target_rate = self.start_rate * self.target_dynamics
        self.winner_bets = {
            True: BetSide.ABOVE_EQ,
            False: BetSide.BELOW,
        }[self.closed_rate >= target_rate]


class Bet(Model):
    id = fields.IntField(pk=True)
    side = fields.CharEnumField(BetSide)
    amount = fields.DecimalField(10, 6)
    reward = fields.DecimalField(10, 6)
    event = fields.ForeignKeyField('models.Event', 'bets')
    user = fields.ForeignKeyField('models.User', 'bets')


class Deposit(Model):
    id = fields.IntField(pk=True)
    amount_above_eq = fields.DecimalField(10, 6)
    amount_below = fields.DecimalField(10, 6)
    shares = fields.DecimalField(16, share_precision)
    event = fields.ForeignKeyField('models.Event', 'deposits')
    user = fields.ForeignKeyField('models.User', 'deposits')


class Withdrawal(Model):
    id = fields.IntField(pk=True)
    amount = fields.DecimalField(10, 6)
    event = fields.ForeignKeyField('models.Event', 'withdrawals')
    user = fields.ForeignKeyField('models.User', 'withdrawals')


class Position(Model):
    id = fields.IntField(pk=True)
    reward_above_eq = fields.DecimalField(10, 6, default=Decimal('0'))
    reward_below = fields.DecimalField(10, 6, default=Decimal('0'))
    liquidity_provided_above_eq = fields.DecimalField(10, 6, default=Decimal('0'))
    liquidity_provided_below = fields.DecimalField(10, 6, default=Decimal('0'))
    shares = fields.DecimalField(16, share_precision, default=Decimal('0'))
    withdrawn = fields.BooleanField(default=False)
    event = fields.ForeignKeyField('models.Event', 'positions')
    user = fields.ForeignKeyField('models.User', 'positions')

    def get_reward(self, side: BetSide) -> Decimal:
        return {
            BetSide.ABOVE_EQ: self.reward_above_eq,
            BetSide.BELOW: self.reward_below,
        }[side]


class User(Model):
    address = fields.TextField(pk=True)
    total_bets_count = fields.IntField(default=0)
    total_bets_amount = fields.DecimalField(10, 6, default=Decimal('0'))
    total_liquidity_provided = fields.DecimalField(10, 6, default=Decimal('0'))
    total_reward = fields.DecimalField(10, 6, default=Decimal('0'))
    total_withdrawn = fields.DecimalField(10, 6, default=Decimal('0'))
    total_fees_collected = fields.DecimalField(10, 6, default=Decimal('0'))
