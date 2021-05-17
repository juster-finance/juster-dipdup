from decimal import Decimal
from typing import Union


def from_mutez(mutez: Union[str, int]) -> Decimal:
    return Decimal(mutez) / (10 ** 6)
