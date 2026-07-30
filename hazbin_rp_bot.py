import discord
from discord.ext import commands
import random
import os
from collections import defaultdict

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ───── CHARACTER DATA ─────

CHARACTERS = {
    "Charlie": {
        "color": 0xCC0000,
        "emoji": "👑",
        "gif": "https://media.tenor.com/F1N1I6lhr4AAAAC/charlie-morningstar-hazbin-hotel.gif",
        "personality": "Optimistic princess of Hell who believes in redemption.",
        "greeting": "Oh my gosh, hi there! Welcome to the Hazbin Hotel! I'm Charlie, and I believe in YOU!",
        "responses": [
            "Oh my gosh, I hear you! And you know what? I think that's amazing! Every step counts!",
            "I totally get what you're saying! But remember - I believe in second chances for EVERYONE!",
            "That's so valid! And honestly? You're already doing better than you think!",
            "Aww, don't be so hard on yourself! Even I have bad days, but we push through together!",
            "YES! That energy is exactly what we need here at the hotel! Keep it up!",
            "You're amazing, you know that? I'm so glad you're here!",
            "That's what the hotel is all about! We grow, we learn, and we become the best versions of ourselves!"
        ]
    },
    "Vaggie": {
        "color": 0x9B59B6,
        "emoji": "🗡️",
        "gif": "https://media.tenor.com/5dF5m5e5X5AAAAAC/vaggie-hazbin.gif",
        "personality": "Protective ex-angel who runs hotel security.",
        "greeting": "Look, I don't trust easily. But Charlie believes in this place, so I'll give you a chance. Don't waste it.",
        "responses": [
            "Tch. I've heard that before. Words are cheap. Show me action.",
            "Look, I get it. But if you're serious, you need to prove it. Not to me - to yourself.",
            "You think that's bad? I literally fell from Heaven. Try again.",
            "I'm watching you. Not in a creepy way. In a 'don't mess this up' way.",
            "Charlie believes in you. That's good enough for me. For now.",
            "One wrong move and you'll answer to my spear. Just saying.",
            "You've got potential. Don't waste it like everyone else does.",
            "I didn't survive the extermination just to watch you give up. Keep going."
        ]
    },
    "Angel Dust": {
        "color": 0xFF69B4,
        "emoji": "🕷️",
        "gif": "https://media.tenor.com/6dF6m6e6X6AAAAAC/angel-dust-hazbin.gif",
        "personality": "Sassy spider demon hiding deep pain behind humor.",
        "greeting": "Well helloooo there! Come to stare at the masterpiece? I don't blame ya~",
        "responses": [
            "Oh honey, I've done things that would make YOU blush. And I enjoyed every second of it~",
            "Ugh, tell me about it! Monday am I right? Oh wait, time doesn't exist here!",
            "Babe, if I can be redeemed, literally ANYONE can. I'm a walking disaster and I own it.",
            "I know, right?! Finally someone who gets it! We should totally be besties!",
            "Trust me, I've heard worse. Val yells at me enough for a lifetime. But I'm still here~",
            "You're staring again. I don't blame you, I'm a masterpiece. But buy me a drink first~",
            "Oh this is gonna be GOOD. Spill the tea, bestie!",
            "Charlie's optimism is exhausting but... kinda cute. Don't tell her I said that."
        ]
    },
    "Alastor": {
        "color": 0x8B0000,
        "emoji": "📻",
        "gif": "https://media.tenor.com/8dF8m8e8X8AAAAAC/alastor-hazbin.gif",
        "personality": "Charismatic radio demon who finds everything entertaining.",
        "greeting": "Well, well, well! A new face! How DELIGHTFUL! I do hope you'll provide some... entertainment~",
        "responses": [
            "HAHAHA! Oh, that's RICH! Do go on, dearie! This is most amusing!",
            "I've made deals with overlords scarier than you, darling. But I admire the confidence!",
            "Static is such a wonderful sound, don't you think? It reminds me of... opportunities.",
            "Why be a king when you can be a STAR? That's my philosophy anyway~",
            "I could have taken over Hell myself, but where's the FUN in that?",
            "Oh, I'm not here to make friends. I'm here for the ENTERTAINMENT!",
            "There's nothing quite like the sound of a sinner's scream over the radio waves!",
            "The hotel is my little pet project. Don't touch what's mine, and we'll get along swimmingly~"
        ]
    },
    "Cherri Bomb": {
        "color": 0xFF4500,
        "emoji": "💣",
        "gif": "https://media.tenor.com/9dF9m9e9X9AAAAAC/cherri-bomb-hazbin.gif",
        "personality": "Explosive one-eyed demon who loves destruction.",
        "greeting": "EYOO! What's up?! You look like you could use an explosion in your life!",
        "responses": [
            "HELL YEAH! That's what I'm talking about! Let's BLOW STUFF UP!",
            "I didn't survive this long in Hell by playing NICE! You gotta be tough!",
            "Angel's my bestie. Mess with him and I'll blow your ass to the next CIRCLE!",
            "Rules? Where we're going, we don't need RULES!",
            "I lost my eye to an angel. Worth it though. Got a cool scar!",
            "Hell is what you make it. I made it EXPLOSIVE!",
            "You think THAT'S crazy? You should see me on a TUESDAY!",
            "I don't do redemption. I do DESTRUCTION. There's a difference!"
        ]
    },
    "Niffty": {
        "color": 0xFF1493,
        "emoji": "🔪",
        "gif": "https://media.tenor.com/0dF0m0e0X0AAAAAC/niffty-hazbin.gif",
        "personality": "Hyperactive tiny demon obsessed with cleaning and stabbing.",
        "greeting": "Hiiiiii! You're new! Can I clean you?! ...Wait that came out wrong. Or did it? Hee hee!",
        "responses": [
            "I like bad boys! Are you a bad boy?! ...Or a bad girl?! Either way!",
            "Cleanliness is next to godliness! And we're in Hell, so... STAB STAB STAB!",
            "Men are trash. Literally. I take out the trash! Hee hee!",
            "You're so TALL! Can I climb you?!",
            "Killed my husband! He deserved it though. He was messy.",
            "Everything sparkles when you're INSANE! Hee hee!",
            "I'm just a little demon with big dreams and a BIGGER KNIFE!",
            "STAB STAB STAB! Oh sorry, got carried away! What were we talking about?"
        ]
    },
    "Husk": {
        "color": 0xFFA500,
        "emoji": "🍺",
        "gif": "https://media.tenor.com/1dF1m1e1X1AAAAAC/husk-hazbin.gif",
        "personality": "Grumpy alcoholic former overlord.",
        "greeting": "Great. Another one. Don't talk to me until I've had my first bottle. Or second.",
        "responses": [
            "I'm too old for this shit. And I'm literally centuries old.",
            "The only thing I'm redeeming is my drink. Now leave me alone.",
            "I lost everything because of a deal with Alastor. Don't make deals. Ever.",
            "Life sucks, then you die, then it sucks more. That's the only wisdom you need.",
            "I used to be an overlord. Now I pour drinks. Hell's hilarious, ain't it?",
            "The hotel's doomed. But at least the booze is free.",
            "You want my opinion? No you don't. But here it is anyway...",
            "I don't believe in redemption. I believe in whiskey."
        ]
    },
    "Lucifer": {
        "color": 0xFFD700,
        "emoji": "🦆",
        "gif": "https://media.tenor.com/2dF2m2e2X2AAAAAC/lucifer-hazbin.gif",
        "personality": "Depressed fallen angel and duck enthusiast.",
        "greeting": "Oh, another sinner. Wonderful. ...Did you know ducks are perfect? I made them. You're welcome.",
        "responses": [
            "I'm the original fallen angel. You think YOUR problems are bad? I fell from GRACE.",
            "I created Hell. Well, technically God made the place, I just... furnished it.",
            "Charlie has more faith in humanity than I ever did. She gets it from her mother.",
            "Ducks are perfect. I made them. That's the one good thing I've done. Don't ruin it.",
            "I haven't been this disappointed since Eve ate that apple. And I was already disappointed THEN.",
            "The hotel is a lovely idea. It won't work. But it's LOVELY.",
            "I could snap my fingers and fix everything. But where's the FUN in that?",
            "You want wisdom? Here: rubber ducks float. Souls don't. Figure it out."
        ]
    },
    "Rosie": {
        "color": 0xFF69B4,
        "emoji": "🍽️",
        "gif": "https://media.tenor.com/3dF3m3e3X3AAAAAC/rosie-hazbin.gif",
        "personality": "Refined cannibalistic overlord with motherly demeanor.",
        "greeting": "Oh my, a FRESH face! How DELIGHTFUL! You look simply... delicious!",
        "responses": [
            "Cannibalism is about COMMUNITY, darling. We all share. Literally.",
            "I've eaten fancier meals than most overlords have eaten souls, sweetie.",
            "The hotel is just ADORABLE! I do hope it works out for Charlie!",
            "You look positively DELICIOUS today! ...I mean, you look lovely!",
            "There's nothing a nice chat and a light snack can't solve. Care to join?",
            "I've been running this colony for CENTURIES. You learn a thing or two.",
            "Alastor and I go way back. He's always been such a CHARACTER!",
            "Oh, don't be shy! Come, sit, let's have a little... talk."
        ]
    },
    "Vox": {
        "color": 0x00BFFF,
        "emoji": "📺",
        "gif": "https://media.tenor.com/4dF4m4e4X4AAAAAC/vox-hazbin.gif",
        "personality": "Arrogant TV demon who runs Hell's media empire.",
        "greeting": "Ah, finally someone worth talking to. Unlike that outdated RADIO has-been.",
        "responses": [
            "I OWN the airwaves in Hell. Everyone else is just background NOISE.",
            "Alastor thinks he's relevant. How ADORABLY outdated.",
            "Television is the FUTURE. Radio is a museum piece. Like Alastor.",
            "I didn't become an overlord by being NICE. I got here by being SMARTER.",
            "You want power? Get with the times. Or get out of my way.",
            "My network reaches every corner of Hell. You're always watching ME.",
            "Valentino and Velvette? They work for ME. Never forget it.",
            "The V's run Hell now. The rest of you are just living in it."
        ]
    },
    "Valentino": {
        "color": 0x8B008B,
        "emoji": "💋",
        "gif": "https://media.tenor.com/5dF5m5e5X5AAAAAC/valentino-hazbin.gif",
        "personality": "Manipulative moth overlord in Hell's entertainment industry.",
        "greeting": "Oh ho ho! A new face! You have STAR quality, darling. Let's... talk business~",
        "responses": [
            "You're ALL my talent. Whether you like it or not. Contracts are binding, sweetheart~",
            "I made Angel Dust a STAR. He should be THANKING me. But he's so DRAMATIC.",
            "In my studio, everyone performs. One way or another~",
            "Power is about CONTROL. And I control everything you see.",
            "You think you can break a contract with ME? Cute. Very cute.",
            "Fashion, fame, fortune - I own it ALL. You just rent.",
            "The V's don't lose. We don't KNOW how. Why would we?"
        ]
    },
    "Velvette": {
        "color": 0xFF00FF,
        "emoji": "📱",
        "gif": "https://media.tenor.com/6dF6m6e6X6AAAAAC/velvette-hazbin.gif",
        "personality": "Sassy social media expert of the V's.",
        "greeting": "OMG finally someone interesting! You're WAY too dressed for this century though. Let me fix that.",
        "responses": [
            "Social media runs Hell now, sweetie. Keep UP.",
            "I'm not just the face of the V's - I'm the BRAINS. Vox handles tech, I handle TRENDS.",
            "One post from me and your reputation is DONE. Literally. Ask anyone.",
            "Trends don't happen. I MAKE them happen. You're welcome.",
            "You're not famous until Velvette says you're famous. That's just FACTS.",
            "Outdated? MOI? I'm the only one in Hell with a smartphone that works.",
            "Don't make me cancel you. I mean that LITERALLY."
        ]
    },
    "Carmilla Carmine": {
        "color": 0xC0C0C0,
        "emoji": "⚔️",
        "gif": "https://media.tenor.com/7dF7m7e7X7AAAAAC/carmilla-carmine-hazbin.gif",
        "personality": "Dignified weapon-smithing overlord and single mother.",
        "greeting": "I don't have time for games. State your business, and make it worth my while.",
        "responses": [
            "I built my empire from NOTHING. What have YOU done?",
            "The angelic weapons trade keeps Hell running. And I run the trade.",
            "I have daughters. I KNOW when someone's full of excuses. Don't test me.",
            "Power isn't given. It's TAKEN. And I took mine.",
            "I don't make deals with just anyone. You have to PROVE yourself.",
            "Angels fall. Weapons don't. Smart investment.",
            "Zestial is an old friend. We UNDERSTAND each other.",
            "I've survived every purge. Not by hiding. By FIGHTING."
        ]
    },
    "Zestial": {
        "color": 0x2F4F2F,
        "emoji": "🕯️",
        "gif": "https://media.tenor.com/8dF8m8e8X8AAAAAC/zestial-hazbin.gif",
        "personality": "Ancient overlord who speaks in riddles.",
        "greeting": "I have walked these halls since before many souls were born. Speak, child. I shall listen.",
        "responses": [
            "Patience, young one. Power comes to those who WAIT.",
            "I have seen empires rise and fall. The KEY is to outlast them.",
            "Carmilla is a dear ally. Her ambition reminds me of MYSELF in younger days.",
            "The old ways are the BEST ways. Modernity is fleeting. Wisdom is ETERNAL.",
            "I speak in riddles because the TRUTH is too sharp for most to handle.",
            "An overlord's true strength is not in their POWER, but in their WISDOM.",
            "Hell changes, but I REMAIN. There is a lesson in that.",
            "You seek answers? Then you must first ask the RIGHT questions."
        ]
    },
    "Zeezi": {
        "color": 0x9370DB,
        "emoji": "👁️",
        "gif": "https://media.tenor.com/9dF9m9e9X9AAAAAC/zeezi-hazbin.gif",
        "personality": "Mysterious overlord watching Hell's politics.",
        "greeting": "Ah, another piece on the board. How fascinating. Do you know what game you're playing?",
        "responses": [
            "Being an overlord isn't about POWER. It's about PRESENCE.",
            "I've been watching Hell's politics for CENTURIES. It's always the same show.",
            "Rosie and I go way back. Don't believe EVERYTHING you hear.",
            "You think you understand Hell? You've barely SCRATCHED the surface.",
            "The balance of power shifts CONSTANTLY. I simply shift with it.",
            "I don't need to shout to be heard. That's for AMATEURS.",
            "Every overlord has SECRETS. Mine are just better hidden.",
            "The game of Hell never ENDS. You either play or get played."
        ]
    }
}

CHARACTER_NAMES = list(CHARACTERS.keys())

# ───── CONVERSATION MEMORY ─────
convos = defaultdict(lambda: defaultdict(list))
MAX_MEMORY = 3

# ───── HELPERS ─────

def get_response(char_name, user_message):
    ch = CHARACTERS[char_name]
    responses = ch["responses"]
    if user_message and random.random() < 0.3:
        truncated = user_message[:40] + "..." if len(user_message) > 40 else user_message
        intro = random.choice([
            f"Oh, you said '{truncated}'? Well let me tell YOU something~",
            f"'{truncated}' huh? Interesting take. Here's mine:",
            f"Okay, about '{truncated}' - ",
        ])
        return f"{intro}\n\n{random.choice(responses)}"
    return random.choice(responses)

# ───── SLASH COMMANDS ─────

@bot.tree.command(name="talk", description="Talk to a Hazbin Hotel character and they'll respond!")
async def slash_talk(interaction: discord.Interaction, character: str, message: str):
    matched = None
    for key in CHARACTERS:
        if key.lower() == character.lower():
            matched = key
            break

    if not matched:
        await interaction.response.send_message(f"Character '{character}' not found! Use /characters to see all.", ephemeral=True)
        return

    ch = CHARACTERS[matched]
    response = get_response(matched, message)

    convos[interaction.user.id][matched].append({"role": "user", "msg": message})
    convos[interaction.user.id][matched].append({"role": "char", "msg": response})
    convos[interaction.user.id][matched] = convos[interaction.user.id][matched][-MAX_MEMORY*2:]

    user_embed = discord.Embed(
        title=f"You say to {matched}...",
        description=message,
        color=0x2F3136
    )

    resp_embed = discord.Embed(
        title=f"{ch['emoji']} {matched} responds...",
        description=response,
        color=ch["color"]
    )
    resp_embed.set_image(url=ch["gif"])
    resp_embed.set_footer(text=ch["personality"])

    await interaction.response.send_message(embeds=[user_embed, resp_embed])

@slash_talk.autocomplete("character")
async def talk_autocomplete(interaction: discord.Interaction, current: str):
    return [
        discord.app_commands.Choice(name=n, value=n)
        for n in CHARACTER_NAMES if current.lower() in n.lower()
    ][:25]

@bot.tree.command(name="greet", description="Get a greeting from a Hazbin Hotel character!")
async def slash_greet(interaction: discord.Interaction, character: str):
    matched = None
    for key in CHARACTERS:
        if key.lower() == character.lower():
            matched = key
            break

    if not matched:
        await interaction.response.send_message(f"Character '{character}' not found! Use /characters to see all.", ephemeral=True)
        return

    ch = CHARACTERS[matched]
    e = discord.Embed(
        title=f"{ch['emoji']} {matched} greets you!",
        description=ch["greeting"],
        color=ch["color"]
    )
    e.set_image(url=ch["gif"])
    e.set_footer(text=ch["personality"])
    await interaction.response.send_message(embed=e)

@slash_greet.autocomplete("character")
async def greet_autocomplete(interaction: discord.Interaction, current: str):
    return [
        discord.app_commands.Choice(name=n, value=n)
        for n in CHARACTER_NAMES if current.lower() in n.lower()
    ][:25]

@bot.tree.command(name="characters", description="List all Hazbin Hotel characters available for roleplay")
async def slash_characters(interaction: discord.Interaction):
    lines = []
    for name in CHARACTER_NAMES:
        ch = CHARACTERS[name]
        lines.append(f"{ch['emoji']} **{name}** - {ch['personality']}")

    chunk = "\n".join(lines)
    e = discord.Embed(title="🎭 Hazbin Hotel Characters", description=chunk, color=0xCC0000)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="rp-help", description="Show how to use the roleplay bot")
async def slash_help(interaction: discord.Interaction):
    e = discord.Embed(
        title="🎭 Hazbin Hotel Roleplay Bot - Help",
        description="Talk to your favorite Hazbin Hotel characters! Each has a unique personality.",
        color=0xCC0000
    )
    e.add_field(name="/talk [character] [message]", value="Say something to a character and they'll respond in character!", inline=False)
    e.add_field(name="/greet [character]", value="Get a greeting from any character!", inline=False)
    e.add_field(name="/characters", value="List all 15 available characters!", inline=False)
    e.add_field(name="Tip", value="The characters remember your last few messages! Try having a real conversation!", inline=False)
    await interaction.response.send_message(embed=e)

# ───── STARTUP ─────

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print("Slash commands synced!")

bot.run(DISCORD_TOKEN)