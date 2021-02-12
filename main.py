import discord
import os
from discord.ext import commands
import urllib.parse, urllib.request, re
from keep_alive import keep_alive
import youtube_dl
import asyncio
from discord.voice_client import VoiceClient

'''@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client:
    return

  if message.content.startswith('$ola'):
    await message.channel.send('Olá!')

  if message.content.startswith('$entrar'):
    canal = message.author.voice.voice_channel
    await client.join_voice_channel(canal)

  if message.content.startswith('$play'):
    voiceChannel = discord.utils.get(ctx)'''

client = commands.Bot(command_prefix='!')

@client.command(pass_context=True)
async def join(ctx):
  channel = ctx.message.author.voice.voice_channel
  await client.join_voice_channel(channel)


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@client.command()
async def youtube (ctx, *, search):
  query_string = urllib.parse.urlencode({
    'search_query': search
  })

  htm_content = urllib.request.urlopen(
    'http://www.youtube.com/results?' + query_string
  )

  search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
  await ctx.send('http://youtube.com/watch?v=' + search_results[0])

  voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='Geral')
  await voiceChannel.connect()
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  
  async with ctx.typing():
    player = await YTDLSource.from_url(search_results[0])
    voice.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

@client.command()
async def leave (ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
      await voice.disconnect()
    else:
      await ctx.send('The bot is not connected to a voie channel')

@client.command()
async def pause (ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
  else:
    await ctx.send('No audio is playing')


@client.command()
async def resume (ctx):
   voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
   if voice.is_paused():
     voice.resume()
   else:
    await ctx.send('The audio is not paused')


keep_alive()
client.run(os.getenv('TOKEN'))