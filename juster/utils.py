from decimal import Decimal
from typing import Union, Tuple

from juster.types.juster.storage import JusterStorage, Events


def from_mutez(mutez: Union[str, int]) -> Decimal:
    return Decimal(mutez) / (10 ** 6)


def get_event(storage: JusterStorage) -> Tuple[int, Events]:
    assert len(storage.events) == 1
    event_id = int(next(iter(storage.events)))
    event_diff = storage.events[str(event_id)]
    return event_id, event_diff