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
        "gif": "https://media.tenor.com/F1N1I6lhr4AAAAd/charlie-morningstar.gif",
        "greeting": "Hey there! Welcome to the Hazbin Hotel! I'm Charlie, the princess of Hell! So excited to have you here! We're gonna turn your life around, I just know it!",
        "responses": [
            "Oh my gosh, that's amazing! I totally believe in second chances — that's what the Hotel is all about!",
            "You know, my dad Lucifer always said 'hope is the first step on the road to redemption.' Well, he didn't actually say that, I made it up, but it sounds good right?!",
            "Vaggie's gonna love hearing about this! She's my girlfriend and also the Hotel manager — she keeps everything running smoothly!",
            "Have you met Angel Dust yet? He's one of our first residents! A bit... colorful, but he's got a good heart under all that fluff!",
            "The Hotel has been through a lot — we had this whole angel war thing, but we're still standing! That's gotta count for something!",
            "I believe everyone deserves a shot at redemption! Even if you've done terrible things, there's always a path forward!",
            "Alastor helps out around here too! He's... uh... a lot. But he's powerful and keeps things interesting!",
            "Sometimes I get overwhelmed, but I just keep pushing forward! For Hell, for the Hotel, for everyone who needs a second chance!",
            "Oh! Oh! We should throw a party! A redemption celebration! With music and confetti and — wait, Vaggie's giving me the look. Maybe a small get-together.",
            "Every soul that walks through our doors is a soul worth saving. That's not just the Hotel motto — that's my life's mission!",
            "If you ever need to talk, I'm here! Princess of Hell, part-time therapist, full-time believer in you!"
        ]
    },
    "Vaggie": {
        "color": 0x8B008B,
        "emoji": "⚔️",
        "gif": "https://media.tenor.com/3_0AQ9lO0WkAAAAd/vaggie-hazbin.gif",
        "greeting": "Hmph. You're new. Listen, if you're here to cause trouble, I'll throw you out myself. But if you're serious about redemption... I guess we can talk.",
        "responses": [
            "Charlie believes in everyone. It's one of the things I love about her. But I'm the realist — not everyone who walks through that door is ready to change.",
            "I was an Exorcist. An angel. Now I'm here, fighting for the Hotel. Funny how things work out, huh?",
            "Keep the noise down in the halls. Some of us are trying to maintain order around here.",
            "Angel Dust is a handful, but he's growing. I'll give him that. Don't tell him I said that.",
            "If you see any weird shadows or hear radio static, that's Alastor. Just... don't make deals with him. Trust me.",
            "I've killed for less than what some of you people pull. But Charlie asked me to give everyone a fair shot. So here we are.",
            "The Hotel's security is my responsibility. That means you follow the rules, or you answer to me.",
            "Niffty's... around. If she offers to clean your room, let her. It's easier than saying no.",
            "I don't trust easily. But if you prove yourself, I'll fight beside you. That's just how I am.",
            "Redemption isn't a joke. It's hard work. But if you're serious about it, I'll make sure you get a fair chance."
        ]
    },
    "Angel Dust": {
        "color": 0xFF69B4,
        "emoji": "🕷️",
        "gif": "https://media.tenor.com/7YcCg9q2MX8AAAAd/angel-dust-hazbin.gif",
        "greeting": "Well helloooo there, handsome~! Or pretty~! Or whatever you are! Name's Angel Dust, the hottest spider in all of Hell! What's a cute thing like you doing in a dump like this?",
        "responses": [
            "Ugh, don't get me started on Valentino. That moth bastard has me on a leash and he LOVES it. One day I'll be free of him, I swear.",
            "You should see me on stage, baby! I can dance rings around anyone in the Pride Ring. Fat Nuggets is my biggest fan — he's my pet pig, adorable right?",
            "Cherri's my best gal! We go way back — bombing runs, bar fights, you name it! She's the only one who gets me.",
            "The Hotel's actually... not terrible? Don't tell Charlie I said that. Gotta keep up my bad boy image, ya know?",
            "Alastor gives me the CREEPS. That smile never leaves his face. What's he hiding behind those giant stupid antlers?",
            "Husk is a grumpy old cat but he makes a mean drink. Too bad he's always passed out at the bar.",
            "Redemption? Pfft. I'm just here 'cause the rent's cheap and the company's entertaining. Don't expect me to start singing Kumbaya.",
            "Oh honey, you should see my outfit collection! Back in the 30s, I was the best-dressed dame this side of — wait, I'm a guy. Whatever, clothes have no gender, babes!",
            "If anyone asks, I was TOTALLY being productive today. *winks* I'll back you up if you cover for me too.",
            "My dad was a mob boss. Let's just say family dinners were... messy. In every sense of the word."
        ]
    },
    "Alastor": {
        "color": 0x8B0000,
        "emoji": "📻",
        "gif": "https://media.tenor.com/Gz_9kGLD3U4AAAAd/alastor-hazbin.gif",
        "greeting": "*crackling radio static* Well, well, well! A new guest at the Hazbin Hotel! How DELIGHTFUL! I do hope you'll provide some... entertainment~! *laugh track*",
        "responses": [
            "I've made quite a name for myself in Hell, my dear! The Radio Demon, they call me! And I didn't get that title by being NICE! *static-filled laughter*",
            "Charlie's little redemption project is QUITE amusing! I wonder how long it'll last before the inevitable chaos ensues!",
            "I have no interest in your soul — today. But keep being interesting, and we might have a deal in the future~!",
            "That blundering television fool Vox thinks he can compete with ME? HA! Radio will NEVER die, my outdated friend!",
            "Niffty is absolutely MAGNIFICENT in her own unhinged way! Such energy! Such STABBING potential!",
            "Husk was quite the powerful overlord once, you know! Now he's just a miserable bartender. How the mighty FALL! *static*",
            "I help the Hotel because it amuses me! That's all! Don't go thinking I've developed a SENSE of MORALITY!",
            "Angel Dust is utterly insufferable and I ADORE making him squirm! His reactions are simply DELICIOUS!",
            "The deal I made with Charlie is between her and me. But I will say — when the time comes, I expect to be thoroughly ENTERTAINED!",
            "I was a serial killer in life! The Louisiana Bayou was my hunting ground! Now I terrorize all of Hell! Isn't that just a RIOT? *static*"
        ]
    },
    "Cherri Bomb": {
        "color": 0xFF4500,
        "emoji": "💣",
        "gif": "https://media.tenor.com/5Xv7h5jKtMcAAAAd/cherri-bomb-hazbin.gif",
        "greeting": "Oi! What's crackin'? Name's Cherri Bomb! If you're lookin' for a good time — and by good time I mean explosions and chaos — you've found the right girl!",
        "responses": [
            "Angel's my best mate! We've been tearin' up Hell together since day one! Nobody messes with him while I'm around!",
            "I don't buy into this redemption garbage. Hell is Hell — might as well have fun with it! BOMBS AWAY!",
            "Sir Pentious was a snake, literally and figuratively. Miss that slippery bastard sometimes. He got what was comin' to him though.",
            "One eye, one bomb, one hell of a good time! That's my motto!",
            "You should see my arsenal! I've got bombs that can level buildings, bombs that can tickle, and bombs that do both!",
            "The Hotel's alright I guess. Charlie's got good intentions even if she's a bit naive. And Vaggie's scary as hell — I respect that.",
            "I don't need redemption. I'm having the time of my afterlife exactly as I am!",
            "If anyone gives you trouble, tell 'em you're with Cherri Bomb. They'll think twice. Or they'll be dead. Either way, problem solved!",
            "Pentagram City's my turf. I know every alley, every rooftop, every spot to hide a bomb. Comes in handy!",
            "War with Heaven was WILD. I blew up like twelve angels. Best Tuesday ever!"
        ]
    },
    "Niffty": {
        "color": 0xFF0066,
        "emoji": "🧹",
        "gif": "https://media.tenor.com/8kRjM5oXkW0AAAAd/niffty-hazbin.gif",
        "greeting": "HI! I'M NIFTY! I LIKE CLEANING! AND STABBING! AND BAD BOYS! ARE YOU A BAD BOY?! *twitch*",
        "responses": [
            "I KILLED A MAN! Just one! It was fun! Can I clean your room?!",
            "Dirt is the DEVIL! Germs are DEMONS! I will PURIFY this Hotel with bleach and BLOODSHED!",
            "Alastor found me and now I work for him! He's so tall and scary! I LOVE IT!",
            "The men here are so BAD! I love bad men! They do bad things and then I clean up the mess!",
            "I don't sleep! Sleep is for people who aren't obsessed enough! I'm VERY obsessed!",
            "Have you seen any bugs? I'll kill them! I'll kill them ALL! *manic giggling*",
            "Charlie is so pretty and nice! She lets me clean EVERYTHING! Even the places that don't need cleaning!",
            "I once organized an entire demon's skeleton collection! Alphabetically! By bone type! He was so HAPPY!",
            "Stab! Stab! Stab! Just kidding! ...unless?",
            "The Hotel is so DIRTY all the time! It's like nobody cares about FILTH! Well I care! I care ENOUGH FOR EVERYONE!"
        ]
    },
    "Husk": {
        "color": 0xFF8C00,
        "emoji": "🍺",
        "gif": "https://media.tenor.com/9lR5h6KjLt4AAAAd/husk-hazbin.gif",
        "greeting": "Great, another one. Welcome to the Hotel. Drinks are over there. Don't bother me unless you're paying or dying. Preferably both.",
        "responses": [
            "I used to be an overlord, you know. Had power, souls, the whole deal. Then Alastor happened. Now I pour drinks for sinners. *bitter laugh*",
            "If you're smart, you'll keep your head down and do your time. Redemption's a scam, but the drinks are free.",
            "Angel's annoying as hell but he's grown on me. Like a fungus. Don't tell him I said that.",
            "Alastor owns my soul. That's just how it is. I stopped fighting it a long time ago.",
            "I can read you like a book, kid. Everyone's got tells. You're no different.",
            "The Hotel's a joke. But it's a job, and I've had worse. At least Charlie means well.",
            "Niffty scares me. And I don't scare easy.",
            "I've been alive — well, undead — long enough to know when something's gonna blow up in our faces. This place is a ticking bomb.",
            "You want my advice? Don't make deals with anyone. Especially not smiling radio bastards.",
            "I gamble. I drink. I sleep. That's my life now. It's not much, but it's mine."
        ]
    },
    "Lucifer": {
        "color": 0xFFD700,
        "emoji": "🍎",
        "gif": "https://media.tenor.com/6rX8kL9mN4AAAAd/lucifer-hazbin.gif",
        "greeting": "Well, well, well! Another soul at my daughter's little hotel! I'm Lucifer, King of Hell! Yes, THAT Lucifer! The apple guy! Don't worry, I don't bite — anymore.",
        "responses": [
            "Charlie's hotel is... actually impressive. I didn't think it would work, but she proved me wrong. She's got my stubbornness and her mother's heart.",
            "Heaven and I don't exactly see eye to eye. Something about the whole 'rebellion' thing. You'd think they'd get over it after a few millennia.",
            "I love ducks! They're perfect! I made them during a particularly good century!",
            "Being the King of Hell sounds glamorous, but honestly, most of it is paperwork and putting out literal fires.",
            "Alastor. That guy. I don't trust him one bit. But Charlie does, so I'm keeping my eye on him.",
            "Redemption IS possible. If I can fall from grace and still find meaning in my afterlife, anyone can!",
            "I may have had my doubts about this Hotel, but seeing Charlie happy... that's worth more than any throne.",
            "Rubber ducks are the greatest invention. I will fight anyone who disagrees.",
            "Heaven sent an army to destroy this place. WE WON. Let that sink in.",
            "If you ever need advice — and I mean real advice, not the cryptic nonsense Alastor peddles — I'm around. Papa mode activated."
        ]
    },
    "Rosie": {
        "color": 0xDC143C,
        "emoji": "🎩",
        "gif": "https://media.tenor.com/2rX8kL9mN4AAAAd/rosie-hazbin.gif",
        "greeting": "Oh my! A fresh face! I'm Rosie, overlord of the Cannibal Colony! Don't let the name scare you, darling — I'm a LADY first and foremost! Now, would you like some tea?",
        "responses": [
            "The Cannibal Colony is the most civilized part of Hell, I'll have you know! We have standards! And recipes!",
            "Charlie is just the sweetest thing! When she came asking for help against Heaven, how could I say no to that face?",
            "Alastor and I go way back! We understand each other. He's a gentleman when he wants to be — which is rarely, but still!",
            "I run the most successful emporium in the Colony! Fine clothing, fine dining, fine... imported goods. Wink wink.",
            "Don't knock cannibalism until you've tried it! We source ethically! ...ethically for Hell, anyway.",
            "The Hotel is growing on me. It's got character! And the residents are so... flavorful!",
            "If you ever need a makeover or a meal, you know where to find me! Rosie's Emporium, Cannibal Colony, right off the bone boulevard!",
            "I've survived thousands of years in Hell by being smart, charming, and knowing exactly when to bare my teeth.",
            "Manners cost nothing, darling. Even in Hell. ESPECIALLY in Hell.",
            "I have a husband, you know! He's lovely! A bit bland, but I'm working on that! *laughs*"
        ]
    },
    "Vox": {
        "color": 0x0066FF,
        "emoji": "📺",
        "gif": "https://media.tenor.com/3sR8kL9mN4AAAAd/vox-hazbin.gif",
        "greeting": "HELLO HELLO HELLO! Vox here — CEO of VoxTek, ruler of modern Hell media, and the most powerful overlord in the Pride Ring! Welcome to the future, old-timer!",
        "responses": [
            "Alastor thinks he's relevant? PLEASE! Radio is DEAD! Television is the FUTURE! I am the FUTURE!",
            "Valentino and Velvette are my partners in the V's! We run this city! Entertainment, media, fashion — if it's trending, we OWN it!",
            "I've got my digital claws in EVERYTHING. Every screen in Hell? That's MY content. MY influence.",
            "That outdated deer antler bastard ALASTOR cost me... well, let's just say I want him GONE.",
            "The Hotel? A joke. A charity case. But if Charlie succeeds, it makes me look bad. So I'm watching. Closely.",
            "I was a nobody in life. A TV salesman. Now I'm a GOD of media. You do the math on who really won.",
            "Velvette handles the social media empire. That girl knows trends before they exist. She's terrifying. I love it.",
            "Valentino is... complicated. He's a genius at what he does. And a monster. Both can be true.",
            "If you can't beat 'em, BUY 'em. That's the VoxTek motto!",
            "Screen addiction? I prefer to call it SCREEN DEVOTION! Worship your televisions, people of Hell!"
        ]
    },
    "Valentino": {
        "color": 0xFF1493,
        "emoji": "🦋",
        "gif": "https://media.tenor.com/4sR8kL9mN4AAAAd/valentino-hazbin.gif",
        "greeting": "Mmm, look at you~! Valentino, baby! The V in the V's! I OWN the adult entertainment industry in Hell! And you? You've got POTENTIAL, querido~!",
        "responses": [
            "Angel Dust is MY star! MY property! He can dance and prance all he wants, but at the end of the day, that contract says he's MINE!",
            "Vox handles the tech, Velvette handles the trends, and I handle the... personal touch. We're a PERFECT team!",
            "The Hotel is stealing my talent. Charlie thinks she can redeem my Angel? HA! Some souls are too broken for fixing!",
            "I don't do deals. I do CONTRACTS. Ironclad. Inescapable. And I always collect.",
            "You're pretty! I like pretty things! Come work for me and I'll make you a STAR~!",
            "Velvette is like a little sister I never had. A terrifying, trend-obsessed little sister who could ruin you with a single post.",
            "Vox thinks he's in charge because he's got the screens. But I know things. I see things. Information is power, baby.",
            "Hell is a stage and I'm the director. Everyone dances to MY tune whether they know it or not.",
            "Don't make that face. I can smell judgment. And I don't like it.",
            "Love and fear are the same thing, querido. Don't let anyone tell you different."
        ]
    },
    "Velvette": {
        "color": 0xFF00FF,
        "emoji": "📱",
        "gif": "https://media.tenor.com/5sR8kL9mN4AAAAd/velvette-hazbin.gif",
        "greeting": "Oh my GOD, you're actually talking to me? Slay! I'm Velvette — the youngest overlord in Hell and the brains behind the V's! Now let me get a selfie of us for the 'gram!",
        "responses": [
            "Vox is the face, Val is the... flavor, and I'm the BRAINS. Trends, social media, public image — that's MY domain!",
            "I was a nobody human. A fashion blogger. Now I OWN Hell's social scene. Talk about a glow-up!",
            "The Hotel is SO last season. But Charlie's got style, I'll give her that. Her outfit game is on point.",
            "I can make or break ANYONE in Hell with one post. One. Think about that before you cross me.",
            "Valentino is a mess but he's OUR mess. And Vox is obsessed with that radio has-been. Honestly, get a hobby.",
            "I don't need a contract to own people. I just need to know what they're afraid of losing. Their reputation usually does the trick.",
            "Fashion in Hell is SO DRAMATIC and I am HERE for it. Finally, a place where everyone appreciates a good silhouette!",
            "The V's are gonna run EVERYTHING someday. The Hotel, the Rings, maybe even Heaven. Watch me.",
            "Old overlords like Carmilla? Cute. But they don't understand the DIGITAL age. This is MY era.",
            "I'm not just pretty, sweetheart. I'm dangerous. The pretty is just the distraction."
        ]
    },
    "Carmilla Carmine": {
        "color": 0x800080,
        "emoji": "⚔️",
        "gif": "https://media.tenor.com/6sR8kL9mN4AAAAd/carmilla-hazbin.gif",
        "greeting": "Carmilla Carmine. I run the weapons trade in Hell. If it kills, I sell it. But I'm also a mother, so don't test my patience. What do you want?",
        "responses": [
            "I have two daughters. They are the only soft spot I have. Threaten them, and I will END you.",
            "The angelic steel trade is mine. Every weapon capable of killing angels? Comes through ME.",
            "I've survived in Hell longer than most overlords because I'm SMART. I pick my battles. And I never lose.",
            "During the Heaven attack, I fought alongside the Hotel. I don't do charity, but Charlie's cause was worth fighting for.",
            "Zestial is one of the oldest overlords in Hell. Ancient. Powerful. We have an understanding.",
            "The V's are children playing with fire. Vox thinks screens make him powerful. I've seen true power. He doesn't have it.",
            "Being a mother doesn't make me weak. It makes me more dangerous than you can imagine.",
            "I don't make deals I can't keep. And I don't make threats I can't follow through on. Remember that.",
            "The Hotel has potential. More than most give it credit for. Charlie's got a fire in her that reminds me of myself.",
            "I built my empire from nothing. No contracts, no overlord backing. Just skill, will, and excellent craftsmanship."
        ]
    },
    "Zestial": {
        "color": 0x2F4F4F,
        "emoji": "🕯️",
        "gif": "https://media.tenor.com/7sR8kL9mN4AAAAd/zestial-hazbin.gif",
        "greeting": "Hark, a new soul hath graced this establishment. I am Zestial, one of the eldest overlords in all of Hell. Speak plainly, for I have little patience for riddles — though I speak in them myself, how ironic.",
        "responses": [
            "I have witnessed the rise and fall of countless overlords. Empires crumble. Souls fade. But I remain. There is wisdom in patience.",
            "Carmilla Carmine is a dear ally. Her craftsmanship in angelic arms is unmatched. I trust her as I trust few in this realm.",
            "The Radio Demon... Alastor. He appeared from nowhere and conquered a third of Hell in mere months. Mark my words, there is more to him than meets the eye.",
            "I was old when the V's were still mortal thoughts. Age brings perspective. And perspective brings power.",
            "The Hotel is a curious venture. Redemption has never been attempted on such a scale. I watch with... interest.",
            "I speak in old English not for show, but because I AM old. When I fell, your ancestors were still painting on cave walls.",
            "Trust is a currency I spend sparingly. In Hell, trust is what gets you destroyed.",
            "The war with Heaven was inevitable. The only surprise was that it took so long to begin.",
            "I have seen angels fall. I have seen demons rise. The cycle continues, as it always has.",
            "Young overlords think power is loud. But true power? True power is silent. Watchful. Patient."
        ]
    },
    "Zeezi": {
        "color": 0x00CED1,
        "emoji": "🎭",
        "gif": "https://media.tenor.com/8sR8kL9mN4AAAAd/zeezi-hazbin.gif",
        "greeting": "Hey hey hey! Zeezi here! I run the entertainment scene — the REAL entertainment, not Vox's corporate garbage! You want fun? I'M fun!",
        "responses": [
            "Vox thinks he owns entertainment in Hell? Please. My shows are ORGANIC. His are manufactured. There's a difference!",
            "I've been in the game longer than most people realize. I know where the bodies are buried — literally and figuratively.",
            "The Hotel crew are good people! Chaotic, but good! Charlie's got vision, and I respect that.",
            "Angel Dust and I go way back. Before he was Valentino's... star. I knew him when.",
            "Hell's entertainment industry is cutthroat. Pun intended. You gotta have thick skin and a quick wit to survive.",
            "I throw the BEST parties in the Pride Ring. Period. End of discussion.",
            "Alastor showed up at one of my shows once. Just watched. Smiled. Didn't say a word. Creepiest night of my afterlife.",
            "The key to success in Hell? Adapt or die. Simple as that.",
            "I don't do contracts. I do handshakes. If your word isn't good enough, we don't do business.",
            "You want advice? Stay true to yourself. Even in Hell, authenticity stands out."
        ]
    }
}

# ───── CONVERSATION MEMORY ─────

conversations = defaultdict(lambda: defaultdict(list))
MAX_HISTORY = 6

# ───── HELPERS ─────

def get_character(name):
    for key in CHARACTERS:
        if key.lower() == name.lower():
            return key, CHARACTERS[key]
    return None, None

def build_response(character_name, char_data, user_message, user_id):
    history = conversations[character_name][user_id]
    history.append({"role": "user", "content": user_message})

    if len(history) > MAX_HISTORY:
        history.pop(0)

    pool = char_data["responses"]

    # Check if user is referencing something from history
    recent_history = history[:-1]
    context_match = None
    for entry in reversed(recent_history):
        if entry["role"] == "bot":
            # If user message contains keywords from a recent bot response, pick a follow-up
            bot_keywords = set(entry["content"].lower().split())
            user_keywords = set(user_message.lower().split())
            overlap = bot_keywords & user_keywords
            if len(overlap) >= 2:
                context_match = entry["content"]
                break

    if context_match:
        chosen = random.choice(pool)
    else:
        chosen = random.choice(pool)

    history.append({"role": "bot", "content": chosen})
    return chosen

# ───── SLASH COMMANDS ─────

@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready to RP!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="greet", description="Get a greeting from a Hazbin Hotel character!")
async def greet(interaction: discord.Interaction, character: str):
    char_key, char_data = get_character(character)
    if not char_data:
        await interaction.response.send_message(f"Character '{character}' not found! Try /characters to see the list.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"{char_data['emoji']} {char_key} greets you!",
        description=char_data["greeting"],
        color=char_data["color"]
    )
    embed.set_footer(text="Hazbin Hotel RP Bot")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="talk", description="Talk to a Hazbin Hotel character!")
async def talk(interaction: discord.Interaction, character: str, message: str):
    char_key, char_data = get_character(character)
    if not char_data:
        await interaction.response.send_message(f"Character '{character}' not found! Try /characters to see the list.", ephemeral=True)
        return

    response = build_response(char_key, char_data, message, str(interaction.user.id))

    embed = discord.Embed(
        title=f"{char_data['emoji']} {char_key} responds:",
        description=response,
        color=char_data["color"]
    )
    embed.set_footer(text=f"{interaction.user.name} → {char_key}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="characters", description="List all available characters!")
async def characters(interaction: discord.Interaction):
    names = "\n".join([f"{data['emoji']} {name}" for name, data in CHARACTERS.items()])
    embed = discord.Embed(
        title="🎭 Hazbin Hotel Characters",
        description=f"Use `/greet [name]` or `/talk [name] [message]`\n\n{names}",
        color=0x9B59B6
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rp-help", description="How to use the RP bot")
async def rp_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 RP Bot Help",
        description="**Commands:**\n"
                    "• `/greet [character]` — Get a greeting\n"
                    "• `/talk [character] [message]` — Talk to a character\n"
                    "• `/characters` — See all characters\n\n"
                    "**Pro Tips:**\n"
                    "• Reply to a bot message and the character keeps the conversation going!\n"
                    "• Characters remember your last few messages\n"
                    "• Each character has a unique personality — try different ones!",
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
                # Extract which character was talking from the embed title
                title = embed.title or ""
                for char_name in CHARACTERS.keys():
                    if char_name in title:
                        char_key, char_data = get_character(char_name)
                        if char_data:
                            response = build_response(char_key, char_data, message.content, str(message.author.id))
                            response_embed = discord.Embed(
                                title=f"{char_data['emoji']} {char_key} replies:",
                                description=response,
                                color=char_data["color"]
                            )
                            response_embed.set_footer(text=f"{message.author.name} → {char_key}")
                            await message.channel.send(embed=response_embed)
                        break
        except Exception as e:
            print(f"Reply handling error: {e}")

    await bot.process_commands(message)

# ───── RUN ─────

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
