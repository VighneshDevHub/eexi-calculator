"""
calculators/linear_interpolator/calculator.py
-----------
Linear Interpolation calculator module.
"""

from .interpolator import calculate, FIELD_NAMES

def calculate_linear_interpolator(inputs: dict) -> dict:
    return calculate(inputs)
