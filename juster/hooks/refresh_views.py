from dipdup.context import HookContext


async def refresh_views(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('refresh_views')
