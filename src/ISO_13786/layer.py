import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class Material:
    """Thermal and hygric properties of a homogeneous material."""

    name: str
    thermal_conductivity: float  # lambda, W/(m K)
    vapor_permeability: float  # mu
    density: float  # kg/m3
    specific_heat: float  # J/(kg K)

    def __hash__(self):
        """Return a hash based on the material properties."""
        return hash((self.name,
                     self.thermal_conductivity,
                     self.vapor_permeability,
                     self.density,
                     self.specific_heat))

    def __eq__(self, other):
        """Return True when two materials have identical properties."""
        if not isinstance(other, Material):
            return NotImplemented
        return (
            self.name == other.name and
            self._float_eq(self.thermal_conductivity, other.thermal_conductivity) and
            self._float_eq(self.vapor_permeability, other.vapor_permeability) and
            self._float_eq(self.density, other.density) and
            self._float_eq(self.specific_heat, other.specific_heat)
        )

    @staticmethod
    def _float_eq(a: Optional[float], b: Optional[float], tol: float = 1e-9) -> bool:
        """Compare two floating-point values with a small tolerance."""
        # Handle cases where either or both are None
        if a is None or b is None:
            return a == b
        # Use math.isclose for floating-point comparison
        return math.isclose(a, b, abs_tol=tol)


@dataclass
class Layer:
    """A single layer in a construction assembly."""

    name: str
    thickness: float  # in meters
    material: Material
    color: Optional[str] = "white"

    def __post_init__(self):
        """Populate derived attributes from the underlying material."""
        self.thermal_conductivity = self.material.thermal_conductivity
        self.vapor_permeability = self.material.vapor_permeability
        self.density = self.material.density
        self.specific_heat = self.material.specific_heat

    def __hash__(self):
        """Return a hash based on the layer name, thickness, material and color."""
        return hash((self.name,
                     self.thickness,
                     self.material,
                     self.color))

    def __eq__(self, other):
        """Return True when two layers are equivalent."""
        if not isinstance(other, Layer):
            return NotImplemented
        return (
            self.name == other.name and
            self._float_eq(self.thickness, other.thickness) and
            self.material == other.material and
            self.color == other.color
        )

    @staticmethod
    def _float_eq(a: Optional[float], b: Optional[float], tol: float = 1e-9) -> bool:
        """Compare two floating-point values with a small tolerance."""
        # Handle cases where either or both are None
        if a is None or b is None:
            return a == b
        # Use math.isclose for floating-point comparison
        return math.isclose(a, b, abs_tol=tol)

    # TODO add is_air

    @property
    def equivalent_thickness(self):
        """Return the equivalent diffusion air layer thickness $s_d$ in metres."""
        return self.thickness * self.vapor_permeability

    @property
    def thermal_resistance(self):
        """Return the thermal resistance of the layer in metres squared kelvin per watt."""
        return self.thickness / self.thermal_conductivity

    def properties(self):
        """Return a dictionary of the layer properties for tabular output."""
        return {'name': self.name,  # layer name
                's (m)': self.thickness,
                'lam (W/(m K))': self.thermal_conductivity,
                'rho (kg/m3)': self.density,
                'c (J/(kg K))': self.specific_heat
                }
