"""
interpolator.py
---------------
Linear interpolation engine — ASME B31.3 §304.1.2 derivation style.

A straight line through (x1, y1) and (x2, y2) satisfies:

    y = (x2 - x) / (x2 - x1) * y1  +  (x1 - x) / (x1 - x2) * y2

Setting x = x3 gives the four formulas used here.

Rules (from project spec):
  - x values must be unique
  - y values must be unique
  - Exactly one of the six fields must be empty
"""

from __future__ import annotations
import math


FIELD_NAMES = ["x1", "y1", "x2", "y2", "x3", "y3"]

EPSILON = 1e-12   # near-zero denominator guard


def _fmt(v: float) -> str:
    """Round-trip float → clean string without trailing zeros."""
    if v == 0.0:
        return "0"
    # Up to 10 significant figures, strip trailing zeros
    s = f"{v:.10g}"
    return s


def calculate(inputs: dict) -> dict:
    """
    Solve for the one missing value using linear interpolation.

    Parameters
    ----------
    inputs : dict
        Keys: "x1", "y1", "x2", "y2", "x3", "y3"
        Exactly one value must be None / empty string / absent.
        All others must be finite floats (or numeric strings).

    Returns
    -------
    dict:
        blank_field  : str    Which field was solved
        result       : float  The computed value
        result_str   : str    Clean string representation
        all_values   : dict   Complete set of six values after solution
        formula_used : str    Human-readable formula
        steps        : list   Step-by-step derivation strings
    """
    # --- 1. Parse inputs ------------------------------------------------
    parsed: dict[str, float | None] = {}
    for key in FIELD_NAMES:
        raw = inputs.get(key, None)
        if raw is None or str(raw).strip() == "":
            parsed[key] = None
        else:
            try:
                v = float(raw)
                if not math.isfinite(v):
                    raise ValueError(f"Value for {key} is not finite.")
                parsed[key] = v
            except (TypeError, ValueError):
                raise ValueError(f"Invalid number for {key}: {raw!r}")

    # --- 2. Find blank field -------------------------------------------
    blanks = [k for k, v in parsed.items() if v is None]
    if len(blanks) != 1:
        raise ValueError(
            f"Exactly one field must be empty. "
            f"Found {len(blanks)} empty field(s): {blanks or 'none'}."
        )
    blank = blanks[0]

    # Convenience references
    x1 = parsed["x1"]
    y1 = parsed["y1"]
    x2 = parsed["x2"]
    y2 = parsed["y2"]
    x3 = parsed["x3"]
    y3 = parsed["y3"]

    # --- 3. Uniqueness checks (filled values only) ---------------------
    filled_x = [v for k, v in parsed.items() if k.startswith("x") and v is not None]
    filled_y = [v for k, v in parsed.items() if k.startswith("y") and v is not None]

    if len(filled_x) != len(set(filled_x)):
        raise ValueError("The x values must be unique.")
    if len(filled_y) != len(set(filled_y)):
        raise ValueError("The y values must be unique.")

    # --- 4. Solve -------------------------------------------------------
    result: float
    formula: str
    steps: list[str]

    if blank == "y3":
        # y3 = ((x2 - x3)*y1 + (x3 - x1)*y2) / (x2 - x1)
        denom = x2 - x1
        _check(denom, "x₂ − x₁", "x₁ and x₂ cannot be equal.")
        result = ((x2 - x3) * y1 + (x3 - x1) * y2) / denom
        formula = "y₃ = [(x₂ − x₃)·y₁ + (x₃ − x₁)·y₂] / (x₂ − x₁)"
        steps = [
            f"x₂ − x₁ = {x2} − {x1} = {x2 - x1}",
            f"x₂ − x₃ = {x2} − {x3} = {x2 - x3}",
            f"x₃ − x₁ = {x3} − {x1} = {x3 - x1}",
            f"Numerator = ({x2 - x3})×{y1} + ({x3 - x1})×{y2}",
            f"         = {(x2 - x3) * y1:.6g} + {(x3 - x1) * y2:.6g}",
            f"         = {(x2 - x3) * y1 + (x3 - x1) * y2:.6g}",
            f"y₃ = {(x2 - x3) * y1 + (x3 - x1) * y2:.6g} / {denom:.6g}",
            f"y₃ = {result:.10g}",
        ]

    elif blank == "x3":
        # x3 = ((y2 - y3)*x1 + (y3 - y1)*x2) / (y2 - y1)
        denom = y2 - y1
        _check(denom, "y₂ − y₁", "y₁ and y₂ cannot be equal.")
        result = ((y2 - y3) * x1 + (y3 - y1) * x2) / denom
        formula = "x₃ = [(y₂ − y₃)·x₁ + (y₃ − y₁)·x₂] / (y₂ − y₁)"
        steps = [
            f"y₂ − y₁ = {y2} − {y1} = {y2 - y1}",
            f"y₂ − y₃ = {y2} − {y3} = {y2 - y3}",
            f"y₃ − y₁ = {y3} − {y1} = {y3 - y1}",
            f"Numerator = ({y2 - y3})×{x1} + ({y3 - y1})×{x2}",
            f"         = {(y2 - y3) * x1:.6g} + {(y3 - y1) * x2:.6g}",
            f"         = {(y2 - y3) * x1 + (y3 - y1) * x2:.6g}",
            f"x₃ = {(y2 - y3) * x1 + (y3 - y1) * x2:.6g} / {denom:.6g}",
            f"x₃ = {result:.10g}",
        ]

    elif blank == "y1":
        # From: y3*(x2-x1) = (x2-x3)*y1 + (x3-x1)*y2
        # y1 = [y3*(x2-x1) - (x3-x1)*y2] / (x2-x3)
        denom = x2 - x3
        _check(denom, "x₂ − x₃", "x₂ and x₃ cannot be equal.")
        result = (y3 * (x2 - x1) - (x3 - x1) * y2) / denom
        formula = "y₁ = [y₃·(x₂−x₁) − (x₃−x₁)·y₂] / (x₂−x₃)"
        steps = [
            f"x₂ − x₁ = {x2 - x1}",
            f"x₃ − x₁ = {x3 - x1}",
            f"x₂ − x₃ = {x2 - x3}  (denominator)",
            f"Numerator = {y3}×({x2 - x1}) − ({x3 - x1})×{y2}",
            f"         = {y3 * (x2 - x1):.6g} − {(x3 - x1) * y2:.6g}",
            f"         = {y3 * (x2 - x1) - (x3 - x1) * y2:.6g}",
            f"y₁ = {y3 * (x2 - x1) - (x3 - x1) * y2:.6g} / {denom:.6g}",
            f"y₁ = {result:.10g}",
        ]

    elif blank == "y2":
        # y2 = [y3*(x2-x1) - (x2-x3)*y1] / (x3-x1)
        denom = x3 - x1
        _check(denom, "x₃ − x₁", "x₁ and x₃ cannot be equal.")
        result = (y3 * (x2 - x1) - (x2 - x3) * y1) / denom
        formula = "y₂ = [y₃·(x₂−x₁) − (x₂−x₃)·y₁] / (x₃−x₁)"
        steps = [
            f"x₂ − x₁ = {x2 - x1}",
            f"x₂ − x₃ = {x2 - x3}",
            f"x₃ − x₁ = {x3 - x1}  (denominator)",
            f"Numerator = {y3}×({x2 - x1}) − ({x2 - x3})×{y1}",
            f"         = {y3 * (x2 - x1):.6g} − {(x2 - x3) * y1:.6g}",
            f"         = {y3 * (x2 - x1) - (x2 - x3) * y1:.6g}",
            f"y₂ = {y3 * (x2 - x1) - (x2 - x3) * y1:.6g} / {denom:.6g}",
            f"y₂ = {result:.10g}",
        ]

    elif blank == "x1":
        # From rearranging: x1*(y2 - y3) = x2*(y1 - y3) + x3*(y2 - y1)  -- wait,
        # Full derivation:
        # y3*(x2-x1) = (x2-x3)*y1 + (x3-x1)*y2
        # y3*x2 - y3*x1 = x2*y1 - x3*y1 + x3*y2 - x1*y2
        # x1*(y2 - y3) = x2*(y1 - y3) + x3*(y2 - y1)   [collect x1 terms]
        # x1 = [x2*(y1-y3) + x3*(y2-y1)] / (y2-y3)
        denom = y2 - y3
        _check(denom, "y₂ − y₃", "y₂ and y₃ cannot be equal.")
        result = (x2 * (y1 - y3) + x3 * (y2 - y1)) / denom
        formula = "x₁ = [x₂·(y₁−y₃) + x₃·(y₂−y₁)] / (y₂−y₃)"
        steps = [
            f"y₁ − y₃ = {y1 - y3}",
            f"y₂ − y₁ = {y2 - y1}",
            f"y₂ − y₃ = {y2 - y3}  (denominator)",
            f"Numerator = {x2}×({y1 - y3}) + {x3}×({y2 - y1})",
            f"         = {x2 * (y1 - y3):.6g} + {x3 * (y2 - y1):.6g}",
            f"         = {x2 * (y1 - y3) + x3 * (y2 - y1):.6g}",
            f"x₁ = {x2 * (y1 - y3) + x3 * (y2 - y1):.6g} / {denom:.6g}",
            f"x₁ = {result:.10g}",
        ]

    elif blank == "x2":
        # Collect x2 terms:
        # y3*x2 - y3*x1 = x2*y1 - x3*y1 + x3*y2 - x1*y2
        # x2*(y3-y1) = y3*x1 - x3*y1 + x3*y2 - x1*y2  -- nope, rearrange properly:
        # x2*y3 - x2*y1 = ... collect x2:
        # x2*(y3-y1) = x1*(y3-y2) + x3*(y2-y1)
        # x2 = [x1*(y3-y2) + x3*(y2-y1)] / (y3-y1)
        denom = y3 - y1
        _check(denom, "y₃ − y₁", "y₁ and y₃ cannot be equal.")
        result = (x1 * (y3 - y2) + x3 * (y2 - y1)) / denom
        formula = "x₂ = [x₁·(y₃−y₂) + x₃·(y₂−y₁)] / (y₃−y₁)"
        steps = [
            f"y₃ − y₂ = {y3 - y2}",
            f"y₂ − y₁ = {y2 - y1}",
            f"y₃ − y₁ = {y3 - y1}  (denominator)",
            f"Numerator = {x1}×({y3 - y2}) + {x3}×({y2 - y1})",
            f"         = {x1 * (y3 - y2):.6g} + {x3 * (y2 - y1):.6g}",
            f"         = {x1 * (y3 - y2) + x3 * (y2 - y1):.6g}",
            f"x₂ = {x1 * (y3 - y2) + x3 * (y2 - y1):.6g} / {denom:.6g}",
            f"x₂ = {result:.10g}",
        ]
    else:
        raise RuntimeError(f"Unhandled blank field: {blank}")  # pragma: no cover

    if not math.isfinite(result):
        raise ValueError("Result is not finite — check for degenerate inputs.")

    # Build complete value set
    all_values = dict(parsed)
    all_values[blank] = result

    return {
        "blank_field":  blank,
        "result":       result,
        "result_str":   _fmt(result),
        "all_values":   {k: _fmt(v) for k, v in all_values.items()},
        "formula_used": formula,
        "steps":        steps,
    }


def _check(denom: float, label: str, message: str) -> None:
    if abs(denom) < EPSILON:
        raise ValueError(f"{message} (|{label}| < {EPSILON})")