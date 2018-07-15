from sc2.constants import *


class EconomyGeneral(object):
    def __init__(self, bot):
        self.bot = bot
        self.HARD_LIMIT = 62
        self.PROBES_PER_BASE = 16

    async def on_step(self, iteration):
        await self.bot.distribute_workers()
        await self.create_workers()
        await self.assimilate_green_shit()

    @property
    def needed_vespene(self):
        # TODO: improve ratio / add some logic for the ratios
        return self.bot.minerals*.5

    async def assimilate_green_shit(self):
        if self.bot.vespene > self.needed_vespene\
                or self.bot.already_pending(ASSIMILATOR)\
                or not self.bot.can_afford(ASSIMILATOR):
            return

        for nexus in self.bot.units(NEXUS).ready:
            vespenes = self.bot.state.vespene_geyser.closer_than(15.0, nexus)
            for vespene in vespenes:
                worker = self.bot.select_build_worker(vespene.position)
                if not self.bot.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
                    await self.bot.do(worker.build(ASSIMILATOR, vespene))
                    return

    async def create_workers(self):
        if self.bot.units(PROBE).amount >= self.HARD_LIMIT or\
                not self.bot.can_afford(PROBE):
            return
        if self.bot.units(NEXUS).amount * self.PROBES_PER_BASE\
                <= self.bot.units(PROBE).amount:
            try:
                await self.bot.expand_now()
            except:
                pass
            return
        for nexus in self.bot.units(NEXUS).ready.noqueue:
            if self.bot.can_afford(PROBE):
                await self.bot.do(nexus.train(PROBE))
