from random import choice
import discord
from discord.ext import commands
from tinydb import TinyDB, where

# opens the active_games database, and makes tables for current games 
db = TinyDB("data/charidiots_db.json")
agTable = db.table("active_games")

words = [
	"no mans sky", "charmander", "bulbasaur", "squirtle", "chuck norris", "spanish inquisition", "minecraft", "triforce",
	"water", "emoji", "jim", "ur mom", "eevee", "you", "dungeons and dragons", "python", "racism", "pokemon", "eggplant",
	"copy", "cringe", "kill yourself", "intrusive thoughts", "kyrgyzstan", "bystander", "jury duty", "shrek", "charidiots",
	"supercalifragilisticexpialidocious", "7", "titanfall", "mario", "tetris", "minesweeper", "discord", "wumpus", "kirby", "cola",
	"socialized medicine", "capitalism", "communism", "public", "existential crisis", "satan", "god", "crusades", "murder", "harambe",
	"vehicular manslaughter", "corporate espionage", "electromagnetism", "meh", "area 51 raid", "tardis", "transformers", "constipation",
	"audience", "quality assurance", "critic", "movie", "pentagon", "lines", "square", "circle", "enigma", "quest", "clorox", "democracy"
]

def get_table(thread_id: int):
	result = agTable.search(where("thread_id") == thread_id)
	return result

# purges the table of all active games, so that unexpected restarts wont leave broken data
agTable.truncate()

class GameLogic(commands.Cog):
	def __init__(self, bot_):
		self.bot = bot_

	# starts a round of charidiots
	@discord.slash_command(
		name="start",
		description="Starts a Charidiots game"
	)
	async def start(
		self,
		ctx,
	):
		queryResultAuthor = agTable.search(where("author_username") == ctx.author.name) # change to use get_table()
		# prevents a new game from starting if the user is already author of an active game or if not in a text channel
		if queryResultAuthor == [] and ctx.channel.type == discord.ChannelType.text:
			# picks the word at random from the words list
			word = choice(words)

			# makes the thread and links it in the chat
			await ctx.respond(f":arrow_down: :arrow_down: Starting game in the thread! :arrow_down: :arrow_down:")
			thread = await ctx.channel.create_thread(name=f"{ctx.author.display_name}'s Charidiots game", type=discord.ChannelType.public_thread)
			await ctx.respond(content=
f"""The players need to guess: `{word}`\nReact to the first message in the thread to give your hints!\n
**Sending messages in the thread chat or reacting to other messages in the thread will instantly set your score to 0!**""", ephemeral=True)

			hintMessage = await thread.send(content="Welcome to **Charidiots**! Whoever started this game, you have been given a word or short phrase, react to this message to give hints to the other players so that they can guess it. Every hint increases your score, and the lower the score, the better you did!\nPlayers, when you think you've solved it, type `/guess` followed by your guess to try and guess the word/phrase!\nYour hints are:")

			# makes a database entry for the current game
			agTable.insert({
				"thread_id": thread.id,
				  "channel_id": ctx.channel.id, 
				  "author_username": ctx.author.name, 
				  "hint_id": hintMessage.id, 
				  "word": word, 
				  "score":0, 
				  "cheating": False
				})
		else:
			await 	ctx.respond("Error! Please make sure you are in a text channel and have not started any other games!", ephemeral=True)
	# command to allow players to guess the phrase
	@discord.slash_command(
		name="guess",
		description="Guesses the word"
	)
	async def guess(
		self,
		ctx,
		guess: str = discord.Option(description="Your word guess", input_type=discord.SlashCommandOptionType.string)
	):
		queryResult = queryResult = get_table(ctx.channel.id)

		if not queryResult:
			await ctx.respond("Use this command in a game thread!", ephemeral=True)
			return
		
		if ctx.author.name == queryResult[0]['author_username']:
			await ctx.respond("You cannot guess in your own game!", ephemeral=True)
			return

		if queryResult[0]['word'] == guess.lower():
			await ctx.respond(f"Correct! The word was `{queryResult[0]['word']}`")
			thread = self.bot.get_channel(queryResult[0]['thread_id'])
			channel = self.bot.get_channel(queryResult[0]['channel_id'])
			await thread.edit(
				archived=True
			)
			
			if queryResult[0]['cheating']:
				score = 999
			else: 
				score = queryResult[0]['score']

			await channel.send(content=f"{ctx.author.mention} guessed the word! It was `{queryResult[0]['word']}`!\n Score: {score}") # maybe make this silent?
			agTable.remove(where("thread_id") == thread.id)

	# detects if the author of the game is cheating
	@commands.Cog.listener()
	async def on_message(self, message):
		queryResult = get_table(message.channel.id)

		if queryResult: # Check if message was sent in a game thread
			for result in queryResult:
				# checks if the message was sent by the author
				if message.author.name == (result["author_username"]):
					if not result["cheating"]:
						thread = self.bot.get_channel(message.channel.id)
						await thread.send("Cheating detected!")
					agTable.update({'cheating': True}, where("thread_id") == message.channel.id)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		queryResult = get_table(payload.channel_id)
		if queryResult:
			for result in queryResult:
				if result['hint_id'] == payload.message_id:
					score = result['score'] + 1
					agTable.update({'score':score}, where("hint_id") == payload.message_id)

def setup(bot):
	bot.add_cog(GameLogic(bot))
