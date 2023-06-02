from typing import Dict
import string
import random


class NFTProfitParams:
    @staticmethod
    async def get_parms_data(
        wallet: str, contract_address: str, api_key: str
    ) -> Dict[str, str]:
        return {
            "module": "account",
            "action": "tokennfttx",
            "contractaddress": contract_address,
            "address": wallet,
            "sort": "asc",
            "apikey": api_key,
        }

    @staticmethod
    async def get_parms_purchase_price(hash: str, api_key: str) -> Dict[str, str]:
        return {
            "module": "proxy",
            "action": "eth_getTransactionByHash",
            "txhash": hash,
            "apikey": api_key,
        }

    @staticmethod
    async def get_parms_sale_price(wallet: str, api_key: str) -> Dict[str, str]:
        return {
            "module": "account",
            "action": "txlistinternal",
            "address": wallet,
            "apikey": api_key,
        }


class NFTProfitHeaders:
    @staticmethod
    def id_generator(size):
        return "".join(random.choice(string.digits) for _ in range(size))

    @staticmethod
    async def get_buy_rate_limit_bypass_header():
        return {
            "authority": "api.etherscan.io",
            "X-Forwarded-For": f"{NFTProfitHeaders.id_generator(3)}.{NFTProfitHeaders.id_generator(1)}.{NFTProfitHeaders.id_generator(3)}.{NFTProfitHeaders.id_generator(3)}",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "referer": "https://api.etherscan.io/apis",
            "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        }
