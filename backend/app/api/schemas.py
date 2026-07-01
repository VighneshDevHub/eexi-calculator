from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# EEXI Calculator Schemas
class EEXIRequest(BaseModel):
    vessel_name: Optional[str] = Field(None, description="Vessel name")
    ship_type: str = Field(..., description="Ship type (e.g., bulk_carrier)")
    dwt: Optional[float] = Field(None, description="Deadweight tonnage")
    gt: Optional[float] = Field(None, description="Gross tonnage")
    mcr: float = Field(..., description="Main engine MCR (kW)")
    sfc: float = Field(..., description="Specific fuel consumption (g/kWh)")
    fuel_type: str = Field(..., description="Fuel type (e.g., HFO, MDO)")
    speed: float = Field(..., description="Design speed (knots)")
    pae: Optional[float] = Field(0.0, description="Auxiliary engine power (kW)")
    sfc_ae: Optional[float] = Field(0.0, description="Auxiliary SFC (g/kWh)")
    fuel_type_ae: Optional[str] = Field(None, description="Auxiliary fuel type")
    f_eff: Optional[float] = Field(1.0, description="Efficiency factor")
    f_i: Optional[float] = Field(1.0, description="Innovation factor")
    f_w: Optional[float] = Field(1.0, description="Weather factor")
    user_local_time: Optional[str] = Field(None, description="User's local time")


class EEXIResponse(BaseModel):
    attained_eexi: float
    required_eexi: float
    status: str
    margin: Optional[float]
    vessel_id: Optional[int]
    vessel_name: Optional[str]


# CII Calculator Schemas
class CIIRequest(BaseModel):
    ship_type: str = Field(..., description="Ship type")
    year: int = Field(..., description="Year for CII calculation")
    # Add more fields as needed based on your CII calculator


class CIIResponse(BaseModel):
    attained_cii: float
    required_cii: float
    rating: Dict[str, Any]


# EGBP Calculator Schemas
class EGBPElement(BaseModel):
    element_type: str
    # Add specific fields based on your EGBP calculator elements


class EGBPRequest(BaseModel):
    mass_flow_kgs: float = Field(..., description="Mass flow rate (kg/s)")
    temp_tc_c: float = Field(..., description="Temperature at TC (°C)")
    max_bp_pa: float = Field(..., description="Maximum back pressure (Pa)")
    elements: List[EGBPElement] = Field(..., description="List of exhaust elements")


class EGBPResponse(BaseModel):
    total_pressure_pa: float
    status: str
    id: Optional[int]


# Pipe Wall Calculator Schemas
class PipeWallRequest(BaseModel):
    nps: float = Field(..., description="Nominal pipe size")
    pressure_mpa: float = Field(..., description="Design pressure (MPa)")
    temp_c: float = Field(..., description="Design temperature (°C)")
    material: str = Field(..., description="Pipe material")
    weld_type: str = Field(..., description="Weld type")
    corrosion_mm: Optional[float] = Field(0.0, description="Corrosion allowance (mm)")
    threaded: Optional[bool] = Field(False, description="Is pipe threaded?")
    mill_tolerance: Optional[float] = Field(12.5, description="Mill tolerance (%)")


class PipeWallResponse(BaseModel):
    t_dis_mm: float
    t_req_mm: float
    t_min_mm: float
    S_mpa: float
    dext_mm: float
    recommended_schedule: Optional[Dict[str, Any]]
    id: Optional[int]


# Linear Interpolator Schemas
class LinearInterpolatorRequest(BaseModel):
    x1: Optional[float] = None
    y1: Optional[float] = None
    x2: Optional[float] = None
    y2: Optional[float] = None
    x3: Optional[float] = None
    y3: Optional[float] = None


class LinearInterpolatorResponse(BaseModel):
    blank_field: str
    result: float
    formula_used: str
    id: Optional[int]


# Error Response Schema
class ErrorResponse(BaseModel):
    error: str
