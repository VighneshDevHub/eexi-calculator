'use client';

import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCube, faCalculator, faDownload, faMagic } from '@fortawesome/free-solid-svg-icons';
import AppLayout from '@/components/AppLayout';
import { NPS_OPTIONS, MATERIAL_OPTIONS, WELD_OPTIONS } from '@/lib/constants';
import { apiRequest, downloadReport } from '@/lib/api';

interface PipeFormData {
  nps: string;
  pressure_mpa: string;
  temp_c: string;
  material: string;
  weld_type: string;
  material_type: 'ferritic' | 'austenitic' | 'other';
  corrosion_mm: string;
  threaded: 'true' | 'false';
  mill_tolerance: string;
  dext_override: string;
  s_allow_override: string;
}

interface PipeSchedule {
  schedule: string;
  thickness_mm: number;
  adequate: boolean;
}

interface PipeResults {
  t_dis_mm: number;
  t_req_mm: number;
  t_min_mm: number;
  S_mpa: number;
  recommended_schedule?: { schedule: string; thickness_mm: number };
  schedules: PipeSchedule[];
  thin_wall_ok: boolean;
}

export default function PipePage() {
  const [formData, setFormData] = useState<PipeFormData>({
    nps: '2',
    pressure_mpa: '1.034',
    temp_c: '260',
    material: 'A53B',
    weld_type: 'S',
    material_type: 'ferritic',
    corrosion_mm: '1.5875',
    threaded: 'true',
    mill_tolerance: '12.5',
    dext_override: '',
    s_allow_override: '',
  });

  const [results, setResults] = useState<PipeResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData(prev => ({ ...prev, [e.target.id]: e.target.value }));
  };

  const loadExample = () => {
    setFormData({
      nps: '2',
      pressure_mpa: '1.034',
      temp_c: '260',
      material: 'A53B',
      weld_type: 'S',
      material_type: 'ferritic',
      corrosion_mm: '1.5875',
      threaded: 'true',
      mill_tolerance: '12.5',
      dext_override: '',
      s_allow_override: '',
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setResults(null);
    setLoading(true);

    try {
      const payload: any = {
        nps: parseFloat(formData.nps),
        pressure_mpa: parseFloat(formData.pressure_mpa),
        temp_c: parseFloat(formData.temp_c),
        material: formData.material,
        weld_type: formData.weld_type,
        material_type: formData.material_type,
        corrosion_mm: parseFloat(formData.corrosion_mm),
        threaded: formData.threaded === 'true',
        mill_tolerance: parseFloat(formData.mill_tolerance),
      };

      if (formData.dext_override) {
        payload.dext_override = parseFloat(formData.dext_override);
      }
      if (formData.s_allow_override) {
        payload.s_allow_override = parseFloat(formData.s_allow_override);
      }

      const data = await apiRequest<PipeResults>('/api/calculate-pipe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      setResults(data);
    } catch (err) {
      alert('Calculation failed!');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!results) {
      alert("Please run a calculation first!");
      return;
    }
    setLoadingReport(true);
    try {
      await downloadReport(
        "/api/pipe-report",
        { input_data: formData, result_data: results },
        `Pipe_Wall_Report_${new Date().toISOString().split("T")[0]}.pdf`
      );
    } catch (err) {
      console.error("Failed to generate report:", err);
      alert("Failed to generate report!");
    } finally {
      setLoadingReport(false);
    }
  };

  const getScheduleCardClass = (sched: PipeSchedule) => {
    if (results?.recommended_schedule?.schedule === sched.schedule) {
      return "p-4 rounded-xl text-center border-2 bg-blue-50 border-blue-300";
    } else if (sched.adequate) {
      return "p-4 rounded-xl text-center border-2 bg-green-50 border-green-300";
    } else {
      return "p-4 rounded-xl text-center border-2 bg-red-50 border-red-300";
    }
  };

  return (
    <AppLayout title="Pipe Wall Thickness">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <FontAwesomeIcon
                icon={faCube}
                className="text-3xl text-blue-600"
              />
              <div>
                <h2 className="text-2xl font-bold text-slate-800">
                  Pipe Wall Thickness
                </h2>
                <p className="text-slate-500 text-sm">
                  Calculate pipe wall thickness per ASME B31.3
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={loadExample}
              className="flex items-center gap-2 px-4 py-2 border-2 border-slate-200 hover:border-blue-500 hover:text-blue-600 rounded-lg text-sm font-semibold transition-all"
            >
              <FontAwesomeIcon icon={faMagic} /> Load Example
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Nominal Pipe Size (NPS)
                </label>
                <select
                  id="nps"
                  value={formData.nps}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                >
                  {NPS_OPTIONS.map((val) => (
                    <option key={val} value={val}>
                      NPS {val}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Design Pressure (MPa)
                </label>
                <input
                  type="number"
                  id="pressure_mpa"
                  step="0.001"
                  required
                  placeholder="1.034"
                  value={formData.pressure_mpa}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Design Temperature (°C)
                </label>
                <input
                  type="number"
                  id="temp_c"
                  required
                  placeholder="260"
                  value={formData.temp_c}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Material
                </label>
                <select
                  id="material"
                  value={formData.material}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                >
                  {Object.entries(MATERIAL_OPTIONS).map(([key, val]) => (
                    <option key={key} value={key}>
                      {val.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Weld Type
                </label>
                <select
                  id="weld_type"
                  value={formData.weld_type}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                >
                  {Object.entries(WELD_OPTIONS).map(([key, val]) => (
                    <option key={key} value={key}>
                      {val.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Material Type (Y Factor)
                </label>
                <select
                  id="material_type"
                  value={formData.material_type}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                >
                  <option value="ferritic">Ferritic Steel</option>
                  <option value="austenitic">Austenitic Steel</option>
                  <option value="other">Other Ductile Metals</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Corrosion Allowance (mm)
                </label>
                <input
                  type="number"
                  id="corrosion_mm"
                  step="0.1"
                  placeholder="1.5875"
                  value={formData.corrosion_mm}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">
                  Threaded End?
                </label>
                <select
                  id="threaded"
                  value={formData.threaded}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                >
                  <option value="false">No</option>
                  <option value="true">Yes</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/30 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              <FontAwesomeIcon icon={faCalculator} />
              {loading ? 'Calculating...' : 'Calculate Thickness'}
            </button>
          </form>
        </div>

        {results && (
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-slate-800 mb-6">
                Calculation Results
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl text-center">
                  <div className="text-xs text-slate-500 font-semibold uppercase mb-2">
                    Pressure Design (tₛᵤₛ)
                  </div>
                  <div className="text-3xl font-extrabold text-slate-800">
                    {results.t_dis_mm.toFixed(3)}
                  </div>
                  <div className="text-sm text-slate-500">mm</div>
                </div>
                <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl text-center">
                  <div className="text-xs text-slate-500 font-semibold uppercase mb-2">
                    Required (tᵣₑq)
                  </div>
                  <div className="text-3xl font-extrabold text-slate-800">
                    {results.t_req_mm.toFixed(3)}
                  </div>
                  <div className="text-sm text-slate-500">mm</div>
                </div>
                <div className="p-5 bg-blue-50 border border-blue-200 rounded-xl text-center">
                  <div className="text-xs text-blue-600 font-semibold uppercase mb-2">
                    Minimum (tₘᵢₙ)
                  </div>
                  <div className="text-3xl font-extrabold text-blue-900">
                    {results.t_min_mm.toFixed(3)}
                  </div>
                  <div className="text-sm text-blue-700">mm</div>
                </div>
                <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl text-center">
                  <div className="text-xs text-slate-500 font-semibold uppercase mb-2">
                    Allowable Stress (S)
                  </div>
                  <div className="text-3xl font-extrabold text-slate-800">
                    {results.S_mpa.toFixed(2)}
                  </div>
                  <div className="text-sm text-slate-500">MPa</div>
                </div>
              </div>
            </div>

            <div className="mb-6">
              <h3 className="text-lg font-semibold text-slate-800 mb-4">
                Recommended Schedules
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {results.schedules.map((sched, idx) => (
                  <div key={idx} className={getScheduleCardClass(sched)}>
                    <div className="text-sm font-semibold text-slate-700">
                      SCH {sched.schedule}
                    </div>
                    <div className="text-lg font-bold text-slate-800">
                      {sched.thickness_mm.toFixed(2)} mm
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={handleDownload}
              disabled={loadingReport}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl shadow-lg shadow-blue-500/30 transition-all disabled:opacity-70"
            >
              <FontAwesomeIcon icon={faDownload} />
              {loadingReport ? 'Generating...' : 'Download Report'}
            </button>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
