"""
MIT License

Copyright (c) 2018 William Lomas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
from discord.ext import commands
import json
import asyncio
import async_timeout
import os
import datetime
from utils.chat_formatting import pagify, box

prefixes = ['<@442185653992816640> ', '<@!442185653992816640> ', 'c4-', 'C4-']
client = commands.Bot(command_prefix=prefixes)
client.remove_command('help')
sessions = []
rankslist = {
    "Learner": -1,
    "Average": 151,
    "Pro": 401,
    "Master": 751,
    "God": 1501,
    "Legend": 2501
}
activegames = 0

def get_leaderboard():
    fp = open('data/userstats.data')
    content = json.load(fp)
    pointsdict = {}
    for user, value in content.items():
        points = ((value['wins']*10)+(value['losses']*-5)+(value['ties']*3))
        if points < 0:
            points = 0
        pointsdict[user] = points
    sortedpoints = reversed(sorted(pointsdict, key=pointsdict.get))
    users = []
    for user in sortedpoints:
        users.append(user) 
    return users

def get_rank(userid):
    try:
        if str(userid) == get_leaderboard()[0]:
            return 'Dominator'
        fp = open('data/userstats.data')
        content = json.load(fp)
        wins = content[str(userid)]['wins']
        losses = content[str(userid)]['losses']
        draws = content[str(userid)]['ties']
        points = ((wins*10)+(losses*-5)+(draws*3))
        if (points / rankslist['Legend']) >= 1:
            return 'Legend'
        elif (points / rankslist['God']) >= 1:
            return 'God'
        elif (points / rankslist['Master']) >= 1:
            return 'Master'
        elif (points / rankslist['Pro']) >= 1:
            return 'Pro'
        elif (points / rankslist['Average']) >= 1:
            return 'Average'
        else:
            return 'Learner'
    except: return 'Learner'

async def update_server_roles(userid):
    server = client.get_guild(442186373089198080)
    user = discord.utils.get(server.members, id=userid)
    if user is None:
        return
    roles = [discord.utils.get(server.roles, id=442626469597020192), discord.utils.get(server.roles, id=442626468154048514), discord.utils.get(server.roles, id=442626465767489537), discord.utils.get(server.roles, id=442626463380799488), discord.utils.get(server.roles, id=442626453931032577), discord.utils.get(server.roles, id=442626446742257675), discord.utils.get(server.roles, id=442626725604753408)]
    rank = get_rank(userid)
    if rank == 'Learner':
        rank = roles[0]
    elif rank == 'Average':
        rank = roles[1]
    elif rank == 'Pro':
        rank = roles[2]
    elif rank == 'Master':
        rank = roles[3]
    elif rank == 'God':
        rank = roles[4]
    elif rank == 'Legend':
        rank = roles[5]
    elif rank == 'Dominator':
        try:
            await update_server_roles(roles[6].members[0].id)
        except: pass
        rank = roles[6]
    await user.remove_roles(roles[0], roles[1], roles[2], roles[3], roles[4], roles[5], roles[6])
    await user.add_roles(rank)

def check_blacklist(user):
    userid = user.id
    fp = open('data/blacklist.data')
    content = json.load(fp)
    try:
        if user.bot or content[str(userid)] == 1:
            return True
        return False
    except KeyError:
        return False

async def status_rotation():
    while True:
        await client.change_presence(activity=discord.Game(name="Connect 4 | c4-help"))
        await asyncio.sleep(30)
        await client.change_presence(activity=discord.Activity(name="your moves 👀 | c4-help", type=discord.ActivityType.watching))
        await asyncio.sleep(30)

def count_active_games():
    c = 0
    for session in sessions:
        if session.active:
            c += 1
    return c

def display_time(seconds, granularity=2):
    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1)
    )
    result = []
    for name, count in intervals:
        value = round(seconds // count)
        if value:
            seconds -= round(value * count)
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

class Grid:
    def __init__(self, session):
        self.a1 = ':black_circle:'
        self.a2 = ':black_circle:'
        self.a3 = ':black_circle:'
        self.a4 = ':black_circle:'
        self.a5 = ':black_circle:'
        self.a6 = ':black_circle:'
        self.b1 = ':black_circle:'
        self.b2 = ':black_circle:'
        self.b3 = ':black_circle:'
        self.b4 = ':black_circle:'
        self.b5 = ':black_circle:'
        self.b6 = ':black_circle:'
        self.c1 = ':black_circle:'
        self.c2 = ':black_circle:'
        self.c3 = ':black_circle:'
        self.c4 = ':black_circle:'
        self.c5 = ':black_circle:'
        self.c6 = ':black_circle:'
        self.d1 = ':black_circle:'
        self.d2 = ':black_circle:'
        self.d3 = ':black_circle:'
        self.d4 = ':black_circle:'
        self.d5 = ':black_circle:'
        self.d6 = ':black_circle:'
        self.e1 = ':black_circle:'
        self.e2 = ':black_circle:'
        self.e3 = ':black_circle:'
        self.e4 = ':black_circle:'
        self.e5 = ':black_circle:'
        self.e6 = ':black_circle:'
        self.f1 = ':black_circle:'
        self.f2 = ':black_circle:'
        self.f3 = ':black_circle:'
        self.f4 = ':black_circle:'
        self.f5 = ':black_circle:'
        self.f6 = ':black_circle:'
        self.g1 = ':black_circle:'
        self.g2 = ':black_circle:'
        self.g3 = ':black_circle:'
        self.g4 = ':black_circle:'
        self.g5 = ':black_circle:'
        self.g6 = ':black_circle:'
        self.session = session
        self.message = None

    async def display(self, mode=None):
        if self.message is not None:
            try:
                await self.message.delete() # There's a possibility of the old message being deleted, this tryexcept fixes that.
            except: pass
        letters = ['\U0001f1e6', '\U0001f1e7', '\U0001f1e8', '\U0001f1e9', '\U0001f1ea', '\U0001f1eb', '\U0001f1ec']
        embed = discord.Embed(color=0x00bdff, description=':red_circle: = {}\n:large_blue_circle: = {}'.format(self.session.player1, self.session.player2))
        embed.title = "Grid"
        if mode is None:
            embed.set_footer(text='It\'s currently {}\'s turn.'.format(self.session.turnholder.name))
        embed.add_field(name=":regional_indicator_a:​:regional_indicator_b:​:regional_indicator_c:​:regional_indicator_d:​:regional_indicator_e:​:regional_indicator_f:​:regional_indicator_g:", value="{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}".format(self.a1, self.b1, self.c1, self.d1, self.e1, self.f1, self.g1, self.a2, self.b2, self.c2, self.d2, self.e2, self.f2, self.g2, self.a3, self.b3, self.c3, self.d3, self.e3, self.f3, self.g3, self.a4, self.b4, self.c4, self.d4, self.e4, self.f4, self.g4, self.a5, self.b5, self.c5, self.d5, self.e5, self.f5, self.g5, self.a6, self.b6, self.c6, self.d6, self.e6, self.f6, self.g6), inline=False)
        try:
            self.message = await self.session.channel.send(embed=embed)
            if mode == '-nr':
                return
            for letter in letters:
                await self.message.add_reaction(letter)
            await self.session.move()
        except Exception as e:
            await self.session.channel.send(e)
            await self.session.channel.send('I need the Embed Links, and Add Reactions permission to show the grid. :no_entry:')

class Connect4Session:
    def __init__(self, channel, p1, p2=None):
        self.channel = channel
        self.active = True
        self.player1 = p1
        self.player2 = p2
        self.turnholder = p1
        self.nonturnholder = p2
        self.gameid = None
        self.timestamp = None
        self.grid = Grid(self)
        sessions.append(self)

    def save_data(self, winner=None):
        global activegames
        if winner is not None:
            winner = winner.id
        data = {"player1": self.player1.id, "player2": self.player2.id, "winner": winner, "channel": self.channel.id, "timestamp": str(self.timestamp), "grid": {"a1": self.grid.a1, "a2": self.grid.a2, "a3": self.grid.a3, "a4": self.grid.a4, "a5": self.grid.a5, "a6": self.grid.a6, "b1": self.grid.b1, "b2": self.grid.b2, "b3": self.grid.b3, "b4": self.grid.b4, "b5": self.grid.b5, "b6": self.grid.b6, "c1": self.grid.c1, "c2": self.grid.c2, "c3": self.grid.c3, "c4": self.grid.c4, "c5": self.grid.c5, "c6": self.grid.c6, "d1": self.grid.d1, "d2": self.grid.d2, "d3": self.grid.d3, "d4": self.grid.d4, "d5": self.grid.d5, "d6": self.grid.d6, "e1": self.grid.e1, "e2": self.grid.e2, "e3": self.grid.e3, "e4": self.grid.e4, "e5": self.grid.e5, "e6": self.grid.e6, "f1": self.grid.f1, "f2": self.grid.f2, "f3": self.grid.f3, "f4": self.grid.f4, "f5": self.grid.f5, "f6": self.grid.f6, "g1": self.grid.g1, "g2": self.grid.g2, "g3": self.grid.g3, "g4": self.grid.g4, "g5": self.grid.g5, "g6": self.grid.g6}}
        fp = open('data/games.data', 'r+')
        content = json.load(fp)
        content[str(self.gameid)] = data
        fp.seek(0)
        json.dump(content, fp)
        fp.truncate()
        activegames = activegames - 1

    def check_win(self):
        '''Sorry, mom'''
        if self.grid.a6 == self.grid.b6 == self.grid.c6 == self.grid.d6 != ":black_circle:" or self.grid.b6 == self.grid.c6 == self.grid.d6 == self.grid.e6 != ":black_circle:" or self.grid.c6 == self.grid.d6 == self.grid.e6 == self.grid.f6 != ":black_circle:" or self.grid.d6 == self.grid.e6 == self.grid.f6 == self.grid.g6 != ":black_circle:" or self.grid.a5 == self.grid.b5 == self.grid.c5 == self.grid.d5 != ":black_circle:" or self.grid.b5 == self.grid.c5 == self.grid.d5 == self.grid.e5 != ":black_circle:" or self.grid.c5 == self.grid.d5 == self.grid.e5 == self.grid.f5 != ":black_circle:" or self.grid.d5 == self.grid.e5 == self.grid.f5 == self.grid.g5 != ":black_circle:" or self.grid.a4 == self.grid.b4 == self.grid.c4 == self.grid.d4 != ":black_circle:" or self.grid.b4 == self.grid.c4 == self.grid.d4 == self.grid.e4 != ":black_circle:" or self.grid.c4 == self.grid.d4 == self.grid.e4 == self.grid.f4 != ":black_circle:" or self.grid.d4 == self.grid.e4 == self.grid.f4 == self.grid.g4 != ":black_circle:" or self.grid.a3 == self.grid.b3 == self.grid.c3 == self.grid.d3 != ":black_circle:" or self.grid.b3 == self.grid.c3 == self.grid.d3 == self.grid.e3 != ":black_circle:" or self.grid.c3 == self.grid.d3 == self.grid.e3 == self.grid.f3 != ":black_circle:" or self.grid.d3 == self.grid.e3 == self.grid.f3 == self.grid.g3 != ":black_circle:" or self.grid.a2 == self.grid.b2 == self.grid.c2 == self.grid.d2 != ":black_circle:" or self.grid.b2 == self.grid.c2 == self.grid.d2 == self.grid.e2 != ":black_circle:" or self.grid.c2 == self.grid.d2 == self.grid.e2 == self.grid.f2 != ":black_circle:" or self.grid.d2 == self.grid.e2 == self.grid.f2 == self.grid.g2 != ":black_circle:" or self.grid.a1 == self.grid.b1 == self.grid.c1 == self.grid.d1 != ":black_circle:" or self.grid.b1 == self.grid.c1 == self.grid.d1 == self.grid.e1 != ":black_circle:" or self.grid.c1 == self.grid.d1 == self.grid.e1 == self.grid.f1 != ":black_circle:" or self.grid.d1 == self.grid.e1 == self.grid.f1 == self.grid.g1 != ":black_circle:":
            return True
        elif self.grid.a6 == self.grid.a5 == self.grid.a4 == self.grid.a3 != ":black_circle:" or self.grid.a5 == self.grid.a4 == self.grid.a3 == self.grid.a2 != ":black_circle:" or self.grid.a4 == self.grid.a3 == self.grid.a2 == self.grid.a1 != ":black_circle:" or self.grid.b6 == self.grid.b5 == self.grid.b4 == self.grid.b3 != ":black_circle:" or self.grid.b5 == self.grid.b4 == self.grid.b3 == self.grid.b2 != ":black_circle:" or self.grid.b4 == self.grid.b3 == self.grid.b2 == self.grid.b1 != ":black_circle:" or self.grid.c6 == self.grid.c5 == self.grid.c4 == self.grid.c3 != ":black_circle:" or self.grid.c5 == self.grid.c4 == self.grid.c3 == self.grid.c2 != ":black_circle:" or self.grid.c4 == self.grid.c3 == self.grid.c2 == self.grid.c1 != ":black_circle:" or self.grid.d6 == self.grid.d5 == self.grid.d4 == self.grid.d3 != ":black_circle:" or self.grid.d5 == self.grid.d4 == self.grid.d3 == self.grid.d2 != ":black_circle:" or self.grid.d4 == self.grid.d3 == self.grid.d2 == self.grid.d1 != ":black_circle:" or self.grid.e6 == self.grid.e5 == self.grid.e4 == self.grid.e3 != ":black_circle:" or self.grid.e5 == self.grid.e4 == self.grid.e3 == self.grid.e2 != ":black_circle:" or self.grid.e4 == self.grid.e3 == self.grid.e2 == self.grid.e1 != ":black_circle:" or self.grid.f6 == self.grid.f5 == self.grid.f4 == self.grid.f3 != ":black_circle:" or self.grid.f5 == self.grid.f4 == self.grid.f3 == self.grid.f2 != ":black_circle:" or self.grid.f4 == self.grid.f3 == self.grid.f2 == self.grid.f1 != ":black_circle:" or self.grid.g6 == self.grid.g5 == self.grid.g4 == self.grid.g3 != ":black_circle:" or self.grid.g5 == self.grid.g4 == self.grid.g3 == self.grid.g2 != ":black_circle:" or self.grid.g4 == self.grid.g3 == self.grid.g2 == self.grid.g1 != ":black_circle:":
            return True
        elif self.grid.a4 == self.grid.b3 == self.grid.c2 == self.grid.d1 != ":black_circle:" or self.grid.b4 == self.grid.c3 == self.grid.d2 == self.grid.e1 != ":black_circle:" or self.grid.c4 == self.grid.d3 == self.grid.e2 == self.grid.f1 != ":black_circle:" or self.grid.d4 == self.grid.e3 == self.grid.f2 == self.grid.g1 != ":black_circle:" or self.grid.g4 == self.grid.f3 == self.grid.e2 == self.grid.d1 != ":black_circle:" or self.grid.f4 == self.grid.e3 == self.grid.d2 == self.grid.c1 != ":black_circle:" or self.grid.e4 == self.grid.d3 == self.grid.c2 == self.grid.b1 != ":black_circle:" or self.grid.d4 == self.grid.c3 == self.grid.b2 == self.grid.a1 != ":black_circle:" or self.grid.a6 == self.grid.b5 == self.grid.c4 == self.grid.d3 != ":black_circle:" or self.grid.b6 == self.grid.c5 == self.grid.d4 == self.grid.e3 != ":black_circle:" or self.grid.c6 == self.grid.d5 == self.grid.e4 == self.grid.f3 != ":black_circle:" or self.grid.d6 == self.grid.e5 == self.grid.f4 == self.grid.g3 != ":black_circle:" or self.grid.g6 == self.grid.f5 == self.grid.e4 == self.grid.d3 != ":black_circle:" or self.grid.f6 == self.grid.e5 == self.grid.d4 == self.grid.c3 != ":black_circle:" or self.grid.e6 == self.grid.d5 == self.grid.c4 == self.grid.b3 != ":black_circle:" or self.grid.d6 == self.grid.c5 == self.grid.b4 == self.grid.a3 != ":black_circle:" or self.grid.a5 == self.grid.b4 == self.grid.c3 == self.grid.d2 != ":black_circle:" or self.grid.b5 == self.grid.c4 == self.grid.d3 == self.grid.e2 != ":black_circle:" or self.grid.c5 == self.grid.d4 == self.grid.e3 == self.grid.f2 != ":black_circle:" or self.grid.d5 == self.grid.e4 == self.grid.f3 == self.grid.g2 != ":black_circle:" or self.grid.g5 == self.grid.f4 == self.grid.e3 == self.grid.d2 != ":black_circle:" or self.grid.f5 == self.grid.e4 == self.grid.d3 == self.grid.c2 != ":black_circle:" or self.grid.e5 == self.grid.d4 == self.grid.c3 == self.grid.b2 != ":black_circle:" or self.grid.d5 == self.grid.c4 == self.grid.b3 == self.grid.a2 != ":black_circle:":
            return True
        else:
            return False

    async def finish_turn(self, mode, reaction):
        if mode == 1:
            embed = discord.Embed(color=0x00bdff, description=':red_circle: = {}\n:large_blue_circle: = {}'.format(self.player1, self.player2))
            embed.title = "Grid"
            embed.set_footer(text='It\'s currently {}\'s turn.'.format(self.turnholder.name))
            embed.add_field(name=":regional_indicator_a:​:regional_indicator_b:​:regional_indicator_c:​:regional_indicator_d:​:regional_indicator_e:​:regional_indicator_f:​:regional_indicator_g:", value="{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}".format(self.grid.a1, self.grid.b1, self.grid.c1, self.grid.d1, self.grid.e1, self.grid.f1, self.grid.g1, self.grid.a2, self.grid.b2, self.grid.c2, self.grid.d2, self.grid.e2, self.grid.f2, self.grid.g2, self.grid.a3, self.grid.b3, self.grid.c3, self.grid.d3, self.grid.e3, self.grid.f3, self.grid.g3, self.grid.a4, self.grid.b4, self.grid.c4, self.grid.d4, self.grid.e4, self.grid.f4, self.grid.g4, self.grid.a5, self.grid.b5, self.grid.c5, self.grid.d5, self.grid.e5, self.grid.f5, self.grid.g5, self.grid.a6, self.grid.b6, self.grid.c6, self.grid.d6, self.grid.e6, self.grid.f6, self.grid.g6), inline=False)
            if self.check_win():
                embed.set_footer(text=embed.Empty)
                await self.grid.message.edit(embed=embed)
                try:
                    await self.grid.message.clear_reactions()
                except:
                    pass
                return await self.end(self.nonturnholder)
            elif ':black_circle:' not in [self.grid.a1, self.grid.b1, self.grid.c1, self.grid.d1, self.grid.e1, self.grid.f1, self.grid.g1]:
                embed.set_footer(text=embed.Empty)
                await self.grid.message.edit(embed=embed)
                try:
                    await self.grid.message.clear_reactions()
                except:
                    pass
                return await self.end()
            await self.grid.message.edit(embed=embed)
            try:
                await self.grid.message.remove_reaction(reaction, self.nonturnholder)
            except:
                pass
            await self.move()
        else:
            try:
                await self.grid.message.remove_reaction(reaction, self.nonturnholder)
            except:
                pass
            await self.channel.send('{}, that column is full! :no_entry:'.format(self.nonturnholder.mention))
            if self.turnholder == self.player1:
                self.turnholder = self.nonturnholder
                self.nonturnholder = self.player1
            else:
                self.turnholder = self.nonturnholder
                self.nonturnholder = self.player2
            await self.move()

    async def move(self):
        gridmessage = self.grid.message
        letters = ['\U0001f1e6', '\U0001f1e7', '\U0001f1e8', '\U0001f1e9', '\U0001f1ea', '\U0001f1eb', '\U0001f1ec']
        def check(reaction, user):
            return user == self.turnholder and str(reaction.emoji) in letters and reaction.message.id == gridmessage.id
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except:
            if self.active and self.grid.message.id == gridmessage.id:
                await self.end(self.nonturnholder)
        else:
            if not self.active:
                return
            if self.turnholder == self.player1:
                tile = ':red_circle:'
                self.turnholder = self.player2
                self.nonturnholder = self.player1
            else:
                tile = ':large_blue_circle:'
                self.turnholder = self.player1
                self.nonturnholder = self.player2
            if str(reaction.emoji) == letters[0]:
                if self.grid.a6 == ':black_circle:':
                    self.grid.a6 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.a5 == ':black_circle:':
                    self.grid.a5 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.a4 == ':black_circle:':
                    self.grid.a4 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.a3 == ':black_circle:':
                    self.grid.a3 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.a2 == ':black_circle:':
                    self.grid.a2 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.a1 == ':black_circle:':
                    self.grid.a1 = tile
                    await self.finish_turn(1, reaction)
                else:
                    await self.finish_turn(0, reaction)
            elif str(reaction.emoji) == letters[1]:
                if self.grid.b6 == ':black_circle:':
                    self.grid.b6 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.b5 == ':black_circle:':
                    self.grid.b5 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.b4 == ':black_circle:':
                    self.grid.b4 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.b3 == ':black_circle:':
                    self.grid.b3 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.b2 == ':black_circle:':
                    self.grid.b2 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.b1 == ':black_circle:':
                    self.grid.b1 = tile
                    await self.finish_turn(1, reaction)
                else:
                    await self.finish_turn(0, reaction)
            elif str(reaction.emoji) == letters[2]:
                if self.grid.c6 == ':black_circle:':
                    self.grid.c6 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.c5 == ':black_circle:':
                    self.grid.c5 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.c4 == ':black_circle:':
                    self.grid.c4 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.c3 == ':black_circle:':
                    self.grid.c3 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.c2 == ':black_circle:':
                    self.grid.c2 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.c1 == ':black_circle:':
                    self.grid.c1 = tile
                    await self.finish_turn(1, reaction)
                else:
                    await self.finish_turn(0, reaction)
            elif str(reaction.emoji) == letters[3]:
                if self.grid.d6 == ':black_circle:':
                    self.grid.d6 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.d5 == ':black_circle:':
                    self.grid.d5 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.d4 == ':black_circle:':
                    self.grid.d4 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.d3 == ':black_circle:':
                    self.grid.d3 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.d2 == ':black_circle:':
                    self.grid.d2 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.d1 == ':black_circle:':
                    self.grid.d1 = tile
                    await self.finish_turn(1, reaction)
                else:
                    await self.finish_turn(0, reaction)
            elif str(reaction.emoji) == letters[4]:
                if self.grid.e6 == ':black_circle:':
                    self.grid.e6 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.e5 == ':black_circle:':
                    self.grid.e5 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.e4 == ':black_circle:':
                    self.grid.e4 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.e3 == ':black_circle:':
                    self.grid.e3 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.e2 == ':black_circle:':
                    self.grid.e2 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.e1 == ':black_circle:':
                    self.grid.e1 = tile
                    await self.finish_turn(1, reaction)
                else:
                    await self.finish_turn(0, reaction)
            elif str(reaction.emoji) == letters[5]:
                if self.grid.f6 == ':black_circle:':
                    self.grid.f6 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.f5 == ':black_circle:':
                    self.grid.f5 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.f4 == ':black_circle:':
                    self.grid.f4 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.f3 == ':black_circle:':
                    self.grid.f3 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.f2 == ':black_circle:':
                    self.grid.f2 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.f1 == ':black_circle:':
                    self.grid.f1 = tile
                    await self.finish_turn(1, reaction)
                else:
                    await self.finish_turn(0, reaction)
            elif str(reaction.emoji) == letters[6]:
                if self.grid.g6 == ':black_circle:':
                    self.grid.g6 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.g5 == ':black_circle:':
                    self.grid.g5 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.g4 == ':black_circle:':
                    self.grid.g4 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.g3 == ':black_circle:':
                    self.grid.g3 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.g2 == ':black_circle:':
                    self.grid.g2 = tile
                    await self.finish_turn(1, reaction)
                elif self.grid.g1 == ':black_circle:':
                    self.grid.g1 = tile
                    await self.finish_turn(1, reaction)
                else:
                    await self.finish_turn(0, reaction)

    async def end(self, winner=None):
        def storewindata(winner):
            with open('data/userstats.data', 'r+') as fp:
                content = json.load(fp)
                try:
                    content[str(winner.id)]['wins'] += 1
                except:
                    content[str(winner.id)] = {}
                    content[str(winner.id)]['wins'] = 1
                    content[str(winner.id)]['losses'] = 0
                    content[str(winner.id)]['ties'] = 0
                fp.seek(0)
                json.dump(content, fp)
                fp.truncate()

        def storelossdata(loser):
            with open('data/userstats.data', 'r+') as fp:
                content = json.load(fp)
                try:
                    content[str(loser.id)]['losses'] += 1
                except:
                    content[str(loser.id)] = {}
                    content[str(loser.id)]['losses'] = 1
                    content[str(loser.id)]['wins'] = 0
                    content[str(loser.id)]['ties'] = 0
                fp.seek(0)
                json.dump(content, fp)
                fp.truncate()

        def storetiedata(user):
            with open('data/userstats.data', 'r+') as fp:
                content = json.load(fp)
                try:
                    content[str(user.id)]['ties'] += 1
                except:
                    content[str(user.id)] = {}
                    content[str(user.id)]['ties'] = 1
                    content[str(user.id)]['wins'] = 0
                    content[str(user.id)]['losses'] = 0
                fp.seek(0)
                json.dump(content, fp)
                fp.truncate()

        self.active = False
        try:
            await self.grid.message.clear_reactions()
        except:
            pass
        try:
            embed = self.grid.message.embeds[0]
            embed.set_footer(text=embed.Empty)
        except:
            pass
        await self.grid.message.edit(embed=embed)
        embed = discord.Embed(color=0x00bdff, title='Connect 4', description='Match ending...')
        if winner is None:
            winner = None
            embed.add_field(name='Winner', value='Nobody (Draw)')
            storetiedata(self.player1)
            storetiedata(self.player2)
        elif winner == self.player1:
            embed.add_field(name='Winner', value='{} (:red_circle:)'.format(winner))
            embed.add_field(name='Loser', value='{} (:large_blue_circle:)'.format(self.player2))
            storewindata(winner)
            storelossdata(self.player2)
        else:
            embed.add_field(name='Winner', value='{} (:large_blue_circle:)'.format(winner))
            embed.add_field(name='Loser', value='{} (:red_circle:)'.format(self.player1))
            storewindata(winner)
            storelossdata(self.player1)
        embed.set_footer(text='You can check your Connect 4 stats using c4-stats.')
        embed.add_field(name='Enjoyed this minigame?', value='If so, please consider donating by [clicking here](https://patreon.com/bladebot) to help keep Connect 4 bot alive, and so we may continue further development.')
        await self.channel.send(embed=embed)
        self.timestamp = datetime.datetime.now()
        self.save_data(winner)
        await update_server_roles(self.player1.id)
        await update_server_roles(self.player2.id)

    async def start(self, ctx):
        self.gameid = get_game_id()
        embed = discord.Embed(color=0x00bdff, title='Connect 4', description='Match starting')
        embed.add_field(name='Players', value='{} (:red_circle:)\nvs.\n{} (:large_blue_circle:)'.format(self.player1, self.player2))
        embed.add_field(name='How to Play?', value='Basic Connect 4 rules.\nSimply react with the column you\'d like to place your tile under.\nIf you want the bot to send the grid again, run `c4-view`\nTo quit, use `c4-quit`\nYou have 60 seconds between each turn, be careful not to let it run out.')
        embed.add_field(name='Goodluck', value='May the best win!')
        embed.set_footer(text="The grid will appear in 10 seconds... | Game ID: {}".format(self.gameid))
        await self.channel.send(embed=embed)
        if not ctx.channel.permissions_for(ctx.me).manage_messages:
                await ctx.send(':warning: Heads up! I don\'t have manage messages permission, so you\'ll have to remove your reactions yourself.')
        await asyncio.sleep(10)
        if self.active:
            await self.grid.display()

def get_connect4_session(ctx):
    for session in sessions:
        if session.channel == ctx.channel and session.active is True:
            return session
        pass

def connect4_active(ctx):
    for session in sessions:
        if session.channel == ctx.channel and session.active is True:
            return True
    return False

def already_playing(user):
    for session in sessions:
        if session.player1 == user or session.player2 == user:
            if session.active:
                return True
    return False

def get_game_id():
    global activegames
    fp = open('data/games.data')
    content = json.load(fp)
    id = len(content) + 1 + activegames
    activegames += 1
    return id

@client.event
async def on_ready():
    client.loop.create_task(status_rotation())

@client.event
async def on_member_join(member):
    if member.guild.id != 442186373089198080:
        return
    await update_server_roles(member.id)

@client.command(aliases=['commands'])
async def help(ctx):
    user = ctx.author
    if check_blacklist(user):
        return
    embed = discord.Embed(color=0x3498db, title='Connect 4 Bot Help', description='The command list')
    embed.add_field(name='c4-help', value='View this menu.', inline=False)
    embed.add_field(name='c4-info', value='View info about Connect 4 Bot.', inline=False)
    embed.add_field(name='c4-invite', value='Invite Connect 4 Bot.', inline=False)
    embed.add_field(name='c4-ranks', value='View the list of ranks.', inline=False)
    embed.add_field(name='c4-report', value='Report a user for breaking a rule.', inline=False)
    embed.add_field(name='c4-play', value='Request for a game of Connect 4.', inline=False)
    embed.add_field(name='c4-view', value='Reload the grid.', inline=False)
    embed.add_field(name='c4-quit', value='Surrender your current game.', inline=False)
    embed.add_field(name='c4-game', value='View info on a previous game.', inline=False)
    embed.add_field(name='c4-stats', value='See your own, or someone else\'s Connect 4 stats', inline=False)
    try:
        await user.send(embed=embed)
        await ctx.send('{}, check your DMs.'.format(user.mention))
    except:
        await ctx.send('{}, I couldn\'t send you a DM.'.format(user.mention))

@client.command()
async def info(ctx):
    if check_blacklist(ctx.author):
        return
    embed = discord.Embed(color=0x3498db)
    embed.add_field(name='What is Connect 4 Bot?', value='Connect 4 bot is a bot designed specifically for the gameplay of Connect 4, in Discord!')
    embed.add_field(name='Who made Connect 4 Bot?', value='Connect 4 bot is made by William L. His Discord tag is Mippy#0001.')
    embed.add_field(name='How did Connect 4 Bot come to be?', value='William works on a bot called Blade with his good friend Alexis. On their bot, they perfected the Discord Connect 4 experience. Now, they\'ve made a completely separate bot for Connect 4 altogether!')
    embed.add_field(name='How do I use Connect 4 Bot?', value='Simply type `c4-help` to get the list of commands.')
    embed.add_field(name='How can I donate to Connect 4 Bot?', value='We accept donatons on our [Patreon](https://patreon.com/bladebot). Please note that the link will direct to Blade bot. We are the same developers.')
    try:
        await ctx.send(embed=embed)
    except:
        return await ctx.send('{}, I do not have permission to send this command output. :no_entry:'.format(ctx.author.mention))

@client.command()
async def invite(ctx):
    if check_blacklist(ctx.author):
        return
    embed = discord.Embed(color=0x3498db, description='**Thanks for your interest in Connect 4 Bot!**\n[C4 Bot Link](https://discordapp.com/oauth2/authorize?client_id=442185653992816640&permissions=288832&redirect_uri=https%3A%2F%2Fwilliamlomas.me%2Fthanks&scope=bot)\n[Support Server Invite](https://discord.gg/wzWpsfU)')
    await ctx.send(embed=embed)

@client.command()
async def ranks(ctx):
    user = ctx.author
    if check_blacklist(user):
        return
    embed = discord.Embed(color=0x3498db, title='Ranks', description='The list of ranks you can get.')
    rank = get_rank(user.id)
    if rank == 'Dominator':
        embed.add_field(name='Dominator', value='Be #1 on the points leaderboard. **<<< You are here**', inline=False)
    else:
        embed.add_field(name='Dominator', value='Be #1 on the points leaderboard.', inline=False)
    if rank == 'Legend':
        embed.add_field(name='Legend', value='2501+ Points **<<< You are here**', inline=False)
    else:
        embed.add_field(name='Legend', value='2501+ Points', inline=False)
    if rank == 'God':
        embed.add_field(name='God', value='1501-2500 Points **<<< You are here**', inline=False)
    else:
        embed.add_field(name='God', value='1501-2500 Points', inline=False)
    if rank == 'Master':
        embed.add_field(name='Master', value='751-1500 Points **<<< You are here**', inline=False)
    else:
        embed.add_field(name='Master', value='751-1500 Points', inline=False)
    if rank == 'Pro':
        embed.add_field(name='Pro', value='401-750 Points **<<< You are here**', inline=False)
    else:
        embed.add_field(name='Pro', value='401-750 Points', inline=False)
    if rank == 'Average':
        embed.add_field(name='Average', value='151-400 Points **<<< You are here**', inline=False)
    else:
        embed.add_field(name='Average', value='151-400 Points', inline=False)
    if rank == 'Learner':
        embed.add_field(name='Learner', value='0-150 Points **<<< You are here**', inline=False)
    else:
        embed.add_field(name='Learner', value='0-150 Points', inline=False)
    await ctx.send(embed=embed)

@client.command()
async def blacklist(ctx, mode, userid):
    user = ctx.author
    if user.id != 169275259026014208:
        return
    fp = open('data/blacklist.data', 'r+')
    content = json.load(fp)
    if mode == 'add':
        content[str(userid)] = 1
        await ctx.send('{}, user `{}` successfully blacklisted.'.format(user.mention, userid))
    else:
        content[str(userid)] = 0
        await ctx.send('{}, user `{}` successfully unblacklisted.'.format(user.mention, userid))
    fp.seek(0)
    json.dump(content, fp)
    fp.truncate()

@client.command()
async def shutdown(ctx, mode, force=False):
    user = ctx.author
    if user.id != 169275259026014208:
        return
    if not force:
        games = count_active_games()
        if games > 0:
            return await ctx.send('{}, careful! There are currently **{}** active games. :no_entry:'.format(user.mention, games))
    if mode == '-s':
        await ctx.send('{}, shutting down... :white_check_mark:'.format(user.mention))
        await client.logout()
    elif mode == '-r':
        await ctx.send('{}, restarting... :white_check_mark:'.format(user.mention))
        os.system('bot.py')
        await client.logout()
        
    elif mode == '-u':
        message = await ctx.send('{}, updating... :cd:'.format(user.mention))
        os.system('git pull')
        await message.edit(content='{}, successfully updated! :white_check_mark:'.format(user.mention))
        os.system('bot.py')
        await client.logout()
    else:
        pass

@client.command()
async def debug(ctx, *, code):
    if ctx.author.id != 169275259026014208:
        return
    try:
        code = code.strip('` ')
        result = None

        global_vars = globals().copy()
        global_vars['bot'] = client
        global_vars['ctx'] = ctx
        global_vars['message'] = ctx.message
        global_vars['author'] = ctx.author
        global_vars['channel'] = ctx.message.channel
        global_vars['guild'] = ctx.message.guild

        try:
            result = eval(code, global_vars, locals())
        except Exception as e:
            await ctx.send(box('{}: {}'.format(type(e).__name__, str(e)),
                                   lang='py'))
            return

        if asyncio.iscoroutine(result):
            result = await result

        result = str(result)
        result = list(pagify(result, shorten_by=16))
        await ctx.send(box(result[0], lang='py'))
    except Exception as e:
        await ctx.send("```py\n{}```".format(e))

@client.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def report(ctx, user: discord.Member=None, *, reason=None):
    reporter = ctx.author
    if check_blacklist(reporter):
        return
    if user is None or reason is None:
        embed = discord.Embed(color=0x3498db, description='Command Help', title='c4-report')
        embed.add_field(name='c4-report <user> <reason>', value='Report a rule-breaker.', inline=False)
        embed.add_field(name='About Reporting:', value='Reporting users is taken seriously, please do not send joke reports or you may find yourself revoked of privileges.\n\nWhen reporting, include as much detail as possible, including Game IDs.\nTo get a Game ID, you\'ll see it in the footer of the \'Match Starting\' screen.', inline=False)
        return await ctx.send(embed=embed)
    try:
        guild = reporter.guild
    except:
        return await ctx.send('{}, please use the report command in a server. :no_entry:'.format(reporter.mention))
    if user.id == reporter.id:
        return await ctx.send('{}, the report command is meant for serious inquiries only. :no_entry:'.format(reporter.mention))
    if user.id == client.user.id:
        return await ctx.send('{}, the report command is meant for serious inquiries only. :no_entry:'.format(reporter.mention))
    timestamp = datetime.datetime.now()
    channel = client.get_channel(442239818001416194)
    rbl = open('data/blacklist.data')
    rbl = json.load(rbl)
    try:
        if rbl[str(reporter.id)] == 1:
            return await ctx.send('{}, you\'re not allowed to send reports. :no_entry:'.format(reporter.mention))
    except: pass
    embed = discord.Embed(color=0xe02828, title="New Report", timestamp=timestamp)
    embed.add_field(name="Reporter", value='{} `{}`'.format(reporter, reporter.id))
    embed.add_field(name="User", value='{} `{}`'.format(user, user.id))
    embed.add_field(name="Guild", value='{} `{}`'.format(guild, guild.id))
    embed.add_field(name="Reason", value=reason)
    await channel.send(embed=embed)
    return await ctx.send('{}, your report will be reviewed by a staff member shortly.\nPlease remember that if the report system is abused, your privileges may be revoked.\nWe may also contact you regarding this report.\nThank you for reporting to keep the community wholesome.'.format(reporter.mention))

@client.command(aliases=['start'])
async def play(ctx):
    author = ctx.author
    if check_blacklist(author):
        return
    async def wait_player_two(session):
        def check(reaction, user):
            return str(reaction.emoji) == '🤝' and user != ctx.me and user != author and not already_playing(user) and not user.bot and reaction.message.id == message.id and not check_blacklist(user)
        try:
            reaction = await client.wait_for('reaction_add', timeout=30.0, check=check)
        except:
            session.active = False
            await ctx.send('{}, unfortunately, no one has joined your game. :no_entry:'.format(author.mention))
            await message.delete()
        else:
            session.player2 = reaction[1]
            session.nonturnholder = session.player2
            await message.delete()
            await session.start(ctx)
        
    if not ctx.guild:
        return await ctx.send('{}, you may not start a game in DMs. :no_entry:'.format(author.mention))
    if connect4_active(ctx):
        return await ctx.send('{}, there is already an ongoing game in this channel. :no_entry:'.format(author.mention))
    if already_playing(author):
        return await ctx.send('{}, you\'re already playing a game of Connect 4. :no_entry:'.format(author.mention))
    if not ctx.channel.permissions_for(ctx.me).add_reactions:
        return await ctx.send('{}, I need permissions to Add Reactions to start a game of Connect 4. :no_entry:'.format(author.mention))
    session = Connect4Session(ctx.channel, author)
    message = await ctx.send('**{}** started a game of **Connect 4**. React with 🤝 to join!'.format(author.name))
    await message.add_reaction("🤝")
    await wait_player_two(session)

@client.command()
async def quit(ctx):
    author = ctx.author
    if check_blacklist(author):
        return
    if not connect4_active(ctx):
        return await ctx.send('{}, there are no active games in this channel. :no_entry:'.format(author.mention))
    session = get_connect4_session(ctx)
    if author != session.player1 and author != session.player2:
        return await ctx.send('{}, you aren\'t participating in the current game. :no_entry:'.format(author.mention))
    if author == session.player1:
        if session.player2 is None:
            return await ctx.send('{}, your game hasn\'t started yet. :no_entry:'.format(author.mention))
        return await session.end(session.player2)
    await session.end(session.player1)

@client.command(aliases=['display'])
async def view(ctx):
    author = ctx.author
    if check_blacklist(author):
        return
    if not connect4_active(ctx):
        return await ctx.send('{}, there are no active games in this channel. :no_entry:'.format(author.mention))
    session = get_connect4_session(ctx)
    if author != session.player1 and author != session.player2:
        return await ctx.send('{}, you aren\'t participating in the current game. :no_entry:'.format(author.mention))
    if session.player2 is None:
        return await ctx.send('{}, your game hasn\'t started yet. :no_entry:'.format(author.mention))
    return await session.grid.display()

@client.command()
async def stats(ctx, *, user: discord.Member=None):
    author = ctx.author
    if check_blacklist(author):
        return
    if not user:
        user = author
    embed = discord.Embed(color=0x00bdff, description='Connect 4 Stats for {}'.format(user), title='Connect 4 Profile: {}'.format(user))
    with open('data/userstats.data') as fp:
        try:
            content = json.load(fp)
            wins = content[str(user.id)]['wins']
            losses = content[str(user.id)]['losses']
            draws = content[str(user.id)]['ties']
            total = wins + losses + draws
            points = ((wins*10)+(losses*-5)+(draws*3))
            avgwins = round(wins/total*100, 2)
            rank = get_rank(user.id)
            if points < 0:
                points = 0
        except:
            wins = losses = draws = total = points = 0
            avgwins = 0.00
            rank = 'Learner'
        embed.add_field(name='Games Won', value=wins)
        embed.add_field(name='Games Tied', value=draws)
        embed.add_field(name='Games Lost', value=losses)
        embed.add_field(name='Total Games', value=total)
        embed.add_field(name='Rank', value='{}, {} points'.format(rank, points))
        embed.add_field(name='Average Win Percentage', value='{}%'.format(avgwins))
        return await ctx.send(embed=embed)

@client.command()
async def game(ctx, gameid=None, gridmode=None):
    user = ctx.author
    if check_blacklist(user):
        return
    if gameid is None:
        return await ctx.send('{}, please specify a game ID. :no_entry:'.format(user.mention))
    fp = open('data/games.data')
    content = json.load(fp)
    try:
        game = content[str(gameid)]
    except:
        return await ctx.send('{}, that\'s not a valid game ID. :no_entry:'.format(user.mention))
    if gridmode == 'grid':
        async with ctx.typing():
            pass
        player1 = await client.get_user_info(game['player1'])
        player2 = await client.get_user_info(game['player2'])
        embed = discord.Embed(color=0x3498db, title='Game No. {} - Grid'.format(gameid), description=':red_circle: = {}\n:large_blue_circle: = {}'.format(player1, player2))
        embed.add_field(name=":regional_indicator_a:​:regional_indicator_b:​:regional_indicator_c:​:regional_indicator_d:​:regional_indicator_e:​:regional_indicator_f:​:regional_indicator_g:", value="{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}\n{}{}{}{}{}{}{}".format(game['grid']['a1'], game['grid']['b1'], game['grid']['c1'], game['grid']['d1'], game['grid']['e1'], game['grid']['f1'], game['grid']['g1'], game['grid']['a2'], game['grid']['b2'], game['grid']['c2'], game['grid']['d2'], game['grid']['e2'], game['grid']['f2'], game['grid']['g2'], game['grid']['a3'], game['grid']['b3'], game['grid']['c3'], game['grid']['d3'], game['grid']['e3'], game['grid']['f3'], game['grid']['g3'], game['grid']['a4'], game['grid']['b4'], game['grid']['c4'], game['grid']['d4'], game['grid']['e4'], game['grid']['f4'], game['grid']['g4'], game['grid']['a5'], game['grid']['b5'], game['grid']['c5'], game['grid']['d5'], game['grid']['e5'], game['grid']['f5'], game['grid']['g5'], game['grid']['a6'], game['grid']['b6'], game['grid']['c6'], game['grid']['d6'], game['grid']['e6'], game['grid']['f6'], game['grid']['g6']), inline=False)
        return await ctx.send(embed=embed)
    embed = discord.Embed(color=0x3498db, title='Game No. {}'.format(gameid))
    async with ctx.typing():
        pass
    winner = game['winner']
    winner = await client.get_user_info(winner)
    channel = client.get_channel(game['channel'])
    if channel is None:
        channelname = 'deleted-channel'
        guild = '(Connect 4 Bot Cannot See This Guild Anymore)'
    else:
        channelname = channel.name
        guild = channel.guild.name
    if winner.id == game['player1']:
        winner = str(winner) + ' (:red_circle:)'
        loser = await client.get_user_info(game['player2'])
        loser = str(loser) + ' (:large_blue_circle:)'
    else:
        winner = str(winner) + ' (:large_blue_circle:)'
        loser = await client.get_user_info(game['player1'])
        loser = str(loser) + ' (:red_circle:)'
    timestamp = datetime.datetime.strptime(game['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
    embed.timestamp = timestamp
    embed.add_field(name='Winner', value=winner)
    embed.add_field(name='Loser', value=loser)
    embed.add_field(name='Channel', value='#' + channelname)
    embed.add_field(name='Server', value=guild)
    embed.add_field(name='Grid', value='Run the command `c4-game {} grid` to view this game\'s grid.'.format(gameid))
    await ctx.send(embed=embed)

@report.error
async def report_error(ctx, error):
    user = ctx.author
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.send('{}, please try again in **{}**. :no_entry:'.format(user.mention, display_time(error.retry_after)))

token = open('token')
client.run(token.read())
