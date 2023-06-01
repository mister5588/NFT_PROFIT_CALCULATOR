class NFTWallets:
    def __init__(self):
        pass

    async def add_wallet(self, discord_name: str, wallets) -> bool:
        try:
            current_wallets = self.ref.get()["wallets"][discord_name]
            for wallet in wallets:
                if wallet not in current_wallets and "0x" in wallet:
                    self.data.update(
                        {
                            discord_name
                            + "/"
                            + str(
                                len(self.ref.get()["wallets"][discord_name])
                            ): wallet.replace(" ", "")
                        }
                    )
        except:
            wallet_dic = {discord_name: {}}
            for wallet in wallets:
                if "0x" in wallet:
                    wallet_dic[discord_name][
                        str(len(wallet_dic.get(discord_name)))
                    ] = wallet
            self.data.update(wallet_dic)
        return True

    async def get_wallets(self, discord_name: str) -> dict:
        try:
            return self.ref.get()["wallets"][discord_name]
        except:
            return {}
