import discord
from final_profit_calculator import NFTProfit
from multi_wallet import NFTWallets
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import asyncio
from settings import FIREBASE_DATABASE_URL, DISCORD_BOT_KEY


class NFTProfitDiscordBot:
    def __init__(self, cred, ref, data):
        self.cred = cred
        self.ref = ref
        self.data = data
        self.client = discord.Client()
        self.on_ready = self.client.event(self.on_ready)
        self.on_message = self.client.event(self.on_message)

    async def log_evenets(self, message):
        print(message)

    async def on_ready(self):
        await self.log_evenets("We have logged in as {0.user}".format(self.client))

    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if message.content.startswith("!profit"):
            sent_message = message.content
            message_parts = sent_message.split(" ")
            if len(message_parts) == 3:
                collection = message_parts[1]
                wallet = message_parts[2]
            else:
                collection = message_parts[1]
                wallet = await asyncio.create_task(
                    NFTWallets.get_wallets(self, str(message.author).replace("#", ""))
                )
            if None in wallet:
                await message.channel.send(
                    "None Wallet Found @ROB to sort out this issue"
                )
                for address in wallet:
                    if address == None or address == "" or " " in address:
                        wallet.remove(address)
            if wallet == {}:
                await message.channel.send(
                    "You have no wallets Currently added, use command !add wallet1,wallet2... or !profit contract walletAddress"
                )
            else:
                success = await asyncio.create_task(
                    NFTProfit.run(collection.lower(), wallet, message.author)
                )

                if not success:
                    await message.channel.send(
                        "No Transactions Found for this collection and wallet/wallets"
                    )

        elif message.content.startswith("/profit"):
            sent_message = message.content
            message_parts = sent_message.split(" ")

            collection = message_parts[1]
            name = message_parts[2]
            wallet = await asyncio.create_task(
                NFTWallets.get_wallets(self, str(name).replace("#", ""))
            )
            if None in wallet:
                await message.channel.send(
                    "None Wallet Found @ROB to sort out this issue"
                )
                for address in wallet:
                    if address == None:
                        wallet.remove(address)
            print(wallet)

            if wallet == {}:
                await message.channel.send(
                    "You have no wallets Currently added, use command !add wallet1,wallet2... or !profit contract walletAddress"
                )
            else:
                success = await asyncio.create_task(
                    NFTProfit.run(collection.lower(), wallet, name)
                )
                if not success:
                    await message.channel.send(
                        "No Transactions Found for this collection and wallet/wallets"
                    )

        elif message.content.startswith("!add"):
            sent_message = message.content
            message_parts = sent_message.replace("!add ", "").split(",")

            success = await asyncio.create_task(
                NFTWallets.add_wallet(
                    self, str(message.author).replace("#", ""), message_parts
                )
            )

            if not success:
                await message.channel.send("Error Adding Wallet")
            else:
                await message.channel.send("Added Wallets To Account")
                await self.log_evenets("Added wallets: " + str(message_parts))

    def run(self):
        self.client.run(DISCORD_BOT_KEY)


def setup_database():
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate("profit_service_key.json")

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})

    # As an admin, the app has access to read and write all data, regradless of Security Rules
    ref = db.reference("Hidout-Wallets")
    data = ref.child("wallets")
    return cred, ref, data


if __name__ == "__main__":
    cred, ref, data = setup_database()
    NFTProfitDiscordBot(cred, ref, data).run()
