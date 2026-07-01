export const SHIP_LABELS: Record<string, string> = {
  bulk_carrier: "Bulk Carrier",
  tanker: "Tanker",
  containership: "Containership",
  general_cargo: "General Cargo",
  ro_ro_cargo: "Ro-Ro Cargo",
  ro_ro_pass: "Ro-Ro Passenger",
  cruise: "Cruise Passenger",
  lng: "LNG Carrier",
  gas_carrier: "Gas Carrier",
  chemical: "Chemical Carrier",
  reefer: "Reefer",
  offshore: "Offshore Support",
  fishing: "Fishing Vessel",
  passenger: "Passenger Ship",
  other: "Other",
};

export const CF_LABELS: Record<string, string> = {
  hfo: "HFO / RMG (CF = 3.114)",
  mdo: "MDO / MGO (CF = 3.206)",
  lng: "LNG (CF = 2.750)",
  methanol: "Methanol (CF = 1.375)",
  lpg_propane: "LPG Propane (CF = 3.000)",
  lpg_butane: "LPG Butane (CF = 3.030)",
  ethane: "Ethane (CF = 2.927)",
};

export const CII_YEARS = ["2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030"];

export const NPS_OPTIONS = [
  "0.125", "0.25", "0.375", "0.5", "0.75", "1", "1.25", "1.5", "2", "2.5", "3", "3.5", "4", "5", "6", "8", "10", "12", "14", "16", "18", "20", "24"
];

export const NPS_DEXT: Record<string, number> = {
  "0.125": 10.3,
  "0.25": 13.7,
  "0.375": 17.1,
  "0.5": 21.3,
  "0.75": 26.7,
  "1": 33.4,
  "1.25": 42.2,
  "1.5": 48.3,
  "2": 60.3,
  "2.5": 73.0,
  "3": 88.9,
  "3.5": 101.6,
  "4": 114.3,
  "5": 141.3,
  "6": 168.3,
  "8": 219.1,
  "10": 273.1,
  "12": 323.9,
  "14": 355.6,
  "16": 406.4,
  "18": 457.2,
  "20": 508.0,
  "24": 610.0
};

export const MATERIAL_OPTIONS: Record<string, { label: string; S_values: Record<string, number> }> = {
  A106A: { label: "A106 Grade A", S_values: {} },
  A106B: { label: "A106 Grade B", S_values: {} },
  A106C: { label: "A106 Grade C", S_values: {} },
  A53A: { label: "A53 Grade A", S_values: {} },
  A53B: { label: "A53 Grade B", S_values: {} },
  API5LB: { label: "API 5L Grade B", S_values: {} },
  API5LX42: { label: "API 5L X42", S_values: {} },
  API5LX52: { label: "API 5L X52", S_values: {} },
  SS304L: { label: "304L Stainless Steel", S_values: {} },
  SS316L: { label: "316L Stainless Steel", S_values: {} },
};

export const WELD_OPTIONS: Record<string, { label: string; E_joint: number }> = {
  S: { label: "Seamless", E_joint: 1.0 },
  ERW: { label: "ERW (Electric Resistance Welded)", E_joint: 0.85 },
  LPG: { label: "Longitudinal PGW", E_joint: 0.6 },
  FG: { label: "Furnace Butt Weld", E_joint: 0.7 },
  FBW: { label: "Flash Butt Weld", E_joint: 0.9 },
};

export const ROUGHNESS_OPTIONS: Record<string, number> = {
  steel_welded: 0.06096,
  steel_corroded: 0.3,
  stainless_steel: 0.046,
  steel_galvanized: 0.15,
  iron_cast: 0.26,
  copper_brass: 0.0015,
  plastic: 0.0015,
};

export const ELEMENT_TYPES = [
  { value: "pipe", label: "Straight Pipe" },
  { value: "pipe_bend", label: "Pipe Bend" },
  { value: "diffuser", label: "Diffuser / Reduction" },
  { value: "wye_through", label: "Wye (through)" },
  { value: "wye_branch", label: "Wye (branch)" },
  { value: "butterfly_valve", label: "Butterfly Valve" },
  { value: "gate_valve", label: "Gate Valve" },
  { value: "silencer", label: "Silencer" },
  { value: "boiler", label: "Boiler" },
  { value: "outlet", label: "Outlet" },
  { value: "orifice", label: "Orifice" },
  { value: "custom", label: "Custom ξ" },
];
