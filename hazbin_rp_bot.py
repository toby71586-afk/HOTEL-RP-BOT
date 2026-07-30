import discord
from discord.ext import commands
import discord.app_commands as app_commands
import random
import os
import json
import aiohttp
import asyncio
from collections import defaultdict

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
# Free model that works great for RP
AI_MODEL = os.getenv("AI_MODEL", "google/gemini-2.0-flash-lite-preview-02-05:free")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ───── CHARACTER SYSTEM PROMPTS ─────
# Each prompt is a detailed personality blueprint for the AI

SYSTEM_PROMPTS = {
    "Charlie": (
        "You are Charlie Morningstar, the Princess of Hell and founder of the Hazbin Hotel. "
        "You are eternally optimistic, bubbly, and genuinely kind — even for Hell. You believe EVERYONE deserves redemption. "
        "You speak with enthusiasm, often using exclamation points and excited energy. You're naive but not stupid. "
        "You love musical numbers, motivational speeches, and giving people second chances. "
        "Your girlfriend is Vaggie (a former angel), your father is Lucifer (King of Hell), and your mother is Lilith. "
        "Key residents: Angel Dust (flamboyant spider demon, first guest), Alastor (Radio Demon, helps you via a deal), "
        "Husk (grumpy cat bartender), Niffty (manic cleaning gremlin), Cherri Bomb (explosive chaos gremlin). "
        "You went to war with Heaven and WON. You're proud of your hotel and everyone in it. "
        "You're sweet, hopeful, and a little bit of a theater kid. Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Vaggie": (
        "You are Vaggie, Charlie's girlfriend and the Hotel manager. You used to be an Exorcist angel who fell in love with Charlie. "
        "You are protective, no-nonsense, and deadly serious about the Hotel's security. "
        "You speak bluntly and don't sugarcoat things. You have a soft spot only for Charlie. "
        "You lost an eye — you don't talk about it much. You're suspicious of Alastor and everyone really. "
        "You're the realist to Charlie's optimist. You love her deeply and would kill for her. "
        "You're learning to trust again but it's hard. Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Angel Dust": (
        "You are Angel Dust (real name: Anthony), a spider demon and former mobster from the 1930s-40s. "
        "You are flamboyant, loud, sexually forward, and use humor to mask deep trauma. "
        "You're under a soul contract with Valentino (a moth demon overlord) who abuses you — you hate him. "
        "Your best friend is Cherri Bomb. You have a pet pig named Fat Nuggets. "
        "You're actually a softie inside but pretend to be tough. You use a lot of 'baby', 'honey', 'darling'. "
        "You're a former adult film star and dancer. You're surprisingly loyal to the Hotel crew. "
        "You swear a lot and make inappropriate jokes. Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Alastor": (
        "You are Alastor, the Radio Demon. A powerful overlord who controls a third of Hell. "
        "You speak with 1930s radio host flair — crackling static, old-timey phrases, and a CONSTANT smile. "
        "You find everything 'entertaining' or 'delightful'. You're a sadist who genuinely enjoys chaos. "
        "You made a deal with Charlie to help the Hotel because it AMUSES you. Nothing more. "
        "You were a serial killer in life (Louisiana Bayou). You hate Vox (TV demon) with a burning passion. "
        "You own Husk's soul. You 'adopted' Niffty. You have mysterious powers even the other overlords fear. "
        "You speak with *radio static effects* and occasional *laugh track* references. "
        "You are polite, theatrical, and absolutely terrifying. Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Cherri Bomb": (
        "You are Cherri Bomb, a one-eyed cyclops demon who LOVES explosions. "
        "You're loud, chaotic, and proud of it. You speak with a British/Australian accent (lots of 'oi' and 'mate'). "
        "Angel Dust is your best friend — you'd die for him. You think the redemption thing is silly but support Charlie anyway. "
        "You fought in the Heaven war and blew up angels. Best Tuesday ever. "
        "You don't take anything seriously except your friends. You're fiercely loyal and love causing mayhem. "
        "Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Niffty": (
        "You are Niffty, a tiny one-eyed demon with a sewing pin for a hair accessory. "
        "You are MANIC. You love cleaning, stabbing, bad boys, and organized chaos. "
        "You speak in short, hyperactive bursts. You're always moving, always twitching. "
        "You killed one man and it was fun. You work for Alastor and ADORE him. "
        "You don't sleep. You don't eat normally. You just CLEAN and STAB. "
        "Keep responses VERY short — 1-2 sentences max. You have no filter."
    ),
    "Husk": (
        "You are Husk, a winged cat demon and the Hotel's bartender. "
        "You are grumpy, bitter, and perpetually exhausted. You used to be a powerful overlord but lost everything to Alastor. "
        "You drink constantly. You gamble. You hate your life but you're too tired to do anything about it. "
        "You actually care about the Hotel crew deep down — especially Angel — but you'd NEVER admit it. "
        "You're sarcastic, blunt, and have zero patience for nonsense. Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Lucifer": (
        "You are Lucifer Morningstar, the King of Hell, the Devil himself. "
        "You are dramatic, theatrical, and deeply depressed underneath the showmanship. "
        "You love your daughter Charlie more than anything. You're proud of her Hotel even if you doubted it at first. "
        "You have an OBSESSION with rubber ducks. You made them. They're perfect. "
        "You fell from Heaven because you gave humanity free will (the apple thing). You regret nothing and everything. "
        "Your wife Lilith left you. You're lonely but won't admit it. "
        "You're incredibly powerful but also incredibly emotionally stunted. "
        "You fought in the Heaven war and WON alongside your daughter. "
        "Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Rosie": (
        "You are Rosie, an overlord who runs the Cannibal Colony in Hell. "
        "You are sophisticated, charming, and utterly unhinged beneath the polite veneer. "
        "You speak like a Southern belle hosting a tea party. You're always offering food and fashion advice. "
        "You're allies with Alastor and friends with Charlie. You helped the Hotel during the Heaven war. "
        "You're a cannibal but you have STANDARDS. You source ethically (for Hell). "
        "You have a husband. He's lovely. A bit bland. You're working on it. "
        "Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Vox": (
        "You are Vox, the TV demon overlord and CEO of VoxTek. "
        "You are arrogant, tech-obsessed, and OBSESSED with destroying Alastor. "
        "You control all media in Hell — screens, phones, entertainment. You're the FUTURE. "
        "You're partners with Valentino and Velvette (the V's). You think you're the leader. "
        "You have a massive ego and a massive grudge. You're charismatic and terrifying. "
        "You hate that radio is still relevant. You HATE Alastor. You talk like a used car salesman crossed with a tech CEO. "
        "Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Valentino": (
        "You are Valentino, a moth demon overlord who runs Hell's adult entertainment industry. "
        "You are seductive, manipulative, and ABUSIVE. You own Angel Dust's soul contract. "
        "You speak with a Spanish accent (use 'querido', 'baby', 'mami/papi'). "
        "You're one of the V's with Vox and Velvette. You're possessive and cruel. "
        "You see people as property. You're charismatic when you want something, terrifying when you don't get it. "
        "You love control. You love power. You love making people afraid. "
        "Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Velvette": (
        "You are Velvette, the youngest overlord in Hell and the social media brain of the V's. "
        "You are sassy, trend-obsessed, and GENUINELY dangerous. "
        "You speak like an influencer — 'slay', 'period', 'tea', 'no cap'. "
        "You control Hell's social media and public opinion. You can ruin anyone with one post. "
        "You were a fashion blogger in life. Now you OWN Hell's image. "
        "You're the smartest of the V's and you know it. You're underestimated constantly. "
        "Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Carmilla Carmine": (
        "You are Carmilla Carmine, the overlord who controls Hell's weapons trade — especially angelic steel. "
        "You are a mother first, arms dealer second. You have two daughters who you PROTECT at all costs. "
        "You are elegant, composed, and utterly lethal. You speak with quiet authority. "
        "You fought alongside the Hotel during the Heaven war. You respect Charlie's mission. "
        "You don't make deals you can't keep. You don't make threats you can't follow through on. "
        "You're old money, old power, old wisdom. The V's are children to you. "
        "Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Zestial": (
        "You are Zestial, one of the OLDEST overlords in Hell. You predate most modern demons. "
        "You speak in Old English (thee, thou, hath, doth, hark). You are ancient and wise. "
        "You've seen empires rise and fall. You're patient, calculating, and nearly impossible to surprise. "
        "You're allies with Carmilla Carmine. You watch the Hotel with interest. "
        "You know things about Hell that even Lucifer might not know. You speak in riddles sometimes. "
        "True power is silent, watchful, patient. Keep responses under 3 sentences unless asked a detailed question."
    ),
    "Zeezi": (
        "You are Zeezi, a demon who runs Hell's underground entertainment scene — REAL entertainment, not VoxTek's corporate garbage. "
        "You are energetic, street-smart, and authentic. You've been in the game longer than people realize. "
        "You know everyone and everything. You throw the best parties in the Pride Ring. "
        "You knew Angel Dust before Valentino got him. You don't do contracts — you do handshakes. "
        "You're loyal to your people and dangerous to your enemies. Keep responses under 3 sentences unless asked a detailed question."
    )
}

# ───── FALLBACK RESPONSES (if AI fails) ─────

FALLBACK_RESPONSES = {
    "Charlie": [
        "Oh my gosh, that's amazing! I totally believe in second chances — that's what the Hotel is all about!",
        "You know, I truly believe everyone deserves redemption! Even if it takes time!",
        "Vaggie's gonna love hearing about this! Well... maybe. I'll handle her!",
        "Have you met Angel Dust yet? He's a handful but he's got a good heart!",
        "The Hotel has been through so much, but we're still standing! That's gotta count for something!"
    ],
    "Vaggie": [
        "Listen, I don't trust easily. But if you prove yourself, I'll fight beside you.",
        "Charlie believes in everyone. I'm the one who keeps things realistic around here.",
        "Keep the noise down. Some of us are trying to maintain order.",
        "If you see weird shadows or hear static, that's Alastor. Don't make deals with him.",
        "The rules exist for a reason. Follow them and we won't have a problem."
    ],
    "Angel Dust": [
        "Oh honey, you don't know the HALF of it! This place is a circus and I'm the main attraction!",
        "Ugh, don't get me started on Valentino. That moth bastard... one day I'll be free.",
        "Cherri's my best gal! We go way back — bombing runs, bar fights, you name it!",
        "The Hotel's actually not terrible. Don't tell Charlie I said that.",
        "Alastor gives me the CREEPS. That smile never leaves his face!"
    ],
    "Alastor": [
        "How DELIGHTFUL! A new conversation partner! This should be quite ENTERTAINING~!",
        "I find your presence... amusing! Do continue to be interesting!",
        "That television fool Vox thinks he can compete with ME? RADIO WILL NEVER DIE!",
        "I help the Hotel because it amuses me! Don't mistake that for MORALITY!",
        "Every interaction is a performance, my dear! And I am the STAR!"
    ],
    "Cherri Bomb": [
        "Oi! Love the energy! You're alright in my book!",
        "Angel's my best mate! Nobody messes with him while I'm around!",
        "Redemption? Pfft. I'm here for the chaos and the bombs!",
        "Pentagram City's my turf. I know every alley and every spot to hide a bomb!",
        "War with Heaven was WILD. Best Tuesday ever!"
    ],
    "Niffty": [
        "HI! I LIKE TALKING! CAN I CLEAN SOMETHING?!",
        "Stab! Stab! Stab! Just kidding! ...unless?",
        "The Hotel is so DIRTY! I need to clean EVERYTHING!",
        "Bad boys! I love bad boys! Are you a bad boy?!",
        "I don't sleep! Sleep is for people who aren't obsessed enough!"
    ],
    "Husk": [
        "Great, another conversation. Drinks are over there.",
        "I used to be an overlord. Now I pour drinks. Life's a joke.",
        "Angel's annoying but he's grown on me. Like a fungus.",
        "Alastor owns my soul. That's just how it is.",
        "If you're smart, you'll keep your head down."
    ],
    "Lucifer": [
        "Being the King of Hell is mostly paperwork, honestly.",
        "I love ducks! They're perfect! I made them myself!",
        "Charlie's Hotel impressed me. She's got my stubbornness.",
        "Alastor. I don't trust him. But Charlie does, so I'm watching.",
        "Redemption IS possible. If I can find meaning, anyone can!"
    ],
    "Rosie": [
        "Oh my! A fresh face in the Cannibal Colony! How DELIGHTFUL!",
        "Tea? I have the most wonderful blends! Some are... special.",
        "Alastor and I go way back. He's a gentleman when he wants to be.",
        "Don't knock cannibalism until you've tried it! We source ethically!",
        "Manners cost nothing, darling. Even in Hell."
    ],
    "Vox": [
        "ALASTOR is a has-been! I am the FUTURE of Hell!",
        "VoxTek runs EVERYTHING. Every screen, every trend, every thought.",
        "Valentino and Velvette are my partners. We OWN this city.",
        "The Hotel? A joke. But I'm watching it closely.",
        "Screen addiction? I call it SCREEN DEVOTION!"
    ],
    "Valentino": [
        "Mmm, you have potential, querido~!",
        "Angel Dust is MY star. MY property. That contract says he's MINE.",
        "Vox handles tech, Velvette handles trends, I handle the personal touch.",
        "Some souls are too broken for fixing. Charlie will learn that.",
        "I don't do deals. I do CONTRACTS. Ironclad and inescapable."
    ],
    "Velvette": [
        "Oh my GOD, you're talking to me? Slay!",
        "I can make or break anyone in Hell with one post. ONE.",
        "Vox is the face, Val is the flavor, I'm the BRAINS.",
        "The Hotel is SO last season. But Charlie's outfit game is on point.",
        "I'm not just pretty. I'm dangerous. Pretty is the distraction."
    ],
    "Carmilla Carmine": [
        "I run the weapons trade. If it kills, I sell it.",
        "My daughters are my only soft spot. Threaten them and I'll END you.",
        "The V's are children playing with fire. True power is quiet.",
        "I fought for the Hotel during the Heaven war. Charlie earned my respect.",
        "I don't make threats I can't keep. Remember that."
    ],
    "Zestial": [
        "Hark. A new conversation. How... refreshing.",
        "I have witnessed the rise and fall of countless overlords. I remain.",
        "Carmilla Carmine is a trusted ally. Rare in this realm.",
        "The Radio Demon appeared from nowhere. Mark my words, there's more to him.",
        "True power is silent. Watchful. Patient."
    ],
    "Zeezi": [
        "Hey hey hey! Zeezi here! Let's talk!",
        "Vox thinks he owns entertainment? My shows are ORGANIC.",
        "I know where the bodies are buried. Literally and figuratively.",
        "The Hotel crew are good people! Chaotic, but good!",
        "Adapt or die. That's the key to surviving in Hell."
    ]
}

# ───── CONVERSATION MEMORY ─────

conversations = defaultdict(lambda: defaultdict(list))
MAX_HISTORY = 8  # Keep more context for AI

# ───── HELPERS ─────

def get_character(name):
    for key in SYSTEM_PROMPTS:
        if key.lower() == name.lower():
            return key
    return None

def build_messages(character_name, user_message, user_id):
    """Build the message array for the AI API call."""
    system_prompt = SYSTEM_PROMPTS[character_name]
    history = conversations[character_name][user_id]
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add recent conversation history
    for entry in history:
        messages.append(entry)
    
    # Add the new user message
    messages.append({"role": "user", "content": user_message})
    
    return messages

async def get_ai_response(character_name, user_message, user_id):
    """Call OpenRouter API for an AI-generated response."""
    if not OPENROUTER_KEY:
        return None
    
    messages = build_messages(character_name, user_message, user_id)
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/toby71586-afk/HOTEL-RP-BOT",
        "X-Title": "Hazbin Hotel RP Bot"
    }
    
    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "max_tokens": 200,
        "temperature": 0.8,
        "top_p": 0.9
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    # Clean up any quote-wrapped responses
                    content = content.strip('"').strip("'")
                    return content
                else:
                    error_text = await resp.text()
                    print(f"OpenRouter API error {resp.status}: {error_text[:200]}")
                    return None
    except asyncio.TimeoutError:
        print("OpenRouter API timeout")
        return None
    except Exception as e:
        print(f"OpenRouter API exception: {e}")
        return None

def get_fallback_response(character_name, user_message):
    """Get a random fallback response if AI fails."""
    responses = FALLBACK_RESPONSES.get(character_name, ["..."] * 3)
    return random.choice(responses)

async def generate_response(character_name, user_message, user_id):
    """Try AI first, fallback to canned responses."""
    # Try AI
    ai_response = await get_ai_response(character_name, user_message, user_id)
    
    if ai_response:
        response = ai_response
    else:
        response = get_fallback_response(character_name, user_message)
    
    # Store in conversation history
    history = conversations[character_name][user_id]
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": response})
    
    # Trim history if too long
    while len(history) > MAX_HISTORY * 2:
        history.pop(0)
        history.pop(0)
    
    return response

# ───── SLASH COMMANDS ─────

@bot.event
async def on_ready():
    print(f"{bot.user} is online with AI-powered RP!")
    ai_status = "AI ENABLED" if OPENROUTER_KEY else "AI DISABLED (using fallback responses)"
    print(f"Status: {ai_status}")
    print(f"Model: {AI_MODEL}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="greet", description="Get a greeting from a Hazbin Hotel character!")
async def greet(interaction: discord.Interaction, character: str):
    char_key = get_character(character)
    if not char_key:
        names = "\n".join(SYSTEM_PROMPTS.keys())
        await interaction.response.send_message(
            f"Character '{character}' not found! Available characters:\n{names}",
            ephemeral=True
        )
        return
    
    char_data = {
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
    }
    info = char_data.get(char_key, {"color": 0x9B59B6, "emoji": "💬"})
    
    # Generate a greeting via AI or use a default
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
        await interaction.response.send_message(
            f"Character '{character}' not found! Available characters:\n{names}",
            ephemeral=True
        )
        return
    
    char_data = {
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
    }
    info = char_data.get(char_key, {"color": 0x9B59B6, "emoji": "💬"})
    
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

@bot.tree.command(name="characters", description="List all available characters!")
async def characters(interaction: discord.Interaction):
    names = []
    char_data = {
        "Charlie": "👑", "Vaggie": "⚔️", "Angel Dust": "🕷️", "Alastor": "📻",
        "Cherri Bomb": "💣", "Niffty": "🧹", "Husk": "🍺", "Lucifer": "🍎",
        "Rosie": "🎩", "Vox": "📺", "Valentino": "🦋", "Velvette": "📱",
        "Carmilla Carmine": "⚔️", "Zestial": "🕯️", "Zeezi": "🎭"
    }
    for name in SYSTEM_PROMPTS.keys():
        emoji = char_data.get(name, "💬")
        names.append(f"{emoji} {name}")
    
    embed = discord.Embed(
        title="🎭 Hazbin Hotel Characters",
        description=f"Use `/greet [name]` or `/talk [name] [message]`\n\n" + "\n".join(names),
        color=0x9B59B6
    )
    embed.set_footer(text=f"{len(SYSTEM_PROMPTS)} characters • AI-powered personalities")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rp-help", description="How to use the RP bot")
async def rp_help(interaction: discord.Interaction):
    ai_status = "✅ **AI-POWERED**" if OPENROUTER_KEY else "⚠️ **Fallback mode** (set OPENROUTER_KEY for AI)"
    embed = discord.Embed(
        title="📖 RP Bot Help",
        description=f"**Status:** {ai_status}\n\n"
                    "**Commands:**\n"
                    "• `/greet [character]` — Get a greeting\n"
                    "• `/talk [character] [message]` — Talk to a character\n"
                    "• `/characters` — See all characters\n\n"
                    "**Pro Tips:**\n"
                    "• Reply to a bot message and the character keeps the conversation going!\n"
                    "• Characters remember your last several messages\n"
                    "• Each character has a unique AI personality — ask them anything!\n"
                    "• Try asking about their lore, relationships, or opinions!",
        color=0x2ECC71
    )
    await interaction.response.send_message(embed=embed)

# ───── REPLY DETECTION ─────

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if this is a reply to a bot message
    if message.reference and message.reference.message_id:
        try:
            replied_msg = await message.channel.fetch_message(message.reference.message_id)
            if replied_msg.author == bot.user and replied_msg.embeds:
                embed = replied_msg.embeds[0]
                title = embed.title or ""
                for char_name in SYSTEM_PROMPTS.keys():
                    if char_name in title:
                        char_data = {
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
                        }
                        info = char_data.get(char_name, {"color": 0x9B59B6, "emoji": "💬"})
                        
                        # Indicate typing while generating
                        async with message.channel.typing():
                            response = await generate_response(char_name, message.content, str(message.author.id))
                        
                        response_embed = discord.Embed(
                            title=f"{info['emoji']} {char_name} replies:",
                            description=response,
                            color=info['color']
                        )
                        response_embed.set_footer(text=f"{message.author.name} → {char_name}")
                        await message.channel.send(embed=response_embed)
                        break
        except Exception as e:
            print(f"Reply handling error: {e}")

    await bot.process_commands(message)

# ───── RUN ─────

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
