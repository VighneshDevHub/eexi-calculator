export interface EEXIFormData {
  vessel_name?: string;
  ship_type: keyof typeof import('./constants').SHIP_LABELS;
  dwt?: string;
  gt?: string;
  mcr: string;
  sfc: string;
  fuel_type: keyof typeof import('./constants').CF_LABELS;
  speed: string;
  pae?: string;
  sfc_ae?: string;
  fuel_type_ae?: keyof typeof import('./constants').CF_LABELS | '';
}

export interface CIIFormData {
  ship_type: keyof typeof import('./constants').SHIP_LABELS;
  year: string;
  dwt?: string;
  gt?: string;
  distance_nm: string;
  fc_hfo: string;
  fc_mdo: string;
  fc_lng: string;
  fc_methanol: string;
  fc_lpg_propane: string;
  fc_lpg_butane: string;
  fc_ethane: string;
  tanker_op: 'none' | 'sts' | 'shuttle';
  reefer_kwh: string;
  sfoc_electrical: string;
  voyage_hfo: string;
  voyage_distance: string;
}

export interface CIIResult {
  attained_cii: number;
  required_cii: number;
  rating: {
    rating: 'A' | 'B' | 'C' | 'D' | 'E';
    margin_pct: number;
  };
  [key: string]: any;
}
