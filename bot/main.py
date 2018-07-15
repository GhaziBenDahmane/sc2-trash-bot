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
from .generals import *


class TrashBot(sc2.BotAI):
    with open(Path(__file__).parent / "../botinfo.json") as f:
        NAME = json.load(f)["name"]

    def __init__(self):
        self.economy = EconomyGeneral(self)
        self.builder = Builder(self)
        self.army = ArmyGeneral(self)
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
            print("idle military : %s" % self.army.idle_military.amount)
            print("fire level :%s" % self.fire_level())

        await self.economy.on_step(iteration)
        await self.builder.on_step(iteration)
        await self.army.on_step(iteration)

    def minutes_since_start(self):
        return self.iteration_number / 165

    def fire_level(self):
        if self.minerals < self.MINERAL_LATE:
            self.POP_SHORTAGE = 5
            return 0
        if self.minerals > 2500:
            self.POP_SHORTAGE = 9
            return 3
        if self.army.idle_military.amount < 19:
            self.POP_SHORTAGE = 5
            return 1

        self.POP_SHORTAGE = 8
        return 2

    async def improve_military(self):
        if not self.units(FORGE):
            return
