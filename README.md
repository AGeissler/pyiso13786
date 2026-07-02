# ISO 13786 - dynamic thermal characteristics

Python code for the calculation of the (24 h) periodic thermal characteristics of 
building components and spaces.

Based on the code by Nicola Meoli from the archive  https://github.com/sononicola/Static-and-Dynamic-thermal-characterics-of-buildings-components,
translated to english and extended by the class 'Space'.

## Usage
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
from ISO_13786 import plot_bar_chart_comparison

my_wall1 = Construction(name="mine", layers=[gipsputz, kalksandstein, gipsputz])
my_wall2 = Construction(name="mine", layers=[gipsputz, stahlbeton, gipsputz])
plot_bar_chart_comparasion([my_wall1, my_wall2], latex=True)
plt.show()
```
### Calculating room thermal capacity

Set up a room using class 'Space' after defining some additional construction
types.

```python
window = Construction(name="window", layers=[glass_006], partition=False)
floor = Construction(name="floor",
                     layers=[unterlagsboden_me, trittschalldaemmung_me, beton_me])
my_room = Space(name="my room", width=5.0, height=2.8, depth=4.0,
                construction_list=[('ext', my_wall),
                                   ('window', window),
                                   ('east', my_wall),
                                   ('north', my_wall),
                                   ('west', my_wall),
                                   ('floor', floor),
                                   ('ceiling', floor)],
                depth_factor = 2.5,
                deeper_than = 4.0,
                glass_area_number = 0.25,
                window_frame_fraction = 0.25,
                ceiling_split_fraction = 1.0,
                windows_in_two_facades = False,
                roof_space = False,
                jamb_height = 1.0,
                roof_tilt = 60)
```
Note that 'jamb_height' and 'roof_tilt' are not used if 'roof_space' is false.

Now look at some space values.

```python
print(f"C_R/A_NGF, w/o depth limit: {room.thermal_capacity():.3f}")
print(f"C_R/A_NGF,  w/ depth limit: {room_restricted.thermal_capacity():.3f}")
```

## Documentation
The project now includes a Sphinx documentation tree under [docs](docs). Build it locally with:

```bash
pip install -e .[docs]
make -C docs html
```

The generated API reference is based on the public classes and functions exported by the package.
