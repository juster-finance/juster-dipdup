from datetime import datetime
from decimal import ROUND_DOWN
from decimal import ROUND_UP
from decimal import Context
from decimal import Decimal
from typing import Optional
from typing import Tuple
from typing import Union

import strict_rfc3339  # type: ignore
from dipdup.models import OperationData

import juster.models as models
from juster.types.juster.storage import Events
from juster.types.juster.storage import JusterStorage
from juster.types.pool.storage import Entries
from juster.types.pool.storage import Events as PoolEvents
from juster.types.pool.storage import PoolStorage

default_quantize_precision = Decimal('1')
mutez = Decimal('0.000001')
high_precision = Decimal('0.000000000001')
default_zero = Decimal('0')


def from_mutez(mutez: Union[str, int]) -> Decimal:
    return Decimal(mutez) / (10**6)


def from_high_precision(value: Union[str, int]) -> Decimal:
    return Decimal(value) * high_precision


def get_event(storage: JusterStorage) -> Tuple[int, Events]:
    assert len(storage.events) == 1
    event_id = int(next(iter(storage.events)))
    event_diff = storage.events[str(event_id)]
    return event_id, event_diff


def parse_datetime(value: str) -> datetime:
    return datetime.utcfromtimestamp(strict_rfc3339.rfc3339_to_timestamp(value))


def get_entry(storage: PoolStorage) -> Tuple[int, Entries]:
    assert len(storage.entries) == 1
    entry_id = int(next(iter(storage.entries)))
    entry_diff = storage.entries[str(entry_id)]
    return entry_id, entry_diff


def get_shares(storage: PoolStorage) -> Tuple[str, Decimal]:
    assert len(storage.shares) == 1
    shares_provider = next(iter(storage.shares))
    shares_diff = storage.shares[shares_provider]
    return shares_provider, process_pool_shares(shares_diff)


def get_pool_event(storage: PoolStorage) -> Tuple[int, PoolEvents]:
    assert len(storage.events) == 1
    pool_event_id = int(next(iter(storage.events)))
    pool_event_diff = storage.events[str(pool_event_id)]
    return pool_event_id, pool_event_diff


def process_pool_shares(raw: Union[str, int]) -> Decimal:
    return Decimal(raw) / (10**models.pool_share_precision)


def quantize_down(value: Decimal, precision: Decimal = default_quantize_precision) -> Decimal:
    return Decimal(value).quantize(precision, context=Context(rounding=ROUND_DOWN))


def quantize_up(value: Decimal, precision: Decimal = default_quantize_precision) -> Decimal:
    return Decimal(value).quantize(precision, context=Context(rounding=ROUND_UP))


async def update_pool_state(
    pool: models.Pool,
    action: models.PoolHistoryAction,
    data: OperationData,
    total_liquidity_diff: Decimal = default_zero,
    total_shares_diff: Decimal = default_zero,
    active_liquidity_diff: Decimal = default_zero,
    withdrawable_liquidity_diff: Decimal = default_zero,
    entry_liquidity_diff: Decimal = default_zero,
    affected_user: Optional[models.User] = None,
    affected_event: Optional[models.PoolEvent] = None,
    affected_entry: Optional[models.EntryLiquidity] = None,
    affected_claim: Optional[models.Claim] = None,
):

    # TODO: do not create new state if nothing changed?
    last_state = await pool.get_last_state()

    total_liquidity = last_state.total_liquidity + total_liquidity_diff
    total_shares = last_state.total_shares + total_shares_diff
    share_price = None if total_shares == Decimal(0) else total_liquidity / total_shares

    new_state = models.PoolState(
        pool=pool,
        timestamp=data.timestamp,
        level=data.level,
        counter=last_state.counter + 1,
        total_liquidity=total_liquidity,
        total_shares=total_shares,
        active_liquidity=last_state.active_liquidity + active_liquidity_diff,
        withdrawable_liquidity=last_state.withdrawable_liquidity + withdrawable_liquidity_diff,
        entry_liquidity=last_state.entry_liquidity + entry_liquidity_diff,
        share_price=share_price,
        action=action,
        total_liquidity_diff=total_liquidity_diff,
        total_shares_diff=total_shares_diff,
        active_liquidity_diff=active_liquidity_diff,
        withdrawable_liquidity_diff=withdrawable_liquidity_diff,
        entry_liquidity_diff=entry_liquidity_diff,
        affected_user=affected_user,
        affected_event=affected_event,
        affected_entry=affected_entry,
        affected_claim=affected_claim,
        opg_hash=data.hash,
    )

    assert new_state.total_liquidity >= Decimal(0), "wrong state: negative total liquidity"
    assert new_state.total_shares >= Decimal(0), "wrong state: negative total shares"
    assert new_state.active_liquidity >= Decimal(0), "wrong state: negative active liquidity"
    assert new_state.withdrawable_liquidity >= Decimal(0), "wrong state: negative withdrawable liquidity"
    assert new_state.entry_liquidity >= Decimal(0), "wrong state: negative entry liquidity"

    await new_state.save()
