from requests import get as GET
from time import sleep as timewait
from urllib import parse
from dotenv import dotenv_values
from discord_webhook import DiscordWebhook
from lang import createEmbed, getSize

config = dotenv_values(".env")


class Client:
    def __init__(self, base: str, market: str) -> None:
        if base.endswith("/"):
            base = base[:-1]
        self.baseUrl = base
        self.pair = market
        self.cexPath(market.upper())
        self.cacheTradesObj = []
        pass

    def get_trades(self) -> dict:
        url = self.baseUrl + self.basePath + "trades"
        params = {}
        if self.exchange == "BINANCE":
            params["symbol"] = self.pair
        response = GET(url, params)
        return response.json()

    def cexPath(self, market: str) -> None:
        print(self.baseUrl)
        baseUrl = parse.urlparse(self.baseUrl).netloc
        if not "USD" in market:
            market += "USD"
        if baseUrl == "ftx.com":
            self.basePath = f"/markets/{market.split('USD')[0]}/{market.split(market.split('USD')[0])[1]}/"
            self.exchange = "FTX"
            print(self.basePath)
        if baseUrl == "api.binance.com":
            self.basePath = f"/api/v3/"
            self.exchange = "BINANCE"
            print(self.basePath)

    def get_orders(self) -> dict:
        url = self.baseUrl + self.basePath + "orderbook"
        response = GET(url)
        return response.json()

    def getWhaleTrade(self, price: float) -> dict:
        if self.exchange == "FTX":
            trades = self.get_trades()["result"]
        elif self.exchange == "BINANCE":
            trades = self.get_trades()
        whaleTrades = []
        for trade in trades:
            if round((getSize(trade, self.exchange) * price), 2) >= float(
                config["MINIMUM_SIZE"]
            ):
                whaleTrades.append(trade)
        return whaleTrades

    def cacheTrades(self, trades: dict) -> None:
        self.cacheTradesObj.append(trades)
        pass

    def get_price(self) -> float:
        if self.exchange == "FTX":
            url = (self.baseUrl + self.basePath)[:-1]
            response = GET(url)
            return float(response.json()["result"]["price"])
        elif self.exchange == "BINANCE":
            url = self.baseUrl + self.basePath + "avgPrice"
            response = GET(url, params={"symbol": self.pair})
            return float(response.json()["price"])


ftxBTCUSDT = Client("https://ftx.com/api", "BTCUSDT")
ftxBTCUSD = Client("https://ftx.com/api", "BTCUSD")
bnBTCUSDT = Client("https://api.binance.com/", "BTCUSDT")
pairs = [ftxBTCUSD, ftxBTCUSDT, bnBTCUSDT]
while True:
    for pair in pairs:
        price = pair.get_price()
        trades = pair.getWhaleTrade(price)
        for trade in trades:
            if trade not in pair.cacheTradesObj:
                pair.cacheTrades(trade)
                print(f"{pair.pair}:{trade}")
                webhook = DiscordWebhook(
                    url=config["DISCORD_WEBHOOK"],
                    content="TRADE ALERT",
                )
                embed = createEmbed(trade, pair.exchange, price)
                webhook.add_embed(embed)
                response = webhook.execute()
    timewait(0.8)
