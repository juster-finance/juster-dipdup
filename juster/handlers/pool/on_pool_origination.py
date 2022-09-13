
from juster.types.pool.storage import PoolStorage
from dipdup.models import Origination
from dipdup.context import HandlerContext

async def on_pool_origination(
    ctx: HandlerContext,
    pool_origination: Origination[PoolStorage],
) -> None:

    # TODO: making name from lines params // metadata?
    contract_address = pool_origination.data.originated_contract_address
    creator = pool_origination.data.sender_address
    manager = pool_origination.storage.manager
    approved_source = ctx.template_values['approved_source']

    is_approved = approved_source == creator == manager

    if is_approved:
        await ctx.add_contract(
            name=f'pool_{contract_address}',
            address=contract_address,
            typename='pool'
        )
        # TODO: juster_core added in add_line process...
        # !? bound to ctx.template_values?
        # - bound to add_line?
        # - do not bound to juster_core at all?
        # - other ways?

        await ctx.add_index(
            name=f'pool_{contract_address}',
            template='pool',
            values={
                'datasource': ctx.template_values['datasource'],
                'contract': f'pool_{contract_address}',
                'juster_core': ctx.template_values['juster_core'],
            },
        )

    if not is_approved:
        ctx.logger.info("not approved pool: {contract_address}")

