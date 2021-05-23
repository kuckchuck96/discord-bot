import discord
import config
import requests
import os
import datetime
import json
import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

from discord.ext import commands
from config import default

class R6Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = default.config()
        self.bot_prefix = config.bot_prefix
        self.r6stats_key = config.r6stats.api_key
        self.r6stats_url = config.r6stats.api_url
        self.db = self.initiliazeFirebase()
    
    def initiliazeFirebase(self):
        cred = credentials.Certificate('config/r6roulette-5f65e-83b82e2e691c.json')
        firebase_admin.initialize_app(cred)
        return firestore.client()

    @commands.command(
        name = 'spinR6roulette',
        help = 'Get a LASN challenge. Usage: >spinR6roulette [user] [startSession="false"] [difficulty="medium"]'
    )    
    async def r6_roulette(self, ctx, user, startSession='false', difficulty='medium'):
        try:
            userSession = self.getActiveSession(user)
            if(not userSession["isActive"]):
                challenge = "";
                if difficulty=='easy':
                    challenge = await self.getEasyChallenge(ctx, user, startSession);
                elif difficulty=='hard':
                    challenge = await self.getHardChallenge(ctx, user, startSession);
                elif difficulty=='medium':
                    challenge = await self.getMediumChallenge(ctx, user, startSession);
                self.setupChallenge(user, challenge)
                await self.startSession(ctx, user, True, startSession)
            else:
                await ctx.send(f'Complete your existing challenge, Dummy!')
        except Exception as err:
            print(err)
            await ctx.send('Something went wrong, finding someone to blame...')

    def setupChallenge(self, user, challenge):
        challenge["sessionStartedOn"] = datetime.utcnow()
        self.getActiveSessionRef(user).set(challenge, merge=True)

    def getActiveSession(self, user):
        return self.db.collection("session").document(user).get().to_dict()
    
    def getActiveSessionRef(self, user):
        return self.db.collection("session").document(user)

    async def get_top_operators(self, operators, limit = '5'):
        #operators = sorted(operators['operators'], reverse=True, key=lambda g: int(g['kills']))
        return operators[:limit]  

    async def getEasyChallenge(self, ctx, user, startSession):
        operators = await self.getOperatorsList(ctx, user);
        mission = {"challenge": "", "winValue": 2, "challengePath": "operators.operators.kills", "endValue": 0}
        returnText = "Your mission should you choose to accept it. "
        op = random.choice(operators)
        mission["challenge"] = 'Mission: Get 2 kills with ' + op + "."
        mission["challengePath"] = "operators."+op+".kills"
        mission["oldValue"] = await self.getOperatorCurrentValue(ctx, user, mission["challengePath"])
        if(startSession == 'true'):
            returnText += mission["challenge"]
        else:
            returnText += 'Please enter ">startR6roulette [user]". ' + mission["challenge"]
        await ctx.send(f'{returnText}')
        await ctx.send('So you choose Easy. Scared little child!?')
        return mission

    async def getMediumChallenge(self, ctx, user, startSession):
        operators = await self.getOperatorsList(ctx, user);
        mission = {"challenge": "", "winValue": 2, "challengePath": "operators.operators.headshots", "endValue": 0}
        returnText = "Your mission should you choose to accept it. "
        op = random.choice(operators)
        mission["challenge"] = 'Mission: Get 2 headshots with ' + op + "."
        mission["challengePath"] = "operators."+op+".headshots"
        mission["oldValue"] = await self.getOperatorCurrentValue(ctx, user, mission["challengePath"])
        if(startSession == 'true'):
            returnText += mission["challenge"]
        else:
            returnText += 'Please enter ">startR6roulette [user]". ' + mission["challenge"]
        await ctx.send(f'{returnText}')
        await ctx.send('So you choose Medium. Thought so!')
        return mission

    async def getHardChallenge(self, ctx, user, startSession):
        operators = await self.getOperatorsList(ctx, user);
        mission = {"challenge": "", "winValue": 2, "challengePath": "operators.operators.melee_kills", "endValue": 0}
        returnText = 'Your mission should you choose to accept it. '
        op = random.choice(operators)
        mission["challenge"] = 'Mission: Get 2 melee kills with ' + op + "."
        mission["challengePath"] = "operators."+op+".melee_kills"
        mission["oldValue"] = await self.getOperatorCurrentValue(ctx, user, mission["challengePath"])
        if(startSession == 'true'):
            returnText += mission.get("challenge")
        else:
            returnText += 'Please enter ">startR6roulette [user]". ' + mission.get("challenge")
        await ctx.send(f'{returnText}')
        await ctx.send('So you choose Hard. Don\'t worry, you will find your worth soon!')
        return mission

    @commands.command(
        name = 'startR6roulette',
        help = 'Start your LASN challenge session. Usage >startR6roulette [user]'
    )  
    async def startSession(self, ctx, user, fromCommand = False, startSession='true'):
        if(startSession == 'true'):
            userSession = self.getActiveSession(user)
            if(not userSession["isActive"]):
                self.getActiveSessionRef(user).set({
                    u'isActive': True
                }, merge=True)
                await ctx.send(f'Started Challenge session for {user}. Considering you, I dont think you will fare well. Good Luck, anyway!')
            else:
                await ctx.send(f'Complete your existing challenge, Dummy!')

    @commands.command(
        name = 'endR6roulette',
        help = 'End your active LASN challenge session. Usage >endR6roulette [user]'
    )  
    async def endSession(self, ctx, user):
        userSession = self.getActiveSession(user)
        if(userSession["isActive"]):
            if(userSession["endValue"] > userSession["winValue"] + userSession["oldValue"]):
                status = "won"
            else:
                status = "lost"
            self.getActiveSessionRef(user).set({
                u'isActive': False,
                u'sessionEndedOn': datetime.utcnow(),
                u'status': status
            }, merge=True)
            if(status == 'won'):
                await ctx.send(f'Challenge ended for {user}. Hmmm.. seems like you won. Lucky Noob!')
            else:
                await ctx.send(f'Challenge ended for {user} but you lost, you LOOSER!')
        else:
            await ctx.send(f'Quitting even before you started, you PUSSY!')

    async def getOperatorsList(self, ctx, user):
        operators = await self.get_stats(ctx, user, 'pc', 'operators');
        operators = operators['operators']
        lstOps = [];
        for op in operators:
            lstOps.append(op['name'])
        return lstOps;

    async def getOperatorCurrentValue(self, ctx, user, path):
        operators = await self.get_stats(ctx, user, 'pc', 'operators')
        return self.getKillsInPath(operators, path)

    def getKillsInPath(self, data, path):
        lstPath = path.split(".")
        data = data[lstPath[0]]
        for x in data:
            if(x["name"] == lstPath[1]):
                return x[lstPath[2]]

    def contains(list, filter):
        for x in list:
            if filter(x):
                return True
        return False
    
    async def get_stats(self, ctx, user, platform = 'pc', stat_type = 'generic'):
        api_key = self.r6stats_key
        request_url = f'{self.r6stats_url}/stats/{user}/{platform}/{stat_type}'
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {api_key}'}
        stats_res = requests.get(request_url, headers = headers)
        if stats_res.status_code != 200:
            await ctx.send('Please check the arguments passed...')
        return stats_res.json();

def setup(bot):
    bot.add_cog(R6Roulette(bot))