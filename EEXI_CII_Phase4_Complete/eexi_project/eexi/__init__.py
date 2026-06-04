"""
EEXI & CII Calculator Package
------------------------------
EEXI: IMO Resolution MEPC.350(78)
CII:  IMO Resolutions MEPC.352-355(78)
"""
from .calculator  import calculate
from .cii         import calculate_cii
from .ship_params import SHIP_PARAMS, SHIP_LABELS, CF_MAP, CF_LABELS

__version__ = "1.1.0"
__all__ = ["calculate", "calculate_cii", "SHIP_PARAMS", "SHIP_LABELS", "CF_MAP", "CF_LABELS"]
