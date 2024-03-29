# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

from zlib import compress
from canvas3d import Canvas3D
from server import Server


class Chunk:
    def __init__(self):
        self.blocks = []
        for i in range(16 * 128 * 16):
            self.blocks.append(Block())

    def set(self, x, y, z, block):
        assert x >= 0 and x <= 15
        assert y >= 0 and y <= 127
        assert z >= 0 and z <= 15
        self.blocks[y + z * 128 + x * 16 * 128] = block

    def get(self, x, y, z):
        assert x >= 0 and x <= 15
        assert y >= 0 and y <= 127
        assert z >= 0 and z <= 15
        return self.blocks[y + z * 128 + x * 16 * 128]

    def draw(self, wireframe=True):
        ca = Canvas3D()

        for x in range(16):
            for y in range(128):
                for z in range(16):
                    block = self.get(x, y, z)
                    ca.add(x, y, z, block.color())

        ca.draw(wireframe)

    def lighting(self):
        sources = []
        for x in range(16):
            for z in range(16):
                light = 15
                for y in range(127, -1, -1):
                    block = self.get(x, y, z)
                    block.sky = light
                    if block.color() not in ('', None):
                        light = 0
                    block.light = 0
                    if block.id == 50:
                        sources.append([x, y, z])
        for coord in sources:
            self.spread_light(coord[0], coord[1], coord[2], 14)

    def spread_light(self, x, y, z, level):
        try:
            block = self.get(x, y, z)
        except:
            return
        if block.light >= level:
            return
        block.light = level
        if level == 1:
            return
        if block.color() not in (None, ''):
            return
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if abs(dx) + abs(dy) + abs(dz) != 1:
                        continue
                    self.spread_light(x + dx, y + dy, z + dz, level - 1)

    def adjacent_blocks(self, x, y, z):
        blocks = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if abs(dx) + abs(dy) + abs(dz) != 2:
                        continue
                    try:
                        blocks.append(self.get(x + dx, y + dy, z + dz))
                    except:
                        pass
        return blocks

    def server(self, x=8, y=64, z=8):
        Server(self.compress(), x, y, z)

    def pack(self):
        ids = ''
        meta = ''
        light = ''
        sky = ''
        for i in range(0, 16 * 128 * 16, 2):
            b1 = self.blocks[i]
            b2 = self.blocks[i + 1]
            ids += chr(b1.id)
            ids += chr(b2.id)
            meta += chr((b2.meta << 4) | b1.meta)
            light += chr((b2.light << 4) | b1.light)
            sky += chr((b2.sky << 4) | b1.sky)

        return ids + meta + light + sky

    def compress(self):
        return compress(self.pack())


class Block:
    COLORS = [None,         # air
              "gray",       # stone
              "#009a00",    # grass
              "#644321",    # dirt
              "#666666",    # cobblestone
              "#b68b52",    # wood
              "#42ff20",    # sapling
              "#444444",    # bedrock
              "blue",       # water
              "blue",       # water
              "#ff5208",    # lava
              "#ff5208",    # lava
              "#e7e275",    # sand
              "#ab99a7",    # gravel
              "#eed814",    # gold ore
              "#d0c500",    # iron ore
              "#3e474e",    # coal ore
              "#412b15",    # wood
              "#26c822",    # leaves
              "#f4e50d",    # sponge
              "",           # glass
              "#0449ff",    # lapis lazuli ore
              "#0449ff",    # lapis lazuli
              "#333333",    # dispenser
              "#d9c473",    # sand stone
              "#412b15",    # note block
              "",           # bed
              "",           # powered rail
              "",           # detector rail
              "#333333",    # piston
              "",           # cobweb
              "",           # tall grass
              "",           # dead
              "#333333",    # piston
              "",           # piston extension
              "#111111",    # wool
              "",           # moved block
              "",           # dandelion
              "",           # rose
              "",           # brown mushroom
              "",           # red mushroom
              "#3e474e",    # gold block
              "#555555",    # iron block
              "#666666",    # double slabs
              "#666666",    # slabs
              "#d94c35",    # brick block
              "#d9180e",    # TNT
              "#b68b52",    # bookshelf
              "#586c50",    # moss stone
              "#999999",    # obsidian
              "",           # torch
              "",           # fire
              "#5f66e1",    # moster spawner
              "#b68b52",    # wooden stairs
              "#834c25",    # chest
              "",           # redstone wire
              "#64e9bd",    # diamond ore
              "#64e9bd",    # diamond block
              "#834c25",    # crafting table
              "#15c82c",    # seeds
              "#644321",    # farmland
              "#666666",    # furnace
              "#666666",    # burning furnace
              "",           # sign
              "#b68b52",    # door
              "",           # ladder
              "",           # rails
              "#666666",    # cobblestone stairs
              "",           # sign
              "",           # lever
              "",           # stone pressure plate
              "#888888",    # iron door
              "",           # wooden pressure plate
              "#a0111d",    # redstone ore
              "#a0111d",    # glowing redstone ore
              "",           # redstone torch
              "",           # redstone torch
              "",           # button
              "#111111",    # snow
              "#bbe7f3",    # ice
              "#111111",    # snow block
              "#0caa33",    # cactus
              "#a7bccc",    # clay
              "#62ff60",    # sugar cane
              "#834c25",    # jukebox
              "#b68b52",    # fence
              "#f9c308",    # pumpkin
              "#8e392e",    # netherrack
              "#8e6b54",    # soul sand
              "#ffeb13",    # glow stone
              "#c502a1",    # portal
              "#f9c308",    # jack-o-lantern
              "#8b4a28",    # cake
              "",           # repeater
              "",           # repeater
              "#834c25",    # locked chest
              "",           # trap door
              "#666666",    # hidden silverfish
              "#666666"     # stone brick
        ]

    def __init__(self, id=0, meta=0, light=15, sky=15):
        assert id >= 0 and id <= 255
        assert meta >= 0 and meta <= 15
        assert light >= 0 and light <= 15
        assert sky >= 0 and sky <= 15
        self.id = id
        self.meta = meta
        self.light = light
        self.sky = sky

    def color(self):
        if self.id < len(self.COLORS):
            return self.COLORS[self.id]
        else:
            return "#d916bb"


if __name__ == "__main__":
    c = Chunk()
    for x in range(16):
        for z in range(16):
            c.set(x, 0, z, Block(7))

    c.set(0, 1, 0, Block(50))
    c.set(0, 1, 15, Block(50))
    c.set(15, 1, 15, Block(50))
    c.set(15, 1, 0, Block(50))

    c.lighting()

    f = open("chunk", "w")
    f.write(c.compress())
    f.close()

    c.server()
