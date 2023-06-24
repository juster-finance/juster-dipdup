from decimal import Decimal

from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.pool.parameter.add_line import AddLineParameter
from juster.types.pool.storage import PoolStorage
from juster.utils import get_line
from juster.utils import parse_datetime


async def on_add_line(
    ctx: HandlerContext,
    add_line: Transaction[AddLineParameter, PoolStorage],
) -> None:
    line_id, line_diff = get_line(add_line.storage)

    pool_address = add_line.data.target_address
    pool = await models.Pool.get(address=pool_address)

    currency_pair, _ = await models.CurrencyPair.get_or_create(symbol=line_diff.currencyPair)

    line = models.PoolLine(
        pool_line_id=f'{pool.address}-{line_id}',
        pool=pool,
        line_id=line_id,
        last_bets_close_time=parse_datetime(line_diff.lastBetsCloseTime),
        max_events=int(line_diff.maxEvents),
        currency_pair=currency_pair,
        liquidity_percent=models.to_liquidity(line_diff.liquidityPercent),
        measure_period=int(line_diff.measurePeriod),
        rate_above_eq=Decimal(line_diff.rateAboveEq),
        rate_below=Decimal(line_diff.rateBelow),
        target_dynamics=models.to_dynamics(line_diff.targetDynamics),
        is_paused=line_diff.isPaused,
    )
    await line.save()
