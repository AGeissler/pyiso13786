# ISO 13786 - dynamic thermal characteristics

Python code for the calculation of the (24 h) periodic thermal characteristics of 
building components.

Based on the code by Nicola Meoli from the archive https://github.com/sononicola/Static-and-Dynamic-thermal-characterics-of-buildings-components

## Usage:
### Simple example for a wall
After installing from the clone directory
```
pip install .
```
and then importing
```python
from ISO_13786 import Material, Layer, Construction, Space
from ISO_13786 import material_db as mat
```

Create the Layers of a compund wall
```python
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
```
Then set up a wall construction
```python
my_wall = Construction(name="mine", layers=[gipsputz, kalksandstein, gipsputz])
```
Finally, for example:
```python
print(my_wall.periodic_thermal_transmittance())
```
gives `0.???`

### Plotting a comparison between two Walls:
```python
from ISO_13786 import plot_bar_chart_comparasion

my_wall1 = Construction(name="mine", layers=[gipsputz, kalksandstein, gipsputz])
my_wall2 = Construction(name="mine", layers=[gipsputz, stahlbeton, gipsputz])
plot_bar_chart_comparasion([my_wall1, my_wall2], latex=True)
plt.show()
```
### Calculating room thermal capacity

```python
print(f"C_R/A_NGF, w/o depth limit: {room.thermal_capacity():.3f}")
print(f"C_R/A_NGF,  w/ depth limit: {room_restricted.thermal_capacity():.3f}")
```
