# dipdup: ignore
# generated by datamodel-codegen:
#   filename:  oracleData_value.json

from __future__ import annotations

from pydantic import BaseModel


class OracleDataValue(BaseModel):
    timestamp_0: str
    timestamp_1: str
    nat_0: str # O
    nat_1: str # H
    nat_2: str # L
    nat_3: str # C
    nat_4: str # V