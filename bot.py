from flask import Flask, render_template
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
    return '''<body style="margin: 0; padding: 0;">
    <iframe width="100%" height="100%" src="https://axocoder.vercel.app/" frameborder="0" allowfullscreen></iframe>
  </body>'''

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()

keep_alive()
print("Server Running Because of Axo")
import discord
from discord import ui
from discord.ext import commands
from discord.ui import Button, View, UserSelect
import asyncio
import random
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from colorama import init, Fore, Style
import json


intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


class Select_Menu(discord.ui.UserSelect):
    def __init__(self, ctx):
        super().__init__(placeholder="Выберите пользователя")
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Только автор может выбрать пользователя!", ephemeral=True)
            return
        selected_user = self.values[0]  # Получаем выбранного пользователя

        # Проверяем, является ли выбранный пользователь ботом
        if selected_user.bot:
            await interaction.response.send_message("Боты не могут быть выбраны!", ephemeral=True)
            return

        print(f"Выбран пользователь: {selected_user.display_name}")  # Выводим display name в консоль

        # Respond to the interaction immediately
        await interaction.response.defer()

        # Do the rest of the processing in the background
        await self.process_selected_user(interaction, selected_user)

    async def process_selected_user(self, interaction: discord.Interaction, selected_user: discord.Member):

        with open('channel_ids.json', 'r') as f:
            channel_ids = json.load(f)
            voice_channel_id = channel_ids.get('voice_channel_id')
            stage_channel_id = channel_ids.get('stage_channel_id')

        channels = [bot.get_channel(channel_id) for channel_id in [
            1231932498917851256, 1185507926987780228, 1228628655345762346, 1185509058019594320, 
            1231192622664519770, 1185612251021967360, 1207366348951392327, 1185516791762534430, 
            1230576734777249793, 1230576771515027608, 1230576799910723714, 1230577711479525518, 
            1230577738692300922, 1230578924887609365]]

        if voice_channel_id:
            channels.append(bot.get_channel(voice_channel_id))
        if stage_channel_id:
            channels.append(bot.get_channel(stage_channel_id))

        messages = []
        last_message = None
        for channel in channels:
            channel_messages = [message async for message in channel.history(limit=10)]  # Get the last 100 messages from the channel
            for message in channel_messages:
                if message.author == selected_user:
                    if message.attachments:
                        if message.clean_content:
                            messages.append(f"{message.author.display_name}({message.author.id}) в {channel.name}: {message.clean_content} (Вложение: {', '.join(a.filename for a in message.attachments)})")
                        else:
                            messages.append(f"{message.author.display_name}({message.author.id}) в {channel.name}: (Нет сообщений) (Вложение: {', '.join(a.filename for a in message.attachments)})")
                    else:
                        messages.append(f"{message.author.display_name}({message.author.id}) в {channel.name}: {message.clean_content} (Вложений нет)")
                    last_message = message  # Store the last message object
                    break

        # Send the messages.txt file and the last image attachment to a specific channel
        target_channel = bot.get_channel(1233129553736630273)  # Replace with the ID of the channel you want to send to
        with open("messages.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(messages))
        file1 = discord.File("messages.txt", filename="messages.txt")
        await target_channel.send(file=file1)  # Send the messages.txt file first

        if last_message and last_message.attachments:
            last_attachment = last_message.attachments[0]
            attachment_bytes = await last_attachment.read()
            with open(f"attachments/{last_attachment.filename}", "wb") as f:
                f.write(attachment_bytes)
            file2 = discord.File(f"attachments/{last_attachment.filename}", filename=last_attachment.filename)
            await target_channel.send(file=file2)
        for channel in channels:
            channel_messages = [message async for message in channel.history(limit=5)]  # Get the last 100 messages from the channel
            for message in channel_messages:
                if message.author == selected_user:
                    await message.delete()

        image = Image.open('ser.png')

        # Создаем объект для рисования текста
        draw = ImageDraw.Draw(image)

        # Установка шрифта и размера текста
        font = ImageFont.truetype('arial.ttf', 20)  # замените на свой шрифт и размер

        # Вставляем текст на изображение на координатах
        draw.text((211, 245), selected_user.display_name, font=font, fill=(0, 0, 0), anchor='mm')

        # сохраяем изображение в файл
        with open('image.png', 'wb') as f:
            image.save(f, format='PNG')

        # Отправляем изображение в определенный чат
        channel_id = 1185507926987780228  # замените на ID канала, куда вы хотите отправить изображение
        channel = bot.get_channel(channel_id)
        with open('image.png', 'rb') as f:
            file = discord.File(f, filename='image.png')
            await channel.send(f"{selected_user.mention}", file=file)

        # Выдаем роль по ID пользователя
        role_id = 1220789688940498996  # замените на ID роли, которую вы хотите выдать
        role = interaction.guild.get_role(role_id)
        await selected_user.add_roles(role)

class GiveawayModal(ui.Modal, title='Розыгрыш'):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = ui.TextInput(label='Время (в секундах)', style=discord.TextStyle.short)
        self.text = ui.TextInput(label='Что разыгрывается', style=discord.TextStyle.paragraph)
        self.channel_input = ui.TextInput(label='Канал для розыгрыша (ID или имя)', style=discord.TextStyle.short)

        self.add_item(self.time)
        self.add_item(self.text)
        self.add_item(self.channel_input)

    async def on_submit(self, interaction: discord.Interaction):
        time = int(self.time.value)
        text = self.text.value
        channel_input = self.channel_input.value

        channel = None
        if channel_input.isdigit():
            channel = interaction.guild.get_channel(int(channel_input))
        else:
            channel = discord.utils.get(interaction.guild.channels, name=channel_input)

        if channel is None:
            await interaction.response.send_message('Канал не найден', ephemeral=True)
            return

        await giveaway(interaction, time, text, channel)

async def giveaway(interaction, seconds, text, channel):
    author = interaction.user
    time_end = format_time(seconds)
    msgs = 'ы'
    embed = discord.Embed(
        description=f"**Разыгрывается : `{text}`\nЗавершится через: `{time_end}` \n\nОрганизатор: {author.mention} \nДля участия нажмите на реакцию ниже.**",
        colour=0xa400fc)
    await interaction.response.defer()
    message = await channel.send(embed=embed, content=msgs)
    await message.add_reaction("🎉")  # Добавляем реакцию к сообщению

    while seconds > -1:
        time_end = format_time(seconds)
        text_message = discord.Embed(
            description=f"**Разыгрывается: `{text}`\nЗавершится через: `{time_end}` \n\nОрганизатор: {author.mention} \nДля участия нажмите на реакцию ниже.**",
            colour=0xa400fc)
        await message.edit(embed=text_message)
        await asyncio.sleep(1)
        seconds -= 1
        if seconds < -1:
            break


    #reactions = message.reactions  # Получаем список реакций
    channel = message.channel
    message_id = message.id
    message = await channel.fetch_message(message_id)
    reaction = message.reactions[0]
    print(reaction)

    users = [user async for user in reaction.users()]

    await message.clear_reactions()

    if reaction.count == 1:
        win = discord.Embed(
            description=f'**В этом розыгрыше нет победителя**',
            colour=0xa400fc)
        await message.edit(embed=win)
    else:
        user_win = random.choice(users)
        while str(user_win.id) == str(bot.user.id):
            user_win = random.choice(users)

        win = discord.Embed(
            description=f'**Розыгрыш завершён!\nПобедитель {user_win.mention} выиграл: ```{text}```\nНапишите организатору, {author.mention}, чтобы получить награду.**',
            colour=0xa400fc)
        await message.edit(embed=win)

def format_time(seconds):
    return f"{seconds//3600:02d}:{(seconds//60)%60:02d}:{seconds%60:02d}"


@bot.event
async def on_ready():
    print(f'{Fore.RED}Авторизован как: {Style.RESET_ALL}{bot.user} (ID: {bot.user.id})')
    await asyncio.sleep(1)
    print(f'{Fore.RED}Имя пользователя: {Style.RESET_ALL}{bot.user.name}')
    print(f'{Fore.RED}Дискриминатор: {Style.RESET_ALL}{bot.user.discriminator}')
    print(f'{Fore.RED}Дата создания: {Style.RESET_ALL}{bot.user.created_at}')
    print(f'{Fore.RED}Гильдии: {Style.RESET_ALL}{len(bot.guilds)}')
    print(f'{Fore.RED}Пользователи: {Style.RESET_ALL}{len(set(member for guild in bot.guilds for member in guild.members))}')
    print(f'{Fore.RED}Каналы: {Style.RESET_ALL}{len(set(channel for guild in bot.guilds for channel in guild.channels))}')
    print(f'{Fore.RED}Команды: {Style.RESET_ALL}{len(bot.commands)}')
    print(f'{Fore.RED}Основной Готов к работе{Style.RESET_ALL}')
    await asyncio.sleep(1)
    channel = bot.get_channel(1225481111904190606)
    await channel.send('Перезапустился')

@bot.event
async def is_owner(ctx):
    return ctx.author.id == 833957508979752960

@bot.event
async def on_member_remove(member):
    await asyncio.sleep(1)
    roles = [role.id for role in member.roles if role.id != member.guild.default_role.id]
    roles_db[member.id] = roles
    await asyncio.sleep(1)
    with open('roles.json', 'w') as f:
        json.dump(roles_db, f)

@bot.event
async def on_member_join(member):
    await asyncio.sleep(1)
    if member.id in roles_db:
        roles = [member.guild.get_role(int(role_id)) for role_id in roles_db[member.id]]
        await asyncio.sleep(1)
        for role_id in roles_db[member.id]:
            await asyncio.sleep(1)
            role = member.guild.get_role(int(role_id))
            try:
                await member.add_roles(role)
            except discord.NotFound:
                print(f"Role {role_id} not found. Skipping...")
        del roles_db[member.id]
        with open('roles.json', 'w') as f:
            json.dump(roles_db, f)

'''@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == 1233870994683465921:  # ID Сообщения
        guild = bot.get_guild(payload.guild_id)
        role = None
        if str(payload.emoji) == '✅':  # Emoji для реакций
            role = guild.get_role(1048156318680240179)  # ID Ролей для выдачи
        if role:
            member = await guild.fetch_member(payload.user_id)
            if member:
                await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == 1233870994683465921:  # ID Сообщения
        guild = bot.get_guild(payload.guild_id)
        role = None
        if str(payload.emoji) == '✅':  # Emoji для реакций
            role = guild.get_role(1048156318680240179)  # ID Ролей для выдачи
        if role:
            member = await guild.fetch_member(payload.user_id)
            if member:
                await member.remove_roles(role)
'''

@bot.command()
@commands.has_any_role(1186969159813316618, 1185509847396012172, 1185541872580579428)
async def buttons(ctx):
    await ctx.message.delete()
    button1 = Button(label='Лимитированный Войс', style=discord.ButtonStyle.red)
    button2 = Button(label='Лимитированная Трибуна', style=discord.ButtonStyle.green)
    button3 = Button(label='Дать Говноеда', style=discord.ButtonStyle.primary)
    button4 = Button(label='Розыгрыш', style=discord.ButtonStyle.blurple)
    button5 = Button(label='Удалить Лимитку', style=discord.ButtonStyle.grey)

    category_id = 1232429524143181966  # Replace with the ID of the category
    category = discord.utils.get(ctx.guild.categories, id=category_id)

    ping_messages = ["@everyone ЛИМИТКА", 
    "@everyone Кто не с нами, тот под нами", 
    "@everyone А мы в лимиточке сидим", 
    "@everyone Залетаем в лимиточку, толкаемся сосисочками", 
    "@everyone Заходим в лимитированный головой чат, общаемся, кайфуем", 
    "@everyone Заходите в наш прекрасный лимитированный голосовой", 
    '@everyone Не трогай пипитку, **заходи в Лимитку**',
    '@everyone Я сказал Лимитка класс, кто не верит пидо...',
    '@everyone Челик зайди, мы тут пиздим',
    '@everyone СЮДАААА',
    '@everyone Пьём певко в лимитированном',
    '@everyone Сидим, пердим в лимиточке',
    '@everyone Лимитированный стартовал',
    '@everyone Сегодня снова лимитированный',
    '@everyone Вы не просили, а мы в лимитированном',
    '@everyone Лимит очка началась, залетайте',
    '@everyone Войс открылся, а ну быстро появился']

    async def button1_callback(interaction):
        if interaction.user != ctx.author and not any(role.id in [1186969159813316618, 1185509847396012172] for role in interaction.user.roles):
            await interaction.response.send_message("У вас нет разрешения создавать лимитку!", ephemeral=True)
            return
        with open('channel_ids.json', 'r') as f:
            channel_ids = json.load(f)
        if 'voice_channel_id' in channel_ids or 'stage_channel_id' in channel_ids:
            await interaction.response.send_message("Э, Лимитированый войс или трибуна уже есть, удали их!", ephemeral=True)
            return
        voice_channel = await ctx.guild.create_voice_channel('ЛИМИТИРОВАННЫЙ ВОЙС', category=category, bitrate=64000, user_limit=0)

        role_ids = [1224402728185364532, 1225476474115457124, 1230797770298884206, 1230797927623168000, 1230798076944318486, 1185525808652107777, 1185541872580579428]
        for role_id in role_ids:
            role = ctx.guild.get_role(role_id)
            if role:
                await voice_channel.set_permissions(role, use_soundboard=True)

        await interaction.response.send_message(f'Канал "ЛИМИТИРОВАННЫЙ ВОЙС" создан!', ephemeral=True)

        channel_id = voice_channel.id
        with open('channel_ids.json', 'w') as f:
            json.dump({'voice_channel_id': channel_id}, f)

        channel_id = 1185507926987780228
        channel = interaction.client.get_channel(channel_id)

        ping_message = random.choice(ping_messages)
        await channel.send(ping_message)
        await voice_channel.send(ping_message)

    async def button2_callback(interaction):
        if interaction.user != ctx.author and not any(role.id in [1186969159813316618, 1185509847396012172] for role in interaction.user.roles):
            await interaction.response.send_message("У вас нет разрешения создавать лимитированную трибуну!", ephemeral=True)
            return
        with open('channel_ids.json', 'r') as f:
            channel_ids = json.load(f)
        if 'voice_channel_id' in channel_ids or 'stage_channel_id' in channel_ids:
            await interaction.response.send_message("Чо, ещё одну трибуну хочешь? Перехочешь!", ephemeral=True)
            return
        stage_channel = await ctx.guild.create_stage_channel('ЛИМИТИРОВАННАЯ ТРИБУНА', category=category, bitrate=64000)
        await interaction.response.send_message(f'Трибуна "Лимитированный Войс" создана!', ephemeral=True)

        channel_id = stage_channel.id
        with open('channel_ids.json', 'w') as f:
            json.dump({'stage_channel_id': channel_id}, f)

        channel_id = 1185507926987780228
        channel = interaction.client.get_channel(channel_id)

        ping_message = random.choice(ping_messages)
        await channel.send(ping_message)
        await stage_channel.send(ping_message)

    async def button3_callback(interaction):
        if interaction.user != ctx.author and not any(role.id in [1186969159813316618, 1185509847396012172, 1185541872580579428] for role in interaction.user.roles):
            await interaction.response.send_message("У вас нет разрешения дарить подарок!", ephemeral=True)
            return
        view = discord.ui.View()
        view.timeout = None
        view.add_item(Select_Menu(ctx))  # Помещаем наш класс
        await interaction.response.send_message("Кого выберем?", view=view, ephemeral=True) 

    async def button4_callback(interaction):
        if interaction.user != ctx.author and not any(role.id in [1186969159813316618, 1185509847396012172] for role in interaction.user.roles):
            await interaction.response.send_message("У вас нет разрешения делать розыгрыш!", ephemeral=True)
            return
        modal = GiveawayModal(title='Розыгрыш')
        await interaction.response.send_modal(modal)

    async def button5_callback(interaction):
        with open('channel_ids.json', 'r') as f:
            channel_ids = json.load(f)
        if 'voice_channel_id' in channel_ids:
            voice_channel_id = channel_ids['voice_channel_id']
            voice_channel = interaction.client.get_channel(voice_channel_id)
            await voice_channel.delete()
        if 'stage_channel_id' in channel_ids:
            stage_channel_id = channel_ids['stage_channel_id']
            stage_channel = interaction.client.get_channel(stage_channel_id)
            await stage_channel.delete()
        with open('channel_ids.json', 'w') as f:
            json.dump({}, f)
        await interaction.response.send_message('Лимитка удалена!', ephemeral=True)

    button1.callback = button1_callback
    button2.callback = button2_callback
    button3.callback = button3_callback
    button4.callback = button4_callback
    button5.callback = button5_callback

    view = discord.ui.View()
    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)
    view.add_item(button4)
    view.add_item(button5)

    await ctx.send('Выберите действие:', view=view)

@bot.command(aliases=['с', 'clear'])
@commands.has_any_role(1186969159813316618, 1185509847396012172)
async def cls(ctx, member: discord.Member | None, amount: int):
    if member is None:
        await ctx.channel.purge(limit=amount + 1)
    elif member in ctx.guild.members:
        def predicate(message):
            return message.author == member

        deleted = await ctx.channel.purge(check=predicate, limit=amount)
        await ctx.send(f'Удалено {len(deleted)} сообщений от {member.mention}')

'''@bot.command(aliases=['g'])
@commands.has_any_role(1186969159813316618, 1185509847396012172)
async def giveaway(ctx, seconds: int, *, text):
    def format_time(seconds):
        return f"{seconds//3600:02d}:{(seconds//60)%60:02d}:{seconds%60:02d}"

    author = ctx.message.author
    time_end = format_time(seconds)
    msgs = 'ы'
    message = await ctx.send(embed=discord.Embed(
        description=f"**Разыгрывается : `{text}`\nЗавершится через: `{time_end}` \n\nОрганизатор: {author.mention} \nДля участия нажмите на реакцию ниже.**",
        colour=0xa400fc), content=msgs)
    await message.add_reaction("🎉")

    while seconds > -1:
        time_end = format_time(seconds)
        text_message = discord.Embed(
            description=f"**Разыгрывается: `{text}`\nЗавершится через: `{time_end}` \n\nОрганизатор: {author.mention} \nДля участия нажмите на реакцию ниже.**",
            colour=0xa400fc)
        await message.edit(embed=text_message)
        await asyncio.sleep(1)
        seconds -= 1
        if seconds < -1:
            break

    channel = message.channel
    message_id = message.id
    message = await channel.fetch_message(message_id)
    reaction = message.reactions[0]

    users = [user async for user in reaction.users()]

    await message.clear_reactions()

    if reaction.count == 1:
        win = discord.Embed(
            description=f'**В этом розыгрыше нет победителя**',
            colour=0xa400fc)
        await message.edit(embed=win)
    else:
        user_win = random.choice(users)
        while str(user_win.id) == str(bot.user.id):
            user_win = random.choice(users)

        win = discord.Embed(
            description=f'**Розыгрыш завершён!\nПобедитель {user_win.mention} выиграл: ```{text}```\nНапишите организатору, {author.mention}, чтобы получить награду.**',
            colour=0xa400fc)
        await message.edit(embed=win)'''

@bot.command(aliases=['r'])
@commands.check(is_owner)
async def restart(ctx):
    await ctx.message.delete()
    emb = discord.Embed(
                        title=f"**Перезагрузка**",
                        color=0xa400fc,
                        )
    emb.set_footer(text = f"Выполнено, запросил {ctx.author}({ctx.author.display_name})", icon_url = ctx.author.display_avatar.url)
    await ctx.send(embed=emb)
    os.system("cls")
    os.execl(sys.executable, sys.executable, * sys.argv)

@bot.command()
@commands.has_any_role(1186969159813316618, 1185509847396012172, 1185541872580579428)
async def image(ctx):
    view = discord.ui.View()
    view.timeout = None
    view.add_item(Select_Menu(ctx))  # Помещаем наш класс
    await ctx.send("Кого выберем?", view=view, )  # Отправляем сообщение с данным меню


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(description=f'**У вас нет прав на выполнение этой команды**', color=0xa400fc)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(description=f'**Боту не хватает прав для выполнения этой команды**', color=0xa400fc)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(description=f'**Не хватает обязательного аргумента для этой команды**', color=0xa400fc)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(description=f'**Неправильный аргумент для этой команды**', color=0xa400fc)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(description=f'**Команда не найдена**', color=0xa400fc)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(description=f'**Вы не можете использовать эту команду в этом канале**', color=0xa400fc)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.DisabledCommand):
        embed = discord.Embed(description=f'**Команда отключена**', color=0xa400fc)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(description=f'**Произошла неизвестная ошибка**', color=0xa400fc)
        await ctx.send(embed=embed)
        print(f"Error: {error}")


bot.run(os.getenv("TOKEN"))
