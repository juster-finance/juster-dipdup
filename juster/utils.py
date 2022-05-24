from datetime import datetime
from decimal import ROUND_DOWN
from decimal import Context
from decimal import Decimal
from typing import Tuple
from typing import Union

import strict_rfc3339  # type: ignore

import juster.models as models
from juster.types.juster.storage import Events
from juster.types.juster.storage import JusterStorage
from juster.types.pool.storage import Entries
from juster.types.pool.storage import Events as PoolEvents
from juster.types.pool.storage import PoolStorage
from juster.types.pool.storage import Positions

default_quantize_precision = Decimal('1')


def from_mutez(mutez: Union[str, int]) -> Decimal:
    return Decimal(mutez) / (10**6)


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


def get_position(storage: PoolStorage) -> Tuple[int, Positions]:
    assert len(storage.positions) == 1
    position_id = int(next(iter(storage.positions)))
    position_diff = storage.positions[str(position_id)]
    return position_id, position_diff


def get_pool_event(storage: PoolStorage) -> Tuple[int, PoolEvents]:
    assert len(storage.events) == 1
    pool_event_id = int(next(iter(storage.events)))
    pool_event_diff = storage.events[str(pool_event_id)]
    return pool_event_id, pool_event_diff


def process_pool_shares(raw: Union[str, int]) -> Decimal:
    return Decimal(raw) / (10**models.pool_share_precision)


def quantize_down(value: Decimal, precision: Decimal = default_quantize_precision) -> Decimal:
    return Decimal(value).quantize(precision, context=Context(rounding=ROUND_DOWN))
