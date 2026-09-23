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
fassade = Layer(
    name="Fassade",
    thickness=0.008,
    material=mat.glas
)
gipskarton = Layer(
    name="Gipskarton",
    thickness=0.0125,
    material=mat.gipskarton
)
xlam = Layer( # https://xlam.co/
    name="X-LAM",
    thickness=0.096,
    material=mat.xlam
)
daemmung190 = Layer(
    name="Daemmung hoher Dichte",
    thickness=0.10,
    material=mat.daemmung190
)
gipsputz = Layer(
    name="Gipsputz",
    thickness=0.015,
    material=mat.gipsputz
)
kalksandstein = Layer(
    name="Kalksandstein mittel",
    thickness=0.125,
    material=mat.kalksandstein_md
)
stahlbeton = Layer(
    name="Stahlbeton",
    thickness=0.18,
    material=mat.stahlbeton
)
testbeton = Layer( # https://quickfield.com/advanced/iso_13786_2007_case_d1.htm
    name="Testbeton",
    thickness=0.20,
    material=mat.testbeton
)
porenbeton = Layer(
    name="Porenbeton",
    thickness=0.25,
    material=mat.porenbeton
)

# %%
# Define required construction systems, layers are given inside-to-outside.
window = Construction(name="window", layers=[fassade])
wall_0a = Construction(name="0a", layers=[testbeton])
wall_1a = Construction(name="1a", layers=[fassade])
wall_1b = Construction(name="1b", layers=[gipsputz, kalksandstein, gipsputz])
wall_3c = Construction(name="3c", layers=[gipsputz, stahlbeton, daemmung190, gipsputz])
wall_3d = Construction(name="3d", layers=[gipsputz, porenbeton, daemmung190, gipsputz])

floor_1a = Construction(name="floor", layers=[gipsputz, stahlbeton, gipsputz],
                        type="floor")
ceiling_1a = Construction(name="ceiling", layers=[gipsputz, stahlbeton, gipsputz],
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
# Evaluate thermal capacity of the two rooms.
print(f"C_R/A_NGF, ohne Begrenzung: {room.thermal_capacity():.3f} Wh/(m2 K)")
print(f"C_R/A_NGF,  mit Begrenzung: {room_restricted.thermal_capacity():.3f} Wh/(m2 K)")
