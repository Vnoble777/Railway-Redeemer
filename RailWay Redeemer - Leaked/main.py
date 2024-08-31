import asyncio
from concurrent.futures import ThreadPoolExecutor
import discord
from discord.ext import commands, tasks

from SourceCode.Modules.requirements_installer import *
from SourceCode.Modules.logger import *
from SourceCode.Modules.config_scr import *
from SourceCode.Modules.materials_scr import *
from SourceCode.Redeemer.tc import *
from SourceCode.Redeemer.add_card import *
from SourceCode.Redeemer.redeem import *
from SourceCode.Redeemer.cookie_scraper import *
import time
import json

with open("database/fail_db.json", "r") as f:
    db_f = json.load(f)
with open("database/success_database.json", "r") as f:
    db_s = json.load(f)
start_t = time.time()
CLS()
install_requirements()
CLS()


def clear_file(file_path):
    with open(file_path, "w") as file:
        pass


clear_file("SourceCode/Modules/logs.txt")

s = "✅"
e = "❌"
d = "📣"
logs = f"[{TL.timestamp()}] [📣] - Starting redeemer."
text = """
  _____          _                               
 |  __ \        | |                              
 | |__) |___  __| | ___  ___ _ __ ___   ___ _ __ 
 |  _  // _ \/ _` |/ _ \/ _ \ '_ ` _ \ / _ \ '__|
 | | \ \  __/ (_| |  __/  __/ | | | | |  __/ |   
 |_|  \_\___|\__,_|\___|\___|_| |_| |_|\___|_|   
 Powered by @SwapSway
"""  # Your ASCII art text

print(Style.BRIGHT + Fore.BLUE + text + reset)

TL.log("INITIALIZATION", f"Version: {blue}V1.0", Fore.BLUE)
TL.log(
    "INITIALIZATION",
    f"Service: {blue}{parseConfig()['TerminalLogging']['ServiceName']}",
    Fore.BLUE,
)
if parseConfig()["SilentFeatures"]["CheckTokens"]:
    TL.log("INITIALIZATION", f"Status: {blue}Checking Tokens", Fore.BLUE)
    print()
    tokens = read_file("Input/tokens.txt")
    with ThreadPoolExecutor(max_workers=200) as exc:
        for token in tokens:
            exc.submit(check_token, token)
    print()
    TL.log(
        "INITIALIZATION",
        f"{blue}Checked Tokens {white}| {blue}Removed Invalid Tokens From File {white}| {blue}Redeemer is now started",
        Fore.BLUE,
    )
    print("")
else:
    TL.log("INITIALIZATION", f"Status: {blue}Started", Fore.BLUE)
    print()

tokens = read_file("Input/tokens.txt")
promos = read_file("Input/promo_codes.txt")
vccs = read_file("Input/vccs.txt")

success, fail = 0, 0

bot_log_config = parseConfig()["DiscordBotLogging"]
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def scrape_logs():
    with open("SourceCode/Modules/logs.txt", "r") as f:
        return f.read().splitlines()


@bot.event
async def on_ready():
    TL.log("DBOT", f"Logged in as {bot.user.name} ({bot.user.id})", blue)
    print()
    try:
        channel = await bot.fetch_channel(bot_log_config["LogChannelID"])
        if channel:
            embed_message = await channel.send(embed=create_embed(logs))
            update_embed.start(embed_message, channel)
        else:
            TL.log(
                "DBOT",
                f"BOT ERR -> {red}Channel Not Found! Cant send redeeming logs",
                red,
            )
    except discord.NotFound:
        TL.log(
            "DBOT", f"BOT ERR -> {red}Channel Not Found! Cant send redeeming logs", red
        )
    except discord.Forbidden:
        TL.log(
            "DBOT",
            f"BOT ERR -> {red}No permission to send message in that channel.",
            red,
        )
    except Exception as e:
        TL.log(
            "DBOT", f"BOT ERR ( {yellow}Show this to response {white}) -> {red}{e}", red
        )


@tasks.loop(seconds=1)
async def update_embed(embed_message, channel):
    try:
        embed = create_embed(logs)
        await embed_message.edit(embed=embed)
    except Exception as e:
        pass


def create_embed(log):
    log_lines = log.strip().split("\n")
    last_10_lines = "\n".join(log_lines[-15:])

    embed = discord.Embed(
        title="⭐ - Redeemer Current Status",
        description="```" + last_10_lines + "```",
        color=discord.Color.blue(),
    )
    embed.add_field(name="Counter", value=f"```{get_title()}```")
    embed.add_field(
        name="Elapsed (Seconds)",
        value="```" + str(time.time() - start_t).split(".")[0] + "s```",
        inline=False,
    )
    embed.add_field(
        name="Time (Hour:Minutes:Seconds)",
        value=f"```Last Updated at {discord.utils.utcnow().strftime('%H:%M:%S')}```",
        inline=False,
    )
    embed.set_image(
        url="https://media.discordapp.net/attachments/1271162863360413796/1277654479575056475/image.png?ex=66cdf3f5&is=66cca275&hm=d2418a71fbb32ef557b545e693d0d5b0e815e57c2cc814e769a11d403dc501d0&=&format=webp&quality=lossless"
    )
    embed.set_author(
        name=bot_log_config["ServiceName"],
        url="https://media.discordapp.net/attachments/1271162863360413796/1277654479575056475/image.png?ex=66cdf3f5&is=66cca275&hm=d2418a71fbb32ef557b545e693d0d5b0e815e57c2cc814e769a11d403dc501d0&=&format=webp&quality=lossless",
    )
    return embed


async def runb():
    if bot_log_config["UseBot"]:
        await bot.start(bot_log_config["BotToken"])
    else:
        pass


def get_title():
    global success, fail
    ttl = f"{parseConfig()['TerminalLogging']['ServiceName']} , Powered By @swapsway , V1.0 , Success: {success} , Fails: {fail}"
    return ttl


def format_promo_code(promotion):
    if "https://discord.com/billing/promotions/" in promotion:
        separated_code = promotion.replace(
            "https://discord.com/billing/promotions/", ""
        )
    elif "https://promos.discord.gg/" in promotion:
        separated_code = promotion.replace("https://promos.discord.gg/", "")
    else:
        separated_code = promotion
    return separated_code


def Proccess(vcc, token, promo):
    global success, fail, logs, s, e
    TL.update_console_title(get_title())
    add_card_bool = AddVCC(vcc, token)
    TL.remove_content("Input/tokens.txt", token)
    logs += f"[{TL.timestamp()}] [{d}] - Started redeeming.\n"
    if type(add_card_bool) == str:
        logs += f"[{TL.timestamp()}] [{d}] - Added VCC.\n"
        TL.add_content("SourceCode/Modules/logs.txt", "")
        logs += f"[{TL.timestamp()}] [{d}] - Redeeming promo.\n"
        TL.log(
            "INFO",
            f"Redeeming -> {blue}{vcc[:13]}...:...:... {white}, {blue}{format_promo_code(promo)[:13]}...",
            blue,
        )
        redeem = RedeemPromotion(
            format_promo_code(promo), Payment_Source=add_card_bool, Token=token
        )
        if redeem:
            TL.remove_content("Input/promo_codes.txt", promo)
            logs += f"[{TL.timestamp()}] [{s}] - Redeemed promo successfully.\n"
            db_s["success"].append(token)
            with open("database/success_database", "w") as file:
                json.dump(db_s, file, indent=4)
            print()
            success += 1
        else:
            logs += f"[{TL.timestamp()}] [{e}] - Failed to redeem promo.\n"
            data = {
                "reason": "failed at redeem promo request",
                "failed_at": datetime.now().strftime("%d/%m/%Y - %H:%M:%S"),
            }
            db_f[token] = data
            with open("database/fail_db.json", "w") as file:
                json.dump(data, file, indent=4)
            print()
            fail += 1
    else:
        logs += f"[{TL.timestamp()}] [{e}] - Failed to add vcc.\n"
        data = {
            "reason": "failed to add vcc",
            "failed_at": datetime.now().strftime("%d/%m/%Y - %H:%M:%S"),
        }
        db_f[token] = data
        with open("database/fail_db.json", "w") as file:
            json.dump(data, file, indent=4)
        print()
        fail += 1


async def concurrent_tasks():
    with ThreadPoolExecutor(max_workers=int(parseConfig()["Threads"])) as exc:
        futures = []
        for vcc in vccs:
            for i in range(int(parseConfig()["Redeeming"]["VccUsage"])):
                futures.append(
                    asyncio.get_event_loop().run_in_executor(
                        exc, Proccess, vcc, tokens[i], promos[i]
                    )
                )
        await asyncio.gather(*[asyncio.wrap_future(future) for future in futures])


async def main():
    bot_task = asyncio.create_task(runb())
    await asyncio.sleep(10)
    await concurrent_tasks()
    await bot_task


if __name__ == "__main__":
    asyncio.run(main())

input()
