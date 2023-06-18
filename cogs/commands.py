from uuid import uuid4
import discord
from discord.ext import commands
from tinydb import TinyDB, Query

# opens the active_games database, and makes tables for current games 
db = TinyDB("data/charidiots_db.json")
ag_table = db.table("active_games")


# purges the table of all active games, so that unexpected restarts wont leave broken data
ag_table.truncate()

class Commands(commands.Cog):
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
		if (ctx.user.nick != None):
			author_name = ctx.author.nick
		else:
			author_name = ctx.author.display_name

		# makes the thread and links it in the chat
		thread = await ctx.channel.create_thread(name=f"{author_name}'s Charidiots game")
		await ctx.respond(f":arrow_down: :arrow_down: Starting game in the thread! :arrow_down: :arrow_down:\nhttps://discord.com/channels/{ctx.channel.id}/{thread.id}")

		# # assigns a random id to the current game
		# id = str(uuid4())

		# makes a database entry for the current game
		# ag_table.insert({"game_id": id,"thread_id": thread_id,"author_username": author_username, "hints":0})
		ag_table.insert({"thread_id": thread.id,"author_username": ctx.author.name, "hints":0}) # not sure i need a game id anymore

def setup(bot):
	bot.add_cog(Commands(bot))