from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
from utils.data_objects import Calculations_Data, Opensea_Data


class NFTWebhook:
    @staticmethod
    async def personal_webhook(
        project_name: str,
        opensea_data: Opensea_Data,
        calculations: Calculations_Data,
        author: str,
        addresses: list,
    ):
        webhook = DiscordWebhook(
            url="https://discord.com/api/webhooks/1004368109131530240/wqFJyl4-Zn1IBfD42x1wyMUjHMSCmEf4KJbUFh6ZWqp8A5ToKgLum_PodBZlRdoCKw9_"
        )

        embed = DiscordEmbed(
            description=f"**[{project_name}]({opensea_data.opensea_url})**",
            color=2021216,
        )
        embed.set_thumbnail(url=opensea_data.image_url)
        embed.add_embed_field(
            name="Number Bought", value=str(calculations.number_bought), inline=True
        )
        embed.add_embed_field(
            name="Total Price", value=str(calculations.total_cost), inline=True
        )
        embed.add_embed_field(
            name="Average Price", value=str(calculations.average_cost), inline=True
        )
        embed.add_embed_field(
            name="Number Sold", value=str(calculations.number_sold), inline=True
        )
        embed.add_embed_field(
            name="Total Revenue", value=str(calculations.total_revenue), inline=True
        )
        embed.add_embed_field(
            name="Average Sale Price",
            value=str(calculations.average_sale_price),
            inline=True,
        )
        embed.add_embed_field(
            name="Number Remaining",
            value=str(calculations.number_remaining),
            inline=True,
        )
        embed.add_embed_field(
            name="Unrealised Profit/Loss",
            value=str(calculations.unrealised_profit),
            inline=True,
        )
        embed.add_embed_field(
            name="Average/Floor",
            value=str(calculations.unrealised_average),
            inline=True,
        )
        embed.add_embed_field(
            name="Transactions Number",
            value=str(calculations.number_of_transactions),
            inline=True,
        )
        embed.add_embed_field(
            name="Total Gas", value=str(calculations.total_gas_cost), inline=True
        )
        embed.add_embed_field(
            name="Average Gas", value=str(calculations.average_gas), inline=True
        )
        embed.add_embed_field(
            name="Price To Break Even",
            value=str(calculations.price_to_break_even),
            inline=True,
        )
        embed.add_embed_field(
            name="Potential Profit/Loss",
            value=str(calculations.potential_total_profit),
            inline=True,
        )
        embed.add_embed_field(
            name="Potential ROI",
            value=str(calculations.potential_total_roi) + "%",
            inline=True,
        )
        embed.add_embed_field(
            name="------------------->", value="------------------->", inline=True
        )
        embed.add_embed_field(
            name="Realised Profit", value=str(calculations.realised_profit), inline=True
        )
        embed.add_embed_field(
            name="<-------------------", value="<-------------------", inline=True
        )

        embed.set_footer(
            text="Hideout Bots By Rob | "
            + str(datetime.now())
            + " | "
            + "Requested By:"
            + str(author)
            + " | "
            + "Wallets: "
            + str(len(addresses))
        )
        webhook.add_embed(embed)
        webhook.execute()
