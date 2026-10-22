# SPDX-FileCopyrightText: 2024 Achim Geissler <achim.geissler@acatalepsy.ch>
# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass

from pyiso13786 import Material

@dataclass
class MaterialDataBase:
    glass: Material = Material(
        name="float glass",
        density=2500,
        thermal_conductivity=1.0,
        specific_heat=750,
        vapor_permeability=1E12,
    )
    plywood_md: Material = Material(
        name="medium density plywood",
        density=500,
        thermal_conductivity=0.13,
        specific_heat=1600,
        vapor_permeability=40.0,
    )
    parquet: Material = Material(
        name="parquet",
        density=1000,
        thermal_conductivity=0.24,
        specific_heat=1610,
        vapor_permeability=40.0,
    )
    lightweight_panel_me: Material = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Aussenwand, Innenwand, Decke 2
        name="lightweight panel me",
        density=650,
        thermal_conductivity=0.13,
        specific_heat=1700,
        vapor_permeability=30.0,
    )
    insulation_me: Material = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Aussenwand, Decke 2
        name="insulation me",
        density=30.0,
        thermal_conductivity=0.041,
        specific_heat=1030,
        vapor_permeability=25.0,
    )
    impact_sound_insulation_me: Material = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Boden
        name="impact sound insulation me",
        density=48.0,
        thermal_conductivity=0.034,
        specific_heat=1030,
        vapor_permeability=25.0,
    )
    plasterboard: Material = Material(
        name="plasterboard",
        density=1150,
        thermal_conductivity=0.21,
        specific_heat=1100,
        vapor_permeability=5.0,
    )
    xlam: Material = Material(
        name="X-LAM",
        density=500.0,
        thermal_conductivity=0.13,
        specific_heat=1600,
        vapor_permeability=25.0,
    )
    acoustic_panel: Material = Material(
        name="acoustic panel",
        density=500.0,
        thermal_conductivity=0.10,
        specific_heat=1100,
        vapor_permeability=25.0,
    )
    insulation190: Material = Material(
        name="high density insulation",
        density=190,
        thermal_conductivity=0.043,
        specific_heat=2100,
        vapor_permeability=5.0,
    )
    gypsum_plaster: Material = Material(
        name="gypsum plaster",
        density=1800,
        thermal_conductivity=0.9,
        specific_heat=1000,
        vapor_permeability=20.0,
    )
    screed: Material = Material(
        name="screed",
        density=2200,
        thermal_conductivity=1.5,
        specific_heat=1100,
        vapor_permeability=20.0,
    )
    screed_me: Material = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Boden
        name="screed me",
        density=1850,
        thermal_conductivity=1.2,
        specific_heat=850,
        vapor_permeability=15.0,
    )
    calcium_silicate_md: Material = Material(
        name="calcium silicate brick medium density",
        density=1800,
        thermal_conductivity=1.0,
        specific_heat=900,
        vapor_permeability=10.0,
    )
    reinforced_concrete: Material = Material(
        name="reinforced concrete",
        density=2300,
        thermal_conductivity=2.3,
        specific_heat=1000,
        vapor_permeability=130.0,
    )
    test_concrete: Material = Material( # https://quickfield.com/advanced/iso_13786_2007_case_d1.htm
        name="test concrete",
        density=2400,
        thermal_conductivity=1.8,
        specific_heat=1000,
        vapor_permeability=130.0,
    )
    reinforced_concrete_me: Material = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Boden, Decke 1, Decke 2
        name="reinforced concrete me",
        density=2400,
        thermal_conductivity=2.5,
        specific_heat=1000,
        vapor_permeability=150.0,
    )
    aerated_concrete: Material = Material(
        name="aerated concrete",
        density=600,
        thermal_conductivity=0.3,
        specific_heat=1000,
        vapor_permeability=20.0,
    )

material_db = MaterialDataBase()
