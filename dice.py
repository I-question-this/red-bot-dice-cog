from collections import defaultdict
import datetime
import discord
import logging
import os
import random
random.seed()
import re

from redbot.core import checks, commands, Config
from redbot.core.data_manager import cog_data_path
from redbot.core.bot import Red

log = logging.getLogger("red.dad")
_DEFAULT_GUILD = {
    "change_nickname": False,
    "barely_know_her": True,
    "i_am_dad": True,
    "rank_joke": True,
    "response_chance": 60,
}
_DEFAULT_USER = {
        "rolls": {}
}

class Dice(commands.Cog):
    """Dice cog"""

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self._conf = Config.get_conf(None, 202020, cog_name=f"{self.__class__.__name__}", force_registration=True)
        self._conf.register_user(**_DEFAULT_USER)
        self.dice_re = re.compile(
                r"(?P<n_rolls>\d+)d(?P<n_faces>\d+)(?P<modifier>[+-]\d+)?",
                re.IGNORECASE)



    @commands.command(name="roll")
    async def roll(self, ctx: commands.Context, roll:str):
        """Roll some dice

        Parameters
        ----------
        roll: str
            Description of the dice to roll.
        """
        # Remove spaces from input
        roll = roll.replace(" ", "")
        match = self.dice_re.match(roll)

        if match is None:
            title="I am confusion"
            description=f"{ctx.author.mention} It's got to be 'NdN+/-N'"
        else:
            n_rolls = int(match.group("n_rolls"))
            n_faces = int(match.group("n_faces"))
            if match.group("modifier") is not None:
                modifier = int(match.group("modifier"))
            else:
                modifier = 0
            if n_rolls < 0:
                title="I am confusion"
                description="Why would you ask me to roll a die less than once??"
            elif n_rolls > 100:
                title="I am confusion"
                description="What possible use is there to roll more than 100 dice??"
            elif n_faces < 2:
                title="I am confusion"
                description="How can I roll it if it has less than 2 sides?? That's not even a coin!?!"
            else:
                rs = []
                for n in range(n_rolls):
                    rs.append(random.randint(1,n_faces))
                result = sum(rs) + modifier
                title="Your sweet roll, my lord"
                rs_str = '+'.join((str(r) for r in rs))
                description=f"({rs_str})+{modifier}={result}"

        contents = dict(
                title=title,
                description=f"{ctx.author.mention}{description}"
                )
        embed = discord.Embed.from_dict(contents)
        return await ctx.send(embed=embed)

