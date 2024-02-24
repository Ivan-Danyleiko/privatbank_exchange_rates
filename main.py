import sys
from datetime import datetime, timedelta
import platform
import aiohttp
import asyncio
import json


class HttpError(Exception):
    pass


async def req(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    raise HttpError(f"Error status: {resp.status} for {url}")
        except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:
            raise HttpError(f"Connection error {url}", str(err))


async def main(num_of_days):
    num_of_days = min(int(num_of_days), 10)
    result = []

    for i in range(num_of_days):
        d = datetime.now() - timedelta(days=i)
        shift = d.strftime("%d.%m.%Y")
        try:
            response = await req(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')

            exchange_rates = response.get('exchangeRate', [])
            euro_rate = next((rate for rate in exchange_rates if rate['currency'] == 'EUR'), None)
            usd_rate = next((rate for rate in exchange_rates if rate['currency'] == 'USD'), None)

            result.append({
                shift: {
                    'EUR': {'sale': euro_rate['saleRate'], 'purchase': euro_rate['purchaseRate']},
                    'USD': {'sale': usd_rate['saleRate'], 'purchase': usd_rate['purchaseRate']}
                }
            })
        except HttpError as err:
            print(err)

    return result

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main(sys.argv[1]))
    print(json.dumps(r, indent=2, ensure_ascii=False))

