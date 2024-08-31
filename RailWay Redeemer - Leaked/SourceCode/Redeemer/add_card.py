import tls_client
from SourceCode.Redeemer.cookie_scraper import Obtain_Cookies
from SourceCode.Modules.config_scr import *
import random
import uuid
from SourceCode.Modules.logger import *
from SourceCode.Redeemer.fingerprints import *


def AddVCC(vcc: str, Token: str) -> bool:
    ja3_properties = random.choice(fps)
    ja3 = ja3_properties["ja3"]
    logging_mode = parseConfig()["TerminalLogging"]["LoggingMode"]
    client = tls_client.Session(
        client_identifier="chrome_126",
        ja3_string=ja3,
        h2_settings={
            "HEADER_TABLE_SIZE": 65536,
            "MAX_CONCURRENT_STREAMS": 1000,
            "INITIAL_WINDOW_SIZE": 6291456,
            "MAX_HEADER_LIST_SIZE": 262144,
        },
        h2_settings_order=[
            "HEADER_TABLE_SIZE",
            "MAX_CONCURRENT_STREAMS",
            "INITIAL_WINDOW_SIZE",
            "MAX_HEADER_LIST_SIZE",
        ],
        supported_signature_algorithms=[
            "ECDSAWithP256AndSHA256",
            "PSSWithSHA256",
            "PKCS1WithSHA256",
            "ECDSAWithP384AndSHA384",
            "PSSWithSHA384",
            "PKCS1WithSHA384",
            "PSSWithSHA512",
            "PKCS1WithSHA512",
        ],
        supported_versions=["GREASE", "1.3", "1.2"],
        key_share_curves=["GREASE", "X25519"],
        cert_compression_algo="brotli",
        pseudo_header_order=[":method", ":authority", ":scheme", ":path"],
        connection_flow=15663105,
        header_order=["accept", "user-agent", "accept-encoding", "accept-language"],
    )
    if parseConfig()["ProxySetting"]["UseProxy"]:
        client.proxies = {
            "http": f"http://" + parseConfig["ProxySetting"]["Proxy"],
            "https": f"http://" + parseConfig["ProxySetting"]["Proxy"],
        }
    else:
        client.proxies = None
    if ":" in vcc:
        ccn = vcc.split(":")[0]
        exp_day = vcc.split(":")[1][:2]
        exp_year = vcc.split(":")[1][2:]
        cvc = vcc.split(":")[2]
    elif "|" in vcc:
        ccn, exp_day, exp_year, cvc = vcc.split("|")
    else:
        TL.log("FAIL", f"{yellow}Bad VCC Format", yellow)
        return
    ua = ja3_properties["user-agent"]
    token = Token if not "@" in Token else Token.split(":")[2]
    xprop = ja3_properties["x-super-properties"]
    config = parseConfig()
    headers = {
        "authority": "api.stripe.com",
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": ua,
    }
    data = f"card[number]={ccn}&card[cvc]={cvc}&card[exp_month]={exp_day}&card[exp_year]={exp_year}&guid={uuid.uuid4()}&muid={uuid.uuid4()}&sid={uuid.uuid4()}&payment_user_agent=stripe.js%2F28b7ba8f85%3B+stripe-js-v3%2F28b7ba8f85%3B+split-card-element&referrer=https%3A%2F%2Fdiscord.com&time_on_page=415638&key=pk_live_CUQtlpQUF0vufWpnpUmQvcdi&pasted_fields=number%2Ccvc"
    response = client.post(
        "https://api.stripe.com/v1/tokens", headers=headers, data=data
    )
    if '"id"' in response.text:
        vcc_token = response.json()["id"]
        if logging_mode.lower() == "all":
            TL.log("INFO", f"Tokenized -> {blue}{vcc_token}", magenta)
        else:
            pass
    else:
        TL.log(
            "FAIL",
            f"Failed To Tokenize Card ({yellow}Show this to response{white}) -> {red}{vcc} {white}| Response: {red}{response.json()}",
            red,
        )
        return False
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ua,
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-discord-timezone": "Europe/Budapest",
        "x-super-properties": xprop,
    }
    response = client.post(
        "https://discord.com/api/v9/users/@me/billing/stripe/setup-intents",
        headers=headers,
        cookies=Obtain_Cookies(),
    )
    if '"client_secret"' in response.text:
        client_secret = response.json()["client_secret"]
        separated_secret = client_secret.split("_secret_")[0]
        if logging_mode.lower() == "all":
            TL.log("INFO", f"Client Secret -> {blue}{client_secret}", magenta)
        else:
            pass
    else:
        TL.log(
            "FAIL",
            f"Failed To Scrape Client Secret -> {red}{vcc} {white}| {red}{response.json() if not '401' in response.text else 'Invalid Token Provided'}",
            red,
        )
        return False
    redeeming_config = config["Redeeming"]
    billing_config = config["Redeeming"]["BillingINFO"]
    json = {
        "billing_address": {
            "name": "Joseph Dbratt",
            "line_1": billing_config["Address"],
            "line_2": "",
            "city": billing_config["City"],
            "state": billing_config["State"],
            "postal_code": billing_config["Postal"],
            "country": billing_config["Country"],
            "email": "",
        },
    }
    response = client.post(
        "https://discord.com/api/v9/users/@me/billing/payment-sources/validate-billing-address",
        headers=headers,
        json=json,
        cookies=Obtain_Cookies(),
    )
    if '"token"' in response.text:
        billing_token = response.json()["token"]
        if logging_mode.lower() == "all":
            TL.log("INFO", f"Billing Token -> {blue}{billing_token}", magenta)
        else:
            pass
    else:
        TL.log(
            "FAIL",
            f"Failed To Scrape Billing Token -> {red}{vcc} | {response.json()}",
            red,
        )
        return False
    headers = {
        "authority": "api.stripe.com",
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://js.stripe.com",
        "referer": "https://js.stripe.com/",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": ua,
    }
    data = f"payment_method_data[type]=card&payment_method_data[card][token]={vcc_token}&payment_method_data[billing_details][address][line1]={billing_config['Address']}&payment_method_data[billing_details][address][line2]=&payment_method_data[billing_details][address][city]={billing_config['City']}&payment_method_data[billing_details][address][state]={billing_config['State']}&payment_method_data[billing_details][address][postal_code]={billing_config['Postal']}&payment_method_data[billing_details][address][country]={billing_config['Country']}&payment_method_data[billing_details][name]=Joseph Dbratt&payment_method_data[guid]={uuid.uuid4()}&payment_method_data[muid]={uuid.uuid4()}&payment_method_data[sid]={uuid.uuid4()}&payment_method_data[payment_user_agent]=stripe.js%2F28b7ba8f85%3B+stripe-js-v3%2F28b7ba8f85&payment_method_data[referrer]=https%3A%2F%2Fdiscord.com&payment_method_data[time_on_page]=707159&expected_payment_method_type=card&use_stripe_sdk=true&key=pk_live_CUQtlpQUF0vufWpnpUmQvcdi&client_secret={client_secret}"
    response = client.post(
        f"https://api.stripe.com/v1/setup_intents/{separated_secret}/confirm",
        headers=headers,
        data=data,
    )
    if response.status_code == 200:
        pmtok = response.json()["payment_method"]
        if logging_mode.lower() == "all":
            TL.log("INFO", f"Payment Method -> {blue}{pmtok}", magenta)
        else:
            pass
    else:
        TL.log(
            "FAIL",
            f"Failed To Payment Method -> {red}{vcc} {white}| {red}{response.json()}",
            red,
        )
        return False
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ua,
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-discord-timezone": "Europe/Budapest",
        "x-super-properties": xprop,
    }
    json = {
        "payment_gateway": 1,
        "token": pmtok,
        "billing_address": {
            "name": "Joseph Dbratt",
            "line_1": billing_config["Address"],
            "line_2": None,
            "city": billing_config["City"],
            "state": billing_config["State"],
            "postal_code": billing_config["Postal"],
            "country": billing_config["Country"],
            "email": "",
        },
        "billing_address_token": billing_token,
    }
    response = client.post(
        "https://discord.com/api/v9/users/@me/billing/payment-sources",
        headers=headers,
        json=json,
        cookies=Obtain_Cookies(),
    )
    if '"id"' in response.text:
        TL.remove_content('Input/vccs.txt',vcc)
        TL.log("VCC", f"Added VCC -> {blue}{token[:23]}....", magenta)
        return response.json()["id"]
    else:
        TL.log(
            "FAIL",
            f"Failed to add card -> {red}{response.json() if not 'captcha' in response.text else 'Captcha Encountered'}",
            red,
        )
        return False
