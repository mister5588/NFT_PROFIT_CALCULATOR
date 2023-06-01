from typing import NamedTuple
from typing import Dict, Tuple, Optional, Callable, List, Iterable
from data_objects import Calculations_Data, User_Data


class NFTCalculations:  ##TODO remove class
    def __init__(self):
        pass

    def number_bought(hash_and_name_and_gas_dictionary_example):
        return len(hash_and_name_and_gas_dictionary_example.keys())

    def total_cost(hash_and_name_and_gas_dictionary_example):
        total_cost = 0
        total_gem_refund = 0
        for nft in hash_and_name_and_gas_dictionary_example:
            total_cost += hash_and_name_and_gas_dictionary_example[nft]["buy price"]
            total_gem_refund += hash_and_name_and_gas_dictionary_example[nft][
                "gem_refund_amount"
            ]
        return total_cost - total_gem_refund

    def average_cost(total_cost, number_bought):
        return total_cost / number_bought

    def number_sold(hash_and_name_and_gas_dictionary_example):
        number_sold = 0
        for nft in hash_and_name_and_gas_dictionary_example:
            if hash_and_name_and_gas_dictionary_example[nft]["sell hash"] != None:
                number_sold += 1
        return number_sold

    def total_revenue(hash_and_name_and_gas_dictionary_example):
        total_revenue = 0
        for nft in hash_and_name_and_gas_dictionary_example:
            if hash_and_name_and_gas_dictionary_example[nft]["sell price"] != None:
                total_revenue += hash_and_name_and_gas_dictionary_example[nft][
                    "sell price"
                ]
        return total_revenue

    def average_sale_price(total_revenue, number_sold):
        if number_sold == 0:
            return 0
        return total_revenue / number_sold

    def number_remaining(number_bought, number_sold):
        return number_bought - number_sold

    def unrealized_profit(number_remaining, floor_price, average_cost):
        return (number_remaining * floor_price) - (
            number_remaining * average_cost
        )  # TODO add it to exact price not floor price

    def unrealised_average(floor_price):
        return floor_price

    def number_of_transactions(gas_dict):
        return len(gas_dict.keys())

    def total_gas_cost(hash_and_name_and_gas_dictionary_example):
        total_gas_cost = 0
        for nft in hash_and_name_and_gas_dictionary_example:
            total_gas_cost += hash_and_name_and_gas_dictionary_example[nft]["gas price"]
        return total_gas_cost

    def average_gas(total_gas_cost, number_bought):
        return total_gas_cost / number_bought

    def price_to_break_even(total_revenue, total_cost, number_remaining):
        if total_revenue - total_cost > 0:
            return "Break Even Met"
        elif number_remaining == 0:
            return "No More NFTs"
        return str(abs(round((total_revenue - total_cost) / number_remaining, 4)))

    def potential_total_roi(potential_total_profit, total_cost):
        return potential_total_profit / total_cost * 100

    def realised_profit(total_revenue, total_cost):
        return total_revenue - total_cost

    def potential_total_profit(
        unrealised_profit, total_revenue, number_sold, average_cost
    ):
        return unrealised_profit + (total_revenue) - (number_sold * average_cost)

    def run(users_data: User_Data, floor_price: float) -> Calculations_Data:
        number_bought: int = NFTCalculations.number_bought(users_data.transaction_data)
        total_cost = NFTCalculations.total_cost(users_data.transaction_data)
        total_gas_cost = NFTCalculations.total_gas_cost(users_data.transaction_data)
        total_cost = total_cost + total_gas_cost
        average_cost = NFTCalculations.average_cost(total_cost, number_bought)
        number_sold = NFTCalculations.number_sold(users_data.transaction_data)
        total_revenue = NFTCalculations.total_revenue(users_data.transaction_data)
        average_sale_price = NFTCalculations.average_sale_price(
            total_revenue, number_sold
        )
        number_remaining = NFTCalculations.number_remaining(number_bought, number_sold)
        unrealised_profit = NFTCalculations.unrealized_profit(
            number_remaining, floor_price, average_cost
        )
        unrealised_average = NFTCalculations.unrealised_average(floor_price)
        number_of_transactions = NFTCalculations.number_of_transactions(
            users_data.gas_dict
        )
        average_gas = NFTCalculations.average_gas(total_gas_cost, number_bought)
        price_to_break_even = NFTCalculations.price_to_break_even(
            total_revenue, total_cost, number_remaining
        )
        realised_profit = NFTCalculations.realised_profit(total_revenue, total_cost)
        potential_total_profit = NFTCalculations.potential_total_profit(
            unrealised_profit, total_revenue, number_sold, average_cost
        )
        potential_total_roi = NFTCalculations.potential_total_roi(
            potential_total_profit, total_cost
        )
        return Calculations_Data(
            str(round(number_bought, 4)),
            str(round(total_cost, 4)),
            str(round(total_gas_cost, 4)),
            str(round(average_cost, 4)),
            str(round(number_sold, 4)),
            str(round(total_revenue, 4)),
            str(round(average_sale_price, 4)),
            str(round(number_remaining, 4)),
            str(round(unrealised_profit, 4)),
            str(round(unrealised_average, 4)),
            str(round(number_of_transactions, 4)),
            str(round(average_gas, 4)),
            price_to_break_even,
            str(round(realised_profit, 4)),
            str(round(potential_total_profit, 4)),
            str(round(potential_total_roi, 4)),
        )
