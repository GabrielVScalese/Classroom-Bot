##### Libraries
import discord
import os
from discord.ext import commands, tasks
import urllib.parse
import urllib.request
import re
from keep_alive import keep_alive
import youtube_dl
import asyncio


##### Tests
import datetime
print(datetime.datetime.strptime('February 12, 2021', '%B %d, %Y').strftime('%a'))


##### Variables:

is_connected = False
current_song = ''
queue = []
news_queue = []
songs = -1
client = commands.Bot(command_prefix='$')  # Define the client

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
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

## Class
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.duration = data.get('duration')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music:
  def __init__(self, title, duration, link):
    self.title = title
    self.duration = duration
    self.link = link

##### Methods:

async def search_music (search):
    query_string = urllib.parse.urlencode({
        'search_query': search
    })

    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )

    search_results = re.findall(
        r'/watch\?v=(.{11})', htm_content.read().decode())

    return search_results[0]

## Method for play music from Youtube
async def play_music(ctx, search):
    global current_song
    global is_connected

    '''query_string = urllib.parse.urlencode({
        'search_query': search
    })

    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )

    search_results = re.findall(
        r'/watch\?v=(.{11})', htm_content.read().decode())'''

    channel = ctx.message.author.voice.channel
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=str(channel))
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice is None:
        await voiceChannel.connect()
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    '''player = await YTDLSource.from_url(search_results[0])'''

    result = await search_music(search)
    player = await YTDLSource.from_url(result)
    current_song = player.title
    voice.play(player, after=lambda e: print(
        'Player error: %s' % e) if e else None)

    video_minutes = str(datetime.timedelta(seconds=player.duration))
    video_link = 'http://www.youtube.com/watch?v=' + result
    await ctx.send('**Now playing:** ' + '\n' + 'Title: ' + player.title + '\n' + 'Duration: ' + video_minutes + '\n' + 'Link: ' + video_link)


##### Commands:

## Play music from Youtube
@client.command()
async def play(ctx, *, search):
    global songs

    author_voice = ctx.message.author.voice

    if not author_voice:
        await ctx.send('Join a channel!')
        return

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice is None:
        await play_music(ctx, search)
    else:
        if voice.is_playing():
            songs += 1
            result = await search_music(search)
            player = await YTDLSource.from_url(result)
            queue.append(Music(player.title, player.duration,  'http://www.youtube.com/watch?v=' + result))
            return

## Show all commands
@client.command()
async def commands(ctx):
    string = '```All commands:' + '\n\n-- About Music--' + '\n\n' + '$play "music": play the music' + '\n' + '$pause: pause the music' + '\n' + '$resume: continue the music' + '\n' + \
    '$skip: play next music in queue' + '\n' + '$leave: disconnect the bot' + '\n' + \
    '$show_queue: show all musics in queue' + '\n$now: show the current music' \
    '\n\n' + '-- About School --' + '\n\n' + '$school_schedules: show school schedules```'

    await ctx.send(string)

## Disconnect client
@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send('The bot is not connected to a voie channel')

## Pause the music from Yotube
@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('No audio is playing')

## Play next music in queue
@client.command()
async def skip(ctx):
    global songs

    if len(queue) != 0:
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        voice.pause()
        await play_music(ctx, queue[0])
        del queue[0]
        songs -= 1
    else:
        await ctx.send('There not more musics')

## Resume the music from Youtube
@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('The audio is not paused')

## Show the queue
@client.command()
async def show_queue(ctx):
    global queue
    index = 1
    string = 'Musics in queue:' + '\n' + '\n'

    if len(queue) != 0:
        for music in queue:
            video_minutes = str(datetime.timedelta(seconds=music.duration))
            string += 'Title: ' + music.title + '\n' + 'Duration: ' + video_minutes + '\n' + 'Link: ' + music.link + '\n' + '------------------------------------------------------------------' + '\n'
    else:
        string = 'There not queue'

    string = '```' + string + '```'
    await ctx.send(string)

## Show the current song
@client.command()
async def now(ctx):
  global current_song

  await ctx.send('****Is playing:**** ' + current_song)

## Show the school schedules
@client.command()
async def school_schedules(ctx):
    await ctx.send(file=discord.File('school_schedules.png'))

keep_alive()  # Client keep alive
client.run(os.getenv('TOKEN'))  # Run the client