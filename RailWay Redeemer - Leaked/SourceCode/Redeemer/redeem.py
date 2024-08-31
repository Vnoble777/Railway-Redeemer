import tls_client
from SourceCode.Modules.logger import *
from SourceCode.Redeemer.fingerprints import fps
import random
from SourceCode.Redeemer.cookie_scraper import Obtain_Cookies
from SourceCode.Modules.config_scr import *
import time

counter = {}


def RedeemPromotion(promo: str, Payment_Source: str, Token: str):
    global counter
    ja3_properties = random.choice(fps)
    counter_json = {Token: 0}
    max_tries = 0
    counter.update(counter_json)
    ja3 = ja3_properties["ja3"]
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
    ua = ja3_properties["user-agent"]
    token = Token if not "@" in Token else Token.split(":")[2]
    xprop = ja3_properties["x-super-properties"]
    sleep_after = parseConfig()["Redeeming"]["SleepAfterRedeem"]
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": token,
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": f"https://discord.com/billing/promotions/{promo}",
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
        "channel_id": None,
        "payment_source_id": Payment_Source,
        "gateway_checkout_context": None,
    }
    response = client.post(
        f"https://discord.com/api/v9/entitlements/gift-codes/{promo}/redeem",
        headers=headers,
        json=json,
        cookies=Obtain_Cookies(),
    )
    if '"id"' in response.text:
        TL.log("REDEEMED", f"Redeemed Promo In -> {green}{token[:23]}....", Fore.GREEN)
        TL.add_content("Output/success.txt", Token)
        if sleep_after > 0:
            time.sleep(sleep_after)
        else:
            pass
        return True
    elif "Authentication" in response.text:
        try:
            TL.log(
                "AUTH",
                f"Authenticating VCC... Please wait this will take {blue}4-5s",
                blue,
            )
            pi = response.json()["payment_id"]
            response = client.get(
                f"https://discord.com/api/v9/users/@me/billing/stripe/payment-intents/payments/{pi}",
                headers=headers,
                cookies=Obtain_Cookies(),
            )
            full_secret = str(response.json()["stripe_payment_intent_client_secret"])
            secret = str(response.json()["stripe_payment_intent_client_secret"]).split(
                "_secret_"
            )[0]
            headers = {
                "accept": "application/json",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://js.stripe.com",
                "referer": "https://js.stripe.com/",
                "sec-ch-ua": '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": ua,
            }
            data = {
                "expected_payment_method_type": "card",
                "use_stripe_sdk": "true",
                "key": "pk_live_CUQtlpQUF0vufWpnpUmQvcdi",
                "client_secret": full_secret,
            }
            response = client.post(
                f"https://api.stripe.com/v1/payment_intents/{secret}/confirm",
                headers=headers,
                params=data,
            )
            three_ds_source = response.json()["next_action"]["use_stripe_sdk"][
                "three_d_secure_2_source"
            ]
            response = client.post(
                "https://api.stripe.com/v1/3ds2/authenticate",
                headers=headers,
                data=f"source={three_ds_source}&browser=%7B%22fingerprintAttempted%22%3Afalse%2C%22fingerprintData%22%3Anull%2C%22challengeWindowSize%22%3Anull%2C%22threeDSCompInd%22%3A%22Y%22%2C%22browserJavaEnabled%22%3Afalse%2C%22browserJavascriptEnabled%22%3Atrue%2C%22browserLanguage%22%3A%22en-US%22%2C%22browserColorDepth%22%3A%2224%22%2C%22browserScreenHeight%22%3A%221080%22%2C%22browserScreenWidth%22%3A%221920%22%2C%22browserTZ%22%3A%22-345%22%2C%22browserUserAgent%22%3A%22Mozilla%2F5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML%2C+like+Gecko)+Chrome%2F123.0.0.0+Safari%2F537.36+Edg%2F123.0.0.0%22%7D&one_click_authn_device_support[hosted]=false&one_click_authn_device_support[same_origin_frame]=false&one_click_authn_device_support[spc_eligible]=false&one_click_authn_device_support[webauthn_eligible]=false&one_click_authn_device_support[publickey_credentials_get_allowed]=true&key=pk_live_CUQtlpQUF0vufWpnpUmQvcdi",
            )
            TL.log(
                "3DS2",
                f"https://api.stripe.com/v1/3ds2/authenticate -> {blue}{response.json()}",
                blue,
            )
            RedeemPromotion(promo, Payment_Source, Token)
        except Exception as e:
            if counter[Token] < max_tries:
                counter[Token] += 1
                RedeemPromotion(promo=promo, Payment_Source=Payment_Source, Token=Token)
            else:
                TL.log("AUTH", f"VCC Auth Error -> {yellow}{token[:23]}...", yellow)
        if "Authentication" in response.text and counter[Token] < max_tries:
            counter[Token] += 1
            RedeemPromotion(promo=promo, Payment_Source=Payment_Source, Token=Token)
    else:

        TL.log("FAILED", f"Failed To Redeem Promo -> {red}{response.json()}", red)
        return False
