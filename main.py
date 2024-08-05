#main.py
import discord, os

# gets bot token from env
BOT_TOKEN = os.getenv("BOT_TOKEN")

# defines the bot obj
bot = discord.Bot(intents=discord.Intents.default())

@bot.event
# prints when the bot has connected to discord
async def on_connect():
	print (f'\n{bot.user} has connected to Discord!')
	# loads the commands
	bot.load_extension('cogs.game_logic')
	await bot.sync_commands()

# prints what guilds the bot is connected to
@bot.event
async def on_ready():
	await bot.wait_until_ready()
	print(
		f'Logged in as {bot.user} ID: {bot.user.id}\n{bot.user} has connected to the following guild(s):\n'
	)
	async for guild in bot.fetch_guilds(limit=None):
		print (f'{guild.name} (id: {guild.id})')

# runs the bot
bot.run(BOT_TOKEN)

# invite url
# live: https://discord.com/oauth2/authorize?client_id=1118308598938878074&permissions=36507224064&scope=bot
#
# beta: https://discord.com/oauth2/authorize?client_id=1270098326016098326&permissions=8&integration_type=0&scope=bot
