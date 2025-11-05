from .construction import Construction
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_bar_chart_comparison(structures: list[Construction],
                               latex: bool = False) -> plt.Axes:
    """
    Make a bar plot comparasion. Resulting data are a little scaled
    due to very different values.

    https://stackoverflow.com/questions/14270391/python-matplotlib-multiple-bars
    """
    names = [struct.name for struct in structures]
    data = [struct.create_dict_valuable_properties() for struct in structures]

    df = pd.DataFrame(data, index=names)

    # Since numbers to compare are very different, we "scale" values.
    df["surface mass"] = df["surface mass"] / 100
    # periodischer Wärmedurchgangskoeffizient
    df["|Y12|"] = df["|Y12|"] * 100
    # daempfungsfaktor
    df["decrement factor"] = df["decrement factor"] * 10
    # innere waermekapazitaet
    df["internal area heat capacity"] = df["internal area heat capacity"] / 10

    ax = df.plot(
        kind="bar", rot=0, xlabel="Pareti", title="Comparison", figsize=(6, 4)
    )

    # Add some labels.
    for c in ax.containers:
        # set the bar label
        ax.bar_label(c, fmt="%.2f", label_type="edge")

    # Add a little space at the top of the plot for the annotation.
    ax.margins(y=0.5)

    if latex:
        custom_labels = [
            "$d_{tot}$ [m]",
            "R [m$^2$ K W$^{-1}$]",
            "m' [$\\times10^2$ kg m$^{-2}$]",
            "$|Y_{12}|$ [$\\times10^{-2}$ W m$^{-2}$ K$^{-1}$]",
            "$\varphi$ [h]",
            "f [$\\times10^{-1}$]",
            "$\kappa_1$ [$\\times10^{1}$ kJ m$^{-2}$ K$^{-1}$]",
        ]
    else:
        custom_labels = [
            "d_tot [m]",
            "R [m2 K W-1]",
            "m' [100 * kg m-1]",
            "|Y12| [0.01 *  W m-2 K-1]",
            "phi [h]",
            "f [* 0.1]",
            "k1 [10 * kJ m-2 K-1]",
        ]
    ax.legend(loc="upper center", labels=custom_labels, frameon=True, ncol=2)

    return ax

# https://stackoverflow.com/questions/12642256/find-area-of-polygon-from-xyz-coordinates
# Unit normal vector of plane defined by points a, b, and c.
def unit_normal(a, b, c):
    x = np.linalg.det([[1,a[1],a[2]],
         [1,b[1],b[2]],
         [1,c[1],c[2]]])
    y = np.linalg.det([[a[0],1,a[2]],
         [b[0],1,b[2]],
         [c[0],1,c[2]]])
    z = np.linalg.det([[a[0],a[1],1],
         [b[0],b[1],1],
         [c[0],c[1],1]])
    magnitude = (x**2 + y**2 + z**2)**.5
    return (x/magnitude, y/magnitude, z/magnitude)

# Area of polygon poly.
def poly_area(poly):
    if len(poly) < 3: # not a plane - no area
        return 0
    total = [0, 0, 0]
    N = len(poly)
    for i in range(N):
        vi1 = poly[i]
        vi2 = poly[(i+1) % N]
        prod = np.cross(vi1, vi2)
        total[0] += prod[0]
        total[1] += prod[1]
        total[2] += prod[2]
    result = np.dot(total, unit_normal(poly[0], poly[1], poly[2]))
    return abs(result/2)

def poly_side_lengths(poly):
    """Calculate the side-lengths of (rectangular) polygon. 'Side' is defined
       by the vertices being in the same x-plane or y-plane."""
    # Find the two points of interest.
    sorted_poly = sorted(poly, key=lambda x: x[0])

    p1 = np.array(list(sorted_poly[0]))
    p2 = np.array(list(sorted_poly[1]))
    p3 = np.array(list(sorted_poly[2]))

    squared_dist0 = np.sum((p1-p2)**2, axis=0)
    squared_dist1 = np.sum((p1-p3)**2, axis=0)

    # return values for x-plane, y-plane.
    return np.sqrt(squared_dist0), np.sqrt(squared_dist1)

# Bespoke dimension dict for roof-space type Space instances.
def create_dimension_dict(w_, d_, h_, h2_, tilt, gan):
    d2_ = d2_fun(tilt, h_, h2_, d_)

    dims = {
        'roof': [(0,0,h2_), (w_,0,h2_), (w_,d2_,h_), (0,d2_,h_)],
        'jamb wall': [(0,0,0), (w_,0,0), (w_,0,h2_), (0,0,h2_)],
        'west': [(0,0,0), (0,0,h2_), (0,d2_,h_), (0,d_,h_), (0,d_,0)],
        'north': [(0,d_,0), (0,d_,h_), (w_,d_,h_), (w_,d_,0)],
        'east': [(w_,0,0), (w_,d_,0), (w_,d_,h_), (w_,d2_,h_), (w_,0,h2_)],
        'floor': [(0,0,0), (0,d_,0), (w_,d_,0), (w_,0,0)],
        'ceiling': [(0,d2_,h_),(w_,d2_,h_), (w_,d_,h_), (0,d_,h_)]
    }

    dims['window'] = tilted_window_vertices(dims, gan)

    return dims

def d2_fun(a, h, h2, d, rnd=8):
    """Calculate y-value for 'tilted roof'-'ceiling' junction."""
    l = (h-h2)/round(np.cos(np.deg2rad(a)), rnd)
    return round(d - l*round(np.sin(np.deg2rad(a)), rnd), rnd)

def tilted_window_vertices(roof_space, glass_area_number):
    """Calculate vertices of glass/window inserted into the tilted roof
       with size 'glass_area_number'. Check first, if the desired size is
       realistic."""
    glass_area = glass_area_number*poly_area(roof_space['floor'])

    roof_area = poly_area(roof_space['roof'])

    if glass_area <= 0.9*roof_area:
        # Glass/window fits into roof assuming 10 % window frame area.
        size_percentage = np.sqrt(glass_area/roof_area)  # scale x,y!
        original_polygon = np.array(roof_space['roof'])
        centroid = np.mean(original_polygon, axis=0)
        scaled_polygon = (original_polygon - centroid)*size_percentage\
            + centroid
        return scaled_polygon.tolist()
    else:
        print(f"GAN={glass_area_number} is too large for roof space!")

    return None

