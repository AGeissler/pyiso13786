#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Achim Geissler <achim.geissler@acatalepsy.ch>
# SPDX-License-Identifier: GPL-3.0-or-later
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
reinforced_concrete = Layer(
    name="reinforced concrete",
    thickness=0.18,
    material=mat.reinforced_concrete
)
aerated_concrete = Layer(
    name="aerated concrete",
    thickness=0.25,
    material=mat.aerated_concrete
)

# %%
# Define two construction systems, layers inside-to-outside.
wall_3c = Construction(name="3c", layers=[gypsum_plaster,
                                          reinforced_concrete,
                                          insulation190,
                                          gypsum_plaster])
wall_3d = Construction(name="3d", layers=[gypsum_plaster,
                                          aerated_concrete,
                                          insulation190,
                                          gypsum_plaster])

# %%
# Show property comparison.
plot_bar_chart_comparison([wall_3c, wall_3d], latex=True)
plt.show()
