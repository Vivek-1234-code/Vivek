import telebot
import requests

# Set your bot token from BotFather
TOKEN = "7391763155:AAG7JF2snXAPNUM8OiQ1pBr9QNUgqg5GNtE"
bot = telebot.TeleBot(TOKEN)

# The API URL
URL = "https://shop2game.com/api/auth/player_id_login"

# Define the required headers for the request
HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8,ar-EG;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Referer": "https://shop2game.com/app/100067/buy/0",
    "Sec-Ch-Ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "X-Datadome-Clientid": "t0uHUTg4ECL0w9RPVL~I2l30Pp~ta9tGx7wZlobnhfc6Y8wuLODwqFb1NAuVNXaOvWcVa1qY5byaZn4stChSHmOLbt8bDgxpub_9n0dCcXoNZNcHdpx6EMVmCt6fC6CN"
}

# Define the required cookies for the request
COOKIES = {
    "mspid2": "8def57b0182b87ef73e212616f5e07ea",
    "_ga": "GA1.1.1204646774.1716228484",
    "_fbp": "fb.1.1716228484399.358077362",
    "region": "DZ",
    "source": "pc",
    "session_key": "rwdtsagbjclbcma7u9izqad6qtepoyy1",
    "_ga_TVZ1LG7BEB": "GS1.1.1716374301.3.1.1716374416.0.0.0",
    "datadome": "vcPWWfxDqMrMOABc4znI7xQ4EykzGKU5WFtbC1cFQolLBfby58PljA_H5SoICBuxPFA48YqjWH7ML9_EZrCuu_s4Cenn4iP7p9U2R4KlYskeQJYirKDTznKdREgw0SAP"
}

# Platform map
PLATFORM_MAP = {
    8: 'Google',
    4: 'Guest',
    3: 'Facebook',
    11: 'Twitter',
    5: 'VK'
}

# Function to check the account ban status
def check_account_status(uid):
    url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={uid}"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ar,en-US;q=0.9,en;q=0.8,ar-EG;q=0.7",
        "cache-control": "no-cache",
        "cookie": "_ga_3LHB0DGPG8=GS1.1.1716924019.1.1.1716924021.0.0.0; _gid=GA1.2.1230499507.1717356976; _ga_KE3SY7MRSD=GS1.1.1717356973.4.1.1717358048.0.0.0; _ga_RF9R6YT614=GS1.1.1717356976.4.1.1717358050.0.0.0; _ga=GA1.1.2009590643.1716923940",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://ff.garena.com/en/support/",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
        "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "success":
            if data["data"]["is_banned"] == 0:
                return "Account is not banned."
            else:
                return "Account is banned."
        return "Error: Status not success."
    except requests.RequestException as e:
        return f"Error retrieving account status: {e}"

# Function to get player information
def get_player_info(login_id):
    try:
        # Create a new session
        session = requests.Session()

        # Set up the payload with the login data
        payload = {
            "app_id": 100067,
            "login_id": login_id,
            "app_server_id": 0
        }

        # Send a POST request and get the session_key from the response cookies
        response = session.post(URL, headers=HEADERS, json=payload, cookies=COOKIES)
        response.raise_for_status()
        session_key = response.cookies.get("session_key")

        if not session_key:
            return "Error: Unable to get session key."

        # Update the cookies with the new session_key
        session_cookies = COOKIES.copy()
        session_cookies["session_key"] = session_key

        # Send a GET request to retrieve the player information
        user_info_response = session.get('https://shop2game.com/api/auth/get_user_info/multi', cookies=session_cookies)
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        # Replace platform ID with platform name
        platform_id = user_info['player_id']['platform']
        platform_name = PLATFORM_MAP.get(platform_id, 'Unknown')
        user_info['player_id']['platform'] = platform_name

        # Call the function to check account status and add it to the user info
        account_status = check_account_status(user_info['player_id'].get('uid', ''))
        user_info['player_id']['account_status'] = account_status

        # Format the information to be returned
        formatted_info = (
            f"Login ID: {user_info['player_id'].get('login_id', 'None')}\n"
            f"UID: {user_info['player_id'].get('uid', 'None')}\n"
            f"Open ID: {user_info['player_id'].get('open_id', 'None')}\n"
            f"Image URL: {user_info['player_id'].get('img_url', 'None')}\n"
            f"App ID: {user_info['player_id'].get('app_id', 'None')}\n"
            f"Platform: {user_info['player_id'].get('platform', 'None')}\n"
            f"Garena UID: {user_info['player_id'].get('garena_uid', 'None')}\n"
            f"Nickname: {user_info['player_id'].get('nickname', 'None')}\n"
            f"Nationality: {user_info['player_id'].get('nationality', 'None')}\n"
            f"Payable: {user_info['player_id'].get('payable', 'None')}\n"
            f"Avatar: {user_info['player_id'].get('avatar_url', 'None')}\n"
            f"Celebrities: {user_info['player_id'].get('celebrity', 'None')}\n"
            f"Status: {user_info['player_id'].get('status', 'None')}\n"
            f"Player: {user_info['player_id'].get('player', 'None')}\n"
            f"Region: {user_info['player_id'].get('region', 'None')}\n"
            f"Language: {user_info['player_id'].get('language', 'None')}\n"
            f"Account Status: {user_info['player_id'].get('account_status', 'None')}\n"
            f"Registration Date: {user_info['player_id'].get('registration_date', 'None')}\n"
        )
        return formatted_info

    except requests.RequestException as e:
        return f"Error retrieving player information: {e}"

# Define command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Use /Get or /like followed by a login ID to get player information.")

@bot.message_handler(commands=['Get', 'like'])
def handle_commands(message):
    command = message.text.split()[0]
    login_id = ' '.join(message.text.split()[1:]).strip()
    if not login_id:
        bot.reply_to(message, "Please provide a valid login ID.")
        return

    # Fetch and send player information
    player_info = get_player_info(login_id)
    bot.reply_to(message, player_info)

# Start the bot
bot.polling()
  
