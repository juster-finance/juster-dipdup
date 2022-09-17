from dipdup.context import HandlerContext
from dipdup.models import Origination

import juster.models as models
from juster.types.pool.storage import PoolStorage
from juster.utils import from_high_precision
from juster.utils import process_pool_shares


async def on_pool_origination(
    ctx: HandlerContext,
    pool_origination: Origination[PoolStorage],
) -> None:

    # TODO: making name from lines params // metadata?
    contract_address = pool_origination.data.originated_contract_address
    assert contract_address

    creator = pool_origination.data.sender_address
    manager = pool_origination.storage.manager
    approved_source = ctx.template_values['approved_source']

    is_approved = approved_source == creator == manager

    if is_approved:
        await ctx.add_contract(name=f'pool_{contract_address}', address=contract_address, typename='pool')

        await ctx.add_index(
            name=f'pool_{contract_address}',
            template='pool',
            values={
                'datasource': ctx.template_values['datasource'],
                'contract': f'pool_{contract_address}',
                'juster_core': ctx.template_values['juster_core'],
            },
        )

        # TODO: consider adding origination with amount > 0 case
        pool, _ = await models.Pool.get_or_create(address=contract_address)
        storage = pool_origination.data.storage
        pool_state = models.PoolState(
            pool=pool,
            timestamp=pool_origination.data.timestamp,
            level=pool_origination.data.level,
            counter=0,
            total_liquidity=from_high_precision(storage['activeLiquidityF']),
            total_shares=process_pool_shares(storage['totalShares']),
            active_liquidity=from_high_precision(storage['activeLiquidityF']),
            withdrawable_liquidity=from_high_precision(storage['withdrawableLiquidityF']),
            entry_liquidity=from_high_precision(storage['entryLiquidityF']),
        )
        await pool_state.save()

    if not is_approved:
        ctx.logger.info("not approved pool: {contract_address}")
