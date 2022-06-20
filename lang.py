from discord_webhook import DiscordEmbed
from dotenv import dotenv_values

config = dotenv_values(".env")
MINIMUM_SIZE, SND_MINIMUM_SIZE, TRD_MINIMUM_SIZE, FTH_MINIMUM_SIZE = (
    config["MINIMUM_SIZE"],
    config["SND_MINIMUM_SIZE"],
    config["TRD_MINIMUM_SIZE"],
    config["FTH_MINIMUM_SIZE"],
)
langSup = {"CN": {}, "EN": {}}
cexSup = {
    "FTX": {
        "type": "side",
        "price": "price",
        "size": "size",
    },
    "BINANCE": {
        "type": "isBuyerMaker",
        "price": "price",
        "size": "qty",
    },
}


# create discord embed based on trade size and side
# if size >= 1000, then it's a  huge whale trade
# elif size >= 500, then it's a whale trade
# elif size >= 100, then it's a small whale trade
# else size >= 50, then it's a regular trade
# the color of the embed is based on the side
# if side is buy, then the color is green
# if side is sell, then the color is red


def createEmbed(trade: dict, cex: str) -> DiscordEmbed:
    if trade[cexSup[cex]["type"]] == "sell":
        color = 0x00FF00
    else:
        color = 0xFF0000
    size = getSize(trade, cex)
    if size >= float(FTH_MINIMUM_SIZE):
        title = "❗❗❗❗❗❗🔔🔔🔔HUGE WHALE TRADE❗❗❗❗❗❗🔔🔔🔔"
    elif size >= float(TRD_MINIMUM_SIZE):
        title = "❗❗❗❗❗❗❗WHALE TRADE❗❗❗❗❗❗❗"
    elif size >= float(SND_MINIMUM_SIZE):
        title = "❗❗❗SMALL WHALE TRADE❗❗❗"
    elif size >= float(MINIMUM_SIZE):
        title = "❗REGULAR TRADE❗"
    embed = DiscordEmbed(
        title=title,
        description=cex,
        color=color,
    )
    if cex == "BINANCE":
        if trade[cexSup[cex]["type"]] == True:
            embed.add_embed_field(
                name=f"SIDE",
                value=f"``sell``",
            )
        else:
            embed.add_embed_field(
                name=f"SIDE",
                value=f"``buy``",
            )
    else:
        embed.add_embed_field(
            name=f"SIDE",
            value=f"``{trade[cexSup[cex]['type']]}``",
        )
    embed.add_embed_field(
        name=f"PRICE",
        value=f"``{trade[cexSup[cex]['price']]}``",
    )
    embed.add_embed_field(
        name=f"SIZE",
        value=f"``{trade[cexSup[cex]['size']]}``",
    )
    return embed


def getSize(trade: dict, cex: str) -> str:
    return float(trade[cexSup[cex]["size"]])
