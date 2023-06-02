import requests
from utils.profit_webhook import NFTWebhook
from utils.profit_calculations import NFTCalculations
from api_calls.opensea_data import NFTOpensea
import asyncio
import time
import aiohttp
from typing import Dict, Tuple, Optional, Callable, List, Iterable, Union
from utils.data_objects import User_Info, User_Data
from utils.request_componesnts import NFTProfitParams, NFTProfitHeaders
from ratelimit import limits, RateLimitException, sleep_and_retry

from constants.settings import ETHERSCAN_API_KEY


ONE_SECOND = 1
MAX_CALLS_PER_SECOND = 15


class NFTProfit:
    @staticmethod
    async def log_evenets(message: str):
        print(message)

    @staticmethod
    async def get_users_data(  ###async it
        users_info: User_Info,
    ) -> List[dict]:
        json_dictionary: list = []
        for wallet in users_info.wallet_address:
            response = requests.get(
                f"https://api.etherscan.io/api",
                params=await NFTProfitParams.get_parms_data(
                    wallet,
                    users_info.contract_address,
                    users_info.api_key,
                ),
            )
            json_dictionary = json_dictionary + list(response.json()["result"])
        return json_dictionary  # response.json()["result"]

    @staticmethod
    async def get_base_data(
        users_info: User_Info,
        users_data: User_Data,
    ) -> str:
        await NFTProfit.log_evenets(
            "Getting base data for " + str(users_info.contract_address)
        )
        project_name = None
        for item in users_data.transactions_raw:
            if item["contractAddress"] == users_info.contract_address:
                project_name = item["tokenName"]
                nft_name = item["tokenName"] + "#" + item["tokenID"]

                users_data.transaction_data[nft_name] = users_data.transaction_data.get(
                    nft_name,
                    {
                        "buy hash": None,
                        "sell hash": None,
                        "gas price": 0,
                        "buy price": 0,
                        "sell price": 0,
                        "wallet address": None,
                        "gem_refund_amount": 0,
                    },
                )

                if users_data.transaction_data.get(nft_name)["buy hash"] == None:
                    users_data.transaction_data[nft_name]["wallet address"] = item["to"]
                    users_data.transaction_data[nft_name]["buy hash"] = item["hash"]

                    users_data.transaction_data[nft_name]["gas price"] = (
                        int(item["gasPrice"])
                        * int(item["gasUsed"])
                        / 1000000000000000000
                    )  # need to adjust for multi

                    users_data.gas_dict[item["hash"]] = users_data.gas_dict.get(
                        item["hash"], {"number of nfts": 0}
                    )
                    users_data.gas_dict[item["hash"]]["number of nfts"] = (
                        users_data.gas_dict[item["hash"]]["number of nfts"] + 1
                    )

                else:
                    users_data.transaction_data[nft_name]["sell hash"] = item["hash"]
                    users_data.sell_hash_dict[
                        item["hash"]
                    ] = users_data.sell_hash_dict.get(
                        item["hash"], {"number of nfts": 0}
                    )
                    users_data.sell_hash_dict[item["hash"]]["number of nfts"] = (
                        users_data.sell_hash_dict[item["hash"]]["number of nfts"] + 1
                    )

        return project_name

    @staticmethod
    async def bid_transaction_sale_price(
        wallet_address,
        nft: str,
        users_info: User_Info,
        users_data: User_Data,
    ):
        url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={wallet_address}&sort=asc&apikey={users_info.api_key}"
        sale_price: int = 0
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                json = await resp.json()
                if "Max rate limit reached" in str(json):
                    await asyncio.sleep(1)
                    await NFTProfit.bid_transaction_sale_price(
                        wallet_address,
                        nft,
                        users_info,
                        users_data,
                    )
                else:
                    for transaction in json["result"]:
                        if (
                            transaction["hash"]
                            == users_data.transaction_data.get(nft)["sell hash"]
                        ):
                            if transaction["to"] == wallet_address:
                                sale_price = sale_price + round(
                                    int(transaction["value"]) / 1000000000000000000,
                                    4,
                                )
                            elif transaction["from"] == wallet_address:
                                sale_price = sale_price - round(
                                    int(transaction["value"]) / 1000000000000000000,
                                    4,
                                )
                    return sale_price

    @staticmethod
    async def gem_handling(
        session: aiohttp.ClientSession,
        hash: str,
        nft: str,
        users_info: User_Info,
        users_data: User_Data,
    ):
        url = f"https://api.etherscan.io/api?module=account&action=txlistinternal&txhash={hash}&apikey={users_info.api_key}"
        async with session.get(url) as resp:
            json = await resp.json()
            if "Max rate limit reached" in str(json):
                await asyncio.sleep(1)
                await NFTProfit.gem_handling(
                    session,
                    hash,
                    nft,
                    users_info,
                    users_data,
                )
            else:
                for transaction in json["result"]:
                    if transaction["to"] == users_info.wallet_address:
                        users_data.transaction_data[nft]["gem_refund_amount"] = (
                            round(int(transaction["value"]) / 1000000000000000000, 4)
                            / users_data.gas_dict[hash]["number of nfts"]
                        )
                        await NFTProfit.log_evenets(
                            nft
                            + " Refunded Amount: "
                            + users_data.transaction_data[nft]["gem_refund_amount"]
                        )

    @staticmethod
    @sleep_and_retry
    @limits(calls=MAX_CALLS_PER_SECOND, period=ONE_SECOND)
    async def get_purchase_price(
        session: aiohttp.ClientSession,
        nft: str,
        url: str,
        params: dict,
        headers: dict,
        hash: str,
        users_info: User_Info,
        users_data: User_Data,
    ):

        async with session.get(url, params=params, headers=headers) as resp:
            try:
                json = await resp.json()
            except:
                html = await resp.text()
                await NFTProfit.log_evenets("HTML: " + html)
                await NFTProfit.log_evenets(html)  ## got html error in txt file
                await asyncio.sleep(5)
                await NFTProfit.get_purchase_price(
                    session,
                    nft,
                    url,
                    params,
                    headers,
                    hash,
                    users_info,
                    users_data,
                )
            if "Max rate limit reached" in str(json):
                await NFTProfit.log_evenets("RATE LIMITED")
                await asyncio.sleep(1)
                await NFTProfit.get_purchase_price(
                    session,
                    nft,
                    url,
                    params,
                    await NFTProfitHeaders.get_buy_rate_limit_bypass_header(),
                    hash,
                    users_info,
                    users_data,
                )
            else:
                await NFTProfit.log_evenets("NO RATE LIMIT")
                users_data.transaction_data[nft]["buy price"] = (
                    round(int(json["result"]["value"], 16) / 1000000000000000000, 4)
                    / users_data.gas_dict[hash]["number of nfts"]
                )
                if json["result"]["to"] == "0x83c8f28c26bf6aaca652df1dbbe0e1b56f8baba2":
                    await NFTProfit.gem_handling(
                        session,
                        hash,
                        nft,
                        users_info,
                        users_data,
                    )
                await NFTProfit.log_evenets(
                    str(users_info.author)
                    + " --> For item "
                    + nft
                    + " Purchase price was: "
                    + str(users_data.transaction_data[nft]["buy price"])
                    + " ETH"
                )

    @staticmethod
    async def get_sale_price_transaction(  # block specific
        nft: str,
        internal_transactions: List[dict],
        users_info: User_Info,
        users_data: User_Data,
    ):
        price: int = 0
        for wallet_transaction in internal_transactions:
            if (
                wallet_transaction["hash"]
                == users_data.transaction_data.get(nft)["sell hash"]
                and wallet_transaction["hash"] + ":" + nft not in users_data.trace_ids
            ):
                price = round(
                    int(wallet_transaction["value"]) / 1000000000000000000,
                    4,
                )
                users_data.transaction_data[nft]["sell price"] = price
                users_data.trace_ids.append(wallet_transaction["hash"] + ":" + nft)
                break

        if price == 0:
            price = await NFTProfit.bid_transaction_sale_price(
                users_data.transaction_data.get(nft)["wallet address"],
                nft,
                users_info,
                users_data,
            )

        users_data.transaction_data[nft]["sell price"] = price
        await NFTProfit.log_evenets(
            str(users_info.author)
            + " --> For item "
            + nft
            + " Sale price was: "
            + str(price)
            + " ETH"
        )

    @staticmethod
    async def get_sale_price_data(
        session: aiohttp.ClientSession,
        wallet_address: str,
        url: str,
        params: dict,
        users_info: User_Info,
        users_data: User_Data,
    ):
        async with session.get(url, params=params) as resp:
            try:
                json = await resp.json()
                if "Max rate limit reached" in str(json):
                    await asyncio.sleep(1)
                    await NFTProfit.get_sale_price_data(
                        session,
                        wallet_address,
                        url,
                        params,
                        users_info,
                        users_data,
                    )
                else:
                    users_data.internal_transactions[wallet_address] = json["result"]
            except:
                await asyncio.sleep(1)
                await NFTProfit.get_sale_price_data(
                    session,
                    wallet_address,
                    url,
                    params,
                    users_info,
                    users_data,
                )

    @staticmethod
    async def get_nft_prices(
        users_info: User_Info,
        users_data: User_Data,
    ):
        t0 = time.time()
        async with aiohttp.ClientSession() as session:
            tasks = []
            for nft in users_data.transaction_data:
                tasks.append(
                    asyncio.ensure_future(
                        NFTProfit.get_purchase_price(
                            session,
                            nft,
                            url=f"https://api.etherscan.io/api",
                            params=await NFTProfitParams.get_parms_purchase_price(
                                users_data.transaction_data[nft]["buy hash"],
                                "YourApiKeyToken",
                            ),
                            headers=await NFTProfitHeaders.get_buy_rate_limit_bypass_header(),
                            hash=users_data.transaction_data[nft]["buy hash"],
                            users_info=users_info,
                            users_data=users_data,
                        )
                    )
                )
                for wallet in users_info.wallet_address:
                    tasks.append(
                        asyncio.ensure_future(
                            NFTProfit.get_sale_price_data(
                                session,
                                wallet,
                                url=f"https://api.etherscan.io/api",
                                params=await NFTProfitParams.get_parms_sale_price(
                                    wallet,
                                    users_info.api_key,
                                ),
                                users_info=users_info,
                                users_data=users_data,
                            )
                        )
                    )
            await asyncio.gather(*tasks)

        for (nft, nft_val) in users_data.transaction_data.items():
            if nft_val["sell hash"] != None:
                await NFTProfit.get_sale_price_transaction(
                    nft,
                    users_data.internal_transactions[nft_val["wallet address"]],
                    users_info,
                    users_data,
                )

            else:
                await NFTProfit.log_evenets(
                    str(users_info.author) + " --> Item " + nft + " Has Not Been Sold"
                )

        await NFTProfit.log_evenets(
            str(users_info.author)
            + " --> Time elapsed: "
            + str(time.time() - t0)
            + "seconds"
        )

    @staticmethod
    async def fix_gas_price(transaction_data: dict, gas_dict: dict):
        for nft_name in transaction_data:
            for gas_number_of_users in gas_dict:
                if transaction_data[nft_name]["buy hash"] == gas_number_of_users:
                    transaction_data[nft_name]["gas price"] = (
                        transaction_data[nft_name]["gas price"]
                        / gas_dict[gas_number_of_users]["number of nfts"]
                    )

    @staticmethod
    async def fix_sell_price(transaction_data: dict, sell_hash_dict: dict):
        for nft_name in transaction_data:
            for sell_number_per_hash in sell_hash_dict:
                if transaction_data[nft_name]["sell hash"] == sell_number_per_hash:
                    transaction_data[nft_name]["sell price"] = (
                        transaction_data[nft_name]["sell price"]
                        / sell_hash_dict[sell_number_per_hash]["number of nfts"]
                    )

    @staticmethod
    async def run(contract_address: str, wallet_address: str, author: str) -> bool:
        multi = isinstance(wallet_address, (dict, list))
        await NFTProfit.log_evenets(str(author) + " --> Gathering Data.....")
        # print(wallet_address)
        info = User_Info(
            contract_address=contract_address,
            wallet_address=[element.lower() for element in wallet_address]
            if multi
            else [
                wallet_address.lower()
            ],  ##TODO move up so pass array of addresses and check no repeats
            api_key=ETHERSCAN_API_KEY,
            multi=multi,
            author=author,
        )

        data = User_Data(
            await NFTProfit.get_users_data(info),
            sell_hash_dict={},
            transaction_data={},
            gas_dict={},
            internal_transactions={},
            trace_ids=[],
        )

        project_name = await NFTProfit.get_base_data(info, data)

        if project_name == None:
            await NFTProfit.log_evenets(
                str(author) + " --> Error: Project name is None"
            )
            return False

        await NFTProfit.get_nft_prices(info, data)
        await NFTProfit.log_evenets(str(author) + " --> NFT Prices Updated")

        opensea_data = await NFTOpensea.run(info)
        await NFTProfit.log_evenets(str(author) + " --> Got Data From Opensea")

        await NFTProfit.fix_gas_price(data.transaction_data, data.gas_dict)
        await NFTProfit.log_evenets(str(author) + " --> Gas Prices Fixed")
        await NFTProfit.fix_sell_price(data.transaction_data, data.sell_hash_dict)
        await NFTProfit.log_evenets(str(author) + " --> Sell Prices Fixed")

        calculations = NFTCalculations.run(data, opensea_data.floor_price)
        await NFTProfit.log_evenets(str(author) + " --> Completed Calculations")

        await NFTWebhook.personal_webhook(
            project_name, opensea_data, calculations, info.author, info.wallet_address
        )
        await NFTProfit.log_evenets(str(author) + " --> Webhook Sent")
        return True
