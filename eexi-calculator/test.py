from eexi.calculator import calculate

data = {
    "ship_type": "bulk_carrier",
    "dwt": 75000,
    "mcr": 12000,
    "sfc": 175,
    "fuel": "hfo",
    "speed": 14.5
}

result = calculate(data)

print(result)