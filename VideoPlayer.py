import discord
import asyncio
import datetime

from YTDLSource import YTDLSource
from DiscordActions import DiscordActions

class VideoPlayer:

  @staticmethod
  ## Method for play music from Youtube
  async def play_music(self, ctx, client, search, queue):
      global current_song

      channel = ctx.message.author.voice.channel
      voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=str(channel))

      if not DiscordActions.is_connected(ctx):
          await voiceChannel.connect()
          
      voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
      url_video = await YTDLSource.get_url_video(search)
      player = await YTDLSource.from_url(url_video)
      current_song = player.title
      
      video_minutes = str(datetime.timedelta(seconds=player.duration))
      
      await ctx.send('**Now playing:** ' + '\n' + 'Title: ' + player.title + '\n' + 'Duration: ' + video_minutes + '\n' + 'Link: ' + url_video)

      voice.play(player)
      
      while voice.is_playing():
        await asyncio.sleep(1)

      if len(queue) != 0:
        video = queue[0]
        del queue[0]
        await self.play_music(VideoPlayer, ctx, client, video.title, queue)
