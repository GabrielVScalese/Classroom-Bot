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

client = commands.Bot(command_prefix='$')  # Define the client
channel_id = 817054317294387300

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

    embed = discord.Embed(title=course['name'][:256], url= course_announcement['alternateLink'], description=description, color=discord.Color.blue())

    try:
      teacher = ClassroomRepository.get_teacher(service, course_announcement["courseId"], course_announcement['creatorUserId'])
      embed.set_author(name=teacher["profile"]["name"]["fullName"][:256],  icon_url="https:" + teacher["profile"]["photoUrl"])

      await channel.send(embed=embed)
    except:
      teacher = ClassroomRepository.get_teacher(service, course_announcement["courseId"], course_announcement['creatorUserId'])
      embed.set_author(name=teacher["profile"]["name"]["fullName"][:256],  icon_url=teacher["profile"]["photoUrl"])

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

    embed = discord.Embed(title=course_work['title'][:256], url=course_work['alternateLink'], description=description, color=discord.Color.blue())
    
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

    embed = discord.Embed(title=course_material['title'][:256], url=course_material['alternateLink'], description=description, color=discord.Color.blue())

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

## Run
called_once_a_day.start() # Loop
keep_alive()  # Client keep alive
client.run(os.getenv('TOKEN'))  # Run the client