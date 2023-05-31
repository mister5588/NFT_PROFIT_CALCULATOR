from typing import NamedTuple


class Opensea_Data(NamedTuple):  # TODO
    image_url: str
    opensea_url: str
    floor_price: float


class User_Info(NamedTuple):
    contract_address: str
    wallet_address: list
    api_key: str
    multi: bool
    author: str


class User_Data(NamedTuple):
    transactions_raw: list
    sell_hash_dict: dict
    transaction_data: dict
    gas_dict: dict
    internal_transactions: dict
    trace_ids: list


class Calculations_Data(NamedTuple):
    number_bought: str
    total_cost: str
    total_gas_cost: str
    average_cost: str
    number_sold: str
    total_revenue: str
    average_sale_price: str
    number_remaining: str
    unrealised_profit: str
    unrealised_average: str
    number_of_transactions: str
    average_gas: str
    price_to_break_even: str
    realised_profit: str
    potential_total_profit: str
    potential_total_roi: str
