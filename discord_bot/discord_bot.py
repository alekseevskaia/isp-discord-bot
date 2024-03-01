import configparser
import os
import random
import re
from datetime import datetime

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import MeetingNotes
from discord.ext import commands

os.chdir('/home/alekseevskaia/discord-bot')
CONFIG = configparser.ConfigParser()
CONFIG.read('discord-bot.conf')
id_general = int(CONFIG['discord']['id_general'])
token = CONFIG['discord']['token']

meeting_notes = AsyncIOScheduler()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)
db = MeetingNotes()


def find_day():
    day_of_today_english = datetime.now().strftime('%A')
    dict_of_days = {
        'Monday': 'В понедельник',
        'Tuesday': 'Во вторник',
        'Wednesday': 'В среду',
        'Thursday': 'В четверг',
        'Friday': 'В пятницу',
        'Saturday': 'В субботу',
        'Sunday': 'В воскресенье',
    }
    day_of_today = dict_of_days.get(day_of_today_english)
    return day_of_today


def generate_writer(list_of_members, trigger):
    try:
        number = random.randint(0, len(list_of_members) - 1)
        writer = list_of_members[number]
        day_of_today = find_day()
        text = f'{day_of_today} записи делает: {writer}'
        if trigger == 'empty':
            db.add_writer(writer, day_of_today, datetime.now())
        elif trigger == 'update':
            history_writers = db.get_table()
            db.update(history_writers[0][0], writer, day_of_today, datetime.now())
    except ValueError:
        text = 'Похоже все спят и я спать)'
    return text


def generate_members():
    guild = client.guilds[0]
    for voice_channel in guild.voice_channels:
        if str(voice_channel) == 'MeetingNotes':
            return [str(member.name).split('#')[0] for member in voice_channel.members]
    raise RuntimeError('Канал MeetingNotes не найден!')


def generate_message(answer, key):
    list_of_members = generate_members()
    day_of_today = find_day()
    history_writers = db.get_table()

    if len(history_writers) == 0:
        return generate_writer(list_of_members, trigger='empty')

    day_of_last_notification = history_writers[0][2]
    if day_of_today == day_of_last_notification and key != 'change':
        return f'Уже сгенерировано - **{history_writers[0][1]}** :white_check_mark:'

    if len(list_of_members) < 2:
        return answer

    reserve = []
    for writer in history_writers:
        check_writer_in_members = False
        if writer[1] in list_of_members:
            check_writer_in_members = True
            list_of_members.remove(writer[1])
        if check_writer_in_members and len(list_of_members) == 1:
            reserve.append(writer[1])
            break
    if key == 'schedule':
        writer = list_of_members[0]
        db.add_writer(writer, day_of_today, datetime.now())
    elif key == 'change':
        writer = reserve[0]
        history_writers = db.get_table()
        db.update(str(history_writers[0][0]), writer, day_of_today, datetime.now())
    return f'{day_of_today} записи делает: {writer}'


async def send_message(answer, key):
    general_channel = client.get_channel(id_general)
    text = generate_message(answer, key)
    history_writers = db.get_table()
    if len(history_writers) > 70:
        db.delete(str(history_writers[-1][0]))
    await general_channel.send(text)


@client.event
async def on_ready():
    db.delete(str(20))
    answer = 'Где все? :scream:'
    key = 'schedule'
    meeting_notes.add_job(
        send_message,
        args=[answer, key],
        trigger='cron',
        day_of_week='mon-fri',
        hour=13,
        minute=0,
        second=20,
    )
    meeting_notes.start()


@client.event
async def on_message(message):
    if message.author != client.user:
        message_from_text_channel = message.content.lower()

        if re.search(r'\bwho\b|\bкто\b|\bгуся\b', message_from_text_channel):
            answer = 'Ждем ещё :alarm_clock:'
            await send_message(answer, key='schedule')

        elif re.search(r'\bзаменаа\b|\bзапаснойй\b|\bchangee\b', message_from_text_channel):
            answer = 'Ждем ещё :alarm_clock:'
            await send_message(answer, key='change')

        elif re.search(r'\bгусь\b|\bagainn\b|\bещее\b', message_from_text_channel):
            try:
                list_of_members = generate_members()
                text = generate_writer(list_of_members, trigger='update')
            except ValueError:
                text = 'Отказываюсь работать :sunglasses:'
            await message.channel.send(text)

        if re.search(r'\bбаг\b|\bбага\b', message_from_text_channel):
            await message.channel.send('Воо дела :woozy_face:')

        elif re.search(
            r'\bзакончил\b|\bзакончила\b|\bсделал\b|\bсделала\b|\bполучилось\b|'
            r'\bнашла\b|\bнашел\b|\bнаписал\b|\bнаписала\b|\bнаписали\b',
            message_from_text_channel,
        ):
            await message.channel.send('Огонь :100: :fire:')

        elif re.search(r'\bпыталась\b|\bзавал\b|\bпытаюсь\b', message_from_text_channel):
            await message.channel.send('Все будет четко :stuck_out_tongue_winking_eye:')

        elif re.search(r'\bзалил\b|\bзалила\b', message_from_text_channel):
            await message.channel.send('Go ревьюить :hammer_and_wrench:')

        if re.search(r'\bеду\b|\bопаздываю\b|\bметро\b|\bпути\b', message_from_text_channel):
            await message.channel.send('Минус премия :smiling_imp:')

        elif re.search(r'\bплохо\b', message_from_text_channel) is not None:
            await message.channel.send('Просто релакс :tropical_drink:')

        elif re.search(
            r'\bразболеться\b|\bпростывать\b|\bпростыл\b|\bпростыла\b|\bзаболеваю\b|'
            r'\bзаболел\b|\bзаболела\b|\bзаболеть\b|\bболею\b|\bболит\b|\bврача\b',
            message_from_text_channel,
        ):
            await message.channel.send('Выздоравливай! :cherry_blossom:')

        elif re.search(r'в 14', message_from_text_channel) is not None:
            await message.channel.send('Опаздываем? :joy:')

        if re.search(r'ахах', message_from_text_channel) is not None:
            await message.channel.send('Зачетно :rolling_on_the_floor_laughing: ')

        elif re.search(r'\bок\b', message_from_text_channel) is not None:
            await message.channel.send(':stuck_out_tongue_winking_eye:')

        if re.search(r'\bдумаю\b', message_from_text_channel) is not None:
            await message.channel.send('А это весьма интересно :face_with_monocle:')

        elif re.search(r'\bтекстом\b', message_from_text_channel) is not None:
            await message.channel.send('Слушаю внимательно :hamster:')

        elif re.search(r'\bдома\b', message_from_text_channel) is not None:
            await message.channel.send('А в офисе веселее :zany_face:')

        if re.search(r'\bhelp\b', message_from_text_channel) is not None:
            text = (
                '1) сгенерировать по плану: who, кто, ктоо, гуся\n'
                + '2) сгенерировать запасного: changee, запаснойй, заменаа\n'
                + '3) рандомно: againn, ещее, эй гусь'
            )
            await message.channel.send(text)


def main():
    client.run(token)


if __name__ == '__main__':
    main()
