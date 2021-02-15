import discord
import asyncio
import youtube_dl
import urllib.parse
import urllib.request
import re

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.duration = data.get('duration')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):

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

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
    
    @staticmethod
    async def get_url_video (search):

      query_string = urllib.parse.urlencode({
        'search_query': search
      })

      htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
      )

      search_results = re.findall(
          r'/watch\?v=(.{11})', htm_content.read().decode())

      return 'http://www.youtube.com/watch?v=' + search_results[0]
      
    

    