from decimal import Decimal
import json

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

    pool_metadata_raw = pool_origination.storage.metadata['contents']
    metadata = json.loads(bytes.fromhex(pool_metadata_raw))
    contract_address = pool_origination.data.originated_contract_address
    assert contract_address

    creator = pool_origination.data.sender_address
    manager = pool_origination.storage.manager
    approved_source = ctx.template_values['approved_source']

    is_approved = approved_source == creator == manager

    if is_approved:
        contracts_names = {contract.address: name for name, contract in ctx.config.contracts.items()}
        is_added_to_indexer = contract_address in contracts_names
        contract_name = contracts_names.get(contract_address)

        if not is_added_to_indexer:
            contract_name = f'pool_{contract_address}'
            await ctx.add_contract(name=contract_name, address=contract_address, typename='pool')

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
            is_disband_allow=storage['isDisbandAllow'],
            is_deposit_paused=storage['isDepositPaused'],
            name=metadata.get('name'),
            version=metadata.get('version'),
        )
        await pool.save()

        amt = pool_origination.data.amount
        initial_liquidity = from_mutez(amt) if amt else Decimal(0)
        total_liquidity = from_high_precision(storage['activeLiquidityF']) + initial_liquidity

        # TODO: consider using update_pool_state with last_state initiated with zeros to create first state?
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
            opg_hash=pool_origination.data.hash,
        )
        await pool_state.save()

    if not is_approved:
        ctx.logger.info("not approved pool: {contract_address}")
