import os
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

# --- 1. Flask сервер (Render дээр 24/7 ажиллуулах зорилгоор) ---
app = Flask("")


@app.route("/")
def home():
  return "Reaction Role болон Voice Log Бот амжилттай ажиллаж байна! (24/7 Alive)"


def run():
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)


def keep_alive():
  t = Thread(target=run)
  t.start()


# --- 2. Discord Бот тохиргоо ---
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID-уудаа энд тохируулна уу
LOG_CHANNEL_ID = 1566394985329328148  # Voice log орох сувгийн ID

# Таны өгсөн эможи болон ролуудын холбоос (Эндхийн Role ID-г өөрийн сервер дээрх ролынхоо ID-гаар солино уу)
REACTION_ROLES = {
    1567487340954263553: 111111111111111111,  # Anclous
    1567487230354657321: 222222222222222222,  # Minecraft
    1567485405647998977: 333333333333333333,  # Counter Strike
    1567485457636528182: 444444444444444444,  # Valorant
    1567485538402050051: 555555555555555555,  # Roblox
    1567485508828008449: 666666666666666666,  # Mobile Legends
    1567487284226293823: 777777777777777777,  # NOVA
    1567484797696082031: 888888888888888888,  # FACEIT-8
    1567484824447623300: 999999999999999999,  # FACEIT-9
    1567484971902443523: 101010101010101010,  # FACEIT-10
}

# Reaction Role мессежийн ID (Setup команд ажиллуулсны дараа гарч ирэх ID-г энд тавина)
ROLE_MESSAGE_ID = None


@bot.event
async def on_ready():
  print(f"Бот амжилттай холбогдлоо: {bot.user}")


# --- 3. Voice Log хэсэг ---
@bot.event
async def on_voice_state_update(member, before, after):
  log_channel = bot.get_channel(LOG_CHANNEL_ID)
  if not log_channel:
    return

  if before.channel is None and after.channel is not None:
    embed = discord.Embed(
        title="🎤 Дуут сувагт орлоо",
        description=(
            f"**{member.mention}** гишүүн **{after.channel.name}** сувагт"
            " орлоо."
        ),
        color=discord.Color.green(),
    )
    embed.set_footer(text=f"Хэрэглэгчийн ID: {member.id}")
    await log_channel.send(embed=embed)

  elif before.channel is not None and after.channel is None:
    embed = discord.Embed(
        title="🚪 Дуут сувгаас гарлаа",
        description=(
            f"**{member.mention}** гишүүн **{before.channel.name}** сувгаас"
            " гарлаа."
        ),
        color=discord.Color.red(),
    )
    embed.set_footer(text=f"Хэрэглэгчийн ID: {member.id}")
    await log_channel.send(embed=embed)

  elif (
      before.channel != after.channel
      and before.channel is not None
      and after.channel is not None
  ):
    embed = discord.Embed(
        title="🔄 Суваг сольсон",
        description=(
            f"**{member.mention}** гишүүн **{before.channel.name}** ->"
            f" **{after.channel.name}** руу шилжлээ."
        ),
        color=discord.Color.orange(),
    )
    await log_channel.send(embed=embed)

  if not before.self_stream and after.self_stream:
    embed = discord.Embed(
        title="🖥️ Дэлгэцээ хуваалцлаа",
        description=(
            f"**{member.mention}** гишүүн **{after.channel.name}** дээр"
            " дэлгэцээ цацлаа."
        ),
        color=discord.Color.blue(),
    )
    await log_channel.send(embed=embed)

  elif before.self_stream and not after.self_stream:
    embed = discord.Embed(
        title="⏹️ Дэлгэц хуваалцахаа зогсоолоо",
        description=(
            f"**{member.mention}** гишүүн дэлгэцээ хуваалцахаа болилоо."
        ),
        color=discord.Color.light_gray(),
    )
    await log_channel.send(embed=embed)


# --- 4. Reaction Roles (Эможи ID-гаар рол өгөх/хасах) хэсэг ---


@bot.event
async def on_raw_reaction_add(payload):
  if payload.member.bot:
    return
  if ROLE_MESSAGE_ID and payload.message_id != ROLE_MESSAGE_ID:
    return

  # Custom emoji-ны ID-г шалгах
  emoji_id = payload.emoji.id
  if emoji_id in REACTION_ROLES:
    guild = bot.get_guild(payload.guild_id)
    role_id = REACTION_ROLES[emoji_id]
    role = guild.get_role(role_id)

    if role:
      await payload.member.add_roles(role)
      print(f"{payload.member.name} гишүүнд {role.name} рол өглөө.")


@bot.event
async def on_raw_reaction_remove(payload):
  if ROLE_MESSAGE_ID and payload.message_id != ROLE_MESSAGE_ID:
    return

  emoji_id = payload.emoji.id
  if emoji_id in REACTION_ROLES:
    guild = bot.get_guild(payload.guild_id)
    role = guild.get_role(REACTION_ROLES[emoji_id])
    member = guild.get_member(payload.user_id)

    if role and member:
      await member.remove_roles(role)
      print(f"{member.name} гишүүнээс {role.name} ролыг хаслаа.")


# Туслах команд: Эможи рол сонгох самбарыг үүсгэх
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_game_roles(ctx):
  embed = discord.Embed(
      title="🎮 Тоглоом болон сонирхлын ролоо сонгоно уу!",
      description=(
          "Доорх эможинууд дээр дарж өөрт тохирох ролоо аваарай:\n\n"
          "<:anclous:1567487340954263553> — Anclous\n"
          "<:minecraft:1567487230354657321> — Minecraft\n"
          "<:cs:1567485405647998977> — Counter Strike\n"
          "<:valorant:1567485457636528182> — Valorant\n"
          "<:roblox:1567485538402050051> — Roblox\n"
          "<:mlbb:1567485508828008449> — Mobile Legends\n"
          "<:nova:1567487284226293823> — NOVA\n"
          "<:faceit8:1567484797696082031> — FACEIT Level 8\n"
          "<:faceit9:1567484824447623300> — FACEIT Level 9\n"
          "<:faceit10:1567484971902443523> — FACEIT Level 10"
      ),
      color=discord.Color.blue(),
  )
  msg = await ctx.send(embed=embed)

  # Эможинуудаа ботоор дамжуулан мессеж дээр автоматаар нэмэх
  for emoji_id in REACTION_ROLES.keys():
    emoji = bot.get_emoji(emoji_id)
    if emoji:
      await msg.add_reaction(emoji)

  await ctx.send(
      f"Мэдэгдэл: Game Reaction Role амжилттай үүслээ! Мессежийн ID:"
      f" `{msg.id}`"
  )
  print(
      f"Энэ мессежийн ID-г код доторх `ROLE_MESSAGE_ID = {msg.id}` болгож"
      " тавиарай!"
  )


# --- 5. Ажиллуулах хэсэг ---
if __name__ == "__main__":
  keep_alive()
  TOKEN = os.getenv("DISCORD_TOKEN")
  bot.run(TOKEN)