.. _how-to:

How to use pyiso13786
=====================

Installation
------------

Install the package from the repository root:

.. code-block:: bash

   pip install -e .

Quick start
-----------

Create a simple wall and inspect its periodic thermal transmittance:

.. code-block:: python

   from ISO_13786 import Construction, Layer, Material
   from ISO_13786 import material_db as mat

   plaster = Layer(name="Plaster", thickness=0.015, material=mat.gipsputz)
   wall = Construction(name="sample wall", layers=[plaster])
   print(wall.periodic_thermal_transmittance())

Plotting
--------

You can compare several construction systems in a single chart:

.. code-block:: python

   from pyiso13786 import Construction, Layer, Material, plot_bar_chart_comparison
   import matplotlib.pyplot as plt

   wall_a = Construction(name="A", layers=[Layer(name="L1", thickness=0.1, material=mat.gipsputz)])
   wall_b = Construction(name="B", layers=[Layer(name="L2", thickness=0.2, material=mat.kalksandstein_md)])
   plot_bar_chart_comparison([wall_a, wall_b], latex=False)
   plt.show()

Working with spaces
-------------------

Use the :class:`pyiso13786.space.Space` class to calculate room-level properties such as
thermal capacity and glazing ratios.
