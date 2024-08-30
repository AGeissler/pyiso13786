from dataclasses import dataclass
from typing import Optional


@dataclass
class Material:
    name: str
    thermal_conductivity: float  # lambda
    vapor_permeability: float  # mu
    density: float
    specific_heat: float


@dataclass
class Layer:
    name: str
    thickness: float  # in meters
    material: Material
    color: Optional[str] = "white"

    def __post_init__(self):
        self.thermal_conductivity=self.material.thermal_conductivity
        self.vapor_permeability=self.material.vapor_permeability
        self.density=self.material.density
        self.specific_heat=self.material.specific_heat

    # TODO add is_air

    @property
    def equivalent_thickness(self):
        "Equivalent diffusion air layer thickness sd, m"
        return self.thickness * self.vapor_permeability

    @property
    def thermal_resistance(self):
        "Thermal resistance R, m2 K/W"
        return self.thickness / self.thermal_conductivity
