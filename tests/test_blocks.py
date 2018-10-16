import sys
import os

try:
    import api
except ModuleNotFoundError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

import unittest
from api import blocks


class BlockTestCase(unittest.TestCase):
    def test_get_from_blockstate(self):  # This is mostly just sanity checks
        air = blocks.Block.get_from_blockstate("minecraft:air")

        self.assertIsInstance(air, blocks.Block)
        self.assertEqual("minecraft", air.namespace)
        self.assertEqual("air", air.base_name)
        self.assertEqual({}, air.properties)
        self.assertEqual((), air.extra_blocks)
        self.assertEqual("minecraft:air", air.blockstate)

        stone = blocks.Block.get_from_blockstate("minecraft:stone")

        self.assertIsInstance(stone, blocks.Block)
        self.assertEqual("minecraft", stone.namespace)
        self.assertEqual("stone", stone.base_name)
        self.assertEqual({}, stone.properties)
        self.assertEqual((), stone.extra_blocks)
        self.assertEqual("minecraft:stone", stone.blockstate)

        self.assertNotEqual(air, stone)

        oak_leaves = blocks.Block.get_from_blockstate(
            "minecraft:oak_leaves[distance=1,persistent=true]"
        )

        self.assertIsInstance(oak_leaves, blocks.Block)
        self.assertEqual("minecraft", oak_leaves.namespace)
        self.assertEqual("oak_leaves", oak_leaves.base_name)
        self.assertEqual({"distance": "1", "persistent": "true"}, oak_leaves.properties)
        self.assertEqual((), oak_leaves.extra_blocks)
        self.assertEqual(
            "minecraft:oak_leaves[distance=1,persistent=true]", oak_leaves.blockstate
        )

    def test_extra_blocks(self):
        stone = blocks.Block.get_from_blockstate("minecraft:stone")
        water = blocks.Block.get_from_blockstate("minecraft:water[level=1]")
        granite = blocks.Block.get_from_blockstate("minecraft:granite")
        dirt = blocks.Block.get_from_blockstate("minecraft:dirt")

        conglomerate_1 = stone + water + dirt
        self.assertIsInstance(conglomerate_1, blocks.Block)
        self.assertEqual("minecraft", conglomerate_1.namespace)
        self.assertEqual("stone", conglomerate_1.base_name)
        self.assertEqual({}, conglomerate_1.properties)
        self.assertEqual(2, len(conglomerate_1.extra_blocks))
        for block_1, block_2 in zip(conglomerate_1.extra_blocks, (water, dirt)):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        conglomerate_2 = conglomerate_1 + granite
        self.assertIsInstance(conglomerate_2, blocks.Block)
        self.assertEqual("minecraft", conglomerate_2.namespace)
        self.assertEqual("stone", conglomerate_2.base_name)
        self.assertEqual({}, conglomerate_2.properties)
        self.assertEqual(3, len(conglomerate_2.extra_blocks))
        for block_1, block_2 in zip(
            conglomerate_2.extra_blocks, (water, dirt, granite)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        self.assertNotEqual(conglomerate_1, conglomerate_2)

        conglomerate_3 = conglomerate_2 - dirt
        self.assertIsInstance(conglomerate_3, blocks.Block)
        self.assertEqual("minecraft", conglomerate_3.namespace)
        self.assertEqual("stone", conglomerate_3.base_name)
        self.assertEqual({}, conglomerate_3.properties)
        self.assertEqual(2, len(conglomerate_3.extra_blocks))
        for block_1, block_2 in zip(conglomerate_3.extra_blocks, (water, granite)):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

    def test_remove_layer(self):
        stone = blocks.Block.get_from_blockstate("minecraft:stone")
        water = blocks.Block.get_from_blockstate("minecraft:water[level=1]")
        granite = blocks.Block.get_from_blockstate("minecraft:granite")
        dirt = blocks.Block.get_from_blockstate("minecraft:dirt")
        oak_log_axis_x = blocks.Block.get_from_blockstate("minecraft:oak_log[axis=x]")

        conglomerate_1 = stone + water + dirt + dirt + granite
        self.assertIsInstance(conglomerate_1, blocks.Block)
        self.assertEqual("minecraft", conglomerate_1.namespace)
        self.assertEqual("stone", conglomerate_1.base_name)
        self.assertEqual({}, conglomerate_1.properties)
        self.assertEqual(4, len(conglomerate_1.extra_blocks))
        for block_1, block_2 in zip(
            conglomerate_1.extra_blocks, (water, dirt, dirt, granite)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        new_conglomerate = conglomerate_1.remove_layer(1)
        for block_1, block_2 in zip(
            new_conglomerate.extra_blocks, (water, dirt, granite)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        conglomerate_2 = granite + water + stone + dirt + oak_log_axis_x
        self.assertIsInstance(conglomerate_2, blocks.Block)
        self.assertEqual("minecraft", conglomerate_2.namespace)
        self.assertEqual("granite", conglomerate_2.base_name)
        self.assertEqual({}, conglomerate_2.properties)
        self.assertEqual(4, len(conglomerate_2.extra_blocks))
        for block_1, block_2 in zip(
            conglomerate_2.extra_blocks, (water, stone, dirt, oak_log_axis_x)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        new_conglomerate = conglomerate_2.remove_layer(2)
        self.assertEqual(3, len(new_conglomerate.extra_blocks))
        for block_1, block_2 in zip(
            new_conglomerate.extra_blocks, (water, stone, oak_log_axis_x)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

    def test_hash(self):
        stone = blocks.Block.get_from_blockstate("minecraft:stone")
        water = blocks.Block.get_from_blockstate("minecraft:water[level=1]")
        granite = blocks.Block.get_from_blockstate("minecraft:granite")
        dirt = blocks.Block.get_from_blockstate("minecraft:dirt")

        conglomerate_1 = stone + water + dirt
        conglomerate_2 = stone + dirt + water

        self.assertNotEqual(conglomerate_1, conglomerate_2)
        self.assertNotEqual(hash(conglomerate_1), hash(conglomerate_2))

        conglomerate_3 = dirt + water + dirt
        conglomerate_4 = dirt + dirt + water

        self.assertNotEqual(conglomerate_3, conglomerate_4)
        self.assertNotEqual(hash(conglomerate_3), hash(conglomerate_4))

        conglomerate_5 = conglomerate_1 + granite
        conglomerate_6 = conglomerate_3 + granite

        self.assertNotEqual(conglomerate_1, conglomerate_5)
        self.assertNotEqual(conglomerate_3, conglomerate_6)
        self.assertNotEqual(conglomerate_5, conglomerate_6)
        self.assertNotEqual(hash(conglomerate_5), hash(conglomerate_6))


if __name__ == "__main__":
    unittest.main()
