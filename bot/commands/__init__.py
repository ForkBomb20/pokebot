from bot.commands.data import DataCog
from bot.commands.learnset import LearnsetCog
from bot.commands.evolution import EvolutionCog
from bot.commands.session import SessionCog
from bot.commands.stats import StatsCog
from bot.commands.abilities import AbilitiesCog
from bot.commands.calc import CalcCog


async def setup_commands(bot):
    await bot.add_cog(DataCog(bot))
    await bot.add_cog(LearnsetCog(bot))
    await bot.add_cog(EvolutionCog(bot))
    await bot.add_cog(SessionCog(bot))
    await bot.add_cog(StatsCog(bot))
    await bot.add_cog(AbilitiesCog(bot))
    await bot.add_cog(CalcCog(bot))
