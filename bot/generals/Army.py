
from sc2.constants import *
import random


class ArmyGeneral(object):
    def __init__(self, bot):
        self.bot = bot
        self.in_attack = False
        self.being_attacked = False

    @property
    def idle_military(self):
        return self.bot.units(ZEALOT).idle | self.bot.units(STALKER).idle

    @property
    def all_military(self):
        return self.bot.units(ZEALOT) | self.bot.units(STALKER)

    @property
    def all_military(self):
        return self.bot.units(ZEALOT) | self.bot.units(STALKER)

    async def on_step(self, iteration):
        await self.distribute_military()
        await self.create_military_forces()

    async def create_military_forces(self):
        if self.bot.units(CYBERNETICSCORE).ready.amount > 0:
            for gw in self.bot.units(GATEWAY).ready.noqueue:
                if self.bot.can_afford(STALKER):
                    await self.bot.do(gw.train(STALKER))
        else:
            for gw in self.bot.units(GATEWAY).ready.noqueue:
                if self.bot.can_afford(ZEALOT):
                    await self.bot.do(gw.train(ZEALOT))

    async def attack_structures(self):
        target = self.bot.known_enemy_structures if self.bot.known_enemy_structures else self.bot.enemy_start_locations[
            0]
        if self.idle_military.amount > 10:
            for s in self.idle_military:
                await self.bot.do(s.attack(target))

    async def harass_early(self, target):
        if self.bot.units(ZEALOT).idle.amount >= 2:
            for s in self.idle_military:
                await self.bot.do(s.attack(target))

    async def distribute_military(self):
        if not self.bot.known_enemy_units:
            await self.attack_structures()
            return

        if self.idle_military.amount:
            await self.attack_known_units()
            return

    async def attack_known_units(self):
        for s in self.idle_military:
            await self.bot.do(s.attack(random.choice(self.bot.known_enemy_units)))
