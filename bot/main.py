import json
import random
import time
from pathlib import Path

import sc2
from sc2 import Difficulty, Race, maps, run_game
from sc2.constants import (ASSIMILATOR, CYBERNETICSCORE, FORGE, GATEWAY, NEXUS,
                           PROBE, PROTOSSGROUNDARMORSLEVEL1,
                           PROTOSSGROUNDWEAPONSLEVEL1, PYLON, STALKER, ZEALOT)
from sc2.player import Bot, Computer


class TrashBot(sc2.BotAI):
    with open(Path(__file__).parent / "../botinfo.json") as f:
        NAME = json.load(f)["name"]

    def __init__(self):
        self.PROBES_PER_BASE = 22
        self.HARD_LIMIT = 50
        self.EXPAND_TIMER = 2
        self.start = time.time()
        self.POP_SHORTAGE = 5
        self.MINERAL_LATE = 700
        self.EARLY_GAME_TIMER = 5

    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send(f"Name: {self.NAME}")
        self.iteration_number = iteration
        if iteration % 165 == 0:
            print(self.minutes_since_start())
            print("idle military : %s" % self.idle_military().amount)
            print("fire level :%s" % self.fire_level())
        try:
            await self.distribute_workers()
        except Exception as e:
            pass
        try:
            await self.create_workers()
        except Exception as e:
            pass
        try:
            await self.create_pylons()
        except Exception as e:
            pass
        try:
            await self.create_military_base()
        except Exception as e:
            pass
        try:
            await self.create_military_forces()
        except Exception as e:
            pass
        try:
            await self.assimilate_green_shit()
        except Exception as e:
            pass
        try:
            await self.distribute_military()
        except Exception as e:
            pass

    def best_pylon(self):
        return self.units(PYLON).closest_to(self.enemy_start_locations[0])

    def best_nexus(self):
        return self.units(NEXUS).closest_to(self.enemy_start_locations[0])

    def minutes_since_start(self):
        return self.iteration_number / 165

    def fire_level(self):
        if self.minerals < self.MINERAL_LATE:
            self.POP_SHORTAGE = 5
            return 0
        if self.minerals > 2500:
            self.POP_SHORTAGE = 16
            return 3
        if self.idle_military().amount < 19:
            self.POP_SHORTAGE = 5
            return 1

        self.POP_SHORTAGE = 8
        return 2

    def idle_military(self):
        return self.units(ZEALOT).idle | self.units(STALKER).idle

    async def create_workers(self):
        if self.units(PROBE).amount >= self.HARD_LIMIT:
            return
        if self.units(NEXUS).amount * self.PROBES_PER_BASE <= self.units(PROBE).amount:
            await self.expand_now()
            return
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

    async def assimilate_green_shit(self):
        # TODO: improve ratio
        if self.vespene > self.minerals*.5 or self.already_pending(ASSIMILATOR) or not self.can_afford(ASSIMILATOR):
            return

        for nexus in self.units(NEXUS).ready:
            vespenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vespene in vespenes:
                worker = self.select_build_worker(vespene.position)
                if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
                    await self.do(worker.build(ASSIMILATOR, vespene))

    async def improve_military(self):
        if not self.units(FORGE):
            return

    async def create_pylons(self):
        if self.already_pending(PYLON) or not self.can_afford(PYLON):
            return
        if self.units(PYLON).amount < 3 or self.supply_left < self.POP_SHORTAGE:
            await self.build(PYLON, near=self.best_nexus())

    async def create_military_base(self):
        if not self.units(PYLON).amount:
            return
        if self.fire_level() >= 1 and self.minutes_since_start() > self.units(GATEWAY).amount:
            await self.build(GATEWAY, near=self.best_pylon())
            return
        if self.fire_level() == 3:
            await self.build(GATEWAY, near=self.best_pylon())
            return
        if self.units(GATEWAY).amount < 3:
            await self.build(GATEWAY, near=self.best_pylon())
        if self.units(GATEWAY).amount > 0\
                and self.can_afford(GATEWAY) \
                and self.units(CYBERNETICSCORE).amount == 0:
            await self.build(CYBERNETICSCORE, near=self.best_pylon())

    async def create_military_forces(self):
        if self.units(CYBERNETICSCORE).ready.amount > 0:
            for gw in self.units(GATEWAY).ready.noqueue:
                await self.do(gw.train(STALKER))
        else:
            for gw in self.units(GATEWAY).ready.noqueue:
                await self.do(gw.train(ZEALOT))

    async def attack_structures(self):
        target = self.known_enemy_structures if self.known_enemy_structures else self.enemy_start_locations[
            0]
        # if self.minutes_since_start() < self.EARLY_GAME_TIMER:
        #     await self.harass_early(target)
        if self.idle_military().amount > 10:
            for s in self.idle_military():
                await self.do(s.attack(target))

    async def harass_early(self, target):
        if self.units(ZEALOT).idle.amount >= 2:
            for s in self.idle_military():
                await self.do(s.attack(target))

    async def distribute_military(self):
        if not self.known_enemy_units:
            await self.attack_structures()
            return

        if self.idle_military().amount:
            await self.attack_known_units()
            return

        # for s in self.idle_military():
        #     await self.do(s.move(self.best_pylon()))

    async def attack_known_units(self):
        for s in self.idle_military():
            await self.do(s.attack(random.choice(self.known_enemy_units)))
