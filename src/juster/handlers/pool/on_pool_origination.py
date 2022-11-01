from decimal import Decimal

from dipdup.context import HandlerContext
from dipdup.models import Origination

import juster.models as models
from juster.types.pool.storage import PoolStorage
from juster.utils import from_high_precision
from juster.utils import from_mutez
from juster.utils import process_pool_shares


async def on_pool_origination(
    ctx: HandlerContext,
    pool_origination: Origination[PoolStorage],
) -> None:

    # TODO: making name from lines params // metadata?
    contract_address = pool_origination.data.originated_contract_address
    assert contract_address
    # TODO: remove this hotfix that disables indexing for contract with >0 origination balance
    if contract_address == 'KT18yRWV3SxjQXTHAmYMrsVCxapDjAyRc6NX':
        return

    creator = pool_origination.data.sender_address
    manager = pool_origination.storage.manager
    approved_source = ctx.template_values['approved_source']

    is_approved = approved_source == creator == manager

    if is_approved:
        pool_contract_sample = ctx.config.contracts['pool_contract_sample'].address
        contract_name = f'pool_{contract_address}'

        # TODO: get contract name if it is in ctx.config contracts? (independent on its name)
        # pool_contract_sample is one of the contracts to be indexed:
        if not contract_address == pool_contract_sample:
            await ctx.add_contract(name=contract_name, address=contract_address, typename='pool')
        else:
            contract_name = 'pool_contract_sample'

        await ctx.add_index(
            name=contract_name,
            template='pool',
            values={
                'datasource': ctx.template_values['datasource'],
                'contract': contract_name,
                'juster_core': ctx.template_values['juster_core'],
            },
        )

        storage = pool_origination.data.storage
        pool = await models.Pool(
            address=contract_address,
            entry_lock_period=int(storage['entryLockPeriod']),
        )
        await pool.save()

        amt = pool_origination.data.amount
        initial_liquidity = from_mutez(amt) if amt else Decimal(0)
        total_liquidity = from_high_precision(storage['activeLiquidityF']) + initial_liquidity

        pool_state = models.PoolState(
            pool=pool,
            action=models.PoolHistoryAction.POOL_ORIGINATED,
            timestamp=pool_origination.data.timestamp,
            level=pool_origination.data.level,
            counter=0,
            total_liquidity=total_liquidity,
            total_shares=process_pool_shares(storage['totalShares']),
            active_liquidity=from_high_precision(storage['activeLiquidityF']),
            withdrawable_liquidity=from_high_precision(storage['withdrawableLiquidityF']),
            entry_liquidity=from_high_precision(storage['entryLiquidityF']),
        )
        await pool_state.save()

    if not is_approved:
        ctx.logger.info("not approved pool: {contract_address}")
