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
from .utils import create_dimension_dict, poly_area, poly_side_lengths

@dataclass
class Space:
    """ Calculate heat capacity of a box-like space featuring one or two
    facades with a window. The glass area Ag is derived from given GAN and net
    floor area.
    (a) Window in one facade: Ag is inserted in external wall with dimensions
        width x height.
    (b) Windows in two facades: Ag/2 is inserted in each of the external walls
        (width x height, depth x height).

    Construction systems for space surfaces are given as a list of tuples,
    the first element is a descriptive string for which surface the
    construction is applied to. The strings are defined counterclockwise
    from the external wall (assuming a south facing external wall) followed
    by the window in the external wall:
      ext, win, east, north, west, floor, ceiling [, ceiling2]
      roof, win, jamb, east, north, west, floor, ceiling [, ceiling2]

    The second tuple element is an instance of class 'Construction'.

    If two windows are present (windows_in_two_facades == True), the
    construction system for 'west' is set to 'ext'.

    The optional 'ceiling2' covers a fraction of 'ceiling_split_fraction'
    of the total ceiling area and is assumed to be located away from the
    external facade(s) / the roof.
    """
    name: str
    width: float
    height: float
    depth: float
    construction_list: list[(str, Construction)]  # name, instance
    depth_factor: float = 2.5
    deeper_than: float = 4.0  # m
    glass_area_number: float = 0.54
    window_frame_fraction: float = 0.15
    ceiling_split_fraction: float = 1.0
    windows_in_two_facades: bool = False
    roof_space: bool = False
    jamb_height: float = 0.0  # Height of jamb wall (roof_space = True)
    roof_tilt: float = 60

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
                     self.windows_in_two_facades,
                     self.roof_space,
                     self.jamb_height,
                     self.roof_tilt
                     ))

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
            self.windows_in_two_facades == other.windows_in_two_facades and
            self.roof_space == other.roof_space and
            self._float_eq(self.jamb_height, other.jamb_height) and
            self._float_eq(self.roof_tilt, other.roof_tilt)
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
        if self.roof_space:
            # roof, win, jamb, east, north, west, floor, ceiling [, ceiling2]
            self.min_constructions = 8
            self.max_constructions = 9
            ext, win, jamb, east, north, west, floor, ceiling =\
                                                      0, 1, 2, 3, 4, 5, 6, 7
        else:
            # ext, win, east, north, west, floor, ceiling [, ceiling2]
            self.min_constructions = 7
            self.max_constructions = 8
            ext, win, east, north, west, floor, ceiling = 0, 1, 2, 3, 4, 5, 6

        if len(self.construction_list) < self.min_constructions:
            print(f"{len(self.construction_list)} construction types found."\
                   f" Must be at least {self.min_constructions}!")
            sys.exit(9)
        if len(self.construction_list) > self.max_constructions:
            print(f"{len(self.construction_list)} construction types found."\
                   f" Cannot be more than {self.max_constructions}!")
            sys.exit(9)
        if self.windows_in_two_facades and self.roof_space:
            print("Two windows not allowed for roof space!")
            sys.exit(9)

        if self.ceiling_split_fraction >= 0.98:
            self.construction_list = self.construction_list[:self.min_constructions]

        # Store actual space depth and net floor area.
        self.total_depth = self.depth
        self.net_floor_area = self.width*self.depth

        # Calculate total glass area.
        self.glass_area = self.glass_area_number*self.net_floor_area

        self.ignore_north = False
        if self.windows_in_two_facades:
            # With two windows present, full room *must* be considered. Also,
            # the construction for 'west' ("left of south") must be modified
            # to 'ext'.
            self.construction_list[west] = self.construction_list[ext]
        else:
            if not self.roof_space:
                # Set construction 'east' to construction 'west'. Necessary for
                # roll-back from a change in 'windows_in_two_facades' (only
                # possible for box-like space)!
                # << Todo: make "different internal walls" possible ...(!?) >>
                self.construction_list[east] = self.construction_list[west]
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
            self.facade_area[0] += self.height*self.construction_list[ext][1].thickness_tot()
            self.facade_area[1] += self.height*self.construction_list[ext][1].thickness_tot()
            # Add half of east and north walls each.
            self.facade_area[0] += 0.5*self.height*self.construction_list[east][1].thickness_tot()
            self.facade_area[1] += 0.5*self.height*self.construction_list[north][1].thickness_tot()
            # Add half of floor/ceiling each.
            self.facade_area[0] += 0.5*self.width*self.construction_list[floor][1].thickness_tot()
            self.facade_area[0] += 0.5*self.width*self.construction_list[ceiling][1].thickness_tot()
            self.facade_area[1] += 0.5*self.depth*self.construction_list[floor][1].thickness_tot()
            self.facade_area[1] += 0.5*self.depth*self.construction_list[ceiling][1].thickness_tot()
            # Add missing wall/ceiling corner areas.
            self.facade_area[1] += 0.5*(  # short wall, north partition
                self.width*self.construction_list[north][1].thickness_tot()*
                self.width*self.construction_list[floor][1].thickness_tot()+
                self.width*self.construction_list[north][1].thickness_tot()*
                self.width*self.construction_list[ceiling][1].thickness_tot()
                )
            self.facade_area[0] += 0.5*(  # long wall, east partition
                self.width*self.construction_list[east][1].thickness_tot()*
                self.width*self.construction_list[floor][1].thickness_tot()+
                self.width*self.construction_list[east][1].thickness_tot()*
                self.width*self.construction_list[ceiling][1].thickness_tot()
                )
        else:
            if self.roof_space:
                self.dim_dict = create_dimension_dict(self.width, self.depth,
                                                      self.height, self.jamb_height,
                                                      self.roof_tilt,
                                                      self.glass_area_number)
                self.roof_area = poly_area(self.dim_dict['roof'])
                # Add half of west and east wall cross-sections.
                l0 = poly_side_lengths(self.dim_dict['roof'])[0]
                self.roof_area += 0.5*l0*self.construction_list[east][1].thickness_tot()
                self.roof_area += 0.5*l0*self.construction_list[west][1].thickness_tot()
                # Add jamb wall cross-section (ToDo: calculate 'tilt-width').
                self.roof_area += 0.5*self.width*self.construction_list[floor][1].thickness_tot()
                # Add half of ceiling cross-section.
                self.roof_area += 0.5*self.width*self.construction_list[ceiling][1].thickness_tot()
            else:
                self.facade_area = self.width*self.height  # ext including window
                # Add half of west and east walls.
                self.facade_area += 0.5*self.height*self.construction_list[east][1].thickness_tot()
                self.facade_area += 0.5*self.height*self.construction_list[west][1].thickness_tot()
                # Add half of floor/ceiling each.
                self.facade_area += 0.5*self.width*self.construction_list[floor][1].thickness_tot()
                self.facade_area += 0.5*self.width*self.construction_list[ceiling][1].thickness_tot()
                # Add missing wall/ceiling corner areas.
                self.facade_area += 0.5*(  # long wall, east and west partitions
                    self.construction_list[east][1].thickness_tot()*
                    self.construction_list[floor][1].thickness_tot()+
                    self.construction_list[east][1].thickness_tot()*
                    self.construction_list[ceiling][1].thickness_tot()+
                    self.construction_list[west][1].thickness_tot()*
                    self.construction_list[floor][1].thickness_tot()+
                    self.construction_list[west][1].thickness_tot()*
                    self.construction_list[ceiling][1].thickness_tot()
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
            if self.roof_space:
                pass
                ext_wall_area = max(0, poly_area(self.dim_dict['roof'])\
                                                          - self.window_area())
                s = np.array([ ext_wall_area,  # roof
                               self.window_area(),  # window
                               self.jamb_height*self.width,  # jamb wall
                               poly_area(self.dim_dict['east']),  # side wall
                               back_wall_area,
                               poly_area(self.dim_dict['west']),  # side wall
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

        if len(self.construction_list) > self.min_constructions:
            # Add two surface values for ceilings.
            if self.roof_space:
                c0 = poly_area(self.dim_dict['ceiling'])
                surface_heavy = (1 - self.ceiling_split_fraction)*c0
                surface_light = c0 - surface_heavy
            else:
                surface_heavy = (1 - self.ceiling_split_fraction)*self.depth*self.width
                surface_light = self.depth*self.width - surface_heavy
            s = np.append(s, (surface_heavy, surface_light))
        else:
            if self.roof_space:
                s = np.append(s, poly_area(self.dim_dict['ceiling']))
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
        area = self.net_floor_area

        if self.roof_space:
            # roof, win, jamb, east, north, west, floor, ceiling [, ceiling2]
            circumferencelist = [2, 3, 4, 5]
        else:
            # ext, win, east, north, west, floor, ceiling [, ceiling2]
            circumferencelist = [0, 2, 3, 4]

        for i in circumferencelist:
            area += self.construction_list[i][1].thickness_tot()/2

        return area

    def eff_energy_reference_area(self) -> float:
        """ Effective SIA energy reference area w/o 'deep area'. It is
            calculated with 'external' dimensions; mid-line dimensions
            are used for internal walls.
        """
        area = self.eff_net_floor_area

        if self.roof_space:
            # roof, win, jamb, east, north, west, floor, ceiling [, ceiling2]
            circumferencelist = [2, 3, 5]
            north = 4
        else:
            # ext, win, east, north, west, floor, ceiling [, ceiling2]
            circumferencelist = [0, 2, 4]
            north = 3

        if self.ignore_north is False:
            circumferencelist.append(north)

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
        """ Overall (external) window-to-wall or window-to-roof ratio."""
        if self.windows_in_two_facades:
            return [0.5*self.window_area()/self.facade_area[0],
                    0.5*self.window_area()/self.facade_area[1]]
        else:
            if self.roof_space:
                return [self.window_area()/self.roof_area]
            return [self.window_area()/self.facade_area]

    def glass_to_wall_ratio(self) -> list:
        """ Glass to wall ratio defined as glazing area per internal
            wall area. For two windows it is assumed that the *glass area* is
            evenly distributed on the two facades.
            The glass-to-wall ratio can be used as WWR for E+ for box spaces!
        """
        if self.windows_in_two_facades:
            return [0.5*self.glass_area/(self.width*self.height),  # long wall
                    0.5*self.glass_area/(self.depth*self.height)]  # short wall
        else:
            if self.roof_space:
                return [self.glass_area/poly_area(self.dim_dict['roof'])]
            return [self.glass_area/(self.width*self.height)]

    def glass_fraction(self) -> list:
        """ Glass fraction defined as glazing area per (external) facade
            or roof area.
        """
        if self.windows_in_two_facades:
            return [0.5*self.glass_area/self.facade_area[0],  # long wall
                    0.5*self.glass_area/self.facade_area[1]]  # short wall
        else:
            if self.roof_space:
                return [self.glass_area/self.roof_area]
            return [self.glass_area/self.facade_area]

    def opening_dimensions(self, high=False):
        """ Opening dimensions of a ventilation window based on the
            window fraction. It is assumed that 30 % of the frame area
            is part of the opening, i.e. 70 % of the frame are 'fixed'.
        """
        std_height = 1.25  # m
        opening_area = (1 - 0.7*self.window_frame_fraction)\
                                                    *self.window_area()
        if high:
            # Assume window is "as high as possible", i.e. spanning the
            if self.roof_space:
                # available roof 'length' or
                l0 = poly_side_lengths(self.dim_dict['roof'])[0]
            else:
                # the internal ceiling height.
                l0 = self.height
            # Only the fixed frame fraction reduces the clear opening area.
            o_height = (1 - 0.7*self.window_frame_fraction)*l0
            o_width = opening_area/o_height
        else:
            # Assume "standard" height for window, i.e. usual dimension
            # for U-value and sound insulation measurements reduced by
            # the fixed fraction of the frame. Make sure the corresponding
            # window width is less than the available space width!
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
        if self.roof_space:
            return round(poly_area(self.dim_dict['west'])*self.width, 3)
        return self.width*self.height*self.depth

    def properties(self):
        """Dict of (a few) space properties"""
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
        if self.roof_space:
             res += f"roof area A_R = {np.round(self.roof_area, decimals=3)} m2\n"
        else:
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
        if self.roof_space:
            ext_key = 'A_R'
            ext_val = round(self.roof_area, 3)
        else:
            ext_key = 'A_W'
            ext_val = round(self.facade_area, 3)

        return {
            "name": self.name,
            "net floor area": self.net_floor_area,
            "effective net floor area": self.eff_net_floor_area,
            "energy reference area": self.eff_energy_reference_area(),
            "surface areas": self.surface_areas(),
            "NGF": self.eff_net_floor_area,
            "deeper than": self.deeper_than,
            "net deep area": self.net_deep_area(),
            ext_key: ext_val,
            "ceiling split fraction": self.ceiling_split_fraction,
            "windows in two facades": str(self.windows_in_two_facades),
            "WWR_e": self.window_to_wall_ratio(),  # roof_space (key)!
            "A_w": self.window_area(),
            "A_g": self.glass_area,
            "A_g/A_W": self.glass_fraction(),  # roof_space (key)!
            "A_w/NGF": self.window_fraction(),
            "A_g/NGF": self.glass_area_number,
            "GWR_i": self.glass_to_wall_ratio(),
            "opening dimensions": self.opening_dimensions(),
            "opening dimensions high": self.opening_dimensions(high=True),
            "thermal capacity": self.thermal_capacity(),
            "air volume": self.air_volume()
        }
