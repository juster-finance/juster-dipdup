from datetime import datetime
from decimal import Decimal
from enum import Enum

from dipdup.datasources.coinbase.models import CandleInterval
from dipdup.models import Model
from tortoise import ForeignKeyFieldInstance
from tortoise import fields

liquidity_precision = 6
ratio_precision = 8
share_precision = 8
target_dynamics_precision = 6


def to_liquidity(value):
    return int(value) / Decimal(10**liquidity_precision)


def to_ratio(value):
    return int(value) / Decimal(10**ratio_precision)


def to_share(value):
    return int(value) / Decimal(10**share_precision)


def to_dynamics(value):
    return int(value) / Decimal(10**target_dynamics_precision)


def to_decimal(value):
    return Decimal(value) / Decimal(10**6)


class EventStatus(Enum):
    NEW = "NEW"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    CANCELED = "CANCELED"


class BetSide(Enum):
    ABOVE_EQ = "ABOVE_EQ"
    BELOW = "BELOW"


class Source(Enum):
    HARBINGER = 'HARBINGER'
    COINBASE = 'COINBASE'
    MERGED = 'MERGED'


class WithdrawalType(Enum):
    MANUAL = 'MANUAL'
    THIRD_PARTY = 'THIRD_PARTY'


class CurrencyPair(Model):
    id = fields.IntField(pk=True)
    symbol = fields.CharField(max_length=16)
    total_events = fields.IntField(default=0)
    total_volume = fields.DecimalField(decimal_places=6, max_digits=16, default=0)
    total_value_locked = fields.DecimalField(decimal_places=6, max_digits=16, default=0)


def candle_pk(source: Source, currency_pair_id: int, until: datetime) -> int:
    src = {Source.COINBASE: 0, Source.HARBINGER: 1}
    return int(until.timestamp()) * 100 + currency_pair_id * 10 + src[source]


class Candle(Model):
    id = fields.BigIntField(pk=True)
    currency_pair: ForeignKeyFieldInstance[CurrencyPair] = fields.ForeignKeyField("models.CurrencyPair", "candles")
    source = fields.CharEnumField(Source)
    since = fields.DatetimeField()
    until = fields.DatetimeField()
    interval = fields.CharEnumField(CandleInterval)
    open = fields.DecimalField(decimal_places=6, max_digits=16)
    high = fields.DecimalField(decimal_places=6, max_digits=16)
    low = fields.DecimalField(decimal_places=6, max_digits=16)
    close = fields.DecimalField(decimal_places=6, max_digits=16)
    volume = fields.DecimalField(decimal_places=6, max_digits=16)


class User(Model):
    address = fields.CharField(36, pk=True)
    total_bets_count = fields.IntField(default=0)
    total_bets_amount = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))
    total_liquidity_provided = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))
    total_reward = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))
    total_provider_reward = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))
    total_withdrawn = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))
    total_fees_collected = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))


class Event(Model):
    id = fields.BigIntField(pk=True)
    currency_pair: ForeignKeyFieldInstance[CurrencyPair] = fields.ForeignKeyField("models.CurrencyPair", "events")
    creator: ForeignKeyFieldInstance[User] = fields.ForeignKeyField('models.User', 'events')
    status = fields.CharEnumField(EventStatus)
    winner_bets = fields.CharEnumField(BetSide, null=True)

    target_dynamics = fields.DecimalField(max_digits=18, decimal_places=target_dynamics_precision)  # 1.1 == +10%, 0.8 == -20%
    measure_period = fields.BigIntField()  # interval in seconds
    bets_close_time = fields.DatetimeField()  # countdown

    start_rate = fields.DecimalField(18, decimal_places=ratio_precision, null=True)
    closed_rate = fields.DecimalField(18, decimal_places=ratio_precision, null=True)
    closed_dynamics = fields.DecimalField(max_digits=18, decimal_places=target_dynamics_precision, null=True)

    measure_oracle_start_time = fields.DatetimeField(null=True)  # actual start time
    closed_oracle_time = fields.DatetimeField(null=True)  # actual stop time

    created_time = fields.DatetimeField()
    pool_above_eq = fields.DecimalField(decimal_places=6, max_digits=16, default=Decimal('0'))  # available liquidity
    pool_below = fields.DecimalField(decimal_places=6, max_digits=16, default=Decimal('0'))  # and current ratio
    liquidity_percent = fields.DecimalField(max_digits=18, decimal_places=liquidity_precision)  # used to calculate potential reward
    # Calculate: potentialReward(for) =
    # [1 - liquidityPercent * (now - createdTime) / (betsCloseTime - createdTime)] * (poolAgainst / (poolFor + amount))

    total_liquidity_shares = fields.DecimalField(max_digits=18, decimal_places=share_precision, default=Decimal('0'))
    # Calculate: incomingShare = amount / (poolFor + poolAgainst)
    # Calculate: finalReward(for) = poolAgainst * (shares[own] / totalLiquidityShares) + providedLiquidityFor[own]

    total_bets_amount = fields.DecimalField(decimal_places=6, max_digits=16, default=Decimal('0'))
    total_liquidity_provided = fields.DecimalField(decimal_places=6, max_digits=16, default=Decimal('0'))
    total_value_locked = fields.DecimalField(decimal_places=6, max_digits=16, default=Decimal('0'))

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
    id = fields.BigIntField(pk=True)
    opg_hash = fields.CharField(max_length=51)
    created_time = fields.DatetimeField()
    side = fields.CharEnumField(BetSide)
    amount = fields.DecimalField(decimal_places=6, max_digits=16)
    reward = fields.DecimalField(decimal_places=6, max_digits=16)
    event: ForeignKeyFieldInstance[Event] = fields.ForeignKeyField('models.Event', 'bets')
    user: ForeignKeyFieldInstance[User] = fields.ForeignKeyField('models.User', 'bets')


class Deposit(Model):
    id = fields.BigIntField(pk=True)
    opg_hash = fields.CharField(max_length=51)
    created_time = fields.DatetimeField()
    amount_above_eq = fields.DecimalField(decimal_places=6, max_digits=16)
    amount_below = fields.DecimalField(decimal_places=6, max_digits=16)
    shares = fields.DecimalField(16, share_precision)
    event: ForeignKeyFieldInstance[Event] = fields.ForeignKeyField('models.Event', 'deposits')
    user: ForeignKeyFieldInstance[User] = fields.ForeignKeyField('models.User', 'deposits')


class Withdrawal(Model):
    id = fields.BigIntField(pk=True)
    opg_hash = fields.CharField(max_length=51)
    created_time = fields.DatetimeField()
    amount = fields.DecimalField(decimal_places=6, max_digits=16)
    event: ForeignKeyFieldInstance[Event] = fields.ForeignKeyField('models.Event', 'withdrawals')
    user: ForeignKeyFieldInstance[User] = fields.ForeignKeyField('models.User', 'withdrawals')
    fee_collector: ForeignKeyFieldInstance[User] = fields.ForeignKeyField('models.User', 'third_party_withdrawals', null=True)
    type = fields.CharEnumField(WithdrawalType)


class Position(Model):
    id = fields.BigIntField(pk=True)
    reward_above_eq = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))
    reward_below = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))
    liquidity_provided_above_eq = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))
    liquidity_provided_below = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))
    shares = fields.DecimalField(max_digits=18, decimal_places=share_precision, default=Decimal('0'))
    withdrawn = fields.BooleanField(default=False)
    event: ForeignKeyFieldInstance[Event] = fields.ForeignKeyField('models.Event', 'positions')
    user: ForeignKeyFieldInstance[User] = fields.ForeignKeyField('models.User', 'positions')
    value = fields.DecimalField(decimal_places=6, max_digits=32, default=Decimal('0'))

    def get_reward(self, side: BetSide) -> Decimal:
        return {
            BetSide.ABOVE_EQ: self.reward_above_eq,
            BetSide.BELOW: self.reward_below,
        }[side]

    def get_provider_reward(self, side: BetSide, event: Event) -> Decimal:
        if side == BetSide.ABOVE_EQ:
            profit = self.shares * event.pool_below / event.total_liquidity_shares - self.liquidity_provided_below  # type: ignore
        else:
            profit = self.shares * event.pool_above_eq / event.total_liquidity_shares - self.liquidity_provided_above_eq  # type: ignore

        profit *= 1 - event.liquidity_percent  # type: ignore
        profit += max(self.liquidity_provided_below, self.liquidity_provided_above_eq)  # type: ignore
        return profit
