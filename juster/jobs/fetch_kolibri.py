
from decimal import Decimal
from typing import Any, Dict
import aiohttp
from juster import models
from dipdup.context import DipDupContext
from datetime import datetime

async def fetch_kolibri(ctx: DipDupContext, args: Dict[str, Any]) -> None:
    async with aiohttp.ClientSession() as session:
        response = await session.get('https://oracle-data.kolibri.finance/data.json')
        data = await response.json()
        for symbol, price in data['prices'].items():
            await models.Quote(
                price=Decimal(price)*1000000,
                timestamp=datetime.utcnow().isoformat(),
                currency_pair=(await models.CurrencyPair.get_or_create(symbol=f'{symbol}-USD'))[0],
                source=models.QuoteSource.KOLIBRI,
            ).save()
