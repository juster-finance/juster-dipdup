from dipdup.context import HandlerContext
from dipdup.models import Transaction

import juster.models as models
from juster.types.juster.parameter.provide_liquidity import ProvideLiquidityParameter
from juster.types.juster.storage import JusterStorage
from juster.utils import from_mutez
from juster.utils import get_event


async def on_provide_liquidity(
    ctx: HandlerContext,
    provide_liquidity: Transaction[ProvideLiquidityParameter, JusterStorage],
) -> None:
    event_id, event_diff = get_event(provide_liquidity.storage)
    assert provide_liquidity.data.amount
    amount = from_mutez(provide_liquidity.data.amount)

    event = await models.Event.filter(id=event_id).get()
    amount_above_eq = from_mutez(event_diff.poolAboveEq) - event.pool_above_eq
    amount_below = from_mutez(event_diff.poolBelow) - event.pool_below
    # TODO: liquidity shares use 10**8 and from_mutez uses 10**6 [minor bug]:
    new_liquidity_shares = from_mutez(event_diff.totalLiquidityShares)
    liquidity_shares_added = new_liquidity_shares - event.total_liquidity_shares
    event.total_liquidity_shares = new_liquidity_shares
    event.pool_above_eq = from_mutez(event_diff.poolAboveEq)
    event.pool_below = from_mutez(event_diff.poolBelow)
    event.total_liquidity_provided += amount
    event.total_value_locked += amount
    await event.save()

    user, _ = await models.User.get_or_create(address=provide_liquidity.data.sender_address)
    user.total_liquidity_provided += amount
    await user.save()

    position, _ = await models.Position.get_or_create(
        event=event,
        user=user,
    )
    position.shares += liquidity_shares_added
    position.liquidity_provided_above_eq += amount_above_eq
    position.liquidity_provided_below += amount_below
    await position.save()

    await models.Deposit(
        id=provide_liquidity.data.id,  # TzKT operation ID
        opg_hash=provide_liquidity.data.hash,
        created_time=provide_liquidity.data.timestamp,
        event=event,
        user=user,
        amount_above_eq=amount_above_eq,
        amount_below=amount_below,
        shares=liquidity_shares_added,
    ).save()

    currency_pair = await event.currency_pair
    currency_pair.total_volume += amount
    currency_pair.total_value_locked += amount
    await currency_pair.save()
