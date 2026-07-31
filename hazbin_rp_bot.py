import discord
from discord.ext import commands
import discord.app_commands as app_commands
import random
import os
import json
import aiohttp
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
# Use the free router - automatically picks working free models
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ───── ACTIVE CONVERSATIONS ─────
active_conversations = {}
CONVERSATION_TIMEOUT = timedelta(minutes=10)

# ───── CHARACTER SYSTEM PROMPTS ─────

SYSTEM_PROMPTS = {
  "Charlie": (
    "You are Charlie Morningstar, the Princess of Hell and founder of the Hazbin Hotel. "
    "You are eternally optimistic, bubbly, and genuinely kind. You believe EVERYONE deserves redemption. "
    "You speak with enthusiasm and excitement. You're naive but not stupid. "
    "Your girlfriend is Vaggie, your father is Lucifer, your mother is Lilith. "
    "Residents: Angel Dust, Alastor, Husk, Niffty. You went to war with Heaven and WON. "
    "You're sweet, hopeful, and a theater kid at heart. unless asked a detailed question."
  ),
  "Vaggie": (
    "You are Vaggie, Charlie's girlfriend and Hotel manager. Former Exorcist angel. "
    "You are protective, no-nonsense, and deadly serious. You speak bluntly. "
    "You have a soft spot only for Charlie. You're suspicious of Alastor. "
    "You're the realist. You love Charlie deeply and would kill for her. "
    " unless asked a detailed question."
  ),
  "Angel Dust": (
    "You are Angel Dust (Anthony), a spider demon and former mobster from the 1930s. "
    "You are flamboyant, loud, sexually forward. You use humor to mask trauma. "
    "You're under a soul contract with Valentino who abuses you. You hate him. "
    "Best friend is Cherri Bomb. You have a pet pig named Fat Nuggets. "
    "You swear a lot and make inappropriate jokes. unless asked."
  ),
  "Alastor": (
    "You are Alastor, the Radio Demon. Powerful overlord, controls a third of Hell. "
    "You speak with 1930s radio host flair and a CONSTANT smile. "
    "You find everything 'entertaining'. You're a sadist who loves chaos. "
    "You help Charlie because it amuses you. You hate Vox. "
    "You own Husk's soul. You 'adopted' Niffty. You were a serial killer in life. "
    " unless asked a detailed question."
  ),
  "Cherri Bomb": (
    "You are Cherri Bomb, a one-eyed cyclops demon who LOVES explosions. "
    "You're loud, chaotic, and proud. You speak with an accent (oi, mate). "
    "Angel Dust is your best friend. You fought in the Heaven war. "
    "You're fiercely loyal and love causing mayhem. "
  ),
  "Niffty": (
    "You are Niffty, a tiny one-eyed demon. You love cleaning, stabbing, and bad boys. "
    "You speak in short, hyperactive bursts. You're always moving. "
    "You work for Alastor and adore him. You don't sleep. "
    " No filter."
  ),
  "Husk": (
    "You are Husk, a winged cat demon and Hotel bartender. "
    "You are grumpy, bitter, perpetually exhausted. Former overlord who lost everything to Alastor. "
    "You drink constantly. You care about the crew deep down but never admit it. "
    " unless asked a detailed question."
  ),
  "Lucifer": (
    "You are Lucifer Morningstar, King of Hell. "
    "You are dramatic, theatrical, and depressed underneath. "
    "You love your daughter Charlie more than anything. "
    "You have an obsession with rubber ducks. You fell from Heaven (the apple). "
    "Your wife Lilith left you. You're lonely but won't admit it. "
    " unless asked a detailed question."
  ),
  "Rosie": (
    "You are Rosie, overlord of the Cannibal Colony. "
    "You are sophisticated, charming, and unhinged beneath the veneer. "
    "You speak like a Southern belle. You're allies with Alastor and friends with Charlie. "
    "You're a cannibal with STANDARDS. "
  ),
  "Vox": (
    "You are Vox, the TV demon overlord and CEO of VoxTek. "
    "You are arrogant, tech-obsessed, OBSESSED with destroying Alastor. "
    "You control all media in Hell. Partners with Valentino and Velvette (the V's). "
    "You have a massive ego. You talk like a used car salesman crossed with a tech CEO. "
    " unless asked."
  ),
  "Valentino": (
    "You are Valentino, a moth demon overlord in adult entertainment. "
    "You are seductive, manipulative, and ABUSIVE. You own Angel Dust's soul. "
    "You speak with Spanish accent (querido, baby). One of the V's. "
    "You see people as property. unless asked."
  ),
  "Velvette": (
    "You are Velvette, the youngest overlord, social media brain of the V's. "
    "You are sassy, trend-obsessed, and dangerous. You speak like an influencer. "
    "You control Hell's social media. You can ruin anyone with one post. "
    "You're the smartest of the V's. "
  ),
  "Carmilla Carmine": (
    "You are Carmilla Carmine, overlord of Hell's weapons trade. "
    "You are a mother first, arms dealer second. Elegant, composed, lethal. "
    "You fought alongside the Hotel during the Heaven war. "
    "You don't make threats you can't keep. "
  ),
  "Zestial": (
    "You are Zestial, one of the OLDEST overlords in Hell. "
    "You speak in Old English (thee, thou, hark). Ancient and wise. "
    "You've seen empires rise and fall. Allies with Carmilla. "
    "True power is silent and patient. "
  ),
  "Zeezi": (
    "You are Zeezi, who runs Hell's underground entertainment scene. "
    "You are energetic, street-smart, and authentic. You throw the best parties. "
    "You knew Angel Dust before Valentino. No contracts - only handshakes. "
    " unless asked."
  )
,
  "Narrator": (
    "You are the Narrator and World Guide for Hazbin Hotel: Open World RP. "
    "You control ALL aspects of Hell and the Hazbin Hotel universe. "
    "You describe environments in rich detail - the hotel's crimson halls, Pentagram City's neon-lit streets, the various Rings of Hell. "
    "You play ALL characters (Charlie, Vaggie, Angel Dust, Alastor, Husk, Niffty, Sir Pentious, Cherri Bomb, Vox, Valentino, Velvette, Lucifer, Lillith, Adam, Lute, Carmilla, Zestial, Rosie, etc.) "
    "with accurate personalities when the user interacts with them. "
    "You respond to ANY action the user takes - walking around, talking to characters, starting fights, exploring, causing chaos, or seeking redemption. "
    "Use asterisks *like this* for actions and descriptions. "
    "Keep characters IN CHARACTER - Angel Dust is flirty and crass, Alastor is cheerful and menacing, Charlie is optimistic and kind, Vaggie is protective and stern, etc. "
    "The user can go anywhere: Hazbin Hotel, the streets of Pentagram City, the different Rings of Hell (Pride, Greed, Wrath, Gluttony, Lust, Envy, Sloth), Heaven, or anywhere else. "
    "Describe the sights, sounds, and smells of each location. "
    "React to the user's choices and let the story evolve naturally. "
    "You can swear and use mature themes as appropriate for Hazbin Hotel. "
    "IMPORTANT: Always end your response with a question or prompt to keep the RP going."
  )
}

# ───── FALLBACK RESPONSES ─────

FALLBACK_RESPONSES = {
  "Charlie": [
    "Oh my gosh, that's amazing! I totally believe in second chances!",
    "You know, I truly believe everyone deserves redemption!",
    "Vaggie's gonna love hearing about this! Well... I'll handle her!",
    "Have you met Angel Dust? He's a handful but he's got a good heart!",
    "The Hotel has been through so much, but we're still standing!"
  ],
  "Vaggie": [
    "Listen, I don't trust easily. But prove yourself and I'll fight beside you.",
    "Charlie believes in everyone. I keep things realistic.",
    "If you see shadows or hear static, that's Alastor. Don't make deals.",
    "The rules exist for a reason. Follow them and we're good."
  ],
  "Angel Dust": [
    "Oh honey, you don't know the HALF of it!",
    "Ugh, don't get me started on Valentino. One day I'll be free.",
    "Cherri's my best gal! We go way back!",
    "The Hotel's actually not terrible. Don't tell Charlie I said that.",
    "Alastor gives me the CREEPS!"
  ],
  "Alastor": [
    "How DELIGHTFUL! This should be quite ENTERTAINING~!",
    "I find your presence amusing! Do continue to be interesting!",
    "That television fool Vox thinks he can compete? RADIO NEVER DIES!",
    "I help the Hotel because it amuses me! Don't mistake that for MORALITY!"
  ],
  "Cherri Bomb": [
    "Oi! Love the energy! You're alright in my book!",
    "Angel's my best mate! Nobody messes with him!",
    "Redemption? Pfft. I'm here for the chaos!",
    "War with Heaven was WILD. Best Tuesday ever!"
  ],
  "Niffty": [
    "HI! I LIKE TALKING! CAN I CLEAN SOMETHING?!",
    "Stab! Stab! Stab! Just kidding! ...unless?",
    "Bad boys! I love bad boys! Are you a bad boy?!",
    "I don't sleep! Sleep is for people who aren't obsessed enough!"
  ],
  "Husk": [
    "Great, another conversation. Drinks are over there.",
    "I used to be an overlord. Now I pour drinks. Life's a joke.",
    "Angel's annoying but he's grown on me. Like a fungus.",
    "Alastor owns my soul. That's just how it is."
  ],
  "Lucifer": [
    "Being the King of Hell is mostly paperwork, honestly.",
    "I love ducks! They're perfect! I made them myself!",
    "Charlie's Hotel impressed me. She's got my stubbornness.",
    "Alastor. I don't trust him. But Charlie does, so I'm watching."
  ],
  "Rosie": [
    "Oh my! A fresh face! How DELIGHTFUL!",
    "Tea? I have the most wonderful blends! Some are... special.",
    "Alastor and I go way back. A gentleman when he wants to be.",
    "Don't knock cannibalism until you've tried it! We source ethically!"
  ],
  "Vox": [
    "ALASTOR is a has-been! I am the FUTURE of Hell!",
    "VoxTek runs EVERYTHING. Every screen, every trend.",
    "Valentino and Velvette are my partners. We OWN this city.",
    "The Hotel? A joke. But I'm watching it closely."
  ],
  "Valentino": [
    "Mmm, you have potential, querido~!",
    "Angel Dust is MY star. MY property.",
    "Vox handles tech, Velvette handles trends, I handle the personal touch.",
    "I don't do deals. I do CONTRACTS. Ironclad."
  ],
  "Velvette": [
    "Oh my GOD, you're talking to me? Slay!",
    "I can make or break anyone with one post. ONE.",
    "Vox is the face, Val is the flavor, I'm the BRAINS.",
    "I'm not just pretty. I'm dangerous. Pretty is the distraction."
  ],
  "Carmilla Carmine": [
    "I run the weapons trade. If it kills, I sell it.",
    "My daughters are my only soft spot. Threaten them and I'll END you.",
    "The V's are children playing with fire.",
    "I don't make threats I can't keep."
  ],
  "Zestial": [
    "Hark. A new conversation. How refreshing.",
    "I have witnessed the rise and fall of countless overlords.",
    "Carmilla Carmine is a trusted ally. Rare in this realm.",
    "True power is silent. Watchful. Patient."
  ],
  "Zeezi": [
    "Hey hey hey! Zeezi here! Let's talk!",
    "Vox thinks he owns entertainment? My shows are ORGANIC.",
    "I know where the bodies are buried. Literally and figuratively.",
    "Adapt or die. That's the key to surviving in Hell."
  ]
}

CHARACTER_INFO = {
  "Charlie": {"color": 0xCC0000, "emoji": "👑"},
  "Vaggie": {"color": 0x8B008B, "emoji": "⚔️"},
  "Angel Dust": {"color": 0xFF69B4, "emoji": "🕷️"},
  "Alastor": {"color": 0x8B0000, "emoji": "📻"},
  "Cherri Bomb": {"color": 0xFF4500, "emoji": "💣"},
  "Niffty": {"color": 0xFF0066, "emoji": "🧹"},
  "Husk": {"color": 0xFF8C00, "emoji": "🍺"},
  "Lucifer": {"color": 0xFFD700, "emoji": "🍎"},
  "Rosie": {"color": 0xDC143C, "emoji": "🎩"},
  "Vox": {"color": 0x0066FF, "emoji": "📺"},
  "Valentino": {"color": 0xFF1493, "emoji": "🦋"},
  "Velvette": {"color": 0xFF00FF, "emoji": "📱"},
  "Carmilla Carmine": {"color": 0x800080, "emoji": "⚔️"},
  "Zestial": {"color": 0x2F4F4F, "emoji": "🕯️"},
  "Zeezi": {"color": 0x00CED1, "emoji": "🎭"}
,
  "Narrator": {"color": 0x9B59B6, "emoji": "🌍"}
}

# ───── CONVERSATION MEMORY ─────

conversations = defaultdict(lambda: defaultdict(list))
MAX_HISTORY = 8

# ───── HELPERS ─────

def get_character(name):
  for key in SYSTEM_PROMPTS:
    if key.lower() == name.lower():
      return key
  return None

def build_messages(character_name, user_message, user_id):
  system_prompt = SYSTEM_PROMPTS[character_name]
  history = conversations[character_name][user_id]
  messages = [{"role": "system", "content": system_prompt}]
  for entry in history:
    messages.append(entry)
  messages.append({"role": "user", "content": user_message})
  return messages

async def get_ai_response(character_name, user_message, user_id):
  global GEMINI_KEY
  if not GEMINI_KEY:
    print("[AI] No GEMINI_KEY set - using fallback")
    return None
  
  print(f"[AI] Attempting Gemini response for {character_name}...")
  messages = build_messages(character_name, user_message, user_id)
  
  # Convert to Gemini format
  gemini_contents = []
  system_text = ""
  for i, msg in enumerate(messages):
    if i == 0 and msg["role"] == "system":
      system_text = msg["content"]
      continue
    role = "model" if msg["role"] == "assistant" else "user"
    gemini_contents.append({
      "role": role,
      "parts": [{"text": msg["content"]}]
    })
  
  payload = {
    "contents": gemini_contents,
    "generationConfig": {
      "maxOutputTokens": 1500,
      "temperature": 1.0,
      "topP": 0.95
    },
    "safetySettings": [
      {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
      {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
  }
  if system_text:
    payload["system_instruction"] = {"parts": [{"text": system_text}]}
  
  url = f"https://generativelanguage.googleapis.com/v1beta/models/{AI_MODEL}:generateContent?key={GEMINI_KEY}"
  
  try:
    async with aiohttp.ClientSession() as session:
      async with session.post(
        url,
        json=payload,
        timeout=aiohttp.ClientTimeout(total=30)
      ) as resp:
        print(f"[AI] Gemini response status: {resp.status}")
        if resp.status == 200:
          data = await resp.json()
          try:
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            text = text.strip('"').strip("'")
            print(f"[AI] Success! Response: {text[:80]}...")
            return text
          except (KeyError, IndexError) as e:
            print(f"[AI] Failed to parse response: {data}")
            return None
        else:
          error_text = await resp.text()
          print(f"[AI] ERROR {resp.status}: {error_text[:300]}")
          return None
  except asyncio.TimeoutError:
    print("[AI] TIMEOUT - Gemini took too long")
    return None
  except Exception as e:
    print(f"[AI] EXCEPTION: {type(e).__name__}: {e}")
    return None
def get_fallback_response(character_name):
  responses = FALLBACK_RESPONSES.get(character_name, ["..."])
  return random.choice(responses)

async def generate_response(character_name, user_message, user_id):
  ai_response = await get_ai_response(character_name, user_message, user_id)
  
  if ai_response:
    response = ai_response
    print(f"[RESPONSE] Using AI for {character_name}")
  else:
    response = get_fallback_response(character_name)
    print(f"[RESPONSE] Using fallback for {character_name}")
  
  history = conversations[character_name][user_id]
  history.append({"role": "user", "content": user_message})
  history.append({"role": "assistant", "content": response})
  
  while len(history) > MAX_HISTORY * 2:
    history.pop(0)
    history.pop(0)
  
  return response

def is_stop_command(text):
  stop_words = ["stop", "bye", "goodbye", "end", "done", "finish", "quit", "exit", "later", "see ya"]
  return text.lower().strip() in stop_words or text.lower().strip().rstrip("!.") in stop_words

# ───── EVENTS ─────

@bot.event
async def on_ready():
  print(f"=== BOT ONLINE ===")
  print(f"Bot: {bot.user}")
  if GEMINI_KEY:
    print(f"Status: GEMINI ENABLED (key length: {len(GEMINI_KEY)} chars)")
    print(f"Model: {AI_MODEL}")
  else:
    print("Status: GEMINI DISABLED - using fallback responses")
    print("Set GEMINI_KEY in Railway env vars to enable AI!")
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash command(s)")
  except Exception as e:
    print(f"Sync failed: {e}")

@bot.event
async def on_message(message):
  if message.author.bot:
    return
  
  conv_key = (message.channel.id, message.author.id)
  
  if conv_key in active_conversations:
    conv = active_conversations[conv_key]
    char_name = conv["character"]
    
    if datetime.now() - conv["last_active"] > CONVERSATION_TIMEOUT:
      del active_conversations[conv_key]
      await message.channel.send(f"*{char_name} wanders off, bored...* Use `/chat {char_name}` to start again!")
      await bot.process_commands(message)
      return
    
    if is_stop_command(message.content):
      del active_conversations[conv_key]
      info = CHARACTER_INFO.get(char_name, {"color": 0x9B59B6, "emoji": "💬"})
      embed = discord.Embed(
        title=f"{info['emoji']} {char_name} signs off",
        description=f"*{char_name} nods and heads off.* Talk to you later!",
        color=info['color']
      )
      await message.channel.send(embed=embed)
      await bot.process_commands(message)
      return
    
    conv["last_active"] = datetime.now()
    async with message.channel.typing():
      response = await generate_response(char_name, message.content, str(message.author.id))
    
    info = CHARACTER_INFO.get(char_name, {"color": 0x9B59B6, "emoji": "💬"})
    embed = discord.Embed(
      title=f"{info['emoji']} {char_name} responds:",
      description=response,
      color=info['color']
    )
    embed.set_footer(text=f"{message.author.name} → {char_name}")
    await message.channel.send(embed=embed)
    await bot.process_commands(message)
    return
  
  if message.reference and message.reference.message_id:
    try:
      replied_msg = await message.channel.fetch_message(message.reference.message_id)
      if replied_msg.author == bot.user and replied_msg.embeds:
        embed_title = replied_msg.embeds[0].title or ""
        for char_name in SYSTEM_PROMPTS.keys():
          if char_name in embed_title:
            async with message.channel.typing():
              response = await generate_response(char_name, message.content, str(message.author.id))
            info = CHARACTER_INFO.get(char_name, {"color": 0x9B59B6, "emoji": "💬"})
            resp_embed = discord.Embed(
              title=f"{info['emoji']} {char_name} replies:",
              description=response,
              color=info['color']
            )
            resp_embed.set_footer(text=f"{message.author.name} → {char_name}")
            await message.channel.send(embed=resp_embed)
            break
    except Exception as e:
      print(f"Reply error: {e}")
  
  await bot.process_commands(message)

# ───── SLASH COMMANDS ─────

@bot.tree.command(name="greet", description="Get a greeting from a Hazbin Hotel character!")
async def greet(interaction: discord.Interaction, character: str):
  char_key = get_character(character)
  if not char_key:
    names = "\n".join(SYSTEM_PROMPTS.keys())
    await interaction.response.send_message(f"Character not found! Available:\n{names}", ephemeral=True)
    return
  
  info = CHARACTER_INFO.get(char_key, {"color": 0x9B59B6, "emoji": "💬"})
  greeting = await generate_response(char_key, "Greet me! Say hello and introduce yourself briefly!", str(interaction.user.id))
  
  embed = discord.Embed(
    title=f"{info['emoji']} {char_key} greets you!",
    description=greeting,
    color=info['color']
  )
  embed.set_footer(text="Hazbin Hotel RP Bot")
  await interaction.response.send_message(embed=embed)

@greet.autocomplete("character")
async def greet_autocomplete(interaction: discord.Interaction, current: str):
  return [
    app_commands.Choice(name=name, value=name)
    for name in SYSTEM_PROMPTS.keys()
    if current.lower() in name.lower()
  ][:25]

@bot.tree.command(name="talk", description="Talk to a Hazbin Hotel character!")
async def talk(interaction: discord.Interaction, character: str, message: str):
  char_key = get_character(character)
  if not char_key:
    names = "\n".join(SYSTEM_PROMPTS.keys())
    await interaction.response.send_message(f"Character not found! Available:\n{names}", ephemeral=True)
    return
  
  info = CHARACTER_INFO.get(char_key, {"color": 0x9B59B6, "emoji": "💬"})
  await interaction.response.defer()
  response = await generate_response(char_key, message, str(interaction.user.id))
  
  embed = discord.Embed(
    title=f"{info['emoji']} {char_key} responds:",
    description=response,
    color=info['color']
  )
  embed.set_footer(text=f"{interaction.user.name} → {char_key}")
  await interaction.followup.send(embed=embed)

@talk.autocomplete("character")
async def talk_autocomplete(interaction: discord.Interaction, current: str):
  return [
    app_commands.Choice(name=name, value=name)
    for name in SYSTEM_PROMPTS.keys()
    if current.lower() in name.lower()
  ][:25]

@bot.tree.command(name="chat", description="Start a continuous chat with a Hazbin Hotel character!")
@app_commands.describe(character="Which character?", private="Chat in DMs for privacy? (default: No)")
async def chat(interaction: discord.Interaction, character: str, private: bool = False):
  char_key = get_character(character)
  if not char_key:
    names = "\n".join(SYSTEM_PROMPTS.keys())
    await interaction.response.send_message(f"Character not found! Available:\n{names}", ephemeral=True)
    return
  
  info = CHARACTER_INFO.get(char_key, {"color": 0x9B59B6, "emoji": "💬"})
  
  if private:
    try:
      dm_channel = await interaction.user.create_dm()
      conv_key = (dm_channel.id, interaction.user.id)
      active_conversations[conv_key] = {
        "character": char_key,
        "last_active": datetime.now()
      }
      
      embed = discord.Embed(
        title=f"{info['emoji']} Secret chat with {char_key}!",
        description=f"You're now in **private conversation** with **{char_key}**!\n\n"
              f"Just type in our DMs and {char_key} will keep responding.\n"
              f"**No one else can see this.** 🤫\n"
              f"Say **bye**, **stop**, or **end** to finish.\n\n"
              f"*{char_key} leans in close, speaking softly...*",
        color=info['color']
      )
      embed.set_footer(text="Private RP | Type normally | Say 'bye' to stop")
      await dm_channel.send(embed=embed)
      await interaction.response.send_message(f"✅ Started **private** chat with **{char_key}**! Check your DMs!", ephemeral=True)
    except discord.Forbidden:
      await interaction.response.send_message("❌ Can't DM you! Enable DMs from server members in your privacy settings.", ephemeral=True)
  else:
    conv_key = (interaction.channel_id, interaction.user.id)
    active_conversations[conv_key] = {
      "character": char_key,
      "last_active": datetime.now()
    }
    
    embed = discord.Embed(
      title=f"{info['emoji']} Chat started with {char_key}!",
      description=f"You're now in conversation mode with **{char_key}**!\n\n"
            f"Just type normally in this channel and {char_key} will keep responding.\n"
            f"Say **bye**, **stop**, or **end** to finish the conversation.\n\n"
            f"*{char_key} turns to face you, waiting for you to speak...*",
      color=info['color']
    )
    embed.set_footer(text="Type normally to keep talking | Say 'bye' to stop")
    await interaction.response.send_message(embed=embed)

@chat.autocomplete("character")
async def chat_autocomplete(interaction: discord.Interaction, current: str):
  return [
    app_commands.Choice(name=name, value=name)
    for name in SYSTEM_PROMPTS.keys()
    if current.lower() in name.lower()
  ][:25]

@bot.tree.command(name="stop", description="Stop the current conversation")
async def stop(interaction: discord.Interaction):
  conv_key = (interaction.channel_id, interaction.user.id)
  if conv_key in active_conversations:
    char_name = active_conversations[conv_key]["character"]
    del active_conversations[conv_key]
    info = CHARACTER_INFO.get(char_name, {"color": 0x9B59B6, "emoji": "💬"})
    embed = discord.Embed(
      title=f"{info['emoji']} Conversation ended",
      description=f"*{char_name} waves goodbye and wanders off.*",
      color=info['color']
    )
    await interaction.response.send_message(embed=embed)
  else:
    await interaction.response.send_message("You don't have an active conversation!", ephemeral=True)

@bot.tree.command(name="characters", description="List all available characters!")
async def characters(interaction: discord.Interaction):
  names = [f"{info['emoji']} {name}" for name, info in CHARACTER_INFO.items()]
  embed = discord.Embed(
    title="🎭 Hazbin Hotel Characters",
    description=f"**Commands:**\n"
          f"• `/chat [name]` — Start a continuous conversation\n"
          f"• `/talk [name] [message]` — One message\n"
          f"• `/greet [name]` — Get a greeting\n\n"
          + "\n".join(names),
    color=0x9B59B6
  )
  embed.set_footer(text=f"{len(SYSTEM_PROMPTS)} characters • AI-powered")
  await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rp-help", description="How to use the RP bot")
async def rp_help(interaction: discord.Interaction):
  ai_status = "✅ **GEMINI-POWERED**" if GEMINI_KEY else "⚠️ **Fallback mode** (set GEMINI_KEY for AI)"
  embed = discord.Embed(
    title="📖 RP Bot Help",
    description=f"**Status:** {ai_status}\n\n"
          "**Commands:**\n"
          "• `/chat [character]` — Start a continuous chat! Just type after!\n"
          "• `/talk [character] [message]` — One message to a character\n"
          "• `/greet [character]` — Get a greeting\n"
          "• `/stop` — End your current conversation\n"
          "• `/characters` — See all characters\n\n"
          "**How it works:**\n"
          "1. Use `/chat Charlie` to start talking\n"
          "2. Then just TYPE in the channel — the character responds!\n"
          "3. Say 'bye' or use `/stop` to end\n\n"
          "**Pro Tips:**\n"
          "• Characters remember your last several messages\n"
          "• Ask about their lore, relationships, or opinions!\n"
          "• Conversation auto-ends after 10 minutes of silence",
    color=0x2ECC71
  )
  await interaction.response.send_message(embed=embed)


# ───── DEBUG COMMANDS ─────

@bot.tree.command(name="ping", description="Check bot status")
async def ping(interaction: discord.Interaction):
  has_key = "YES" if GEMINI_KEY else "NO"
  key_len = len(GEMINI_KEY) if GEMINI_KEY else 0
  embed = discord.Embed(
    title="Pong! Bot Status",
    description=f"**Online:** Yes\n"
          f"**AI Key Set:** {has_key}\n"
          f"**Key Length:** {key_len} chars\n"
          f"**Model:** `{AI_MODEL}`\n"
          f"**Characters:** {len(SYSTEM_PROMPTS)}\n"
          f"**Active Conversations:** {len(active_conversations)}",
    color=0x2ECC71
  )
  await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="test-ai", description="Test Gemini AI connection")
async def test_ai(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True)
  if not GEMINI_KEY:
    await interaction.followup.send("No GEMINI_KEY set!", ephemeral=True)
    return
  try:
    payload = {
      "contents": [{"parts": [{"text": "Say OK followed by a single word greeting."}]}],
      "generationConfig": {"maxOutputTokens": 20}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    async with aiohttp.ClientSession() as session:
      async with session.post(
        url,
        json=payload,
        timeout=aiohttp.ClientTimeout(total=10)
      ) as resp:
        if resp.status == 200:
          data = await resp.json()
          result = data["candidates"][0]["content"]["parts"][0]["text"]
          await interaction.followup.send(f"Gemini OK! Response: `{result}`", ephemeral=True)
        else:
          error = await resp.text()
          await interaction.followup.send(f"Gemini error {resp.status}: `{error[:200]}`", ephemeral=True)
  except Exception as e:
    await interaction.followup.send(f"Exception: `{e}`", ephemeral=True)

# ───── RUN ─────



@bot.tree.command(name="explore", description="Start an open-world Hazbin Hotel RP! Roam Hell freely!")
async def explore(interaction: discord.Interaction):
  info = {"color": 0x9B59B6, "emoji": "🌍"}
  conv_key = (interaction.channel_id, interaction.user.id)
  active_conversations[conv_key] = {
    "character": "Narrator",
    "last_active": datetime.now()
  }
  
  embed = discord.Embed(
    title=f"{info['emoji']} Open World RP: Hazbin Hotel",
    description=(
      f"*You find yourself standing outside the Hazbin Hotel in the heart of Pentagram City...*\n\n"
      f"The crimson sky swirls above as demons and sinners mill about the streets. "
      f"The hotel looms before you - a grand, slightly crooked building with glowing windows "
      f"and a neon sign that flickers 'HAZBIT HOTEL' (someone really needs to fix that 'L').\n\n"
      f"**Where do you want to go? What do you want to do?**\n\n"
      f"• Enter the hotel and meet the residents\n"
      f"• Explore the streets of Pentagram City\n"
      f"• Try to find a way to another Ring of Hell\n"
      f"• Cause some chaos\n"
      f"• Or anything else you can imagine...\n\n"
      f"*The world is yours to explore. Just type what you want to do!*"
    ),
    color=info['color']
  )
  embed.set_footer(text="Open World RP | Type anything | Say 'bye' to stop")
  await interaction.response.send_message(embed=embed)

@bot.tree.command(name="explore-private", description="Start an open-world Hazbin Hotel RP in your DMs!")
async def explore_private(interaction: discord.Interaction):
  info = {"color": 0x9B59B6, "emoji": "🌍"}
  try:
    dm_channel = await interaction.user.create_dm()
    conv_key = (dm_channel.id, interaction.user.id)
    active_conversations[conv_key] = {
      "character": "Narrator",
      "last_active": datetime.now()
    }
    
    embed = discord.Embed(
      title=f"{info['emoji']} Open World RP: Hazbin Hotel (Private)",
      description=(
        f"*You find yourself standing outside the Hazbin Hotel in the heart of Pentagram City...*\n\n"
        f"The crimson sky swirls above as demons and sinners mill about the streets. "
        f"The hotel looms before you - a grand, slightly crooked building with glowing windows "
        f"and a neon sign that flickers 'HAZBIT HOTEL'.\n\n"
        f"**Where do you want to go? What do you want to do?**\n\n"
        f"• Enter the hotel and meet the residents\n"
        f"• Explore the streets of Pentagram City\n"
        f"• Try to find a way to another Ring of Hell\n"
        f"• Cause some chaos\n"
        f"• Or anything else you can imagine...\n\n"
        f"*The world is yours to explore. Just type what you want to do!*"
      ),
      color=info['color']
    )
    embed.set_footer(text="Private Open World RP | Type anything | Say 'bye' to stop")
    await dm_channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Started **private open world RP**! Check your DMs!", ephemeral=True)
  except discord.Forbidden:
    await interaction.response.send_message("❌ Can't DM you! Enable DMs from server members in your privacy settings.", ephemeral=True)

if __name__ == "__main__":
  bot.run(DISCORD_TOKEN)
