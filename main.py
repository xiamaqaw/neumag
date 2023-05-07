import disnake
from disnake.ext import commands
import os
import openai
from asyncio import sleep as sl
import sqlite3
#from webserver import keep_alive
openai.api_key = "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"
client = commands.Bot(command_prefix='.', intents=disnake.Intents.all())
connection = sqlite3.connect("db.sql")
cursor = connection.cursor()

client.remove_command("help")

for f in os.listdir("./cogs"):
	if f.endswith(".py"):
	    client.load_extension("cogs." + f[:-3])

messages = []

@client.event
async def on_ready():
    print("[info]: Бот запущен и готов к работе")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
    server_id INT,
    work_channel_id INT,
    nsfw INT,
    assistant INT,
    promt TEXT
    )""")
    connection.commit()

    for guild in client.guilds:
        if cursor.execute(f"SELECT nsfw FROM settings WHERE server_id = {guild.id}").fetchone() == None:
            cursor.execute(f"INSERT INTO settings VALUES ({guild.id}, 0, 0, 0, ' ')")
            connection.commit()
        else:
            pass


    await client.change_presence(activity=disnake.Activity(type=disnake.ActivityType.playing,name=f'Loading...'))
    await sl(10)
    await client.change_presence(activity=disnake.Activity(type=disnake.ActivityType.playing,name=f'Loading succesful!'))
    await sl(5)
    while True:
        await client.change_presence(status=disnake.Status.idle,activity=disnake.Activity(type=disnake.ActivityType.listening,name=f'.help | {len(client.guilds)} cерверов'))
        await sl(15)
        members = 0
        for guild in client.guilds:
            members += guild.member_count - 1
        await client.change_presence(status=disnake.Status.idle,activity=disnake.Activity(type=disnake.ActivityType.listening,name=f'{len(client.guilds)} cерверов | {members} users'))
        await sl(15)

@client.event
async def on_guild_join(guild):
    if cursor.execute(f"SELECT nsfw FROM settings WHERE server_id = {guild.id}").fetchone() == None:
            cursor.execute(f"INSERT INTO settings VALUES ({guild.id}, 0, 0, 0, ' ')")
            connection.commit()
    else:
        pass
    embedru=disnake.Embed(title="🇷🇺Добро пожаловать!", description="**Спасибо за выбор нашего бота!\nДля использования бота, необходимо установить:\n1. Канал работы: .selectchannel (channel_id)\n2. Хотите ли вы использовать режим Агрессивного AI? .aggressor (0/1, 0 - нет, 1 - да)\nПодробнее: .help**", color=0xda30ef)
    embedru.set_thumbnail(url="https://i.imgur.com/x0AXT7q.png")
    embedgb=disnake.Embed(title="🇬🇧Welcome!", description="**Thank you for choosing our bot!\nIn order to use the bot, you need to install:\n1. Work channel: .selectchannel (channel_id)\n2. Do you want to use the Aggressive AI mode? .aggressor (0/1, 0 - NO, 1 - YES)\nMore info: .help**", color=0xda30ef)
    embedgb.set_thumbnail(url="https://i.imgur.com/x0AXT7q.png")
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=embedru)
            await channel.send(embed=embedgb)
            break

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, disnake.ext.commands.errors.MissingPermissions):
        await ctx.reply("Данная комманда вам не доступна")
    else:
        pass
    
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("Данной комманды не существует.")
    else:
        pass

@commands.has_permissions(administrator=True)
@client.command(aliases=['selectchannel'])
async def __selectchannel(ctx, channel: int = None):
    if channel is None:
        await ctx.reply("Укажите корректный ID канала.")
    else:
        cursor.execute(f"UPDATE settings SET work_channel_id = {channel} WHERE server_id = {ctx.guild.id}")
        connection.commit()
        await ctx.reply("Успешно! Теперь вы сможете переписываться с AI в указанном канале!")

@commands.has_permissions(administrator=True)
@client.command(aliases=['aggressor'])
async def __aggressor(ctx, nsfw: int = None):
    assistant = cursor.execute(f"SELECT assistant FROM settings WHERE server_id = {ctx.guild.id}").fetchone()[0]
    if int(assistant) == 0:
        if nsfw is None:
            await ctx.reply("Укажите значение 0/1 (0 - запрет на использование агрессивного режима работы, 1 - AI сможет работать в режиме агрессивного AI)")
        else:
            if nsfw == 1:
                cursor.execute(f"UPDATE settings SET nsfw = 1 WHERE server_id = {ctx.guild.id}")
                connection.commit()
                await ctx.reply("Успешно! Теперь вы сможете переписываться с AI в агрессивном режиме!")
            elif nsfw == 0:
                cursor.execute(f"UPDATE settings SET nsfw = 0 WHERE server_id = {ctx.guild.id}")
                connection.commit()
                await ctx.reply("Успешно! Теперь вы не сможете переписываться с AI в агрессивном режиме!")
            else:
                await ctx.reply("Укажите значение 0/1 (0 - запрет на использование агрессивного режима работы, 1 - AI сможет работать в режиме агрессивного AI)")
    else:
        await ctx.send("Данная функция не доступна на этом сервере.")

@client.command(aliases=['help'])
async def __help(ctx):
    embed=disnake.Embed(title="Помощь", color=0xda30ef)
    embed.set_thumbnail(url="https://i.imgur.com/V0pY9Hc.png")
    embed.add_field(name=".help", value="Отображает данное сообщение", inline=False)
    embed.add_field(name=".selectchannel", value="Выбор канала для работы бота", inline=False)
    embed.add_field(name=".aggressor", value="Запретить/Разрешить использование функции агрессивного AI", inline=False)
    embed.add_field(name=".ai", value="Разовый запрос к AI (без запоминания контекста)", inline=False)
    embed.add_field(name=".assistant", value="Установить режим асистента (запрос без контекста + по заданному промпту)", inline=False)
    embed.add_field(name="В указанном канале - reset", value="Сброс контекста", inline=False)
    embed.add_field(name="В указанном канале - aggresor", value="Активация агрессивного AI (если разрешено на сервере)", inline=False)
    embed.set_footer(text="Говорим спасибо IIIpaklevka#2441 за такое чудо!")
    await ctx.send(embed=embed)

@client.command(aliases=['ai'])
async def __ai(ctx, *, promt = None):
    assistant = cursor.execute(f"SELECT assistant FROM settings WHERE server_id = {ctx.guild.id}").fetchone()[0]
    if int(assistant) == 0:
        if promt is None:
            await ctx.reply("Введите корректное сообещние AI")
        else:
            messages = []
            try:
                messages.append({"role": "user", "content": promt})

                completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
                )
                chat_response = completion.choices[0].message.content
                await ctx.reply(chat_response)
            except openai.error.RateLimitError:
                await ctx.send("🛠️ 🇷🇺 **Попробуйте повторить запрос позже.**\n 🛠️🇬🇧 **Please try again later.**")
            except openai.error.InvalidRequestError:
                messages = []
                await ctx.send("🛠️ 🇷🇺 **Попробуйте повторить запрос позже.**\n 🛠️🇬🇧 **Please try again later.**\nИстория сброшена из-за предела символов.")
    elif int(assistant) == 1:
        channel = cursor.execute(f"SELECT work_channel_id FROM settings WHERE server_id = {ctx.guild.id}").fetchone()[0]
        promt1 = cursor.execute(f"SELECT promt FROM settings WHERE server_id = {ctx.guild.id}").fetchone()[0]
        if int(channel) == ctx.channel.id:
            if promt is None:
                await ctx.reply("Введите корректное сообещние AI")
            else:
                messages = [{"role": "system", "content": promt1}]
                promt2 = promt[3:len(promt)]
                try:
                    messages.append({"role": "user", "content": promt2})

                    completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                    )
                    chat_response = completion.choices[0].message.content
                    await ctx.reply(chat_response)
                except openai.error.RateLimitError:
                    await ctx.send("🛠️ 🇷🇺 **Попробуйте повторить запрос позже.**\n 🛠️🇬🇧 **Please try again later.**")
                except openai.error.InvalidRequestError:
                    messages = []
                    await ctx.send("🛠️ 🇷🇺 **Попробуйте повторить запрос позже.**\n 🛠️🇬🇧 **Please try again later.**\nИстория сброшена из-за предела символов.")
        else:
            pass

        

@commands.has_permissions(administrator=True)
@client.command(aliases=['assistant'])
async def __assistant(ctx, assistant = None):
    if assistant is None:
        await ctx.send("Укажите корректное значение (0/1 0 - Выключено 1 - Включено)")
    else:
        if int(assistant) == 0:
            cursor.execute(f"UPDATE settings SET assistant = 0 WHERE server_id = {ctx.guild.id}")
            connection.commit()
            await ctx.send("Успешно!")
        elif int(assistant) == 1:
            cursor.execute(f"UPDATE settings SET assistant = 1 WHERE server_id = {ctx.guild.id}")
            connection.commit()
            await ctx.send("Успешно!")
        else:
            await ctx.send("Укажите корректное значение (0/1 0 - Выключено 1 - Включено)")

@commands.has_permissions(administrator=True)
@client.command(aliases=['promt'])
async def __promt(ctx, *, promt = None):
    if promt is None:
        await ctx.send("Укажите корректный promt")
    else:
        cursor.execute(f"UPDATE settings SET promt = '{promt}' WHERE server_id = {ctx.guild.id}")
        connection.commit()
        await ctx.send(f"promt\n{promt}\nуспешно установлен!")

@client.command(aliases=['request'])
async def __request(ctx, type, *, req):
    if ctx.author.id != 850637553173528597:
        pass
    else:
        if type == 'read':
            await ctx.send(cursor.execute(req).fetchone()[0])
        elif type == 'load':
            cursor.execute(req)
            connection.commit()
            await ctx.add_reaction("✅")

#######################################################################
##################СЛЕШ КОММАНДЫ СУЧКАААА###############################
#######################################################################

@client.slash_command(description="Помощь по командам бота")
async def help(ctx):
    embed=disnake.Embed(title="Помощь", color=0xda30ef)
    embed.set_thumbnail(url="https://i.imgur.com/V0pY9Hc.png")
    embed.add_field(name=".help", value="Отображает данное сообщение", inline=False)
    embed.add_field(name=".selectchannel", value="Выбор канала для работы бота", inline=False)
    embed.add_field(name=".aggressor", value="Запретить/Разрешить использование функции агрессивного AI", inline=False)
    embed.add_field(name=".ai", value="Разовый запрос к AI (без запоминания контекста)", inline=False)
    embed.add_field(name=".assistant", value="Установить режим асистента (запрос без контекста + по заданному промпту)", inline=False)
    embed.add_field(name="В указанном канале - reset", value="Сброс контекста", inline=False)
    embed.add_field(name="В указанном канале - aggresor", value="Активация агрессивного AI (если разрешено на сервере)", inline=False)
    embed.set_footer(text="Говорим спасибо IIIpaklevka#2441 за такое чудо!")
    await ctx.send(embed=embed)

@commands.has_permissions(administrator=True)
@client.slash_command(description="Настройка доступа к агрессивному режиму работы AI")
async def aggressor(ctx, nsfw: int = None):
    assistant = cursor.execute(f"SELECT assistant FROM settings WHERE server_id = {ctx.guild.id}").fetchone()[0]
    if int(assistant) == 0:
        if nsfw is None:
            await ctx.send("Укажите значение 0/1 (0 - запрет на использование агрессивного режима работы, 1 - AI сможет работать в режиме агрессивного AI)")
        else:
            if nsfw == 1:
                cursor.execute(f"UPDATE settings SET nsfw = 1 WHERE server_id = {ctx.guild.id}")
                connection.commit()
                await ctx.send("Успешно! Теперь вы сможете переписываться с AI в агрессивном режиме!")
            elif nsfw == 0:
                cursor.execute(f"UPDATE settings SET nsfw = 0 WHERE server_id = {ctx.guild.id}")
                connection.commit()
                await ctx.send("Успешно! Теперь вы не сможете переписываться с AI в агрессивном режиме!")
            else:
                await ctx.send("Укажите значение 0/1 (0 - запрет на использование агрессивного режима работы, 1 - AI сможет работать в режиме агрессивного AI)")
    else:
        await ctx.send("Данная функция не доступна на этом сервере.")

@commands.has_permissions(administrator=True)
@client.slash_command(description="Установить канал взаимодействия с AI")
async def selectchannel(ctx, channelid: int = None):
    if channelid is None:
        await ctx.send("Укажите корректный ID канала.")
    else:
        cursor.execute(f"UPDATE settings SET work_channel_id = {channelid} WHERE server_id = {ctx.guild.id}")
        connection.commit()
        await ctx.send("Успешно! Теперь вы сможете переписываться с AI в указанном канале!")

"""@client.slash_command(description="Разовый запрос к AI")
async def ai(ctx, promt = None):
    assistant = cursor.execute(f"SELECT assistant FROM settings WHERE server_id = {ctx.guild.id}").fetchone()[0]
    if int(assistant) == 0:
        if promt is None:
            await ctx.reply("Введите корректное сообещние AI")
        else:
            messages = []
            try:
                messages.append({"role": "user", "content": promt})

                completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
                )
                chat_response = completion.choices[0].message.content
                await ctx.reply(chat_response)
            except openai.error.RateLimitError:
                await ctx.send("🛠️ 🇷🇺 **Попробуйте повторить запрос позже.**\n 🛠️🇬🇧 **Please try again later.**")
            except openai.error.InvalidRequestError:
                messages = []
                await ctx.send("🛠️ 🇷🇺 **Попробуйте повторить запрос позже.**\n 🛠️🇬🇧 **Please try again later.**\nИстория сброшена из-за предела символов.")
    elif int(assistant) == 1:
        channel = cursor.execute(f"SELECT work_channel_id FROM settings WHERE server_id = {ctx.guild.id}").fetchone()[0]
        promt1 = cursor.execute(f"SELECT promt FROM settings WHERE server_id = {ctx.guild.id}").fetchone()[0]
        if int(channel) == ctx.channel.id:
            if promt is None:
                await ctx.reply("Введите корректное сообещние AI")
            else:
                messages = [{"role": "system", "content": promt1}]
                try:
                    messages.append({"role": "user", "content": promt})

                    completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                    )
                    chat_response = completion.choices[0].message.content
                    await ctx.send(chat_response)
                except openai.error.RateLimitError:
                    await ctx.send("🛠️ 🇷🇺 **Попробуйте повторить запрос позже.**\n 🛠️🇬🇧 **Please try again later.**")
                except openai.error.InvalidRequestError:
                    messages = []
                    await ctx.send("🛠️ 🇷🇺 **Попробуйте повторить запрос позже.**\n 🛠️🇬🇧 **Please try again later.**\nИстория сброшена из-за предела символов.")
        else:
            await ctx.reply("Не доступно в данном канале.")"""

@commands.has_permissions(administrator=True)
@client.slash_command(description='Установить режим работы')
async def assistant(ctx, assistant = None):
    if assistant is None:
        await ctx.send("Укажите корректное значение (0/1 0 - Выключено 1 - Включено)")
    else:
        if int(assistant) == 0:
            cursor.execute(f"UPDATE settings SET assistant = 0 WHERE server_id = {ctx.guild.id}")
            connection.commit()
            await ctx.send("Успешно!")
        elif int(assistant) == 1:
            cursor.execute(f"UPDATE settings SET assistant = 1 WHERE server_id = {ctx.guild.id}")
            connection.commit()
            await ctx.send("Успешно!")
        else:
            await ctx.send("Укажите корректное значение (0/1 0 - Выключено 1 - Включено)")

@commands.has_permissions(administrator=True)
@client.slash_command(description='Установить начальный промт (для работы в режиме assistant)')
async def promt(ctx, *, promt = None):
    if promt is None:
        await ctx.send("Укажите корректный promt")
    else:
        cursor.execute(f"UPDATE settings SET promt = '{promt}' WHERE server_id = {ctx.guild.id}")
        connection.commit()
        await ctx.send(f"promt\n{promt}\nуспешно установлен!")



client.run("MTEwMTQ5MTY3NDg1ODkyMjA2NQ.GSM047.f_P_H6wTjh7vYXGZVjUYQ7DXJd3tVTrNx27dzg")

