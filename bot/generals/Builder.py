from sc2.constants import *


class Builder(object):
    def __init__(self, bot):
        self.bot = bot

    @property
    def best_pylon(self):
        return self.bot.units(PYLON).closest_to(self.bot.enemy_start_locations[0])

    @property
    def best_nexus(self):
        return self.bot.units(NEXUS).closest_to(self.bot.enemy_start_locations[0])

    async def on_step(self, iteration):
        await self.create_pylons()
        await self.create_military_base()

    async def create_pylons(self):
        if self.bot.already_pending(PYLON) \
                or not self.bot.can_afford(PYLON):
            return
        if self.bot.supply_left < self.bot.POP_SHORTAGE:
            await self.bot.build(PYLON, near=self.best_nexus)

    async def create_military_base(self):
        if not self.bot.units(PYLON).amount or\
                not self.bot.can_afford(GATEWAY):
            return
        if self.bot.fire_level() >= 1 and\
                self.bot.minutes_since_start() > self.bot.units(GATEWAY).amount:
            await self.bot.build(GATEWAY, near=self.best_pylon)
            return
        if self.bot.fire_level() == 3:
            await self.bot.build(GATEWAY, near=self.best_pylon)
            return
        if not self.bot.units(GATEWAY):
            await self.bot.build(GATEWAY, near=self.best_pylon)
        if self.bot.units(GATEWAY).ready.amount > 0\
                and self.bot.units(CYBERNETICSCORE).amount == 0\
                and self.bot.can_afford(CYBERNETICSCORE):
            await self.bot.build(CYBERNETICSCORE, near=self.best_pylon)
