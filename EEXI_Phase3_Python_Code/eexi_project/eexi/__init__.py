"""
EEXI Calculator Package
-----------------------
Web-based Energy Efficiency Existing Ship Index calculator.
IMO Resolution MEPC.350(78) compliant.
"""
from .calculator import calculate
from .ship_params import SHIP_PARAMS, SHIP_LABELS, CF_MAP, CF_LABELS

__version__ = "1.0.0"
__all__ = ["calculate", "SHIP_PARAMS", "SHIP_LABELS", "CF_MAP", "CF_LABELS"]
