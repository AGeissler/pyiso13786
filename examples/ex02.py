r"""
Construction Parameters
-----------------------

.. topic:: Calculate various construction parameters according to ISO 13786 using ``pyiso13786``

   * Define layers based on available materials

   * Compare parameters of two construction systems.

(tbc)

"""
# Import
import matplotlib.pyplot as plt
#plt.style.use(["science", "retro", "no-latex"])

import pandas as pd

# Local imports
from pyiso13786.utils import plot_bar_chart_comparison
from pyiso13786 import Layer, Construction
from pyiso13786.material_db import material_db as mat

# %%
# Define necessary layers using available materials from
# :class:`pyiso13786.material_db.MaterialDataBase`.
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
stahlbeton = Layer(
    name="Stahlbeton",
    thickness=0.18,
    material=mat.stahlbeton
)
porenbeton = Layer(
    name="Porenbeton",
    thickness=0.25,
    material=mat.porenbeton
)

# %%
# Define two construction systems, layers inside-to-outside.
wall_3c = Construction(name="3c", layers=[gipsputz, stahlbeton, daemmung190, gipsputz])
wall_3d = Construction(name="3d", layers=[gipsputz, porenbeton, daemmung190, gipsputz])

# %%
# Show property comparison.
plot_bar_chart_comparison([wall_3c, wall_3d], latex=True)
plt.show()
