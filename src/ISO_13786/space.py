""" A class for a box-like space.

    Width x height (w x h + d x h) is the (internal) area of the external wall
    (external walls) which include a window (include windows). The window area
    is calculated as

         window_area = facade_area x window_to_wall_ratio.

    where 'facade_area' refers to the facade area viewed from outside using
    'ceiling' thickness and ignoring the optional 'ceiling_2'.
    """

import sys
import math
from dataclasses import dataclass
from typing import Optional
import pandas as pd
import numpy as np

# Local imports
from .construction import Construction


@dataclass
class Space:
    """ Calculate heat capacity of a box-like space featuring one or two
    facades with a window. The glass area Ag is derived from given GAN and net
    floor area.
    (a) Window in one facade: Ag is inserted in external wall with dimensions
        width x height.
    (b) Windows in two facades: Ag/2 is inserted in each of the external walls
        (width x height, depth x height).

    Construction types for space surfaces are given as a list of tuples,
    the first element is a descriptive string for which surface the
    construction is applied to. The strings are defined counterclockwise
    from the external wall (assuming a south facing external wall) followed
    by the window in the external wall:
      ext, win, east, north, west, floor, ceiling [, ceiling2]

    If two windows are present (windows_in_two_facades == True), the
    construction system for 'east' is set to 'ext'.

    The optional 'ceiling2' covers a fraction of 'ceiling_split_fraction'
    of the total ceiling area and is assumed to be in located away from the
    external facade(s).
    """
    name: str
    width: float
    height: float
    depth: float
    construction_list: list[(str, Construction)]
    depth_factor: float = 2.5
    deeper_than: float = 4.0  # m
    glass_area_number: float = 0.54
    window_frame_fraction: float = 0.15
    ceiling_split_fraction: float = 1.0
    windows_in_two_facades: bool = False

    def __hash__(self):
        return hash((self.name,
                     self.width,
                     self.height,
                     self.depth,
                     tuple(self.construction_list),
                     self.depth_factor,
                     self.deeper_than,
                     self.glass_area_number,
                     self.window_frame_fraction,
                     self.ceiling_split_fraction,
                     self.windows_in_two_facades))

    def __eq__(self, other):
        if not isinstance(other, Space):
            return NotImplemented
        return (
            self.name == other.name and
            self._float_eq(self.width, other.width) and
            self._float_eq(self.height, other.height) and
            self._float_eq(self.depth, other.depth) and
            self.construction_list == other.construction_list and
            self._float_eq(self.depth_factor, other.depth_factor) and
            self._float_eq(self.deeper_than, other.deeper_than) and
            self._float_eq(self.glass_area_number,
                           other.glass_area_number) and
            self._float_eq(self.window_frame_fraction,
                           other.window_frame_fraction) and
            self._float_eq(self.ceiling_split_fraction,
                           other.ceiling_split_fraction) and
            self.windows_in_two_facades == other.windows_in_two_facades
        )

    @staticmethod
    def _float_eq(a: Optional[float], b: Optional[float], tol: float = 1e-9) -> bool:
        # Handle cases where either or both are None
        if a is None or b is None:
            return a == b
        # Use math.isclose for floating-point comparison
        return math.isclose(a, b, abs_tol=tol)

    def __post_init__(self):
        """ Do some checks and initialisations.
        """
        if len(self.construction_list) < 7:
            print(f"{len(self.construction_list)} construction types found."\
                   " Must be at least 7!")
            sys.exit(9)

        if len(self.construction_list) > 8:
            print(f"{len(self.construction_list)} construction types found."\
                   " Cannot be more than 8!")
            sys.exit(9)

        if self.ceiling_split_fraction >= 0.98:
            self.construction_list = self.construction_list[:7]

        # Store actual space depth and net floor area.
        self.total_depth = self.depth
        self.net_floor_area = self.width*self.depth

        # Calculate total glass area.
        self.glass_area = self.glass_area_number*self.net_floor_area

        self.ignore_north = False
        if self.windows_in_two_facades:
            # With two windows present, full room *must* be considered. Also,
            # the construction for 'east' must be modified to 'ext'.
            self.construction_list[2] = self.construction_list[0]
        else:
            # Set construction 'east' to construction 'west'. Necessary for
            # roll-back from a change in 'windows_in_two_facades'!
            # << Todo: make "different internal walls" possible ...(!!) >>
            self.construction_list[2] = self.construction_list[4]
            # Set effective depth to be used, if less than actual depth,
            # ignore back wall entirely for subsequent calculations!
            if self.depth > self.depth_factor*self.height:
                self.depth = self.depth_factor*self.height
                self.ignore_north = True

        # Set effective net floor area using effective depth.
        self.eff_net_floor_area = self.width*self.depth

        # Calculate external facade area based on mid-line dimensions used for
        # internal walls, floor and ceiling. For two windows, use external
        # dimensions for both external facades ('external dimension reference').
        if self.windows_in_two_facades:
            self.facade_area = []
            self.facade_area.append(self.height*self.width)  # long wall, [0]
            self.facade_area.append(self.height*self.depth)  # short wall, [1]
            # Add external wall corner.
            self.facade_area[0] += self.height*self.construction_list[0][1].thickness_tot()
            self.facade_area[1] += self.height*self.construction_list[0][1].thickness_tot()
            # Add half of west and north walls each.
            self.facade_area[0] += 0.5*self.height*self.construction_list[4][1].thickness_tot()
            self.facade_area[1] += 0.5*self.height*self.construction_list[3][1].thickness_tot()
            # Add half of floor/ceiling each.
            self.facade_area[0] += 0.5*self.width*self.construction_list[5][1].thickness_tot()
            self.facade_area[0] += 0.5*self.width*self.construction_list[6][1].thickness_tot()
            self.facade_area[1] += 0.5*self.depth*self.construction_list[5][1].thickness_tot()
            self.facade_area[1] += 0.5*self.depth*self.construction_list[6][1].thickness_tot()
            # Add missing wall/ceiling corner areas.
            self.facade_area[1] += 0.5*(  # short wall, north partition
                self.width*self.construction_list[3][1].thickness_tot()*
                self.width*self.construction_list[5][1].thickness_tot()+
                self.width*self.construction_list[3][1].thickness_tot()*
                self.width*self.construction_list[6][1].thickness_tot()
                )
            self.facade_area[0] += 0.5*(  # long wall, west partition
                self.width*self.construction_list[4][1].thickness_tot()*
                self.width*self.construction_list[5][1].thickness_tot()+
                self.width*self.construction_list[4][1].thickness_tot()*
                self.width*self.construction_list[6][1].thickness_tot()
                )
        else:
            self.facade_area = self.width*self.height  # ext including window
            # Add half of west and east walls.
            self.facade_area += 0.5*self.height*self.construction_list[2][1].thickness_tot()
            self.facade_area += 0.5*self.height*self.construction_list[4][1].thickness_tot()
            # Add half of floor/ceiling each.
            self.facade_area += 0.5*self.width*self.construction_list[5][1].thickness_tot()
            self.facade_area += 0.5*self.width*self.construction_list[6][1].thickness_tot()
            # Add missing wall/ceiling corner areas.
            self.facade_area += 0.5*(  # long wall, east and west partitions
                self.construction_list[2][1].thickness_tot()*
                self.construction_list[5][1].thickness_tot()+
                self.construction_list[2][1].thickness_tot()*
                self.construction_list[6][1].thickness_tot()+
                self.construction_list[4][1].thickness_tot()*
                self.construction_list[5][1].thickness_tot()+
                self.construction_list[4][1].thickness_tot()*
                self.construction_list[6][1].thickness_tot()+
                )

    def surface_areas(self) -> np.ndarray:
        "Applicable surface area for each construction."
        if self.ignore_north is True:
            back_wall_area = 0
        else:
            back_wall_area = self.width*self.height

        if self.windows_in_two_facades:
            ext_wall_area_1 = max(0, self.width*self.height\
                                     - 0.5*self.window_area())
            ext_wall_area_2 = max(0, self.depth*self.height\
                                     - 0.5*self.window_area())
            s = np.array([ ext_wall_area_1,  # ext 1
                           self.window_area(),  # window
                           ext_wall_area_2,  # ext 2
                           back_wall_area,
                           self.depth*self.height,  # side wall
                           self.eff_net_floor_area  # floor
                           ])
        else:
            ext_wall_area = max(0, self.width*self.height - self.window_area())
            s = np.array([ ext_wall_area,  # ext
                           self.window_area(),  # window
                           self.depth*self.height,  # side wall
                           back_wall_area,
                           self.depth*self.height,  # side wall
                           self.eff_net_floor_area  # floor
                           ])

        if len(self.construction_list) > 7:
            # Add two surface values for ceiling
            surface_heavy = (1 - self.ceiling_split_fraction)*self.depth*self.width
            surface_light = self.depth*self.width - surface_heavy
            s = np.append(s, (surface_heavy, surface_light))
        else:
            s = np.append(s, self.depth*self.width)  # ceiling

        return s

    def surface_internal_area_heat_capacities(self, Rs=True) -> np.ndarray:
        "Internal heat capacities for construction surfaces"
        c = []
        for con in self.construction_list:
            c.append(con[1].internal_area_heat_capacity(Rs=Rs))

        c = np.array(c)

        return c

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
        """ Window area calculated from glass area and frame fraction.
        """
        return self.glass_area*(1+self.window_frame_fraction)

    def window_fraction(self) -> float:
        """ Window fraction defined as window area per net floor area.
        """
        return self.window_area()/self.eff_net_floor_area

    def window_to_wall_ratio(self) -> list:
        """ Overall window-to-wall ratio."""
        if self.windows_in_two_facades:
            return [0.5*self.window_area()/self.facade_area[0],
                    0.5*self.window_area()/self.facade_area[1]]
        return [self.window_area()/self.facade_area]

    def glass_to_wall_ratio(self) -> list:
        """ Glass to wall ratio defined as glazing area per internal
            wall area. For two windows it is assumed that the *glass area* is
            evenly distributed on the two facades.
            The glass-to-wall ratio can be used as WWR for E+!
        """
        if self.windows_in_two_facades:
            return [0.5*self.glass_area/(self.width*self.height),  # long wall
                    0.5*self.glass_area/(self.depth*self.height)]  # short wall
        return [self.glass_area/(self.width*self.height)]

    def glass_fraction(self) -> list:
        """ Glass fraction defined as glazing area per (external) facade
            area.
        """
        if self.windows_in_two_facades:
            return [0.5*self.glass_area/self.facade_area[0],  # long wall
                    0.5*self.glass_area/self.facade_area[1]]  # short wall
        return [self.glass_area/self.facade_area]

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
        """ Calculate the net area of the space which lies more than
            'deeper_than' away from the facade. Valid only for a window in one
            facade!

            This area is used for the calculation of internal lighting
            loads.
        """
        if self.windows_in_two_facades is False:
            if self.total_depth > self.deeper_than:
                return self.width*(self.total_depth - self.deeper_than)
        return 0

    def thermal_capacity(self, Rs=True) -> float:
        """ Space internal heat capacity per net floor area in Wh/(m2 K).
        """
        cr = 0
        area = self.surface_areas()
        for i in range(len(self.surface_areas())):
            cr += area[i]\
                  *self.construction_list[i][1].internal_area_heat_capacity(Rs=Rs)
        return cr/self.eff_net_floor_area

    def air_volume(self) -> float:
        """ Internal air volume in m3.
        """
        return self.width*self.height*self.depth

    def properties(self):
        """Dict of space properties"""
        return {
            'name': self.name,  # space name
            'constructions': {loc: con.properties()
                              for loc, con in self.construction_list}
        }

    def properties_markdown(self):
        """Create DataFrame with multi-index for tabular markdown output"""
        the_multi_index = ['location', 'construction', 'layers']
        # Get all unique property names from all construction layers.
        property_columns = set()
        for construction in self.properties()['constructions'].values():
            for layer_data in construction['layers'].values():
                property_columns.update(layer_data.keys())
        property_columns.discard('name')  # Remove 'name' as it's already in the index

        # Extract data from the nested structure and store in bespoke list.
        data = []
        for location, construction in self.properties()['constructions'].items():
            for layer, layer_data in construction['layers'].items():
                # Create a row for each layer with all properties
                row = {
                    the_multi_index[0]: location,
                    the_multi_index[1]: construction['name'],
                    the_multi_index[2]: layer,
                    'layer_name': layer_data['name']
                }
                # Add all other properties dynamically.
                for prop in property_columns:
                    row[prop] = layer_data.get(prop, None)
                data.append(row)

        # Create the DataFrame.
        df = pd.DataFrame(data)

        # Set the multi-index.
        if not df.empty:
            df = df.set_index(the_multi_index)
            # Reorder columns to have 'name' first, then other properties.
            #col_order = ['layer_name'] + sorted([col for col in df.columns
            #                                         if col != 'layer_name'],
            #                                    reverse=True)
            sort_order = {'s': 0, 'l': 1, 'r': 2, 'c': 3}

            # Sort columns based on their first letter and then alphabetically within each group
            def get_sort_key(col):
                first_char = col[0].lower()
                return (sort_order.get(first_char, 99), col)  # Default to 99 for other letters

            # Get all columns except 'layer_name'
            other_columns = [col for col in df.columns if col != 'layer_name']

            # Put 'layer_name' first, sort others according to custom order.
            col_order = ['layer_name'] + sorted(other_columns, key=get_sort_key)

            df = df[col_order]

        return df

    # ======== PRINTING RESULTS ========

    def show_properties(self) -> str:
        """Return space properties as single (multi-line) string
        """
        res = f"Space '{self.name}':\n"
        res += f"net floor area = {self.net_floor_area} m2\n"
        res += f"energy reference area = {round(self.energy_reference_area(), 3)} m2\n"
        res += f"surface areas = {np.round(self.surface_areas(), decimals=3)} m2\n"
        heatcap = np.round(
            self.surface_internal_area_heat_capacities(Rs=True), decimals=3)
        res += f"surface heat cap = {heatcap} Wh/(m2 K)\n"
        res += f"effective net floor area NGF = {round(self.eff_net_floor_area, 3)} m2\n"
        res += f"net deep area = {round(self.net_deep_area(), 3)} m2\n"
        res += f"facade area A_W = {np.round(self.facade_area, decimals=3)} m2\n"
        res += f"ceiling split fraction = {self.ceiling_split_fraction}\n"
        res += f"windows in two facades is {str(self.windows_in_two_facades)}\n"
        res += f"window-to-wall ratio WWR_e = {np.round(self.window_to_wall_ratio(), decimals=3)}\n"
        res += f"window area A_w = {round(self.window_area(), 3)} m2\n"
        res += f"glass area A_g = {round(self.glass_area, 3)} m2\n"
        res += f"glass fraction A_g/A_W = {np.round(self.glass_fraction(), decimals=3)}\n"
        res += f"window fraction A_w/NGF = {round(self.window_fraction(), 3)}\n"
        res += f"glass area number A_g/NGF = {round(self.glass_area_number, 3)}\n"
        if self.windows_in_two_facades is False:
            res += f"glass-to-wall ratio GWR_i = {round(self.glass_to_wall_ratio()[0], 3)}\n"
        else:
            res += "glass-to-wall ratio GWR_i,long ="\
                   + f" {round(self.glass_to_wall_ratio()[0], 3)}\n"
            res += "glass-to-wall ratio GWR_i,short ="\
                   + f" {round(self.glass_to_wall_ratio()[1], 3)}\n"
        res += "opening dimensions (clear opening area = "\
               + f"{round(self.opening_dimensions()[2], 3)}, m2):\n"
        res += "  high=False: w = "\
               + f"{round(self.opening_dimensions()[0], 3)} m, h = "\
               + f"{round(self.opening_dimensions()[1], 3)} m\n"
        res += "  high=True: w = "\
               + f"{round(self.opening_dimensions(high=True)[0], 3)} m, h = "\
               + f"{round(self.opening_dimensions(high=True)[1], 3)} m\n"
        res += "thermal capacity w/ Rsi/e = "\
               + f"{round(self.thermal_capacity(), 3)} Wh/(m2 K)\n"
        res += "thermal capacity w/o Rsi/e = "\
               + f"{round(self.thermal_capacity(Rs=False), 3)} Wh/(m2 K)\n"
        res += f"air volume = {round(self.air_volume(), 3)} m3\n"
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
            "ceiling split fraction": self.ceiling_split_fraction,
            "windows in two facades": str(self.windows_in_two_facades),
            "WWR_e": self.window_to_wall_ratio(),
            "A_w": self.window_area(),
            "A_g": self.glass_area,
            "A_g/A_W": self.glass_fraction(),
            "A_w/NGF": self.window_fraction(),
            "A_g/NGF": self.glass_area_number,
            "GWR_i": self.glass_to_wall_ratio(),
            "opening dimensions": self.opening_dimensions(),
            "opening dimensions high": self.opening_dimensions(high=True),
            "thermal capacity": self.thermal_capacity(),
            "air volume": self.air_volume()
        }
