from contextlib import redirect_stdout
from platform import python_version
from random import choice, randint
import traceback
import platform
import datetime
import textwrap
import discord
import asyncio
import psutil
import whois
import nekos
import apiai
import time
import sys
import os
import io

from extension import *

default_config = {
    'cmd-prefix': 'n!',
    'mute-role': 'mute',
    'max-warns': 10,
    'admins': [
        297421244402368522
    ]
}

blocked = {
    'guilds': [
        # 489164651293179914
    ],
    'users': [
        # 356045969755734017
    ]
}

p = default_config['cmd-prefix']

react = {'suc': '✅', 'err': '❌', 'pen': '✏', 'pc': '🖥'}
icons = {
    'successful': 'https://cdn.icon-icons.com/icons2/894/PNG/512/Tick_Mark_icon-icons.com_69146.png',
    'error': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/ProhibitionSign2.svg/200px-ProhibitionSign2.svg.png',
    'using': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/1rightarrow_blue.svg/480px-1rightarrow_blue.svg.png',
    'osu!': 'https://upload.wikimedia.org/wikipedia/commons/4/41/Osu_new_logo.png'
}

class Bot(discord.Client):
    '''Основной класс бота.'''

    async def on_ready(self):
        log(f'Подключение успешно осуществлено!\nВ сети: {self.user}')
        self.time_start = time.time()

        async def __presence():
            _sleeping = 12
            while not self.is_closed():
                await client.change_presence(activity=discord.Streaming(name=f'{len(self.guilds)} серверов!', url='https://www.twitch.tv/%none%'))
                await asyncio.sleep(_sleeping)
                await client.change_presence(activity=discord.Streaming(name=f'{len(self.users)} пользователей!', url='https://www.twitch.tv/%none%'))
                await asyncio.sleep(_sleeping)
                await client.change_presence(activity=discord.Streaming(name=f'{p}help', url='https://www.twitch.tv/%none%'))
                await asyncio.sleep(_sleeping)
        self.loop.create_task(__presence())

    async def on_error(self, event, *args, **kwargs):
        warn(str(args))
        message = args[0]
        _exception = traceback.format_exc()
        dev = discord.utils.get(client.users, id=297421244402368522)
        
        try:
            bot_permissions = discord.utils.get(message.guild.members, name=self.user.name).permissions_in(message.channel)
            if bot_permissions.send_messages:
                await message.channel.send('Во время выполнения произошла ошибка.\nНе стоит беспокоиться, она отправлена разработчику и вскоре он ею займется!')
            elif bot_permissions.add_reactions:
                await message.add_reaction(react['err'])
            else:
                pass
        except:
            pass

        return await dev.send(f"Произошло исключение... \nОбнаружено на сервере {message.guild.name}\nИсключение нашел: {message.author}\n```python\n{_exception}```")


    async def on_guild_join(self, guild):
        if guild.id in blocked['guilds']:
            return await guild.leave()


    async def on_message(self, message):
        self.message = message
        self.channel = message.channel
        self.author = message.author
        self.content = message.content
        self.guild = message.guild

        try:
            print(f'{self.guild.name} | {self.channel.name} | {self.author.name}: {self.content}')
        except:
            print(f'[ЛС] {self.author}: {self.content}')
            if self.content.startswith(default_prefix):
                return await self.author.send('Извините, но команды невозможно выполнить в личной переписке.')
            return False

        if self.author.bot:
            return False

        if discord.utils.get(self.guild.members, name=self.user.name).mentioned_in(self.message):
            await self.message.add_reaction('❔')

        try:
            self.permissions = self.author.permissions_in(self.channel)
            self.bot_permissions = discord.utils.get(self.guild.members, name=self.user.name).permissions_in(self.channel)
        except:
            pass
        try:
            # self._bot = Data.config.load(self.guild)
            self._bot = default_config
        except:
            p = default_config['cmd-prefix']
        else:
            p = self._bot['cmd-prefix']



        if self.content.startswith(f'{p}execute'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}execute':
                return False
            if self.author.id != 297421244402368522:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Вы не можете выполнять данную команду.', icon_url=icons['error']))

            user_message = self.message

            async def _execution():
                async with self.channel.typing():
                    env = {
                        'channel': self.channel,
                        'author': self.author,
                        'guild': self.guild,
                        'message': self.message,
                        'bot': self.user,
                        'client': self,
                        'discord': discord
                    }

                    owner = (await client.application_info()).owner

                    env.update(globals())
                    _code = ' '.join(arg[1:]).replace('```python', '').replace('```', '')
                    try:
                        stdout = io.StringIO()
                        interpretate = f'async def virtexec():\n{textwrap.indent(_code, "  ")}'
                        exec(interpretate, env)
                        virtexec = env['virtexec']
                        with redirect_stdout(stdout):
                            function = await virtexec()

                    except Exception as e:
                        stdout = io.StringIO()
                        value = stdout.getvalue()

                        msg = discord.Embed(color=0xff0000, description=f"\n:inbox_tray: Входные данные:\n```python\n{' '.join(arg[1:]).replace('```python', '').replace('```', '')}\n```\n:outbox_tray: Выходные данные:\n```python\n{value}{traceback.format_exc()}```".replace(self.http.token, '•' * len(self.http.token)))
                        msg.set_author(name='Интерпретатор Python кода.')
                        msg.set_footer(icon_url=icons['error'],
                            text=f'Интерпретация не удалась - Python {python_version()} | {platform.system()}')
                        return await self.channel.send(f'{owner.mention}, смотри сюда!', embed=msg)
                    else:
                        value = stdout.getvalue()
                        if function is None:
                            if not value:
                                value = 'None'
                            success_msg = discord.Embed(color=0x00ff00, description=f":inbox_tray: Входные данные:\n```python\n{' '.join(arg[1:]).replace('```python', '').replace('```', '')}```\n\n:outbox_tray: Выходные данные:\n```python\n{value}```".replace(self.http.token, '•' * len(self.http.token)))
                            success_msg.set_author(name='Интерпретатор Python кода.')
                            success_msg.set_footer(icon_url=icons['successful'],
                                text=f'Интерпретация успешно завершена - Python {python_version()} | {platform.system()}')
                            return await self.channel.send(f'{owner.mention}, смотри сюда!', embed=success_msg)
                        else:
                            success_msg = discord.Embed(color=0x00ff00, description=f":inbox_tray: Входные данные:\n```python\n{' '.join(arg[1:]).replace('```python', '').replace('```', '')}```\n\n:outbox_tray: Выходные данные:\n```python\n{value}{function}```".replace(self.http.token, '•' * len(self.http.token)))
                            success_msg.set_author(name='Интерпретатор Python кода.')
                            success_msg.set_footer(icon_url=icons['successful'],
                                text=f'Интерпретация успешно завершена - Python {python_version()} | {platform.system()}')
                            return await self.channel.send(f'{owner.mention}, смотри сюда!', embed=success_msg)

            self.loop.create_task(_execution())

            await asyncio.sleep(1.0)

            try:
                await user_message.delete()
            except discord.errors.Forbidden:
                pass

            return True


        
        if self.author.id in blocked['users'] and self.message.content.startswith(p):
            return await self.author.send('Вам был ограничен доступ к моему функционалу.')


        if self.content.startswith(f'{p}neko'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}neko':
                return False
            if not self.channel.is_nsfw():
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Вы не в NSFW канале!', icon_url=icons['error']))
            _possible = [
                'feet', 'yuri', 'trap', 'futanari', 'hololewd', 'lewdkemo',
                'solog', 'feetg', 'cum', 'erokemo', 'les', 'lewdk', 'ngif',
                'tickle', 'lewd', 'feed', 'eroyuri', 'eron', 'cum_jpg',
                'bj', 'nsfw_neko_gif', 'solo', 'kemonomimi', 'nsfw_avatar', 'poke',
                'anal', 'slap', 'hentai', 'avatar', 'erofeet', 'holo', 'keta',
                'blowjob', 'pussy', 'tits', 'holoero', 'pussy_jpg', 'pwankg',
                'classic', 'kuni', 'pat', 'kiss', 'femdom', 'neko', 'cuddle',
                'erok', 'fox_girl', 'boobs', 'smallboobs', 'hug', 'ero', 'wallpaper'
            ]
            try:
                arg[1]
            except:
                n = discord.Embed(color=0xF13875)
                n.set_image(url=nekos.img(choice(_possible)))
                n.set_footer(text=f'{p}neko | {p}neko help', icon_url='https://i.pinimg.com/originals/85/24/6b/85246bdc4a9e75abada664514153d921.png')
                return await self.channel.send(embed=n)
            else:
                if arg[1].lower() == 'help':
                    return await self.channel.send(embed=discord.Embed(color=0xff0000, description=', '.join(_possible)).set_footer(text=f'{p}neko | {p}neko help', icon_url='https://i.pinimg.com/originals/85/24/6b/85246bdc4a9e75abada664514153d921.png'))
                else:
                    if arg[1].lower() not in _possible:
                        return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Неверный аргумент.', icon_url=icons['error']))
                    n = discord.Embed(color=0xF13875)
                    n.set_image(url=nekos.img(arg[1]))
                    n.set_footer(text=f'{p}neko | {p}neko help', icon_url='https://i.pinimg.com/originals/85/24/6b/85246bdc4a9e75abada664514153d921.png')
                    return await self.channel.send(embed=n)


        if self.content.startswith(f'{p}cleanup'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}cleanup':
                return False

            if not self.permissions.manage_messages and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.manage_messages: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))

            try: arg[1] and arg[2]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xff00ff).set_footer(text=f'{p}cleanup [@пользователь] [кол-во сообщений]', icon_url=icons['using']))

            def is_member(m):
                return m.author == Data.member.get(arg[1], self.guild)

            return await self.channel.purge(limit=int(arg[2]), check=is_member)


        if self.content.startswith(f'{p}purge'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}purge':
                return False
            try: arg[1]
            except: return await self.channel.send(embed=discord.Embed(color=0xff00ff).set_footer(text=f'{p}purge [кол-во сообщений]', icon_url=icons['using']))
            if not arg[1].isnumeric():
                return await self.channel.send(embed=discord.Embed(color=0xff00ff).set_footer(text=f'{p}purge [кол-во сообщений (ЧИСЛО!)]', icon_url=icons['using']))
            if not self.permissions.manage_messages and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.manage_messages: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))
            if int(arg[1]) >= 101:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Невозможно за раз удалить более 99 сообщений (включая сообщение-команду).', icon_url=icons['error']))
            return await self.channel.purge(limit=int(arg[1]) + 1)


        if self.content.startswith(f'{p}calc'):
            arg = self.content.split(' ')
            if arg[0] != f'{p}calc':
                return False
            try: arg[1]
            except: return await self.channel.send(embed=discord.Embed(color=0xff00ff).set_footer(text=f'{p}calc [выражение]', icon_url=icons['using']))
            from math import pi
            from re import sub
            try:
                a = str(' '.join(arg[1:])).replace(':', '/').replace('^', '**').replace(',', '.')
                b = sub('[ йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮQWERTYUIOPASDFGHJKLZXCVBNMqwertyuoasdfghjklzxcvbnm;!@#$=\'\"]', '', a)
            except Exception as e:
                return False
            
            if len(b) >= 8 and b.count('**') != 0:
                return await self.channel.send(embed=discord.Embed(color=0xfA0000).set_footer(text='Недопустимо по причине снижения производительности.', icon_url=icons['error']))
            else:
                try: __eval = str(eval(b))
                except ZeroDivisionError: __eval = '∞'
                except Exception as e:
                    return await self.channel.send(embed=discord.Embed(color=0xf0a302).set_footer(text='Выражение имеет ошибку.\nИсправьте выражение.', icon_url=icons['using']))
                if len(__eval) > 12 and not str(__eval).isnumeric():
                    return await self.channel.send(embed=discord.Embed(color=0xf0a302, description=f'(Указаны первые 12 цифр)\n{str(__eval)[:12]}\n\nОкругленный:\n{round(float(__eval))}').set_footer(text=f'{p}calc [выражение]', icon_url=icons['using']))
                elif len(__eval) > 12 and str(__eval).isnumeric():
                    return await self.channel.send(embed=discord.Embed(color=0xf0a302, description=f'(Указаны первые 12 цифр)\n{str(__eval)[:12]}').set_footer(text=f'{p}calc [выражение]', icon_url=icons['using']))
                else:
                    return await self.channel.send(embed=discord.Embed(color=0xf0a302, description=f'{__eval}').set_footer(text=f'{p}calc [выражение]', icon_url=icons['using']))


        if self.content.startswith(f'{p}help') or self.content.startswith(f'{p}info') or self.content == self.user.mention:
            arg = self.content.split(' ')
            if arg[0] != f'{p}help' and arg[0] != f'{p}info' and arg[0] != self.user.mention:
                return False

            help_main = f'''
Спасибо, что используете {self.user.name}!

Для навигации по справочнику,
 используйте реакции под этим сообщением
 в качестве панели управления.
'''
            help_f01 = f'''
`{p}help     `| Справка по командам;
`{p}neko     `| [NSFW] | Аниме изображения;
`{p}purge    `| Удаление сообщений;
`{p}calc     `| Калькулятор;
`{p}avatar   `| Аватар пользователя;
`{p}myname   `| Сменить Ваш никнейм;
`{p}roleusers`| Пользователи с ролью;
'''
            help_f02 = f'''
`{p}osu      `| Статистика игрока osu!;
`{p}status   `| Статистика бота;
`{p}msg      `| Отправка сообщения;
`{p}hostinfo `| Информация о домене;
`{p}talk     `| Общение с ботом;
`{p}userinfo `| Информация об аккаунте;
'''
            help_adm = f'''
`{p}ban      `| Забанить пользователя;
`{p}unban    `| Разбанить пользователя;
`{p}banlist  `| Банлист сервера;
`{p}kick     `| Выгнать пользователя;
`{p}say      `| Отправка сообщения от имени бота;
'''

            _description = f'[「Наш Discord-сервер」](https://discord.gg/ZQfNQ43) [「Пригласить меня」](https://discordapp.com/oauth2/authorize?client_id=452534618520944649&scope=bot&permissions=301296759) [「GitHub」](https://github.com/AkiraSumato-01/Discord-Bot-Naomi)  \nПрефикс на этом сервере: {p}'

            help_list = {
                'page_start': discord.Embed(color=0x00C6FF, title=':page_facing_up: Справочник по командам', description=_description),
                'page_01': discord.Embed(color=0x00C6FF, title=':page_facing_up: Справочник по командам', description=_description),
                'page_02': discord.Embed(color=0x00C6FF, title=':page_facing_up: Справочник по командам', description=_description),

                'page_system': discord.Embed(color=0x00C6FF, title=':desktop: Системная информация', description=_description),

                'page_guild': discord.Embed(color=0x2388FA, title=f'Сервер {self.guild.name}:', description=_description),
                'page_odmen': discord.Embed(color=0x00C6FF, title=':page_facing_up: Справочник по командам', description=_description),
                'page_me': discord.Embed(color=0x00C6FF, title=':page_facing_up: Информация обо мне', description=_description),
            }

            _bot_count = 0
            for member in self.guild.members:
                if member.bot:
                    _bot_count += 1

            help_list['page_start'].set_footer(text=f'{p}help | Главная', icon_url=icons['using'])
            help_list['page_01'].set_footer(text=f'{p}help | Стр. #1', icon_url=icons['using'])
            help_list['page_02'].set_footer(text=f'{p}help | Стр. #2', icon_url=icons['using'])
            help_list['page_me'].set_footer(text=f'{p}help | Обо мне', icon_url=icons['using'])
            help_list['page_system'].set_footer(text=f'{p}help | Система', icon_url=icons['using'])
            help_list['page_odmen'].set_footer(text=f'{p}help | Команды администрации', icon_url=icons['using'])
            help_list['page_guild'].set_footer(text=f'{p}help | Информация о сервере', icon_url=icons['using'])

            help_list['page_guild'].add_field(name="Регион:", value=f'{self.guild.region}', inline=True)
            help_list['page_guild'].add_field(name="Владелец:", value=f'{self.guild.owner}', inline=True)
            help_list['page_guild'].add_field(name="Всего ролей:", value=f'{len(self.guild.roles)}', inline=True)
            help_list['page_guild'].add_field(name="Участников:", value=f'{self.guild.member_count}', inline=True)
            help_list['page_guild'].add_field(name="Ботов:", value=f'{_bot_count}', inline=True)
            help_list['page_guild'].add_field(name="Текстовых каналов:", value=f'{len(self.guild.text_channels)}', inline=True)
            help_list['page_guild'].add_field(name="Голосовых каналов:", value=f'{len(self.guild.voice_channels)}', inline=True)

            for embed in help_list.values():
                embed.set_thumbnail(url=self.user.avatar_url)
            help_list['page_guild'].set_thumbnail(url=self.guild.icon_url)

            help_list['page_start'].add_field(name='Главная:', value=help_main)
            help_list['page_01'].add_field(name='Стр. #1', value=help_f01)
            help_list['page_02'].add_field(name='Стр. #2', value=help_f02)
            help_list['page_odmen'].add_field(name='Команды администрации', value=help_adm)

            help_list['page_me'].add_field(name='Аккаунт создан:', value=self.user.created_at, inline=False)
            help_list['page_me'].add_field(name='Аккаунт подтвержден:', value=self.user.verified, inline=False)
            help_list['page_me'].add_field(name='Версия Python; DiscordPy:', value=f'{python_version()}; {discord.__version__}', inline=False)
            help_list['page_me'].add_field(name='Разработчик:', value=(await client.application_info()).owner)

            _buttons = {
                '1⃣': '01',
                '2⃣': '02',
                '#⃣': 'odmen',
                'ℹ': 'info',
                '💾': 'serverinfo'
            }

            _user_ = self.author

            _current = await self.channel.send(embed=help_list['page_start'], delete_after=120)

            async def __menu_controller(current, help_list, _buttons):
                for react in _buttons:
                    await current.add_reaction(react)

                def check(r, u):
                    if not current:
                        return False
                    elif str(r) not in _buttons.keys():
                        return False
                    elif u.id != _user_.id or r.message.id != current.id:
                        return False
                    return True

                while current:
                    react, user = await self.wait_for('reaction_add', check=check)
                    try:
                        control = _buttons.get(str(react))
                    except:
                        control = None

                    if control == '01':
                            await current.edit(embed=help_list['page_01'])
                    if control == '02':
                            await current.edit(embed=help_list['page_02'])
                    if control == 'info':
                        await current.edit(embed=help_list['page_me'])
                    if control == 'odmen':
                        await current.edit(embed=help_list['page_odmen'])
                    if control == 'serverinfo':
                        await current.edit(embed=help_list['page_guild'])

                    try:
                        await current.remove_reaction(react, user)
                    except discord.HTTPException:
                        pass
                        
            self.loop.create_task(__menu_controller(_current, help_list, _buttons))


        if self.content.startswith(f'{p}osu'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}osu':
                return False

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xD587F2).set_footer(text=f'{p}osu [никнейм] | lemmy.pw', icon_url=icons['osu!']))

            try: arg[2]
            except:
                game_mode = {'num': 0, 'name': 'osu!'}
            else:
                if arg[2] == 'taiko' or arg[2] == 't':
                    game_mode = {'num': 1, 'name': 'osu!taiko'}
                if arg[2] == 'catch' or arg[2] == 'ctb' or arg[2] == 'c':
                    game_mode = {'num': 2, 'name': 'osu!catch'}
                if arg[2] == 'mania' or arg[2] == 'm':
                    game_mode = {'num': 3, 'name': 'osu!mania'}

            _colour = randint(0x000000, 0xFFFFFF)
            _tc = lambda: randint(0, 255)
            osu_desk_color = '%02X%02X%02X' % (_tc(), _tc(), _tc())
            print(osu_desk_color)

            _image_url = f'http://lemmmy.pw/osusig/sig.php?colour=hex{osu_desk_color}&uname={arg[1]}&mode={game_mode["num"]}&pp=1&countryrank&removeavmargin&flagshadow&flagstroke&darktriangles&opaqueavatar&avatarrounding=5&onlineindicator=undefined&xpbar&xpbarhex'

            osu_st = discord.Embed(color=_colour, title=f'Статистика {arg[1]} в {game_mode["name"]}')
            osu_st.set_image(url=_image_url)
            osu_st.set_footer(icon_url=icons['osu!'], text=f'{p}osu [никнейм] | lemmy.pw')
            return await self.channel.send(embed=osu_st)


        if self.content.startswith(f'{p}ban'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}ban':
                return False

            if not self.permissions.ban_members and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.ban_members: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xD587F2).set_footer(text=f'{p}ban [@пользователь] [причина]', icon_url=icons['using']))

            try:
                try: arg[2]
                except: _r = 'отсутствует'
                else: _r = ' '.join(arg[2:])
                _user = Data.member.get(arg[1], self.guild)
                await self.guild.ban(user=_user, reason=_r)
            except discord.errors.Forbidden:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня нет прав.', icon_url=icons['error']))
            except Exception as e:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=e, icon_url=icons['error']))
            else:
                return await self.channel.send(embed=discord.Embed(color=0x00ff00, description=f'Пользователь {_user} забанен!\nПричина: {_r}.').set_footer(text=f'{p}ban [@пользователь] [причина]', icon_url=icons['using']))


        if self.content.startswith(f'{p}unban'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}unban':
                return False

            if not self.permissions.ban_members and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.ban_members: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xD587F2).set_footer(text=f'{p}unban [никнейм пользователя]', icon_url=icons['using']))

            try:

                _bans = await self.guild.bans()
                _user = None
                unbanned = None

                # TODO: починить эту хрень

                for banned_user in _bans:
                    print(f'{banned_user.user.name} | {arg[1:]}')
                    if banned_user.user.name == ' '.join(arg[1:]):
                        _user = banned_user.user
                        await self.guild.unban(user=_user)
                        unbanned = True

                if not unbanned:
                    return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'Не удалось разбанить пользователя.', icon_url=icons['error']))


            except discord.errors.Forbidden:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня нет прав.', icon_url=icons['error']))
            except Exception as e:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=e, icon_url=icons['error']))
            else:
                return await self.channel.send(embed=discord.Embed(color=0x00ff00, description=f'Пользователь {_user.mention} разбанен.').set_footer(text=f'{p}unban [никнейм пользователя]', icon_url=icons['using']))


        if self.content.startswith(f'{p}banlist'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}banlist':
                return False

            if not self.permissions.ban_members and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.ban_members: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))

            try: _bans = await self.guild.bans()
            except discord.errors.Forbidden:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня нет прав.', icon_url=icons['error']))
            except Exception as e:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Синтаксическая ошибка в команде.', icon_url=icons['error']))
            if len(_bans) <= 0:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Забаненные пользователи отсутствуют.', icon_url=icons['successful']))
            _banned = []
            for user in _bans:
                _banned.append(user.user.name)
            return await self.channel.send(embed=discord.Embed(color=0xff0000, description=f'Забаненные пользователи:\n{", ".join(_banned)}').set_footer(icon_url=icons['using'], text=f'{p}banlist'))


        if self.content.startswith(f'{p}card'):

            return False # Команда временно отключена

            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}card':
                return False
            try:
                arg[1]
            except:
                data = Data.card.load(self.author)
                c = discord.Embed(color=0xD587F2, title=data['status'], description=f"```{data['description']}```")
                if data['status']: c.set_author(name=f'Карточка {self.author}', icon_url=self.author.avatar_url)
                else: c.set_author(name=self.author.name, icon_url=self.author.avatar_url)
                if data['vk']: c.add_field(name='ВКонтакте:', value=data['vk'], inline=False)
                if data['google']: c.add_field(name='Google:', value=data['google'], inline=False)
                if data['facebook']: c.add_field(name='Facebook:', value=data['facebook'], inline=False)
                if data['twitter']: c.add_field(name='Twitter:', value=data['twitter'], inline=False)
                if data['instagram']: c.add_field(name='Instagram:', value=data['instagram'], inline=False)
                c.set_footer(text=f'{p}card [@пользователь] | {p}card set', icon_url=icons['using'])
                c.set_thumbnail(url=self.author.avatar_url)
                if data['banner']: c.set_image(url=data['banner'])
                return await self.channel.send(embed=c)
            else:
                try:
                    _user = Data.member.get(arg[1], self.guild)
                    data = Data.card.load(_user)
                except:
                    if arg[1].lower() == 'set':
                        try: arg[2]
                        except:
                            _possible = ['', 'status', 'vk', 'google', 'facebook', 'twitter', 'instagram', 'banner', 'description']
                            return await self.channel.send(embed=discord.Embed(color=0xfA0000, description="```%s```" % '\n'.join(_possible)).set_footer(text=f'{p}card [@пользователь] | {p}card set', icon_url=icons['using']))
                        else:
                            _local = Data.card.load(self.author)

                            __user = self.author

                            def check(m):
                                return m.author == __user and m.channel == self.channel

                            if arg[2].lower() == 'status':
                                await self.channel.send(embed=discord.Embed(color=0xA1E215).set_footer(text='А теперь введите статус.', icon_url=icons['using']))
                                _msg = await self.wait_for('message', check=check)

                                _local['status'] = _msg.content

                                if Data.card.upload(__user, _local): return await _msg.add_reaction(react['suc'])
                                else: return await _msg.add_reaction(react['err'])

                            if arg[2].lower() == 'description':
                                await self.channel.send(embed=discord.Embed(color=0xA1E215).set_footer(text='А теперь введите описание.', icon_url=icons['using']))
                                _msg = await self.wait_for('message', check=check)

                                _local['description'] = _msg.content

                                if Data.card.upload(__user, _local): return await _msg.add_reaction(react['suc'])
                                else: return await _msg.add_reaction(react['err'])

                            if arg[2].lower() == 'vk':
                                await self.channel.send(embed=discord.Embed(color=0xA1E215).set_footer(text='А теперь введите ссылку на Вашу страницу ВК.', icon_url=icons['using']))
                                _msg = await self.wait_for('message', check=check)

                                _local['vk'] = _msg.content

                                if Data.card.upload(__user, _local): return await _msg.add_reaction(react['suc'])
                                else: return await _msg.add_reaction(react['err'])

                            if arg[2].lower() == 'google':
                                await self.channel.send(embed=discord.Embed(color=0xA1E215).set_footer(text='А теперь введите ссылку на Вашу страницу Google.', icon_url=icons['using']))
                                _msg = await self.wait_for('message', check=check)

                                _local['google'] = _msg.content

                                if Data.card.upload(__user, _local): return await _msg.add_reaction(react['suc'])
                                else: return await _msg.add_reaction(react['err'])

                            if arg[2].lower() == 'facebook':
                                await self.channel.send(embed=discord.Embed(color=0xA1E215).set_footer(text='А теперь введите ссылку на Вашу страницу Facebook.', icon_url=icons['using']))
                                _msg = await self.wait_for('message', check=check)

                                _local['facebook'] = _msg.content

                                if Data.card.upload(__user, _local): return await _msg.add_reaction(react['suc'])
                                else: return await _msg.add_reaction(react['err'])

                            if arg[2].lower() == 'twitter':
                                await self.channel.send(embed=discord.Embed(color=0xA1E215).set_footer(text='А теперь введите ссылку на Вашу страницу Twitter.', icon_url=icons['using']))
                                _msg = await self.wait_for('message', check=check)

                                _local['twitter'] = _msg.content

                                if Data.card.upload(__user, _local): return await _msg.add_reaction(react['suc'])
                                else: return await _msg.add_reaction(react['err'])

                            if arg[2].lower() == 'instagram':
                                await self.channel.send(embed=discord.Embed(color=0xA1E215).set_footer(text='А теперь введите ссылку на Вашу страницу Instagram.', icon_url=icons['using']))
                                _msg = await self.wait_for('message', check=check)

                                _local['instagram'] = _msg.content

                                if Data.card.upload(__user, _local): return await _msg.add_reaction(react['suc'])
                                else: return await _msg.add_reaction(react['err'])

                            if arg[2].lower() == 'banner':
                                await self.channel.send(embed=discord.Embed(color=0xA1E215).set_footer(text='А теперь введите ссылку на изображение / gif-анимацию..', icon_url=icons['using']))
                                _msg = await self.wait_for('message', check=check)

                                _msg_content = _msg.content.replace('<', '').replace('>', '')

                                if not _msg_content.startswith('http://') and not _msg_content.startswith('https://'):
                                    return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Требуется ссылка, начинающаяся с `http://` или `https://`!', icon_url=icons['error']))

                                _local['banner'] = _msg_content

                                if Data.card.upload(__user, _local): return await _msg.add_reaction(react['suc'])
                                else: return await _msg.add_reaction(react['err'])

                    return await self.channel.send(embed=discord.Embed(color=0xfA0000).set_footer(text='Введено некорректное имя пользователя.', icon_url=icons['error']))
                else:
                    c = discord.Embed(color=0xD587F2, title=data['status'], description=f"```{data['description']}```")
                    if data['status']: c.set_author(name=f'Карточка {_user}', icon_url=_user.avatar_url)
                    else: c.set_author(name=_user.name, icon_url=_user.avatar_url)
                    if data['vk']: c.add_field(name='ВКонтакте:', value=data['vk'], inline=False)
                    if data['google']: c.add_field(name='Google:', value=data['google'], inline=False)
                    if data['facebook']: c.add_field(name='Facebook:', value=data['facebook'], inline=False)
                    if data['twitter']: c.add_field(name='Twitter:', value=data['twitter'], inline=False)
                    if data['instagram']: c.add_field(name='Instagram:', value=data['instagram'], inline=False)
                    c.set_footer(text=f'{p}card [@пользователь] | {p}card set', icon_url=icons['using'])
                    c.set_thumbnail(url=_user.avatar_url)
                    if data['banner']: c.set_image(url=data['banner'])
                    return await self.channel.send(embed=c)


        if self.content.startswith(f'{p}avatar'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}avatar':
                return False
            try: arg[1]
            except:
                a = discord.Embed(color=0xfA0000, title=f'Аватарка {self.author}')
                a.set_image(url=self.author.avatar_url_as(static_format='png', size=1024))
                a.set_footer(text=f'{p}avatar [@пользователь]', icon_url=icons['using'])
                return await self.channel.send(embed=a)
            else:
                _user = Data.member.get(arg[1], self.guild)
                if _user is None:
                    return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Некорректно введен никнейм.', icon_url=icons['error']))
                if _user.avatar_url is None or _user.avatar_url == '' or _user.avatar_url == ' ':
                    a = discord.Embed(color=0xfA0000, title=f'Аватарка {_user}')
                    a.set_image(url=_user.default_avatar_url)
                    a.set_footer(text=f'{p}avatar [@пользователь]', icon_url=icons['using'])
                    return await self.channel.send(embed=a)
                a = discord.Embed(color=0xfA0000, title=f'Аватарка {_user}')
                a.set_image(url=_user.avatar_url_as(static_format='png', size=1024))
                a.set_footer(text=f'{p}avatar [@пользователь]', icon_url=icons['using'])
                return await self.channel.send(embed=a)


        if self.content.startswith(f'{p}restart'):
            '''On heroku "exit(0)" will restart bot'''

            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}restart':
                return False

            if self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))

            await self.channel.send(embed=discord.Embed(color=0xff0033).set_footer(icon_url='http://www.palazzorealemilano.it/wps/CustomWfActions/images/loadingImage.gif', text='Перезапускаемся...'))
            return exit(0)



        if self.content.startswith(f'{p}msg'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}msg':
                return False

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xD587F2).set_footer(text=f'{p}msg [сообщение]', icon_url=icons['using']))
            else:
                try:
                    await self.message.delete()
                except discord.errors.Forbidden:
                    pass
                return await self.channel.send(' '.join(arg[1:]) + ' (c) ' + self.author.name)


        if self.content.startswith(f'{p}say'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}say':
                return False

            if not self.permissions.manage_messages and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xD587F2).set_footer(text=f'{p}say [сообщение]', icon_url=icons['using']))
            else:
                try:
                    await self.message.delete()
                except discord.errors.Forbidden:
                    pass
                return await self.channel.send(' '.join(arg[1:]))


        if self.content.startswith(f'{p}warn'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}warn':
                return False

            return False # временно отключено

            if not self.permissions.ban_members and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.ban_members: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xD587F2).set_footer(text=f'{p}warn [@пользователь] [причина]', icon_url=icons['using']))

            try: _r = ' '.join(arg[2:])
            except: _r = 'отсутствует'

            _user = Data.member.get(arg[1], self.guild)
            _data = Data.member.load(_user, self.guild)

            _data['warn_count'] += 1

            try: Data.member.upload(_user, self.guild, _data)
            except Exception as e:
                await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'Не удалось:\n{e}', icon_url=icons['error']))
            else:
                await self.channel.send(embed=discord.Embed(color=0x00ff00, description=f'{self.author} выдал предупреждение {_user}.\nПричина: {_r}.\nПредупреждений всего: {_data["warn_count"]}').set_footer(text=f'{p}warn [@пользователь] [причина]', icon_url=icons['using']))
            if _data['warn_count'] >= 10:
                try: await _user.kick(reason='Набрал(а) слишком много предупреждений.')
                except: return False
                else: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{_user} кикнут за превышение количества предупреждений.', icon_url=icons['error']))
            else:
                return None


        if self.content.startswith(f'{p}unwarn'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}unwarn':
                return False

            return False # временно отключено

            if not self.permissions.ban_members and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.ban_members: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xD587F2).set_footer(text=f'{p}unwarn [@пользователь]', icon_url=icons['using']))

            _user = Data.member.get(arg[1], self.guild)
            _data = Data.member.load(_user, self.guild)

            if _data['warn_count'] <= 0:
                return await self.channel.send(embed=discord.Embed(color=0x00ff00, description=f'{self.author.mention} снял с {_user.mention} 0 предупреждений, \nпотому-что у {_user.mention} они и так отсутствуют.').set_footer(text=f'{p}unwarn [@пользователь]', icon_url=icons['using']))

            _data['warn_count'] -= 1

            try: Data.member.upload(_user, self.guild, _data)
            except Exception as e:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'Не удалось:\n{e}', icon_url=icons['error']))
            else:
                return await self.channel.send(embed=discord.Embed(color=0x00ff00, description=f'{self.author.mention} снял с {_user.mention} 1 предупреждение.').set_footer(text=f'{p}unwarn [@пользователь]', icon_url=icons['using']))


        if self.content.startswith(f'{p}kick'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}kick':
                return False

            if not self.permissions.ban_members and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.ban_members: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))
            
            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xD587F2).set_footer(text=f'{p}kick [@пользователь] [причина]', icon_url=icons['using']))
            
            try: _r = ' '.join(arg[2:])
            except: _r = 'отсутствует'

            try:
                _user = Data.member.get(arg[1], self.guild)

                await _user.kick(reason=_r)
                return await self.channel.send(embed=discord.Embed(color=0x00ff00, description=f'Пользователь {_user} был кикнут.\nПричина: {_r}.').set_footer(text=f'{p}kick [@пользователь] [причина]', icon_url=icons['using']))
            except Exception as e:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'Возникла ошибка: {e}', icon_url=icons['error']))


        if self.content.startswith(f'{p}myname'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}myname':
                return False

            #if not self.permissions.manage_nicknames and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.manage_nicknames: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xD587F2).set_footer(text=f'{p}myname [новый никнейм]]', icon_url=icons['using']))

            try: await self.author.edit(nick=' '.join(arg[1:]))
            except discord.errors.Forbidden:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))
            except Exception as e:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'Неизвестная ошибка, свяжитесь с разработчиком для решения.\n{e}', icon_url=icons['error']))
            else: return await self.message.add_reaction(react['suc'])


        if self.content.startswith(f'{p}status'):
            arg = self.content.split(' ')
            if arg[0] != f'{p}status':
                return False

            if not self.permissions.manage_guild and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))

            time_in_seconds = time.time() - self.time_start

            time_in_minutes = round(time_in_seconds / 60)
            time_in_hours = round(time_in_minutes / 60)

            if time_in_minutes >= 1:
                _time_value = f'{time_in_minutes} минут.'
            if time_in_hours >= 1:
                _time_value = f'{time_in_hours} часов.'
            else:
                _time_value = f'{round(time_in_seconds)} секунд.'

            _status = f'''
Платформа: {platform.system()};
Имя ОС: {os.name};
Оперативная память (всего): {psutil.virtual_memory().total} Б;
Оперативная память (свободно): {psutil.virtual_memory().free} Б;
Загрузка оперативной памяти: {psutil.virtual_memory().percent}%;
Загрузка ЦП: {psutil.cpu_percent()}%;
Загрузка ЦП (система): {psutil.cpu_times_percent().system}%
Кол-во ядер/потоков ЦП: {psutil.cpu_count()};

С момента запуска прошло {_time_value}
'''

            return await self.channel.send(embed=discord.Embed(title='Статистика:', description=_status).set_footer(text=f'{p}status', icon_url=icons['using']))


        if self.content.startswith(f'{p}config'):

            return False # Временно команда отключена.

            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}config':
                return False

            if not self.permissions.manage_guild and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{p}config [параметр (help)] [значение]', icon_url=icons['using']))

            _author = self.author
            data = Data.config.load(self.guild)

            def check(m):
                print(f'{m.author} - {_author}')
                if m.author.id == _author.id:
                    return True
                return False

            if not arg[1] == 'help':
                if arg[1] == 'prefix':

                    _msg = await self.wait_for('message', check=check)

                    data['cmd-prefix'] = _msg.content

                    if Data.config.upload(self.guild, data): return await _msg.add_reaction(react['suc'])
                    else: return await _msg.add_reaction(react['err'])
                if arg[1] == 'max-warns':

                    _msg = await self.wait_for('message', check=check)

                    data['max-warns'] = _msg.content

                    if Data.config.upload(self.guild, data): return await _msg.add_reaction(react['suc'])
                    else: return await _msg.add_reaction(react['err'])
                if arg[1] == 'mute-role':

                    _msg = await self.wait_for('message', check=check)

                    data['mute-role'] = _msg.content

                    if Data.config.upload(self.guild, data): return await _msg.add_reaction(react['suc'])
                    else: return await _msg.add_reaction(react['err'])

                if arg[1] == 'admin':

                    try: arg[2]
                    except: return await self.channel.send(embed=discord.Embed(color=0xff0000, description=f'{p}config admin add [@пользователь]\n{p}config admin remove [@пользователь]'))

                    if arg[2] == 'add':

                        await self.channel.send('Теперь введите никнейм или @упомяните требуемого пользователя.')

                        _msg = await self.wait_for('message', check=check)

                        print(_msg.content)

                        _username = Data.member.get(_msg.content, self.guild)

                        await self.channel.send(f'Введено: {_msg.content}\nПолучен discord.Member пользователя {_username}\n\nРам, вали в osu! если выше `None`.')

                        if _username.id in data['admins']:
                            return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Данный пользователь уже пристствует в списке Администраторов.', icon_url=icons['error']))

                        data['admins'].append(_msg.id)

                        if Data.config.upload(self.guild, data): return await _msg.add_reaction(react['suc'])
                        else: return await _msg.add_reaction(react['err'])

                    if arg[2] == 'remove':

                        await self.channel.send('Теперь введите никнейм или @упомяните требуемого пользователя.')

                        _msg = await self.wait_for('message', check=check)

                        _username = Data.member.get(_msg.content, self.guild)

                        try: data['admins'].remove(_username.id)
                        except ValueError: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Данный пользователь отсутствует в списке Администраторов.', icon_url=icons['error']))

                        if Data.config.upload(self.guild, data): return await _msg.add_reaction(react['suc'])
                        else: return await _msg.add_reaction(react['err'])




            else:

                # TODO: config

                #message = await self.channel.send(embed=discord.Embed(color=0x42E989, title='Параметры конфигурации:', description='Используйте реакции под\nэтим сообщением для\nпросмотра списка параметров.'))

                #menu = {'1⃣': '01','2⃣': '02'}
                pages = {
                    '01': discord.Embed(color=0x42E989, title='Параметры конфигурации:'),
                    #'02': discord.Embed(color=0x42E989, title='Параметры конфигурации:')
                }

                pages['01'].add_field(name='prefix', value='Устанавливает префикс для команд на этом сервере.')
                pages['01'].add_field(name='max-warns', value='Устанавливает макс.кол-во варнов на этом сервере.')
                pages['01'].add_field(name='admin', value='Добавить/удалить Администратора бота на этом сервере.')

                message = await self.channel.send(embed=pages['01'])

                async def __menu_controller(current, _buttons):
                    for react in _buttons:
                        await current.add_reaction(react)

                    def check(r, u):
                        if not current:
                            return False
                        elif str(r) not in _buttons.keys():
                            return False
                        elif u.id == client.user.id or r.message.id != current.id:
                            return False
                        return True

                    while current:
                        react, user = await client.wait_for('reaction_add', check=check)
                        try:
                            control = _buttons.get(str(react))
                        except:
                            control = None

                        if control == '01':
                                await current.edit(embed=pages['01'])
                        if control == '02':
                                await current.edit(embed=pages['02'])

                        try:
                            await current.remove_reaction(react, user)
                        except discord.HTTPException:
                            pass

                #client.loop.create_task(__menu_controller(message, menu))


        if self.content.startswith(f'{p}roleusers'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}roleusers':
                return False

            try: arg[1]
            except: 
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{p}roleusers [имя роли]', icon_url=icons['using']))

            _rolename = ' '.join(arg[1:])

            _role = discord.utils.get(self.guild.roles, name=_rolename)
            if _role is None:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'Мне не удалось найти роль "{_rolename}..."', icon_url=icons['error']))

            _members_with_role = []
            for member in self.guild.members:
                if _role in member.roles:
                    _members_with_role.append(member.name)

            if len(_members_with_role) >= 20:
                _members_with_role = len(_members_with_role)

                return await self.channel.send(embed=discord.Embed(color=0x259EF2,
                    title=f'Кол-во пользователей с ролью "{_rolename}": {_members_with_role}',
                    ).set_footer(text=f'{p}roleusers [имя роли]', icon_url=icons['using']))

            return await self.channel.send(embed=discord.Embed(color=0x259EF2,
                title=f'Пользователи с ролью "{_rolename}":',
                description='\n'.join(_members_with_role)
                ).set_footer(text=f'{p}roleusers [имя роли]', icon_url=icons['using']))


        if self.content.startswith(f'{p}mutethere'):
            return False # Disabled

            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}mutethere':
                return False

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{p}mutethere [@пользователь]', icon_url=icons['using']))

            if not self.permissions.manage_roles and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.manage_roles: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))

            target = Data.member.get(arg[1], self.guild)

            try:
                await self.channel.set_permissions(target, read_messages=True, send_messages=False)
            except discord.errors.InvalidArgument:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Не удалось выполнить команду.', icon_url=icons['error']))
            except discord.errors.Forbidden:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня нет прав.', icon_url=icons['error']))
            else:
                return await self.channel.send(embed=discord.Embed(color=0xff0000, description=f'Пользователь {target.mention} приглушен.').set_footer(text=f'{p}mutethere [@пользователь]', icon_url=icons['using']))


        if self.content.startswith(f'{p}mute'):
            return False # Disabled

            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}mute':
                return False

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{p}mute [@пользователь]', icon_url=icons['using']))

            if not self.permissions.manage_roles and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.manage_roles: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))


            target_member = discord.utils.get(self.guild.members, mention=arg[1])

            if target_member is None:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{self.author.mention}, указанный пользователь не найден.', icon_url=icons['error']))

            target = await self.guild.create_role(name='NaomiMute')

            try:
                for textchannel in self.guild.text_channels:
                    await textchannel.set_permissions(target, read_messages=False, send_messages=False)

                await target_member.add_roles(target)
            except discord.errors.InvalidArgument:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='Не удалось выполнить команду.', icon_url=icons['error']))
            except discord.errors.Forbidden:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня нет прав.', icon_url=icons['error']))
            else:
                return await self.channel.send(embed=discord.Embed(color=0xff0000, description=f'Пользователь {target_member.mention} приглушен.').set_footer(text=f'{p}mute [@пользователь]', icon_url=icons['using']))


        if self.content.startswith(f'{p}unmute'):
            return False # Disabled

            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}unmute':
                return False

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{p}unmute [@пользователь]', icon_url=icons['using']))

            if not self.permissions.manage_roles and self.author.id not in self._bot['admins']: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У вас недостаточно прав.', icon_url=icons['error']))
            if not self.bot_permissions.manage_roles: return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня недостаточно прав.', icon_url=icons['error']))

            
            target = discord.utils.get(self.guild.members, mention=arg[1])

            if target is None:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{self.author.mention}, указанный пользователь не найден.', icon_url=icons['error']))

            mute_role = discord.utils.get(self.guild.roles, name='NaomiMute')

            if mute_role is None:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{self.author.mention}, на этом сервере еще никого не заглушили.', icon_url=icons['error']))

            try:
                await target.remove_roles(mute_role)

            except discord.errors.Forbidden:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text='У меня нет прав.', icon_url=icons['error']))
            else:
                return await self.channel.send(embed=discord.Embed(color=0xff0000, description=f'Пользователь {target.mention} больше не приглушен.').set_footer(text=f'{p}unmute [@пользователь]', icon_url=icons['using']))


        if self.content.startswith(f'{p}#exception'):
            if self.author.id != 297421244402368522:
                return False

            return 5 / 0 # Тупо делим на ноль


        if self.content.startswith(f'{p}hostinfo'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}hostinfo':
                return False

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{p}hostinfo [домен]', icon_url=icons['using']))

            whois_info = whois.whois(arg[1])

            hostinfo = discord.Embed(color=0xff0000, title=f'WHOIS-информация для {arg[1]}')

            try:
                expdata = str(whois_info["expiration_date"][0])
            except:
                expdata = str(whois_info["expiration_date"])

            try:
                crtdata = str(whois_info["creation_date"][0])
            except:
                crtdata = str(whois_info["creation_date"])

            try:
                domain = whois_info["domain_name"][0]
            except:
                domain = whois_info["domain_name"]

            hostinfo.add_field(name="Домен:", value=f'{domain}', inline=True)
            hostinfo.add_field(name="Регистратор:", value=f'{whois_info["registrar"]}', inline=True)
            hostinfo.add_field(name="Whois-сервер:", value=f'{whois_info["whois_server"]}', inline=True)
            hostinfo.add_field(name="Дата окончания:", value=f'{expdata}', inline=True)
            hostinfo.add_field(name="Дата создания:", value=f'{crtdata}', inline=True)
            hostinfo.add_field(name="Регион:", value=f'{whois_info["country"]}', inline=True)

            hostinfo.set_footer(text=f'{p}hostinfo [домен]', icon_url=icons['using'])
            return await self.channel.send(embed=hostinfo)



        if self.content.startswith(f'{p}talk'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}talk':
                return False

            try: arg[1]
            except:
                return await self.channel.send(embed=discord.Embed(color=0xff0000).set_footer(text=f'{p}talk [сообщение] | Dialogflow', icon_url=icons['using']))
            
            ai = apiai.ApiAI(os.getenv('TALK_SERVICE_TOKEN'))

            request = ai.text_request()
            request.lang = 'ru'
            request.session_id = os.getenv('TALK_SERVICE_SESSION_ID')
            request.query = ' '.join(arg[1:])
            responseJson = json.loads(request.getresponse().read().decode('utf-8'))
            response = responseJson['result']['fulfillment']['speech']

            if response:
                return await self.channel.send(response)
            else:
                no_answer = choice(['Не знаю, как ответить...',
                                    'Полагаю, у меня нет ответа.',
                                    '(Как же ответить, как же ответить...)',
                                    'Извиняюсь, но я не знаю, как ответить...'])
                return await self.channel.send(no_answer)



        if self.content.startswith(f'{p}userinfo'):
            self.content = self.content.replace('  ', ' ')
            arg = self.content.split(' ')
            if arg[0] != f'{p}userinfo':
                return False

            try: arg[1]
            except:
                arg.append(message.author.mention)

            target_m = discord.utils.get(self.guild.members, mention=arg[1])

            target_status = str(target_m.status).replace('online', 'В сети').replace('idle', 'Не активен').replace('dnd', 'Не беспокоить').replace('offline', 'Не в сети')

            if target_m.nick is None:
                _title = '%s - %s' % (target_m.name, target_status)
            else:
                _title = '%s (%s) - %s' % (target_m.nick, target_m.name, target_status)

            _info = discord.Embed(color=0x06A9ED, title=_title, inline=True)
            _info.add_field(name='Присоединился к серверу:', value=target_m.joined_at, inline=True)
            _info.add_field(name='Аккаунт создан:', value=target_m.created_at, inline=True)
            _info.add_field(name='Является-ли ботом:', value=str(target_m.bot).replace('True', 'Да').replace('False', 'Нет'), inline=True)
            _info.add_field(name='Высшая роль:', value=target_m.top_role, inline=True)
            _info.add_field(name='Цвет никнейма (hex):', value=target_m.color, inline=True)
            _info.add_field(name='Анимирована-ли аватарка:', value=str(target_m.is_avatar_animated()).replace('True', 'Да').replace('False', 'Нет'), inline=True)
            
            _info.set_thumbnail(url=target_m.avatar_url)

            _info.set_footer(text=f'{p}userinfo [@пользователь]', icon_url=icons['using'])

            return await message.channel.send(embed=_info)


if __name__ == '__main__':
    client = Bot()
    client.run(os.getenv('TOKEN'), reconnect=True)