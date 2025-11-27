from ISO_13786 import Material


glas = Material(
    name="Float Glas",
    density=2500,
    thermal_conductivity=1.0,
    specific_heat=750,
    vapor_permeability=1E12,
)
sperrholz_md = Material(
    name="Sperrholz mittl. Dichte",
    density=500,
    thermal_conductivity=0.13,
    specific_heat=1600,
    vapor_permeability=40.0,
)
parkett = Material(
    name="Parkett",
    density=1000,
    thermal_conductivity=0.24,
    specific_heat=1610,
    vapor_permeability=40.0,
)
leichtbauplatte_me = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Aussenwand, Innenwand, Decke 2
    name="Leichtbauplatte_ME",
    density=650,
    thermal_conductivity=0.13,
    specific_heat=1700,
    vapor_permeability=30.0,
)
daemmung_me = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Aussenwand, Decke 2
    name="Daemmung_ME",
    density=30.0,
    thermal_conductivity=0.041,
    specific_heat=1030,
    vapor_permeability=25.0,
)
trittschalldaemmung_me = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Boden
    name="Trittschalldaemmung_ME",
    density=48.0,
    thermal_conductivity=0.034,
    specific_heat=1030,
    vapor_permeability=25.0,
)
gipskarton = Material(
    name="Gipskarton",
    density=1150,
    thermal_conductivity=0.21,
    specific_heat=1100,
    vapor_permeability=5.0,
)
xlam = Material(
    name="X-LAM",
    density=500.0,
    thermal_conductivity=0.13,
    specific_heat=1600,
    vapor_permeability=25.0,
)
akustikpaneel = Material(
    name="Akustikpaneel",
    density=500.0,
    thermal_conductivity=0.10,
    specific_heat=1100,
    vapor_permeability=25.0,
)
daemmung190 = Material(
    name="Daemmung hoher Dichte",
    density=190,
    thermal_conductivity=0.043,
    specific_heat=2100,
    vapor_permeability=5.0,
)
gipsputz = Material(
    name="Gipsputz",
    density=1800,
    thermal_conductivity=0.9,
    specific_heat=1000,
    vapor_permeability=20.0,
)
unterlagsboden = Material(
    name="Unterlagsboden",
    density=2200,
    thermal_conductivity=1.5,
    specific_heat=1100,
    vapor_permeability=20.0,
)
unterlagsboden_me = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Boden
    name="Unterlagsboden_ME",
    density=1850,
    thermal_conductivity=1.2,
    specific_heat=850,
    vapor_permeability=15.0,
)
kalksandstein_md = Material(
    name="Kalksandstein mittel",
    density=1800,
    thermal_conductivity=1.0,
    specific_heat=900,
    vapor_permeability=10.0,
)
stahlbeton = Material(
    name="Stahlbeton",
    density=2300,
    thermal_conductivity=2.3,
    specific_heat=1000,
    vapor_permeability=130.0,
)
testbeton = Material( # https://quickfield.com/advanced/iso_13786_2007_case_d1.htm
    name="Testbeton",
    density=2400,
    thermal_conductivity=1.8,
    specific_heat=1000,
    vapor_permeability=130.0,
)
beton_me = Material( # Validierungsfaelle_HSLU_ME-SoWS-Tool, Boden, Decke 1, Decke 2
    name="Beton_ME",
    density=2400,
    thermal_conductivity=2.5,
    specific_heat=1000,
    vapor_permeability=150.0,
)
porenbeton = Material(
    name="Porenbeton",
    density=600,
    thermal_conductivity=0.3,
    specific_heat=1000,
    vapor_permeability=20.0,
)
