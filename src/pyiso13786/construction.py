# SPDX-FileCopyrightText: 2020 Nicola Meoli and 2024 Achim Geissler <achim.geissler@acatalepsy.ch>
# SPDX-License-Identifier: GPL-3.0-or-later
import math
from dataclasses import dataclass
import numpy as np
from numpy.testing import assert_almost_equal
from .layer import Layer
import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional


@dataclass
class Construction:
    r"""A construction based on one or more material layers of given thickness.

    Parameters
    ----------
    name : str
        Name of the construction.
    layers : list
        List of layers.
    type : str (optional, default: 'wall')
        Construction type, one of 'wall', 'floor', 'ceiling'.
    partition : bool (optional, default: True)
        Toggle for construction boundary conditions, i.e. a partition is *not* external.
    temp_int : float (optional, default: 20)
        Internal boundary (air) temperature in (°C).
    temp_ext : float (optional, default: -5)
        External boundary (air) temperature in (°C).
    rel_hum_i : float (optional, default: 0.65)
        Relative humidity of internal air in (-).
    rel_hum_e : float (optional, default: 0.9)
        Relative humidity of external air in (-).
    time : int (optional, default: 24)
        Period length of attenuation in (h).

    Notes
    -----
    The element 'type' is the definition of the surface type, i.e. wall, floor, ceiling.
    If Construction.partion is `False`, the outside surface will have :math:`R_{se}` as
    external heat transfer resistance, otherwise :math:`R_{se}\,=\,R_{si}` by 'type'
    according to ISO 6946 [ISO6946]_.

    Layers are given from inside to outside.
    
    Equation numbers following equations refer to the number found in ISO 13786 [ISO13786]_.

    References
    ----------
    ..  [ISO6946] EN ISO 6946 (SIA 180.071), Building components and building elements
            - Thermal resistance and thermal transmittance - Calculation method
            (ISO 6946:2017), CEN - European Committee for Standardization, 2017.
    ..  [ISO13786] EN ISO 13786 (SIA 180.073), Thermal performance of building components
            - Dynamic thermal characteristics - Calculation methods (ISO 13786:2017),
            CEN - European Committee for Standardization, 2017.


    """

    def __init__(self, name, layers, type='wall', partition=True,
                 temp_int=20, temp_ext=-5, rel_hum_i=0.65, rel_hum_e=0.9, time=24):
        """Initialise a construction with layers and boundary conditions."""
        self.name = name
        self.layers = layers  # list[Layer,]
        # int, i = internal, ext, e = external :
        self.temp_int = temp_int  # Temperature in Celsius
        self.temp_ext= temp_ext
        self.rel_hum_i= rel_hum_i  # RHi
        self.rel_hum_e = rel_hum_e  # RHe
        self.time = time  # time of the analysis in hour
        self.type = type  # one of 'wall', 'floor', 'ceiling'
        self.partition = partition

        self.Rsi, self.Rse = self.heat_transfer_resistance(self.partition,
                                                           self.type)

    def __hash__(self):
        """Return a hash based on the construction definition."""
        return hash((self.name,
                     tuple(self.layers),
                     self.temp_int,
                     self.temp_ext,
                     self.rel_hum_i,
                     self.rel_hum_e,
                     self.Rsi,
                     self.Rse,
                     self.time,
                     self.partition))

    def __eq__(self, other):
        """Return True when two constructions describe the same assembly."""
        if not isinstance(other, Construction):
            return NotImplemented
        return (
            self.name == other.name and
            self.layers == other.layers and
            self._float_eq(self.temp_int, other.temp_int) and
            self._float_eq(self.temp_ext, other.temp_ext) and
            self._float_eq(self.rel_hum_i, other.rel_hum_i) and
            self._float_eq(self.rel_hum_e, other.rel_hum_e) and
            self._float_eq(self.Rsi, other.Rsi) and
            self._float_eq(self.Rse, other.Rse) and
            self._float_eq(self.time, other.time) and
            self.partition == other.partition
        )

    @staticmethod
    def _float_eq(a: Optional[float], b: Optional[float], tol: float = 1e-9) -> bool:
        """Compare two floating-point values with a small tolerance."""
        # Handle cases where either or both are None
        if a is None or b is None:
            return a == b
        # Use math.isclose for floating-point comparison
        return math.isclose(a, b, abs_tol=tol)

    @staticmethod
    def heat_transfer_resistance(partition, type):
        r"""Return internal and external heat transfer resistance chosen according to
        ISO 6946 [ISO6946]_ depending on construction situation and type.

        Parameters
        ----------
        partition : bool
            Toggle for construction boundary situation.
        type : str
            Construction type, one of 'wall', 'floor', 'ceiling'.

        Returns
        -------
        R_si, R_se : float
            Internal, external heat transfer resistance in :math:`m^2 W/K`.

        """
        if partition is True:
            # We have an internal construction.
            if type == 'wall':
                return 0.13, 0.13    # Rsi, Rse
            elif type == 'ceiling':
                return 0.10, 0.17
            return 0.17, 0.10
        # We have an external construction.
        if type == 'wall':
            return 0.13, 0.04
        elif type == 'ceiling':  # actually 'roof'
            return 0.10, 0.04
        return 0.17, 0.04  # floor above ambient

    def thicknesses(self) -> np.ndarray:
        r"""numpy.array with thickness of each Layer"""
        return np.array([layer.thickness for layer in self.layers])

    def thickness_tot(self) -> float:
        r"""numpy.array with the total thickness"""
        return np.sum(self.thicknesses())

    def thickness_cumsum(self) -> np.ndarray:
        r"""cumulative sum of thickness of each layer. Starting from 0"""
        s = np.cumsum(self.thicknesses(), dtype=float)
        s = np.insert(s, 0, 0.0)
        return s

    def thermal_conductivities(self) -> np.ndarray:
        r"""numpy.array with thermal conductivitiy :math:`\lambda` in W/(m K) of each
        layer."""
        return np.array([layer.thermal_conductivity for layer in self.layers])

    def vapor_permeabilities(self) -> np.ndarray:
        r"""numpy.array with vapor permeability of each layer."""
        return np.array([layer.vapor_permeability for layer in self.layers])

    def densities(self) -> np.ndarray:
        r"""numpy.array with density of each layer."""
        return np.array([layer.density for layer in self.layers])

    def specific_heats(self) -> np.ndarray:
        r"""numpy.array with specific heat of each layer."""
        return np.array([layer.specific_heat for layer in self.layers])

    # ======== STATIC ANALYSIS ========

    def equivalent_thicknesses(self) -> np.ndarray:
        r"""numpy.array with equivalent thickness :math:`S_d` in (m) of each layer."""
        return np.array([layer.equivalent_thickness for layer in self.layers])

    def equivalent_thickness_tot(self) -> float:
        r"""Sum of :math:`S_d` for all layers."""
        return np.sum(self.equivalent_thicknesses())

    def equivalent_thickness_cumsum(self) -> np.ndarray:
        r"""Cumulative sum of :math:`S_d` up to each layer. Starting from 0."""
        cum_sum = np.cumsum(self.equivalent_thicknesses(), dtype=float)
        cum_sum = np.insert(cum_sum, 0, 0.0)
        return cum_sum

    def thermal_resistances(self) -> np.ndarray:
        r"""Thermal resistance :math:`s/\lambda` in m2 K/W of each layer, with addition
        of the internal and external surface heat transfer resistance."""
        res = np.array([layer.thermal_resistance for layer in self.layers])
        res = np.insert(res, 0, self.Rsi)  # put Rsi as first layer
        res = np.append(res, self.Rse)  # append Rse as last layer

        return res

    def thermal_resistance_tot(self) -> float:
        r"""Total sum of the thermal resistances of all layers including internal and
        external heat transfer.

        :math:`R_{tot} = \sum{R_i}\text{  in }\frac{m^2 K}{W}`

        """
        return np.sum(self.thermal_resistances())

    def thermal_resistance_cumsum(self) -> np.ndarray:
        r"""Cumulative sum of the thermal resistances up to each layer.
        """
        cum_sum = np.cumsum(self.thermal_resistances(), dtype=float)
        return cum_sum

    def thermal_transmittance(self) -> float:
        r"""Thermal transmittance value.
        
        :math:`U = \frac{1}{R_{tot}\text{  in }\frac{W}{m^2 K}}`

        """
        return 1 / self.thermal_resistance_tot()

    def surface_temperatures(self) -> np.ndarray:
        r"""numpy.array of layer surface temperatures."""
        delta_temp = self.temp_int - self.temp_ext
        temp = self.temp_int - (
            (self.thermal_resistance_cumsum() * delta_temp)
            / self.thermal_resistance_tot()
        )
        temp = np.insert(temp, 0, self.temp_int)

        # Last term of temp array should be equal to temp_ext
        assert_almost_equal(temp[-1], self.temp_ext)

        return temp

    def saturation_pressures(self) -> np.ndarray:
        r"""Saturation pressure value :math:`p_{sat}` at each layer boundary temperature.
        """
        return np.array(
            [
                610.5 * np.exp(17.269 * temp / (237.3 + temp))
                if temp >= 0
                else 610.5 * np.exp(21.875 * temp / (265.5 + temp))
                for temp in self.surface_temperatures()
            ]
        )

    def internal_pressures(self) -> np.ndarray:
        r"""Partial vapor pressure at each layer boundary assuming
           a constant value for air vapor conductivity ('Dampfleitfaehigkeit').
        """
        p_int = self.rel_hum_i * self.saturation_pressures()[0]
        p_ext = self.rel_hum_e * self.saturation_pressures()[-1]
        delta_p = p_int - p_ext

        # 1:length-2 because we already know pressure at the boundaries.
        press = p_int - (
            (
                self.equivalent_thickness_cumsum()[
                    1 : len(self.saturation_pressures() - 2)
                ]
                * delta_p
            )
            / self.equivalent_thickness_tot()
        )
        press = np.insert(press, 0, p_int)

        # Last term of press array should be equal to p_ext
        assert_almost_equal(press[-1], p_ext)

        return press

    def plot_glaser(self, show_layer_color: bool = True, show_layer_name: bool = True):
        r"""Plot the Glaser diagram for the considered compound structure."""

        COLORS = [
            list(plt.rcParams["axes.prop_cycle"])[col]["color"]
            for col in range(len(list(plt.rcParams["axes.prop_cycle"])))
        ]  # colors from the matplotlib style
        LINEWIDTH = 1.5

        fig, axs = plt.subplots(2, 1, figsize=(18, 10), tight_layout=True)
        ax1, ax2 = axs

        # == Plot with Thickness as x axis == #
        if show_layer_color:
            for index, layer in enumerate(self.layers):
                ax1.axvspan(
                    self.thickness_cumsum()[index],
                    self.thickness_cumsum()[index + 1],
                    facecolor=layer.color,
                    alpha=0.2,
                )

        ax1.plot(
            self.thickness_cumsum(),
            self.surface_temperatures()[1:-1],
            label="Temperature",
            color=COLORS[0],
            linewidth=LINEWIDTH,
        )
        ax1.set_xlabel("Wall thickness (m)", fontsize=14)
        ax1.set_ylabel("Temperature (°C)", fontsize=14)
        ax1.grid(axis="both")
        ax1.set_xticks(self.thickness_cumsum())
        ax1.tick_params(axis="x", rotation=90)
        ax1.set_xlim(0, self.thickness_cumsum()[-1])

        ax11 = ax1.twinx()
        ax11.plot(
            self.thickness_cumsum(),  # TODO graph with normal thickness
            self.internal_pressures(),
            label="Druck",
            color=COLORS[1],
            linewidth=LINEWIDTH,
        )
        ax11.plot(
            self.thickness_cumsum(),
            self.saturation_pressures()[1:-1],
            label="Saturation pressure",
            color=COLORS[4],
            linewidth=LINEWIDTH,
        )
        ax11.set_ylabel("Pressure (Pa)", fontsize=14)
        ax11.grid(axis="both")

        fig.legend(loc="upper center", fontsize=12, frameon=True)
        # Scritta esterno e interno
        ax1.text(
            0.005,
            self.temp_ext,
            "Internal",
            rotation=90,
            horizontalalignment="center",
            verticalalignment="bottom",
            fontsize=10,
            #transform=fig.transFigure,
            bbox=dict(alpha=1, pad=5, facecolor="white", edgecolor="black"),
        )

        ax1.text(
            self.thickness_cumsum()[-1] - 0.005,
            self.temp_int,
            "External",
            rotation=90,
            horizontalalignment="center",
            verticalalignment="top",
            fontsize=10,
            #transform=fig.transFigure,
            bbox=dict(alpha=1, pad=5, facecolor="white", edgecolor="black"),
        )


        # Layers' names:
        if show_layer_name:
            x_pos = (
                self.thickness_cumsum()[1:] - self.thicknesses() / 2
            )  # x cumulative position in the middle of each layer
            for index, layer in enumerate(self.layers):
                ax1.text(
                    x_pos[index],
                    ax1.get_ylim()[1] / 2,
                    layer.name,
                    rotation=90,
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=10,
                    bbox=dict(alpha=1, pad=1, facecolor="white", edgecolor="black"),
                )

        # == Plot with Equivalent Thickness as x axis == #
        if show_layer_color:
            for index, layer in enumerate(self.layers):
                ax2.axvspan(
                    self.equivalent_thickness_cumsum()[index],
                    self.equivalent_thickness_cumsum()[index + 1],
                    facecolor=layer.color,
                    alpha=0.2,
                )

        ax2.plot(
            self.equivalent_thickness_cumsum(),
            self.surface_temperatures()[1:-1],
            label="Temperature",
            color=COLORS[0],
            linewidth=LINEWIDTH,
        )

        ax2.set_xlabel("Equivalent thickness sd (m)", fontsize=14)
        ax2.set_ylabel("Temperature (°C)", fontsize=14)
        ax2.grid(axis="both")
        ax2.set_xticks(self.equivalent_thickness_cumsum())
        ax2.tick_params(axis="x", rotation=90)
        ax2.set_xlim(0, self.equivalent_thickness_cumsum()[-1])

        ax22 = ax2.twinx()
        ax22.plot(
            self.equivalent_thickness_cumsum(),
            self.internal_pressures(),
            label="Pressure",
            color=COLORS[1],
            linewidth=LINEWIDTH,
        )
        ax22.plot(
            self.equivalent_thickness_cumsum(),
            self.saturation_pressures()[1:-1],
            label="Saturation Pressure",
            color=COLORS[4],
            linewidth=LINEWIDTH,
        )
        ax22.set_ylabel("Pressure (Pa)", fontsize=14)
        ax22.grid(axis="both")

        # ax2.legend(loc="best", fontsize=12, frameon=True)

        # Layers' names:
        if show_layer_name:
            x_pos = (
                self.equivalent_thickness_cumsum()[1:]
                - self.equivalent_thicknesses() / 2
            )  # x cumulative position in the middle of each layer
            for index, layer in enumerate(self.layers):
                ax2.text(
                    x_pos[index],
                    ax2.get_ylim()[1] / 2,
                    layer.name,
                    rotation=90,
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=10,
                    bbox=dict(alpha=1, pad=1, facecolor="white",
                              edgecolor="black"),
                )
        fig.subplots_adjust(hspace=10)
        return fig

    # ======== DYNAMIC ANALYSIS ========
    # Calculation according to ISO 13768:2017, chapters 7 and 8.
    # Equation numbers refer to this standard.
    def delta(self) -> np.ndarray:
        r"""Periodic penetration depth :math:`\delta`, eq. (11) for period T in (s).

        :math:`\delta = \sqrt{\frac{\lambda\,T}{\pi\,\rho\,c_p}}`

        """
        # TIME: hour to seconds
        return np.sqrt(
            (self.thermal_conductivities() * self.time * 3600)
            / (np.pi * self.densities() * self.specific_heats())
        )

    def xi(self) -> np.ndarray:
        """eq. (13)"""
        return self.thicknesses() / self.delta()

    def layer_transfer_matrix(self) -> list[np.ndarray]:
        """ Calculate layer transfer matrix W for each construction
            layer, eq. (14)."""
        xi = self.xi()
        delta = self.delta()
        thermal_conductivity = self.thermal_conductivities()

        zz: list[np.ndarray] = []  # zz : list of layer matrices W
        for i in range(0, len(xi)):
            # z : matrix for each layer of type complex float
            z = np.zeros((2, 2), dtype=np.complex128)
            z[0][0] = complex(
                (np.cosh(xi[i]) * np.cos(xi[i])), (np.sinh(xi[i]) * np.sin(xi[i]))
            )
            z[1][1] = z[0][0]
            z[0][1] = -(delta[i] / (2 * thermal_conductivity[i])) * complex(
                (np.sinh(xi[i]) * np.cos(xi[i]) + np.cosh(xi[i]) * np.sin(xi[i])),
                (np.cosh(xi[i]) * np.sin(xi[i]) - np.sinh(xi[i]) * np.cos(xi[i])),
            )
            z[1][0] = -(thermal_conductivity[i] / (delta[i])) * complex(
                (np.sinh(xi[i]) * np.cos(xi[i]) - np.cosh(xi[i]) * np.sin(xi[i])),
                (np.sinh(xi[i]) * np.cos(xi[i]) + np.cosh(xi[i]) * np.sin(xi[i])),
            )
            # Append to list 'zz'
            zz.append(z)
        return zz

    def construction_transfer_matrix(self, Rs=True) -> np.ndarray:
        """ Calculate construction transfer matrix, optionally include
            surface resistances (eq. (16)).

            :math:`Z = W_N * W_{N-1} * ... * W_1`

        """
        zz = self.layer_transfer_matrix()

        Z = np.zeros((2, 2), dtype=np.complex128)
        Z = zz[-1]  # Z_N
        for i in range(1, len(zz)):  # [1  2 ... N  N+1)
            Z = Z.dot(zz[-1 - i])  # scalar product

        if Rs:
            # Internal heat transfer coefficient, eq. (18).
            Zsi = np.array(
                [
                    [complex(1, 0), complex(-self.Rsi)],
                    [complex(0, 0), complex(1, 0)],
                ],
                dtype=np.complex128,
            )

            # External heat transfer coefficient, eq. (18).
            Zse = np.array(
                [
                    [complex(1, 0), complex(-self.Rse)],
                    [complex(0, 0), complex(1, 0)],
                ],
                dtype=np.complex128,
            )

            # Eq. (17)., as Z is from outside to inside, start with Z_se. (?)
            Z = Zse.dot(Z)
            Z = Z.dot(Zsi)

        return Z

    def internal_thermal_admittance(self) -> float:
        r"""Y11 = -Z11/Z12, eq. (19)"""
        Zee = self.construction_transfer_matrix()

        Y11 = -Zee[0][0] / Zee[0][1]
        Y11 = np.sqrt((Y11.real) ** 2 + (Y11.imag) ** 2)  # the module

        return Y11

    def external_thermal_admittance(self, Rs=True) -> float:
        r"""Y22 = -Z22/Z12, eq. (19)"""
        Zee = self.construction_transfer_matrix(Rs=Rs)

        Y22 = -Zee[1][1] / Zee[0][1]
        Y22 = np.sqrt((Y22.real) ** 2 + (Y22.imag) ** 2)  # the module

        return Y22

    def internal_area_heat_capacity(self, Rs=True) -> float:
        r"""Internal area heat capacity :math:`k_1` in
        :math:`\text{Wh/(m}^{2 }\text{K)}` calculated according to eqn. :eq:`eq. (22)`.

        .. math:: 
           :label: eq. (22)

           k_1 &= \frac{1}{\omega}\left|\frac{(Z_{11}-1)}{Z_{12}}\right|\qquad\text{ eq. (22)} \\
               &= \frac{t}{2\pi} \sqrt{\left(\frac{Z_{11}-1}{Z_{12}}\right)^2}

        """
        Zee = self.construction_transfer_matrix(Rs=Rs)
        kappa = ((self.time * 3600)  # time in seconds
                  / (2 * np.pi)
                  * np.sqrt(
                      (((Zee[0][0] - 1) / Zee[0][1]).real) ** 2
                      + (((Zee[0][0] - 1) / Zee[0][1]).imag) ** 2
                  )) # J/(m2 K)

        return kappa/3600 # Wh/(m2 K)

    def external_area_heat_capacity(self, Rs=True) -> float:
        r"""External area heat capacity :math:`k_2` in 
        :math:`\text{Wh/(m}^{2 }\text{K)}` calculated according to eqn. :eq:`eq. (21)`.

        .. math::
           :label: eq. (21)

           k_2 &= \frac{1}{\omega}\left|\frac{(Z_{22}-1)}{Z_{12}}\right|\qquad\text{ eq. (23)} \\
               &= \frac{t}{2\pi} \sqrt{\left(\frac{Z_{22}-1}{Z_{12}}\right)^2}

        """
        Zee = self.construction_transfer_matrix(Rs=Rs)
        kappa = ((self.time * 3600)  # time in seconds
                  / (2 * np.pi)
                  * np.sqrt(
                      (((Zee[1][1] - 1) / Zee[0][1]).real) ** 2
                      + (((Zee[1][1] - 1) / Zee[0][1]).imag) ** 2
                  )) # J/(m2 K)
        return kappa/3600  # Wh/(m2 K)

    def periodic_thermal_transmittance(self) -> float:
        r"""Absolut value (modulus) of periodic thermal transmittance calculated acc.
        to eqn. :eq:`eq. (24)` in :math:`\text{W/(m}^{2 }\text{K)}`.

        .. math::
           :label: eq. (24)

           Y_{12} = -\frac{1}{Z_{12}}\qquad\text{ eq. (24)}

        """
        Y12 = -1 / self.construction_transfer_matrix()[0][1]
        # Modulus (absolute value) |Y12|.
        Y12 = np.sqrt((Y12.real) ** 2 + (Y12.imag) ** 2)

        return Y12  # W/(m2 K)

    def decrement_factor(self) -> float:
        r"""Decrement factor using the periodic thermal transmittance and overall
        transmittance acc. to eqn. :eq:`eq. (25)`.

        .. math::
           :label: eq. (25)

           f = \frac{\left|Y_{12}\right|}{U}\qquad\text{ eq. (25)}

        """
        return (
            self.periodic_thermal_transmittance() /
                                    self.thermal_transmittance()
        )

    def time_shift(self) -> float:
        """Time shift of periodic thermal transmittance, eq. (26)."""
        Zee = self.construction_transfer_matrix()
        # Time in hours
        return (
            (np.arctan2(Zee[0][1].imag, Zee[0][1].real)) *
                                               self.time / (2 * np.pi)
        )

    def phase_shift(self) -> float:
        r"""Phase shift of periodic thermal transmittance, eq. (??)."""
        return self.time_shift() + self.time / 2

    # ======== SOME COMPOUND STRUCTURE PROPERTIES ========
    def surface_mass(self) -> float:
        r"""Total surface mass of construction in kg/m2."""
        return np.sum(self.thicknesses() * self.densities())

    def static_heat_capacity(self) -> float:
        r"""Total static heat capacity of construction in J/(kg K)."""
        return np.sum(self.thicknesses() * self.densities() * self.specific_heats())

    def thermal_diffusivities(self) -> np.ndarray:
        r"""Thermal diffusivity of each layer in (m2/s)."""
        return (self.thermal_conductivities() / (
            self.densities() * self.specific_heats()
            )
        )

    def thermal_effusivities(self) -> np.ndarray:
        r"""Thermal effusivity of each layer in (W s0.5/(m2 K)). ((tbc))"""
        return np.sqrt(
            self.thermal_conductivities() * self.densities() * self.specific_heats()
        )

    def properties(self):
        r"""Dict of construction properties"""
        # Set up a list of generic layer names.
        laynam = []
        if len(self.layers) == 1:
            laynam.append('layer')
        else:
            laynam.append('inside')
            for i in range(len(self.layers[1:-1])):
                laynam.append('layer ' + str(i + 1))
            laynam.append('outside')

        return {
            'name': self.name,  # construction name
            'layers': {lay: self.layers[k].properties()
                                             for k, lay in enumerate(laynam)}
        }

    # ======== PRINTING RESULTS ========

    def run_analysis(self, rh=False, detailed=False) -> str:
        r"""Return (all) results as a string."""
        # TODO: Add formatting, parameter names and units for nicer output
        res = "\nConstruction '" + self.name + "':"
        res += '\nd_i          ' + str(self.thicknesses())
        res += '\nd_tot        ' + str(self.thickness_cumsum())
        if rh:
            res += '\nsd_i         ' + str(self.equivalent_thicknesses())
            res += '\nsd_tot       ' + str(self.equivalent_thickness_tot())
            res += '\nsd_x         ' + str(self.equivalent_thickness_cumsum())
            res += '\np_sat_i      ' + str(self.saturation_pressures())
            res += '\np_D_i        ' + str(self.internal_pressures())
            res += '\ntheta_s(i,e) ' + str(self.surface_temperatures())
        res += '\nR_i          ' + str(np.round(self.thermal_resistances(), decimals=3))
        if detailed:
            res += '\nR_ges        ' + str(self.thermal_resistance_tot())
            res += '\nR_x          ' + str(self.thermal_resistance_cumsum())
        res += '\nU            ' + str(np.round(self.thermal_transmittance(), decimals=2))
        res += '\ndelta        ' + str(np.round(self.delta(), decimals=3))
        res += f'\nU_{self.time}         ' + str(np.round(self.periodic_thermal_transmittance(), decimals=2))
        if detailed:
            res += '\na            ' + str(np.round(self.thermal_diffusivities(), decimals=3))
            res += '\nb            ' + str(np.round(self.thermal_effusivities(), decimals=3))
            res += '\nxi           ' + str(self.xi())
            res += '\nW_i          ' + str(self.layer_transfer_matrix())
            res += '\nZ w/o Rsi/e  ' + str(self.construction_transfer_matrix(Rs=False))
            res += '\nZ w/ Rsi/e   ' + str(self.construction_transfer_matrix())
            res += '\n|Y12|        ' + str(self.periodic_thermal_transmittance())
            res += '\nf            ' + str(self.decrement_factor())
            res += '\ndt           ' + str(self.time_shift())
            res += '\nphi          ' + str(self.phase_shift())
            res += '\nk1           ' + str(self.internal_thermal_admittance())
            res += '\nk2           ' + str(self.external_thermal_admittance())
        res += '\nc_int        ' + str(np.round(self.internal_area_heat_capacity(), decimals=3))
        return res

    def create_dict_valuable_properties(self) -> dict:
        r"""
        Used to create the bar plot for comparison of different
        constructions.

        The periodic thermal transmittance is given as an absolute value."""
        return {
            "overall thickness": self.thickness_tot(),
            "thermal resistance": self.thermal_resistance_tot(),
            "surface mass": self.surface_mass(),
            "|Y12|": self.periodic_thermal_transmittance(),
            "phase shift": self.phase_shift(),
            "decrement factor": abs(self.decrement_factor()),
            "internal area heat capacity": self.internal_area_heat_capacity(),
        }
