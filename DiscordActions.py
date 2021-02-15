import discord

class DiscordActions:

  @staticmethod
  def is_connected (ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()