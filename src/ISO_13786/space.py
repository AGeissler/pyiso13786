""" A class for a box-like space. 

    Width x height is the (internal) area of the (single) external wall
    which includes a window. The window area is calculated as

         window_area = facade_area x window_to_wall_ratio.

    where 'facade_area' refers to the facade area viewed from outside.
    """

import sys
from dataclasses import dataclass
import numpy as np
from .construction import Construction


@dataclass
class Space:
    """ Calculate heat capacity of box-like space. The basic assumption
    (for now) is that width x height is the (internal) area of the
    external wall which includes the window with a given (external)
    window-to-wall ratio.

    The seven construction types are given as a list of tuples, the first
    element is a descriptive string for which surface the construction
    is applied to. The strings are defined counterclockwise from the
    external wall (assuming a south facing external wall) followed by
    the window in the external wall:
      ext, win, east, north, west, floor, ceiling
    """
    name: str
    width: float
    height: float
    depth: float
    construction_list: list[(str, Construction)]
    orientation: str # S, SE, E, SW, W, NE, N, NW
    depth_factor: float = 2.5
    deeper_than: float = 4.0  # m
    window_to_wall_ratio: float = 0.6
    window_frame_fraction: float = 0.15

    def __post_init__(self):
        """ Do some checks and initialisations.
        """
        if len(self.construction_list) != 7:
            print(f"{len(self.construction_list)} construction types found."\
                    " Must be 7!")
            sys.exit(9)

        # Store actual space depth and net floor area.
        self.total_depth = self.depth
        self.net_floor_area = self.width*self.depth

        # Store external facade area based on mid-line dimensions used for
        # internal walls, floor and ceiling prior to any later rotation.
        # For brevity, it is assumed that internal walls and floor/ceiling
        # have the same thickness.
        self.facade_area = self.width*self.height  # ext including window
        self.facade_area += self.height*self.construction_list[2][1].thickness_tot()
        self.facade_area += self.width*self.construction_list[5][1].thickness_tot()
        self.facade_area += self.construction_list[2][1].thickness_tot()*\
                              self.construction_list[5][1].thickness_tot()

        # Set effective depth to be used, if less than actual depth,
        # ignore back wall entirely for subsequent calculations!
        self.ignore_north = False
        if self.depth > self.depth_factor*self.height:
            self.depth = self.depth_factor*self.height
            self.ignore_north = True

        # Set effective net floor area using effective depth.
        self.eff_net_floor_area = self.width*self.depth

        azimuth = ['S', 'SE', 'E', 'NE', 'N', 'NW', 'W', 'SW']

        # Get index of actual orientation as given in constructor.
        idx = next(i for i, v in enumerate(azimuth) if v == self.orientation)

        # Rotate azimuth list by idx.
        azimuth = azimuth[idx:] + azimuth[:idx]

        # Set azimuth for walls based on actual orientation, [S, E, N, W],
        # note that the facade has two construction systems.
        actual_azim = self.construction_list[1:5]
        actual_azim = [(azimuth[i*2], y) for i, (x, y) in enumerate(actual_azim)]
        # Duplicate actual_azim[0]
        actual_azim = [actual_azim[0]] + actual_azim
        self.construction_list = actual_azim[:5] + self.construction_list[5:]

    def surface_areas(self) -> np.ndarray:
        "Applicable surface area for each construction."
        if self.ignore_north is True:
            back_wall_area = 0
        else:
            back_wall_area = self.width*self.height

        ext_wall_area = max(0, self.width*self.height - self.window_area())

        s = np.array([ ext_wall_area,  # ext
                       self.window_area(),  # window
                       self.depth*self.height,  # side wall
                       back_wall_area,
                       self.depth*self.height,  # side wall
                       self.eff_net_floor_area,  # floor
                       self.depth*self.width  # ceiling
                       ])
        return s

    def energy_reference_area(self) -> float:
        """ SIA energy reference area of space defined when calling
            constructor. It is calculated with 'external' dimensions;
            mid-line dimensions are used for internal walls.
        """
        area = self.total_depth*self.width
        circumferencelist = [0, 2, 3, 4]

        for i in circumferencelist:
            area += self.construction_list[i][1].thickness_tot()/2

        return area

    def eff_energy_reference_area(self) -> float:
        """ Effective SIA energy reference area w/o 'deep area'. It is
            calculated with 'external' dimensions; mid-line dimensions
            are used for internal walls.
        """
        area = self.surface_areas()[4]  # floor
        circumferencelist = [0, 2, 4]

        if self.ignore_north is False:
            circumferencelist.append(3)

        for i in circumferencelist:
            area += self.construction_list[i][1].thickness_tot()/2

        return area

    def window_area(self) -> float:
        """ Window area calculated from external view WWR_e.
        """
        return self.facade_area*self.window_to_wall_ratio

    def window_fraction(self) -> float:
        """ Window fraction defined as window area per net floor area.
        """
        return self.window_area()/self.eff_net_floor_area

    def glass_area(self) -> float:
        """ Glass area in m2.
        """
        glazing_area = (1-self.window_frame_fraction)*self.window_area()

        return glazing_area

    def glass_to_wall_ratio(self) -> float:
        """ Glass to wall ratio defined as glazing area per internal
            wall area. This can be used as WWR for E+!
        """
        return self.glass_area()/(self.width*self.height)

    def glass_fraction(self) -> float:
        """ Glass fraction defined as glazing area per (external) facade
            area.
        """
        return self.glass_area()/self.facade_area

    def glass_area_number(self) -> float:
        """ Glass area number (Minergie) is defined as glazing area 
            per net floor area.
        """
        return self.glass_area()/self.eff_net_floor_area

    def opening_dimensions(self, high=False):
        """ Opening dimensions of a ventilation window based on the
            window fraction. It is assumed that 30 % of the frame area
            is part of the opening, i.e. 70 % of the frame are 'fixed'.
        """
        std_height = 1.55  # m
        opening_area = (1 - 0.7*self.window_frame_fraction)\
                                                    *self.window_area()
        if high:
            # Assume window is "as high as possible", i.e. spanning the
            # internal ceiling height. The clear opening is reduced by
            # the fixed fraction of the frame, only.
            o_height = (1 - 0.7*self.window_frame_fraction)*self.height
            o_width = opening_area/o_height
        else:
            # Assume "standard" height for window, i.e. usual dimension
            # for U-value and sound insulation measurements reduced by
            # the fixed fraction of the frame.
            # Make sure the corresponding window width is less than the
            # available space width!
            w_width = self.window_area()/std_height

            if w_width < self.width:
                o_height = 1.55*(1 - 0.7*self.window_frame_fraction)
                o_width = opening_area/o_height
            else:
                # Minimize height.
                o_width = self.width*(1 - 0.7*self.window_frame_fraction)
                o_height = opening_area/o_width

        return o_width, o_height, opening_area

    def net_deep_area(self) -> float:
        """ Calculate the net area of the space which lies
            more than 'deeper_than' away from the facade.

            This area is used for the calculation of internal lighting
            loads.
        """
        if self.total_depth > self.deeper_than:
            deep_area = self.width*(self.total_depth - self.deeper_than)
        else:
            deep_area = 0

        return deep_area

    def thermal_capacity(self) -> float:
        """ Space internal heat capacity per net floor area
            in Wh/(m2 K).
        """
        cr = 0
        area = self.surface_areas()
        for i in range(len(self.surface_areas())):
            cr += area[i]\
                  *self.construction_list[i][1].internal_area_heat_capacity()
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
        res += "net floor area = " + str(self.net_floor_area) + ", m2\n"
        res += "energy reference area = "\
               + str("%.3f" % round(self.energy_reference_area(), 3)) + ", m2\n"
        res += "surface areas = " + str(self.surface_areas()) + ", m2\n"
        res += "effective net floor area NGF = "\
               + str("%.3f" % round(self.eff_net_floor_area, 3)) + ", m2\n"
        res += "net deep area = " + str("%.3f" % round(self.net_deep_area(), 3)) + ", m2\n"
        res += "facade area A_W = " + str("%.3f" % round(self.facade_area, 3)) + ", m2\n"
        res += "window-to-wall ratio WWR_e = "\
                + str("%.3f" % round(self.window_to_wall_ratio, 3)) + "\n"
        res += "window area A_w = "\
               + str("%.3f" % round(self.window_area(), 3)) + ", m2\n"
        res += "glass area A_g = "\
               + str("%.3f" % round(self.glass_area(), 3)) + ", m2\n"
        res += "glass fraction A_g/A_W = "\
               + str("%.3f" % round(self.glass_fraction(), 3)) + ", %\n"
        res += "window fraction A_w/NGF = "\
               + str("%.3f" % round(self.window_fraction(), 3)) + ", %\n"
        res += "glass area number A_g/NGF = "\
               + str("%.3f" % round(self.glass_area_number(), 3)) + "\n"
        res += "glass-to-wall ratio GWR_i = "\
               + str("%.3f" % round(self.glass_to_wall_ratio(), 3)) + "\n"
        res += "opening dimensions (clear opening area = "\
               + str("%.3f" % round(self.opening_dimensions()[2], 3)) + ", m2):\n"
        res += "  high=False: w = "\
               + str("%.3f" % round(self.opening_dimensions()[0], 3)) + " m, h = "\
               + str("%.3f" % round(self.opening_dimensions()[1], 3)) + " m\n"
        res += "  high=True: w = "\
               + str("%.3f" % round(self.opening_dimensions(high=True)[0], 3)) + " m, h = "\
               + str("%.3f" % round(self.opening_dimensions(high=True)[1], 3)) + " m\n"
        res += "thermal capacity = "\
               + str("%.3f" % round(self.thermal_capacity(), 3)) + ", Wh/(m2 K)\n"
        res += "air volume = " + str("%.3f" % round(self.air_volume(), 3)) + ", m3\n"
        return res

    def dict_of_properties(self) -> dict:
        """Create dict of space properties.
        """
        return {
            "name": self.name,
            "net floor area": self.net_floor_area,
            "effective net floor area": self.eff_net_floor_area,
            "energy reference area": self.eff_energy_reference_area(),
            "surface areas": self.surface_areas(),
            "NGF": self.eff_net_floor_area,
            "deeper than": self.deeper_than,
            "net deep area": self.net_deep_area(),
            "A_W": self.facade_area,
            "WWR_e": self.window_to_wall_ratio,
            "A_w": self.window_area(),
            "A_g": self.glass_area(),
            "A_g/A_W": self.glass_fraction(),
            "A_w/NGF": self.window_fraction(),
            "A_g/NGF": self.glass_area_number(),
            "GWR_i": self.glass_to_wall_ratio(),
            "opening dimensions": self.opening_dimensions(),
            "opening dimensions high": self.opening_dimensions(high=True),
            "thermal capacity": self.thermal_capacity(),
            "air volume": self.air_volume()
        }
