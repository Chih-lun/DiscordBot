from discord.ext import commands, tasks
import discord
from pornhub_api import PornhubApi
import random
import requests
from bs4 import BeautifulSoup
import asyncio
from fake_useragent import UserAgent
import DiscordUtils

client = commands.Bot(command_prefix='!')
api = PornhubApi()
main_channel = None
ptt_popular_channel = None
music = DiscordUtils.Music()

@client.event
async def on_ready():
    global main_channel
    global ptt_popular_channel
    print('Bot is ready')
    main_channel = client.get_channel('channel_id')
    ptt_popular_channel = client.get_channel('channel_id')
    await main_channel.send('Hello!歡迎使用BigBaoyu')


@client.command()
async def porn(msg, arg):
    data = api.search.search(
        arg,
        ordering='mostrecent',
    )
    video = random.choice(data.videos)
    result = f'{video.title}\n{video.url}'
    await msg.send(result)


@client.command()
async def ptt(msg, arg):
    r = requests.Session()
    ua = UserAgent()
    user_agent = ua.random
    headers = {'user-agent': user_agent}
    verification = {"from": f"/bbs/{arg}/index.html", "yes": "yes"}
    verify = r.post(
        f"https://www.ptt.cc/ask/over18?from=%2Fbbs%2F{arg}%2Findex.html",
        verification)
    response = r.get(f'https://www.ptt.cc/bbs/{arg}/index.html',
                     headers=headers).text
    soup = BeautifulSoup(response, 'html.parser')
    result = ''
    title = soup.find_all(name='div', class_='title')
    try:
        for i in title:
            result = result + i.find('a').text + '\n'
            result = result + f"https://www.ptt.cc{i.find('a').get('href')}" + '\n'
        await msg.send(result)
    except:
        await msg.send(f'{arg}找不到!')


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(msg, amount=5):
    await msg.channel.purge(limit=amount)

@client.command()
async def join(msg):
    voice = msg.message.author.voice
    if voice:
        voice_channel = voice.channel
        await voice_channel.connect()
    else:
        await msg.send('偵測不到頻道 請待在語音頻道裡')

@client.command()
async def leave(msg):
    bot_in_voice_channel = msg.guild.voice_client
    if bot_in_voice_channel:
        await bot_in_voice_channel.disconnect()
    else:
        await msg.send('機器人不在語音頻道裡')

@client.command()
async def play(msg,arg):
    bot_in_voice_channel = msg.guild.voice_client
    if arg.startswith('https://www.youtube.com/watch'):
        if not bot_in_voice_channel:
            voice = msg.message.author.voice
            if voice:
                voice_channel = voice.channel
                await voice_channel.connect()
            else:
                await msg.send('偵測不到頻道 請待在語音頻道裡')
                return
        else:
            if bot_in_voice_channel.is_playing():
                bot_in_voice_channel.stop()
        try:
            player = music.create_player(msg,ffmpeg_error_betterfix=True)
            await player.queue(url=arg)
            await player.play()
        except:
            await msg.send('登入驗證的聽不了')
    else:
        await msg.send('網址格式有問題')

@client.command()
async def stop(msg):
    voice = msg.guild.voice_client
    if not voice:
        await msg.send('機器人不在頻道中')
    else:
        voice.stop()

@client.command()
async def opgg(msg,arg):
    await msg.send(f'https://tw.op.gg/champion/{arg.lower()}/statistics')

@client.command()
async def info(msg):
    body = '!porn (keyword) A片查詢\n!ptt (看版) PTT查詢\n!clear(number) 訊息清除\n!join 機器人加入語音頻道\n!play (youtube網址)撥放音樂\n!leave 機器人離開語音頻道\n!stop 音樂暫停\n!opgg (champion) 英雄查詢\n!info (功能表)'
    await msg.send(body)

@tasks.loop(minutes=30.0)
async def ptt_popular_update():
    global ptt_popular_channel
    await asyncio.sleep(4)
    ua = UserAgent()
    user_agent = ua.random
    headers = {'user-agent': user_agent}
    response = requests.get('https://disp.cc/m/', headers=headers).text
    soup = BeautifulSoup(response, 'html.parser')
    data = soup.find_all(name='div', class_='ht_title')
    result = ''
    for i in data[0:20]:
        result = result + i.find('a').text + '\n'
        result = result + f"https://disp.cc/m/{i.find('a').get('href')}" + '\n'
    await ptt_popular_channel.send(result)


ptt_popular_update.start()
client.run('client_id')