from pint import UnitRegistry

unit_registry = UnitRegistry()
Quantity = unit_registry.Quantity

definitions = [
    'fraction = [] = frac',
    'percent = 1e-2 frac = pct',
    'ppm = 1e-6 fraction'
]

for d in definitions:
    unit_registry.define(d)


__all__ = [
    "Quantity"
]
