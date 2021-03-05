## Import - Libraries
import discord
import datetime
import os
from discord.ext import commands, tasks
from keep_alive import keep_alive
import asyncio
import requests
import json
from googleapiclient.discovery import build

## Import - Class
from ClassroomScraping.Credentials import authorization
from ClassroomScraping.ClassroomRepository import ClassroomRepository
from YTDLSource import YTDLSource
from Video import Video
from VideoPlayer import VideoPlayer
from DiscordActions import DiscordActions

## Variables:
queue = []
current_song = ''
# queue = []
client = commands.Bot(command_prefix='$')  # Define the client
channel_id = 817054317294387300

##### Commands:

## Play music from Youtube
@client.command()
async def play(ctx, *, search):
    global queue

    author_voice = ctx.message.author.voice

    if not author_voice:
        await ctx.send('Join a channel!')
        return

    if not DiscordActions.is_connected(ctx):
        await VideoPlayer.play_music(VideoPlayer, ctx, client, search, queue)
    else:
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            result = await YTDLSource.get_url_video (search)
            player = await YTDLSource.from_url(result)
            queue.append(Video(player.title, player.duration,  'http://www.youtube.com/watch?v=' + result))
            return
        else:
            await VideoPlayer.play_music(VideoPlayer, ctx, client, search, queue)

## Show all commands
@client.command()
async def commands(ctx):
  f = open('commands.txt', 'r')
  string = f.read()

  await ctx.send(string)

## Disconnect client
@client.command()
async def leave(ctx):
    global queue

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    queue.clear()
    if DiscordActions.is_connected(ctx):
        await voice.disconnect()
    else:
        await ctx.send('The bot is not connected to a voie channel!')

## Pause the music from Yotube
@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('No audio is playing!')

## Play next music in queue
@client.command()
async def skip(ctx):

    if len(queue) != 0:
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        voice.pause()

        while voice.is_playing():
          await asyncio.sleep(1)

        await VideoPlayer.play_music(VideoPlayer, ctx, client, queue[0], queue)
        del queue[0]
    else:
        await ctx.send('There not more musics!')

## Resume the music from Youtube
@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('The audio is not paused!')

## Show the queue
@client.command()
async def show_queue(ctx):
    # global queue
    string = '**Musics in queue:**' + '\n' + '\n'

    index = 1
    if len(queue) != 0:
        for video in queue:
            video_minutes = str(datetime.timedelta(seconds=video.duration))
            string += str(index) + 'º - Title: ' + video.title + '\n' + 'Duration: ' + video_minutes + '\n\n'
            index += 1
    else:
        string = 'There not queue!'

    await ctx.send(string)

## Show the current song
@client.command()
async def now(ctx):
  global current_song

  await ctx.send('****Is playing:**** ' + current_song)

## Show the school schedules
@client.command()
async def schedules(ctx):
    await ctx.send(file=discord.File('school_schedules.png'))

## Show announcements 
async def show_new_announcements():
  auth = authorization() 
  service = build('classroom', 'v1', credentials=auth.credentials)

  course_announcements = ClassroomRepository.new_announcements_account(service, datetime.datetime.today().now())
    
  channel = client.get_channel(channel_id)
  if len (course_announcements) != 0:
    classroom = discord.utils.get(channel.guild.roles, name='classroom')
    await channel.send(f'\n{classroom.mention} **There are new announcements:**\n\n\n\n')
  else:
    return

  for course_announcement in course_announcements:
    course = ClassroomRepository.get_course(service, course_announcement['courseId'])
    
    description = course_announcement['text'].split(' ')[0:10]

    description = ' '.join([str(elem) for elem in description])

    embed = discord.Embed(title=course['name'], url= course_announcement['alternateLink'], description=description, color=discord.Color.blue())

    await channel.send(embed=embed)

## Show news works
async def show_new_works():
  auth = authorization() 
  service = build('classroom', 'v1', credentials=auth.credentials)

  course_works = ClassroomRepository.new_works_account(service, datetime.datetime.now())

  channel = client.get_channel(channel_id)
  if len (course_works) != 0:
      classroom = discord.utils.get(channel.guild.roles, name='classroom')
      await channel.send(f'\n{classroom.mention} **There are new works:**\n\n\n\n')
  else:
    return

  for course_work in course_works:
    course = ClassroomRepository.get_course(service, course_work['courseId'])

    description = 'none'

    if 'description' in course_work:
      description = course_work['description'].split(' ')[0:10]

      description = ' '.join([str(elem) for elem in description])

    embed = discord.Embed(title=course_work['title'], url=course_work['alternateLink'], description=description, color=discord.Color.blue())
    
    try:
      embed.set_author(name=course['name'],  icon_url="https:" + ClassroomRepository.get_teacher(service, course_work["courseId"], course_work['creatorUserId'])["profile"]["photoUrl"])

      await channel.send(embed=embed)
    except:
      embed.set_author(name=course['name'],  icon_url= ClassroomRepository.get_teacher(service, course_work["courseId"], course_work['creatorUserId'])["profile"]["photoUrl"])

      await channel.send(embed=embed)

## Show news materials
async def show_new_materials():
  auth = authorization() 
  service = build('classroom', 'v1', credentials=auth.credentials)

  course_materials = ClassroomRepository.new_materials_account(service, datetime.datetime.now())

  channel = client.get_channel(channel_id)
  if len (course_materials) != 0:
      classroom = discord.utils.get(channel.guild.roles, name='classroom')
      await channel.send(f'\n{classroom.mention} **There are new materials:**\n\n\n\n')
  else:
    return

  for course_material in course_materials:
    course = ClassroomRepository.get_course(service, course_material['courseId'])

    description = 'none'

    if 'description' in course_material:
      description = course_material['description'].split(' ')[0:10]

      description = ' '.join([str(elem) for elem in description])

    embed = discord.Embed(title=course_material['title'], url=course_material['alternateLink'], description=description, color=discord.Color.blue())

    try:
      embed.set_author(name=course['name'],  icon_url="https:" + ClassroomRepository.get_teacher(service, course_material["courseId"], course_material['creatorUserId'])["profile"]["photoUrl"])

      await channel.send(embed=embed)
    except:
      embed.set_author(name=course['name'],  icon_url=ClassroomRepository.get_teacher(service, course_material["courseId"], course_material['creatorUserId'])["profile"]["photoUrl"])

      await channel.send(embed=embed)

@tasks.loop(minutes=1)
async def called_once_a_day():
    await show_new_announcements()
    await show_new_works()
    await show_new_materials()
    
@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()

## Show a joke
@client.command()
async def joke (ctx):
  r = requests.get('https://api-charada.herokuapp.com/puzzle?lang=ptbr')
  json_string = json.dumps(r.json())
  dict_data = json.loads(json_string)
  
  await ctx.send('**A joke**: ' + '\n\nQuestion: ' + dict_data['question'] + '\nAnswer: ' + dict_data['answer'])

## Run
called_once_a_day.start() # Loop
keep_alive()  # Client keep alive
client.run(os.getenv('TOKEN'))  # Run the client