# Physics - Engine Design Library

Internal combustion engine design toolkit based on Machine Design textbook.

## Features

- **Piston Design** - Head thickness, rings, skirt, thermal analysis
- **Connecting Rod** - I-section optimization, buckling analysis, bearings
- **Crankshaft** - Stress analysis, fillet design, fatigue life
- **Cylinder** - Wall thickness, liner design, cooling system
- **Valve Train** - Valve, spring, seat, timing analysis
- **Thermodynamic Cycles** - Otto cycle, Diesel cycle, efficiency calculations

## Quick Start

```python
from engine.ic_engine.piston import PistonComplete

# Design a piston for 85mm bore engine
piston = PistonComplete(
    bore_mm=85,
    stroke_mm=88,
    max_gas_pressure_mpa=8.0,
    max_rpm=6500,
    reciprocating_mass_kg=0.45
)

# Get complete design report
piston.print_design_report()