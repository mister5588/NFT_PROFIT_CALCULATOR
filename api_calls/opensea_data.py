import requests
from utils.data_objects import Opensea_Data, User_Info
from typing import Dict, Tuple, Optional, Callable, List, Iterable
from constants.settings import OPENSEA_API_KEY


class NFTOpensea:
    def __init__(self):
        pass

    @staticmethod
    async def get_opensea_base_info(contract_address: str) -> Tuple[str, str]:
        url = f"https://api.opensea.io/api/v1/asset_contract/{contract_address}"
        headers = {
            "Accept": "application/json",
            "X-API-KEY": OPENSEA_API_KEY,
        }

        response = requests.get(url, headers=headers)
        return (
            response.json()["collection"]["image_url"],
            response.json()["collection"]["slug"],
        )

    @staticmethod
    async def get_opensea_floor_info(slug: str) -> str:
        url = f"https://api.opensea.io/api/v1/collection/{slug}/stats"

        headers = {
            "Accept": "application/json",
            "X-API-KEY": OPENSEA_API_KEY,
        }

        response = requests.get(url, headers=headers)
        return response.json()["stats"]["floor_price"]

    @staticmethod
    async def run(users_info: User_Info) -> Opensea_Data:
        image_url, slug = await NFTOpensea.get_opensea_base_info(
            users_info.contract_address
        )
        floor_price = await NFTOpensea.get_opensea_floor_info(slug)
        return Opensea_Data(
            image_url, f"https://opensea.io/collection/{slug}", floor_price
        )
