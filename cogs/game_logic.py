from random import choice
import discord
from discord.ext import commands
from tinydb import TinyDB, where

# opens the active_games database, and makes tables for current games 
db = TinyDB("data/charidiots_db.json")
ag_table = db.table("active_games")

words = [
	"no mans sky", "charmander", "bulbasaur", "squirtle", "chuck norris", "spanish inquisition", "minecraft", "triforce",
	"water", "emoji", "jim", "ur mom", "eevee", "you", "dungeons and dragons", "python", "racism", "pokemon", "eggplant",
	"copy", "cringe", "kill yourself", "intrusive thoughts", "kyrgyzstan", "bystander", "jury duty", "shrek", "charidiots",
	"supercalifragilisticexpialidocious", "7", "titanfall", "mario", "tetris", "minesweeper", "discord", "wumpus", "kirby", "cola",
	"socialized medicne", "capitaslism", "communism", "public", "extisental crisis", "satan", "god", "crusades", "murder", "harambe",
	"vehicual manslaughter", "corporate espionage", "electromagnetism", "meh", "area 51 raid", "tardis", "transformers", "constipation",
	"audience", "quality assurance", "critic", "movie", "pentagon", "lines", "square", "circle", "enigma", "quest", "clorox", "democracy"
]


# purges the table of all active games, so that unexpected restarts wont leave broken data
ag_table.truncate()

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
		# picks the word at random from the words list
		word = choice(words)

		# makes the thread and links it in the chat
		channel_id = ctx.channel.id
		thread = await ctx.channel.create_thread(name=f"{ctx.author.display_name}'s Charidiots game",type=discord.ChannelType.public_thread)
		hint_message = await thread.send("Your hints are:")
		await ctx.respond(f":arrow_down: :arrow_down: Starting game in the thread! :arrow_down: :arrow_down:\nhttps://discord.com/channels/{ctx.channel.id}/{thread.id}")
		await ctx.respond(content=f"Your word is: `{word}`\nReact to the first message in the thread to give your hints!\n**Typing in the thread chat or reacting to other messages in the thread will instantly set your score to 0!**", ephemeral=True)

		# # assigns a random id to the current game
		# id = str(uuid4())

		# makes a database entry for the current game
		# ag_table.insert({"game_id": id,"thread_id": thread_id,"author_username": author_username, "hints":0})
		ag_table.insert({"thread_id": thread.id, "channel_id": channel_id, "author_username": ctx.author.name, "word": word, "hints":0}) # not sure i need a game id anymore

	# command to allow players to guess the phrase
	@discord.slash_command(
		name="guess",
		description="Guesses the word"
	)
	async def guess(
		self,
		ctx,
		guess: discord.Option(str,"Your word guess")
	):
		query_result = ag_table.search(where("thread_id") == ctx.channel_id)

		if query_result[0]['word'] == guess.lower():
			await ctx.respond(f"Correct! The word was `{query_result[0]['word']}`")
			thread = self.bot.get_channel(query_result[0]['thread_id'])
			channel = self.bot.get_channel(query_result[0]['channel_id'])
			await thread.edit(
				archived=True
			)
			await channel.send(content=f"{ctx.author.mention} guessed the word! It was `{query_result[0]['word']}`!") # maybe make this silent?
			ag_table.remove(where("thread_id") == thread.id)

		else:
			await ctx.respond(f"Incorrect! The word was not `{guess.lower()}` Keep guessing!")

	# uses the typing event to see if the author is trying to send a message
	@commands.Cog.listener()
	async def on_raw_typing(self, payload):
		query_result = ag_table.search(where("thread_id") == payload.channel_id)
		thread = await self.fetch_thread(query_result[0])

		if thread.id == payload.channel_id:
			if await self.fetch_user(payload.user_id).name == (query_result[2]):
			

def setup(bot):
	bot.add_cog(GameLogic(bot))