r"""
Thermal Capacity of a Room
--------------------------

.. topic:: Calculate the thermal capacity of a room

   * Define materials

   * Define a space

   * Evaluate thermal capacity

(tbc)

"""
# Import
import matplotlib.pyplot as plt
#plt.style.use(["science", "retro", "no-latex"])

import pandas as pd

# Local imports
from ISO_13786.utils import plot_bar_chart_comparison
from ISO_13786 import Material, Layer, Construction, Space
from ISO_13786 import material_db as mat


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

# Set up construction systems, layers inside-to-outside.
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

#print(wall_0a.run_analysis())

#print(wall_3c.periodic_thermal_transmittance())
#print(wall_3c.thermal_diffusivities())
#print(wall_0a.create_dict_valuable_properties())
#print(wall_3c.create_dict_valuable_properties())
#print(wall_3d.create_dict_valuable_properties())

print(f"C_R/A_NGF, ohne Begrenzung: {room.thermal_capacity():.3f} Wh/(m2 K)")
print(f"C_R/A_NGF,  mit Begrenzung: {room_restricted.thermal_capacity():.3f} Wh/(m2 K)")

#plot_bar_chart_comparison([wall_3c, wall_3d], latex=True)
#plt.show()
