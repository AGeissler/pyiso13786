#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Achim Geissler <achim.geissler@acatalepsy.ch>
# SPDX-License-Identifier: GPL-3.0-or-later
r"""
Thermal Capacity of a Room
--------------------------

.. topic:: Calculate the thermal capacity of a room

   * Define layers based on available materials

   * Define a space

   * Evaluate thermal capacity

(tbc)

"""
# Import
import pandas as pd

# Local imports
from pyiso13786 import Material, Layer, Construction, Space
from pyiso13786.material_db import material_db as mat

# %%
# Define necessary layers using available materials from
# :class:`pyiso13786.material_db.MaterialDataBase`.
facade = Layer(
    name="facade",
    thickness=0.008,
    material=mat.glass
)
plasterboard = Layer(
    name="plasterboard",
    thickness=0.0125,
    material=mat.plasterboard
)
xlam = Layer( # https://xlam.co/
    name="X-LAM",
    thickness=0.096,
    material=mat.xlam
)
insulation190 = Layer(
    name="high density insulation",
    thickness=0.10,
    material=mat.insulation190
)
gypsum_plaster = Layer(
    name="gypsum plaster",
    thickness=0.015,
    material=mat.gypsum_plaster
)
calcium_silicate_md = Layer(
    name="calcium silicate brick medium density",
    thickness=0.125,
    material=mat.calcium_silicate_md
)
reinforced_concrete = Layer(
    name="reinforced concrete",
    thickness=0.18,
    material=mat.reinforced_concrete
)
test_concrete = Layer( # https://quickfield.com/advanced/iso_13786_2007_case_d1.htm
    name="test concrete",
    thickness=0.20,
    material=mat.test_concrete
)
aerated_concrete = Layer(
    name="aerated concrte",
    thickness=0.25,
    material=mat.aerated_concrete
)

# %%
# Define required construction systems, layers are given inside-to-outside.
window = Construction(name="window", layers=[facade])
wall_0a = Construction(name="0a", layers=[test_concrete])
wall_1a = Construction(name="1a", layers=[facade])
wall_1b = Construction(name="1b", layers=[gypsum_plaster,
                                          calcium_silicate_md,
                                          gypsum_plaster])
wall_3c = Construction(name="3c", layers=[gypsum_plaster,
                                          reinforced_concrete,
                                          insulation190,
                                          gypsum_plaster])
wall_3d = Construction(name="3d", layers=[gypsum_plaster,
                                          aerated_concrete,
                                          insulation190,
                                          gypsum_plaster])

floor_1a = Construction(name="floor", layers=[gypsum_plaster,
                                              reinforced_concrete,
                                              gypsum_plaster],
                        type="floor")
ceiling_1a = Construction(name="ceiling", layers=[gypsum_plaster,
                                                  reinforced_concrete,
                                                  gypsum_plaster],
                          type="ceiling")

# %%
# Define two rooms using :class:`pyiso13786.space.Space`.
room = Space(name="room", width=6.5, height=2.6, depth=8.5,
             construction_list=[('ext', wall_1a), ('win', window), ('east', wall_1b), 
                                ('north', wall_1b), ('west', wall_1b), 
                                ('floor', floor_1a), ('ceiling', ceiling_1a)],
             depth_factor = 5.0)

room_restricted = Space(name="room_restricted", width=6.5, height=2.6, depth=8.5,
             construction_list=[('ext', wall_1a), ('win', window), ('east', wall_1b), 
                                ('north', wall_1b), ('west', wall_1b), 
                                ('floor', floor_1a), ('ceiling', ceiling_1a)]
             )

# %%
# Evaluate thermal capacity of the rooms with and without size (depth) limit.
print(f"C_R/A_NGF, w/o room size limit: {room.thermal_capacity():.3f} Wh/(m2 K)")
print(f"C_R/A_NGF, w/ room size limit: {room_restricted.thermal_capacity():.3f} Wh/(m2 K)")
