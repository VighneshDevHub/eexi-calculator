'use client';

import { useEffect, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faWind,
  faPlus,
  faTrash,
  faCalculator,
  faDownload,
} from '@fortawesome/free-solid-svg-icons';
import AppLayout from '@/components/AppLayout';
import { ELEMENT_TYPES, ROUGHNESS_OPTIONS } from '@/lib/constants';
import { apiRequest, downloadReport } from '@/lib/api';

interface Engine {
  id: number;
  type: string;
  mass_flow: number;
  temp: number;
  max_bp: number;
  roughness: string;
}

interface Element {
  id: number;
  type: string;
  diameter_mm?: number;
  length_mm?: number;
  rd?: number;
  angle_deg?: number;
  inlet_a_mm?: number;
  outlet_b_mm?: number;
  xi_custom?: number;
}

interface EGBPResult {
  status: string;
  total_pressure_pa: number;
  total_pressure_mmwc: number;
  max_bp_pa: number;
  margin_pct: number;
  elements: Array<{
    position: number;
    label: string;
    velocity: number;
    xi: number;
    pressure_loss_pa: number;
    note: string;
  }>;
}

export default function EGBPPage() {
  const [engines, setEngines] = useState<Engine[]>([]);
  const [elements, setElements] = useState<Element[]>([]);
  const [roughnessKey, setRoughnessKey] = useState('steel_welded');
  const [systemTotals, setSystemTotals] = useState({
    mass_flow_kgs: 0,
    temp_tc_c: 0,
    max_bp_pa: 3000,
  });
  const [results, setResults] = useState<EGBPResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [enginePresets, setEnginePresets] = useState<any>({});

  useEffect(() => {
    async function loadConstants() {
      try {
        const data = await apiRequest<{ engine_presets: any; roughness_options: any }>('/api/egbp/constants');
        setEnginePresets(data.engine_presets);
        // Add initial engine and element
        addEngine('ME');
        addElement('pipe');
      } catch (err) {
        console.error('Failed to load constants:', err);
      }
    }
    loadConstants();
  }, []);

  useEffect(() => {
    calculateSystemTotals();
  }, [engines]);

  function calculateSystemTotals() {
    let totalMass = 0;
    let weightedTempSum = 0;
    let minMaxBp = Infinity;

    engines.forEach((engine) => {
      totalMass += engine.mass_flow;
      weightedTempSum += engine.mass_flow * engine.temp;
      if (engine.max_bp < minMaxBp) minMaxBp = engine.max_bp;
    });

    const avgTemp = totalMass > 0 ? weightedTempSum / totalMass : 0;
    if (minMaxBp === Infinity) minMaxBp = 3000;

    setSystemTotals({
      mass_flow_kgs: totalMass,
      temp_tc_c: avgTemp,
      max_bp_pa: minMaxBp,
    });
  }

  function addEngine(type: string = 'ME') {
    const id = Date.now();
    const preset = enginePresets[type] || {
      mass_flow: 0,
      temp_tc: 0,
      max_bp_pa: 3000,
      roughness: 'steel_welded',
    };
    setEngines([
      ...engines,
      {
        id,
        type,
        mass_flow: preset.mass_flow || 0,
        temp: preset.temp_tc || 0,
        max_bp: preset.max_bp_pa || 3000,
        roughness: preset.roughness || 'steel_welded',
      },
    ]);
  }

  function removeEngine(id: number) {
    setEngines(engines.filter((engine) => engine.id !== id));
  }

  function updateEngineType(id: number, type: string) {
    setEngines(
      engines.map((engine) => {
        if (engine.id === id) {
          const preset = enginePresets[type];
          return {
            ...engine,
            type,
            mass_flow: preset?.mass_flow || 0,
            temp: preset?.temp_tc || 0,
            max_bp: preset?.max_bp_pa || 3000,
            roughness: preset?.roughness || 'commercial_steel',
          };
        }
        return engine;
      })
    );
  }

  function updateEngineParam(id: number, field: keyof Engine, value: string | number) {
    setEngines(
      engines.map((engine) => {
        if (engine.id === id) {
          return {
            ...engine,
            [field]: field === 'roughness' ? value : Number(value) || 0,
          };
        }
        return engine;
      })
    );
  }

  function addElement(type: string = 'pipe') {
    const id = Date.now();
    setElements([...elements, { id, type, diameter_mm: 1600, length_mm: 1000 }]);
  }

  function removeElement(id: number) {
    setElements(elements.filter((el) => el.id !== id));
  }

  function updateElementType(id: number, type: string) {
    setElements(
      elements.map((el) => {
        if (el.id === id) {
          return {
            ...el,
            type,
            diameter_mm: type !== 'diffuser' && type !== 'orifice' ? 1600 : undefined,
            inlet_a_mm: type === 'diffuser' || type === 'orifice' ? 1600 : undefined,
            outlet_b_mm: type === 'diffuser' || type === 'orifice' ? 2410 : undefined,
            rd: type === 'pipe_bend' ? 1.5 : undefined,
            angle_deg: type === 'pipe_bend' ? 90 : undefined,
            xi_custom: type === 'custom' ? 1.0 : undefined,
          };
        }
        return el;
      })
    );
  }

  function updateElementParam(id: number, field: string, value: string) {
    setElements(
      elements.map((el) => {
        if (el.id === id) {
          return {
            ...el,
            [field]: Number(value) || 0,
          };
        }
        return el;
      })
    );
  }

  function renderElementInputs(el: Element) {
    switch (el.type) {
      case 'pipe':
        return (
          <>
            <input
              type="number"
              step="1"
              placeholder="Dia (mm)"
              value={el.diameter_mm || 1600}
              onChange={(e) => updateElementParam(el.id, 'diameter_mm', e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
            <input
              type="number"
              step="1"
              placeholder="Length (mm)"
              value={el.length_mm || 1000}
              onChange={(e) => updateElementParam(el.id, 'length_mm', e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </>
        );
      case 'pipe_bend':
        return (
          <>
            <input
              type="number"
              step="1"
              placeholder="Dia (mm)"
              value={el.diameter_mm || 1600}
              onChange={(e) => updateElementParam(el.id, 'diameter_mm', e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
            <div className="flex gap-2">
              <input
                type="number"
                step="0.1"
                placeholder="R/d"
                value={el.rd || 1.5}
                onChange={(e) => updateElementParam(el.id, 'rd', e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
              <input
                type="number"
                step="1"
                placeholder="Angle (°)"
                value={el.angle_deg || 90}
                onChange={(e) => updateElementParam(el.id, 'angle_deg', e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
          </>
        );
      case 'diffuser':
      case 'orifice':
        return (
          <>
            <input
              type="number"
              step="1"
              placeholder="Inlet (mm)"
              value={el.inlet_a_mm || 1600}
              onChange={(e) => updateElementParam(el.id, 'inlet_a_mm', e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
            <input
              type="number"
              step="1"
              placeholder="Outlet (mm)"
              value={el.outlet_b_mm || 2410}
              onChange={(e) => updateElementParam(el.id, 'outlet_b_mm', e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </>
        );
      case 'custom':
        return (
          <>
            <input
              type="number"
              step="1"
              placeholder="Dia (mm)"
              value={el.diameter_mm || 1600}
              onChange={(e) => updateElementParam(el.id, 'diameter_mm', e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
            <input
              type="number"
              step="0.001"
              placeholder="ξ value"
              value={el.xi_custom || 1.0}
              onChange={(e) => updateElementParam(el.id, 'xi_custom', e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </>
        );
      default:
        return (
          <input
            type="number"
            step="1"
            placeholder="Dia (mm)"
            value={el.diameter_mm || 1600}
            onChange={(e) => updateElementParam(el.id, 'diameter_mm', e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
          />
        );
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...systemTotals,
        roughness_key: roughnessKey,
        engines: engines.map((engine) => ({
          type: engine.type,
          label: enginePresets[engine.type]?.label || 'Custom Source',
          mass_flow: engine.mass_flow,
          temp: engine.temp,
          max_bp: engine.max_bp,
          roughness: engine.roughness,
        })),
        elements: elements.map((el) => ({
          element_type: el.type,
          diameter_mm: el.diameter_mm,
          length_mm: el.length_mm,
          rd: el.rd,
          angle_deg: el.angle_deg,
          inlet_a_mm: el.inlet_a_mm,
          outlet_b_mm: el.outlet_b_mm,
          xi_custom: el.xi_custom,
        })),
      };

      const data = await apiRequest<EGBPResult>('/api/calculate-egbp', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setResults(data);
    } catch (err) {
      console.error('Calculation failed:', err);
      alert('Calculation failed. Please check your inputs.');
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadReport() {
    if (!results) {
      alert('Please run a calculation first.');
      return;
    }

    setLoadingReport(true);
    try {
      await downloadReport(
        '/api/egbp-report',
        results,
        `EGBP_Report_${new Date().toISOString().split('T')[0]}.pdf`
      );
    } catch (err) {
      console.error('Failed to generate report:', err);
      alert('Failed to generate report');
    } finally {
      setLoadingReport(false);
    }
  }

  return (
    <AppLayout title="Exhaust Gas Back Pressure (EGBP)">
      <div className="space-y-8">
        {/* Input Form */}
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Engines */}
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <FontAwesomeIcon icon={faWind} className="text-blue-600" />
                  Exhaust Gas Sources
                </h3>
                <button
                  type="button"
                  onClick={() => addEngine('ME')}
                  className="flex items-center gap-2 px-4 py-2 border-2 border-blue-600 text-blue-600 hover:bg-blue-50 rounded-lg font-semibold transition"
                >
                  <FontAwesomeIcon icon={faPlus} />
                  Add Engine
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">#</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Source</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Parameters</th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 uppercase">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {engines.map((engine, index) => (
                      <tr key={engine.id}>
                        <td className="px-4 py-4 font-semibold text-slate-700">{index + 1}</td>
                        <td className="px-4 py-4">
                          <select
                            value={engine.type}
                            onChange={(e) => updateEngineType(engine.id, e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                          >
                            <option value="custom">-- Custom Source --</option>
                            {Object.entries(enginePresets).map(([key, preset]: [string, any]) => (
                              <option key={key} value={key}>{preset.label}</option>
                            ))}
                          </select>
                        </td>
                        <td className="px-4 py-4">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <div className="space-y-1">
                              <label className="text-xs font-semibold text-slate-500">Mass Flow (kg/s)</label>
                              <input
                                type="number"
                                step="0.001"
                                value={engine.mass_flow}
                                onChange={(e) => updateEngineParam(engine.id, 'mass_flow', e.target.value)}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold text-slate-500">Temp (°C)</label>
                              <input
                                type="number"
                                step="0.1"
                                value={engine.temp}
                                onChange={(e) => updateEngineParam(engine.id, 'temp', e.target.value)}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold text-slate-500">Max BP (Pa)</label>
                              <input
                                type="number"
                                step="1"
                                value={engine.max_bp}
                                onChange={(e) => updateEngineParam(engine.id, 'max_bp', e.target.value)}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold text-slate-500">Roughness</label>
                              <select
                                value={engine.roughness}
                                onChange={(e) => updateEngineParam(engine.id, 'roughness', e.target.value)}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                              >
                                {Object.entries(ROUGHNESS_OPTIONS).map(([key, val]) => (
                                  <option key={key} value={key}>{key.replace('_', ' ').toUpperCase()} ({val}mm)</option>
                                ))}
                              </select>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-center">
                          <button
                            type="button"
                            onClick={() => removeEngine(engine.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          >
                            <FontAwesomeIcon icon={faTrash} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* System Summary */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-slate-800 mb-4">System Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-500">Total Mass Flow (kg/s)</label>
                  <input
                    type="number"
                    value={systemTotals.mass_flow_kgs.toFixed(3)}
                    readOnly
                    className="w-full px-3 py-2 bg-slate-100 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-500">Avg. Temp (°C)</label>
                  <input
                    type="number"
                    value={systemTotals.temp_tc_c.toFixed(1)}
                    readOnly
                    className="w-full px-3 py-2 bg-slate-100 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-500">System Max BP (Pa)</label>
                  <input
                    type="number"
                    value={systemTotals.max_bp_pa}
                    readOnly
                    className="w-full px-3 py-2 bg-slate-100 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-500">Roughness</label>
                  <select
                    value={roughnessKey}
                    onChange={(e) => setRoughnessKey(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  >
                    {Object.entries(ROUGHNESS_OPTIONS).map(([key, val]) => (
                      <option key={key} value={key}>{key.replace('_', ' ').toUpperCase()} ({val}mm)</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Elements */}
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <FontAwesomeIcon icon={faCalculator} className="text-blue-600" />
                  Pipeline Elements
                </h3>
                <button
                  type="button"
                  onClick={() => addElement('pipe')}
                  className="flex items-center gap-2 px-4 py-2 border-2 border-blue-600 text-blue-600 hover:bg-blue-50 rounded-lg font-semibold transition"
                >
                  <FontAwesomeIcon icon={faPlus} />
                  Add Element
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">#</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Type</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Dimensions (mm)</th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 uppercase">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {elements.map((el, index) => (
                      <tr key={el.id}>
                        <td className="px-4 py-4 font-semibold text-slate-700">{index + 1}</td>
                        <td className="px-4 py-4">
                          <select
                            value={el.type}
                            onChange={(e) => updateElementType(el.id, e.target.value)}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                          >
                            {ELEMENT_TYPES.map((type) => (
                              <option key={type.value} value={type.value}>{type.label}</option>
                            ))}
                          </select>
                        </td>
                        <td className="px-4 py-4">
                          <div className="grid grid-cols-2 gap-3">
                            {renderElementInputs(el)}
                          </div>
                        </td>
                        <td className="px-4 py-4 text-center">
                          <button
                            type="button"
                            onClick={() => removeElement(el.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          >
                            <FontAwesomeIcon icon={faTrash} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg transition"
            >
              <FontAwesomeIcon icon={faCalculator} />
              {loading ? 'Calculating...' : 'Run EGBP Calculation'}
            </button>
          </form>
        </div>

        {/* Results */}
        {results && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 text-center">
                <div className="text-sm font-semibold uppercase text-slate-500 mb-3">Status</div>
                <div className={`text-4xl font-extrabold mb-2 ${
                  results.status === 'PASSED' ? 'text-green-600' :
                  results.status === 'BORDERLINE' ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {results.status}
                </div>
                <div className="text-lg text-slate-500">{results.margin_pct.toFixed(1)}% margin</div>
              </div>

              <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 text-center">
                <div className="text-sm font-semibold uppercase text-slate-500 mb-3">Total Back Pressure</div>
                <div className="text-4xl font-extrabold text-slate-800 mb-1">{results.total_pressure_pa.toLocaleString()}</div>
                <div className="text-lg text-slate-500">{results.total_pressure_mmwc.toFixed(1)} mmWC</div>
              </div>

              <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 text-center">
                <div className="text-sm font-semibold uppercase text-slate-500 mb-3">System Limit</div>
                <div className="text-4xl font-extrabold text-slate-800">{results.max_bp_pa.toLocaleString()}</div>
                <div className="text-lg text-slate-500">Pascal (Pa)</div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <FontAwesomeIcon icon={faCalculator} className="text-blue-600" />
                  Pressure Loss Breakdown
                </h3>
                <button
                  onClick={handleDownloadReport}
                  disabled={loadingReport}
                  className="flex items-center gap-2 px-4 py-2 border-2 border-blue-600 text-blue-600 hover:bg-blue-50 rounded-lg font-semibold transition"
                >
                  <FontAwesomeIcon icon={faDownload} />
                  {loadingReport ? 'Generating...' : 'Download Report'}
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">#</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Element</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Velocity (m/s)</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">ξ (loss coeff)</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">ΔP (Pa)</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Notes</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {results.elements.map((el) => (
                      <tr key={el.position}>
                        <td className="px-4 py-3 font-semibold text-slate-700">{el.position}</td>
                        <td className="px-4 py-3 font-medium text-slate-800">{el.label}</td>
                        <td className="px-4 py-3 text-slate-600">{el.velocity.toFixed(2)}</td>
                        <td className="px-4 py-3 text-slate-600">{el.xi.toFixed(4)}</td>
                        <td className="px-4 py-3 font-semibold text-slate-800">{el.pressure_loss_pa.toFixed(1)}</td>
                        <td className="px-4 py-3 text-slate-500 text-sm">{el.note}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
