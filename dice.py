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
_DEFAULT_MEMBER = {
        "rolls": {"weird":"2d6+1"}
}

class Dice(commands.Cog):
    """Dice cog"""

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self._conf = Config.get_conf(None, 202020, cog_name=f"{self.__class__.__name__}", force_registration=True)
        self._conf.register_member(**_DEFAULT_MEMBER)
        self.dice_re = re.compile(
                r"(?P<n_rolls>\d+)"\
                r"d"\
                r"(?P<n_faces>\d+)"\
                r"(?P<modifier>[-+]\d+)?"\
                r"\Z",
                re.IGNORECASE)
        self.saved_re = re.compile(
                r"(?P<name>\w+)"\
                r"(?P<modifier>[-+]\d+)?"\
                r"\Z",
                re.IGNORECASE)

    
    async def send_response(self, ctx: commands.Context,
            title:str, description:str):
        contents = dict(
                title=title,
                description=f"{ctx.author.mention}: {description}"
                )
        embed = discord.Embed.from_dict(contents)
        return await ctx.send(embed=embed)


    @commands.command(name="list_saved_rolls")
    async def list_saved_rolls(self, ctx: commands.Context):
        saved_rolls = await self._conf.member(ctx.author).rolls()
        if len(saved_rolls) == 0:
            description = "You have no saved rolls"
        else:
            description = [""]
            for name, roll in saved_rolls.items():
                description.append(f"{name}: {roll}")
            description = "\n".join(description)

        return await self.send_response(ctx, "Your saved rolls, my lord",
                description)


    @commands.command(name="delete_saved_roll")
    async def delete_saved_roll(self, ctx: commands.Context, name:str):
        saved_rolls = await self._conf.member(ctx.author).rolls()
        if name not in saved_rolls.keys():
            title="I am confusion"
            description=f'"{name}" is not one of your saved rolls!'
        else:
            # Delete it
            del saved_rolls[name]
            # Save it
            await self._conf.member(ctx.author).rolls.set(saved_rolls)
            # Inform them
            title="Successfully deleted"
            description=f'Deleted "{name}"'

        return await self.send_response(ctx, title, description)


    @commands.command(name="save_roll")
    async def save_roll(self, ctx: commands.Context, name:str, roll:str):
        # Is the name valid?
        name = name.replace(" ", "").lower()
        roll_match = self.dice_re.match(name)

        if roll_match is not None:
            title = "I am confusion"
            description = "Heresy! You can't name a roll as a roll!"
        else:
            # Seems legit, move forward
            roll = roll.replace(" ", "").lower()
            roll_match = self.dice_re.match(roll)

            if roll_match is None:
            # It was incompressible garbage
                title="I am confusion, my lord"
                description=f"It's got to be 'NdN+/-N'"
            else:
                saved_rolls = await self._conf.member(ctx.author).rolls()
                saved_rolls[name] = roll
                await self._conf.member(ctx.author).rolls.set(saved_rolls)
                title="Successfully saved"
                description=f'Saved "{roll}" as "{name}"'

        return await self.send_response(ctx, title, description)


    @commands.command(name="roll")
    async def roll(self, ctx: commands.Context, roll:str):
        """Roll some dice

        Parameters
        ----------
        roll: str
            Description of the dice to roll.
        """
        # Default is confusion
        title="I am confusion"
        description=f"It's got to be 'NdN+/-N' or a 'saved_roll_name+/-N'"
        # Remove spaces from input
        roll = roll.replace(" ", "").lower()
        roll_match = self.dice_re.match(roll)

        if roll_match is not None:
            return await self.send_roll_result(ctx, roll_match)
        else:
            # Check if it's a saved roll.
            saved_match = self.saved_re.match(roll)
            if saved_match is not None:
                # Check that the name is not a valid roll
                roll_match = self.dice_re.match(saved_match.group("name"))
                if roll_match is None:
                    saved_rolls = await self._conf.member(ctx.author).rolls()
                    roll = saved_rolls.get(saved_match.group("name"), None)
                    if roll is not None:
                        roll_match = self.dice_re.match(roll)
                        if saved_match.group("modifier") is not None:
                            additional_modifier = int(saved_match.group("modifier"))
                        else:
                            additional_modifier = None
                        return await self.send_roll_result(ctx, roll_match, 
                                additional_modifier)
                    else:
                        description = f"{saved_match.group('name')} is not one "\
                                "of your saved roll names."
        
        # It was incompressible garbage
        return await self.send_response(ctx, title, description)


    async def send_roll_result(self, ctx: commands.Context, match: re.Match, 
            additional_modifier:int=None):
        n_rolls = int(match.group("n_rolls"))
        n_faces = int(match.group("n_faces"))
        if match.group("modifier") is not None:
            modifier = int(match.group("modifier"))
        else:
            modifier = 0
        # Default is confusion
        title="I am confusion, my lord"
        if n_rolls < 0:
            description="Why would you ask me to roll a die less than once??"
        elif n_rolls > 100:
            description="What possible use is there to roll more than 100 dice??"
        elif n_faces < 2:
            description="How can I roll it if it has less than 2 sides?? That's not even a coin!?!"
        else:
            rs = []
            for n in range(n_rolls):
                rs.append(random.randint(1,n_faces))
            result = sum(rs) + modifier
            title="Your sweet roll, my lord"
            rs_str = '+'.join((str(r) for r in rs))
            description = f"({rs_str})+{modifier}"
            if additional_modifier is not None:
                result += additional_modifier
                description += f"+{additional_modifier}"
            description += f"={result}"

        return await self.send_response(ctx, title, description)

