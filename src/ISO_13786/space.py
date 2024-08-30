""" A class for a box-like space. 
    
    The basic assumption (for now) is that width x height is the area of the 
    (single) external wall which includes glazing surfaces."""

import sys
from dataclasses import dataclass
import numpy as np
from .construction import Construction


@dataclass
class Space:
    """ Calculate heat capacity of box-like space. The basic assumption
    (for now) is that width x height is the area of the external wall
    (which includes any windows).

    The six construction types are given as a list of tuples, the first
    element is a descriptive string for which surface the construction
    covers. The strings are defined counterclockwise from the external
    wall (with naming assuming a south facing external wall).
    ext, east, north, west, floor, ceiling
    """
    name: str
    width: float
    height: float
    depth: float
    construction_list: list[(str, Construction)]
    orientation: str # S, SE, E, SW, W, NE, N, NW
    depth_factor: float = 2.5
    deeper_than: float = 4.0  # m
    opening_fraction: int = 5  # %

    def __post_init__(self):
        """ Do some checks and initialisations.
        """
        if len(self.construction_list) != 6:
            print(f"{len(self.construction_list)} construction types found."\
                    " Must be 6!")
            sys.exit(9)

        # Set effective depth to be used, if less than actual depth,
        # ignore back wall entirely!
        self.ignore_north = False
        if self.depth > self.depth_factor*self.height:
            self.depth = self.depth_factor*self.height
            self.ignore_north = True

        # Set effective net floor area using effective depth.
        self.eff_net_floor_area = self.width*self.depth

        azimuth = ['S', 'SE', 'E', 'NE', 'N', 'NW', 'W', 'SW']

        # Get index of orientation.
        idx = next(i for i, v in enumerate(azimuth) if v == self.orientation)

        # Rotate azimuth list by idx.
        azimuth = azimuth[idx:] + azimuth[:idx]

        # Set azimuth for walls based on actual orientation.
        actual_azim = self.construction_list[:4]
        actual_azim = [(azimuth[i*2], y) for i, (x, y) in enumerate(actual_azim)]
        self.construction_list = actual_azim[:4] + self.construction_list[4:]

    def surface_areas(self) -> np.ndarray:
        "Applicable surface area for each construction."
        if self.ignore_north is True:
            back_wall_area = 0
        else:
            back_wall_area = self.width*self.height

        s = np.array([self.width*self.height,  # ext
                       self.depth*self.height,  # side wall
                       back_wall_area,
                       self.depth*self.height,  # side wall
                       self.eff_net_floor_area,  # floor
                       self.depth*self.width  # ceiling
                       ])
        return s

    def energy_reference_area(self) -> float:
        """ SIA energy reference area calculated with external dimensions.
            Here, mid-line dimensions are used for internal walls
        """
        area = self.surface_areas()[4]  # floor
        circumferencelist = [0, 1, 3]

        if self.ignore_north is False:
            circumferencelist.append(2)

        for i in circumferencelist:
            area += self.construction_list[i][1].thickness_tot()/2

        return area

    def facade_area(self) -> float:
        """ External facade area, based on mid-line dimensions are used
            for internal walls, floor and ceiling.
        """
        area = self.surface_areas()[0]  # ext
        circumferencelist = [1, 3, 4, 5]

        for i in circumferencelist:
            area += self.construction_list[i][1].thickness_tot()/2

        return area

    def opening_dimensions(self, high=False):
        """ Opening dimensions of a ventilation window based on the
            opening fraction defined as opening area per net floor area.
        """
        accountable_floor_area = self.depth*self.width - self.deep_area()
        opening_area = accountable_floor_area*self.opening_fraction/100
        if high:
            # assume window is "as high as possible", i.e. internal ceiling
            # height assuming 15 % frame fraction.
            w_height = 0.85*self.height
        else:
            # assume "standard" height for window, i.e. usual dimension
            # for U-value and sound insulation measurements and assuming
            # 15 % frame fraction. << change to parameters? >>
            w_height = 1.55*0.85
        w_width = opening_area/w_height

        return w_width, w_height

    def deep_area(self) -> float:
        """ Calculate the energy reference area of the space which lies
            more than 'deeper_than' away from the facade.
        """
        circumferencelist = [0, 1, 3]

        if self.ignore_north is False:
            circumferencelist.append(2)

        if self.depth > self.deeper_than:
            deep_area = self.width*(self.depth - self.deeper_than)
            for i in circumferencelist:
                deep_area += self.construction_list[i][1].thickness_tot()/2
        else:
            deep_area = 0

        return deep_area

    def thermal_capacity(self) -> float:
        """ Space internal heat capacity per net floor area
            in Wh/(m2 K).
        """
        cr = 0
        area = self.surface_areas()
        for i in range(5):
            cr += area[i]*self.construction_list[i][1].\
                                       internal_areal_heat_capacity()
        return cr/self.eff_net_floor_area

    def air_volume(self) -> float:
        """ Internal air volume in m3.
        """
        return self.width*self.height*self.depth

    # ======== PRINTING RESULTS ========

    def show_properties(self) -> str:
        """Return space properties as single (multi-line) string
        """
        res = "Space '" + self.name + "':\n"
        res += "surface areas = " + str(self.surface_areas()) + ", m2\n"
        res += "energy reference area = "\
               + str("%.3f" % round(self.energy_reference_area(), 3)) + ", m2\n"
        res += "facade area = " + str("%.3f" % round(self.facade_area(), 3)) + ", m2\n"
        res += "opening dimensions (deeper_than = " + str(self.deeper_than)\
               + " m, opening_frac = " + str(self.opening_fraction) + " %):\n"
        res += "  high=False: w = "\
               + str("%.3f" % round(self.opening_dimensions()[0], 3)) + " m, h = "\
               + str("%.3f" % round(self.opening_dimensions()[1], 3)) + " m\n"
        res += "  high=True: w = "\
               + str("%.3f" % round(self.opening_dimensions(high=True)[0], 3)) + " m, h = "\
               + str("%.3f" % round(self.opening_dimensions(high=True)[1], 3)) + " m\n"
        res += "deep area = " + str("%.3f" % round(self.deep_area(), 3)) + ", m2\n"
        res += "thermal capacity = "\
               + str("%.3f" % round(self.thermal_capacity(), 3)) + ", Wh/(m2 K)\n"
        res += "air volume = " + str("%.3f" % round(self.air_volume(), 3)) + ", m3\n"
        return res

    def dict_of_properties(self) -> dict:
        """Create dict of space properties.
        """
        return {
            "name": self.name,
            "deeper than": self.deeper_than,
            "opening fraction": self.opening_fraction,
            "surface areas": self.surface_areas(),
            "energy reference area": self.energy_reference_area(),
            "net floor area": self.surface_areas()[4],
            "facade area": self.facade_area(),
            "opening dimensions": self.opening_dimensions(),
            "opening dimensions high": self.opening_dimensions(high=True),
            "deep area": self.deep_area(),
            "thermal capacity": self.thermal_capacity(),
            "air volume": self.air_volume()
        }
