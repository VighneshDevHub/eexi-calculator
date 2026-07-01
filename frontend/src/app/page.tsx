'use client';

import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faShip,
  faInfoCircle,
  faMicrochip,
  faBolt,
  faCalculator,
  faDownload,
} from '@fortawesome/free-solid-svg-icons';
import AppLayout from '@/components/AppLayout';
import { SHIP_LABELS, CF_LABELS } from '@/lib/constants';
import type { EEXIFormData } from '@/lib/types';
import { apiRequest, downloadReport } from '@/lib/api';

export default function Home() {
  const [formData, setFormData] = useState<EEXIFormData>({
    vessel_name: '',
    ship_type: 'bulk_carrier',
    dwt: '',
    gt: '',
    mcr: '',
    sfc: '',
    fuel_type: 'hfo',
    speed: '',
    pae: '',
    sfc_ae: '',
    fuel_type_ae: '',
  });

  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData((prev) => ({ ...prev, [e.target.id]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setResults(null);

    try {
      const payload: any = {
        user_local_time: new Date().toLocaleString(),
      };
      
      // Only include fields that have valid values
      for (const [key, value] of Object.entries(formData)) {
        if (value !== '' && value !== null && value !== undefined) {
          payload[key] = value;
        }
      }

      const data = await apiRequest<any>('/api/calculate-eexi', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      
      setResults(data);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMsg);
      console.error('Calculation error:', err);
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
        '/api/eexi-report',
        results,
        `EEXI_Report_${new Date().toISOString().split('T')[0]}.pdf`
      );
    } catch (err) {
      console.error('Failed to generate report:', err);
      alert('Failed to generate report');
    } finally {
      setLoadingReport(false);
    }
  };

  const isGTBased = formData.ship_type === 'ro_ro_pass' || formData.ship_type === 'cruise';

  return (
    <AppLayout title="EEXI Calculator">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
          <div className="flex items-center gap-3 mb-8">
            <FontAwesomeIcon
              icon={faShip}
              className="text-3xl text-blue-600"
            />
            <div>
              <h2 className="text-2xl font-bold text-slate-800">
                EEXI Compliance
              </h2>
              <p className="text-slate-500 text-sm">
                Enter vessel design parameters for IMO MEPC.350(78) assessment.
              </p>
            </div>
          </div>

          {error && (
            <div className="mb-6 flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
              <FontAwesomeIcon icon={faInfoCircle} className="text-lg" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h3 className="flex items-center gap-2 text-lg font-bold text-slate-800 mb-5">
                <FontAwesomeIcon
                  icon={faInfoCircle}
                  className="text-blue-500"
                />
                Basic Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label
                    htmlFor="vessel_name"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Vessel Name
                  </label>
                  <input
                    type="text"
                    id="vessel_name"
                    placeholder="e.g., MV Ocean Star"
                    value={formData.vessel_name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="ship_type"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Ship Type
                  </label>
                  <select
                    id="ship_type"
                    required
                    value={formData.ship_type}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  >
                    {Object.entries(SHIP_LABELS).map(([key, label]) => (
                      <option key={key} value={key}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div
                  className={`space-y-2 ${isGTBased ? 'hidden' : 'block'}`}
                >
                  <label
                    htmlFor="dwt"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Deadweight (DWT)
                    <span className="text-slate-400 ml-1">[tonnes]</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    id="dwt"
                    placeholder="e.g., 75000"
                    value={formData.dwt}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div
                  className={`space-y-2 ${isGTBased ? 'block' : 'hidden'}`}
                >
                  <label
                    htmlFor="gt"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Gross Tonnage (GT)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    id="gt"
                    placeholder="e.g., 50000"
                    value={formData.gt}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-slate-200">
              <h3 className="flex items-center gap-2 text-lg font-bold text-slate-800 mb-5">
                <FontAwesomeIcon
                  icon={faMicrochip}
                  className="text-blue-500"
                />
                Main Engine (ME)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label
                    htmlFor="mcr"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Main Engine MCR
                    <span className="text-slate-400 ml-1">[kW]</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    id="mcr"
                    required
                    placeholder="e.g., 12000"
                    value={formData.mcr}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="sfc"
                    className="text-sm font-semibold text-slate-700"
                  >
                    ME SFC at 75% MCR
                    <span className="text-slate-400 ml-1">[g/kWh]</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    id="sfc"
                    required
                    placeholder="e.g., 175"
                    value={formData.sfc}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div className="space-y-2">
                  <label
                    htmlFor="fuel_type"
                    className="text-sm font-semibold text-slate-700"
                  >
                    ME Fuel Type
                  </label>
                  <select
                    id="fuel_type"
                    required
                    value={formData.fuel_type}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  >
                    {Object.entries(CF_LABELS).map(([key, label]) => (
                      <option key={key} value={key}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="speed"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Design Speed (V_ref)
                    <span className="text-slate-400 ml-1">[knots]</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    id="speed"
                    required
                    placeholder="e.g., 14.5"
                    value={formData.speed}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-slate-200">
              <h3 className="flex items-center gap-2 text-lg font-bold text-slate-800 mb-5">
                <FontAwesomeIcon
                  icon={faBolt}
                  className="text-blue-500"
                />
                Auxiliary Engine (AE)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <label
                    htmlFor="pae"
                    className="text-sm font-semibold text-slate-700"
                  >
                    AE Power
                    <span className="text-slate-400 ml-1">[kW]</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    id="pae"
                    placeholder="e.g., 500"
                    value={formData.pae}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="sfc_ae"
                    className="text-sm font-semibold text-slate-700"
                  >
                    AE SFC
                    <span className="text-slate-400 ml-1">[g/kWh]</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    id="sfc_ae"
                    placeholder="e.g., 190"
                    value={formData.sfc_ae}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="fuel_type_ae"
                    className="text-sm font-semibold text-slate-700"
                  >
                    AE Fuel Type
                  </label>
                  <select
                    id="fuel_type_ae"
                    value={formData.fuel_type_ae}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  >
                    <option value="">Same as ME</option>
                    {Object.entries(CF_LABELS).map(([key, label]) => (
                      <option key={key} value={key}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/30 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              <FontAwesomeIcon icon={faCalculator} />
              {loading ? 'Calculating...' : 'Run Compliance Assessment'}
            </button>
          </form>
        </div>

        {results && (
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
            <div className="mb-8 text-center">
              <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full text-white text-6xl font-extrabold shadow-lg mb-3 ${
                results.status === 'COMPLIANT' ? 'bg-gradient-to-br from-green-600 to-green-800' : 'bg-gradient-to-br from-red-600 to-red-800'
              }`}>
                {results.status === 'COMPLIANT' ? '✓' : '✗'}
              </div>
              <h2 className="text-2xl font-bold text-slate-800">
                {results.status === 'COMPLIANT' ? 'Compliant' : 'Non-Compliant'}
              </h2>
              <p className="text-slate-500 text-sm">
                {results.vessel_name || 'EEXI Calculation Result'}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="p-6 bg-slate-50 border border-slate-200 rounded-xl text-center">
                <div className="text-xs text-slate-500 font-semibold uppercase mb-2">
                  Attained EEXI
                </div>
                <div className="text-3xl font-extrabold text-slate-800">
                  {results.attained_eexi?.toFixed(4)}
                </div>
                <div className="text-sm text-slate-500">
                  gCO₂/(DWT·nm)
                </div>
              </div>

              <div className="p-6 bg-blue-50 border border-blue-200 rounded-xl text-center">
                <div className="text-xs text-blue-600 font-semibold uppercase mb-2">
                  Required EEXI
                </div>
                <div className="text-3xl font-extrabold text-blue-800">
                  {results.required_eexi?.toFixed(4)}
                </div>
                <div className="text-sm text-blue-700">
                  gCO₂/(DWT·nm)
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="p-6 bg-slate-50 border border-slate-200 rounded-xl text-center">
                <div className="text-xs text-slate-500 font-semibold uppercase mb-2">
                  Margin
                </div>
                <div className="text-3xl font-extrabold text-slate-800">
                  {results.margin?.toFixed(2)}%
                </div>
              </div>
              <div className="p-6 flex items-center justify-center">
                <button
                  onClick={handleDownloadReport}
                  disabled={loadingReport}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                >
                  <FontAwesomeIcon icon={faDownload} />
                  {loadingReport ? 'Generating...' : 'Download Report'}
                </button>
              </div>
            </div>

            {/* EPL / MCR Lim Recommendation */}
            {results.epl && (
              <div className="p-6 border rounded-xl mb-6 bg-blue-50 border-blue-200">
                <h3 className="text-lg font-bold text-blue-900 mb-4 flex items-center gap-2">
                  <FontAwesomeIcon icon={faCalculator} className="text-blue-600" />
                  EPL / MCR Lim Recommendation
                </h3>
                {results.epl.epl_possible ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 bg-white rounded-lg border border-blue-200 text-center">
                        <div className="text-xs text-slate-500 font-semibold uppercase mb-1">MCR Limit</div>
                        <div className="text-2xl font-extrabold text-blue-900">{results.epl.mcr_lim?.toFixed(1)} kW</div>
                      </div>
                      <div className="p-4 bg-white rounded-lg border border-blue-200 text-center">
                        <div className="text-xs text-slate-500 font-semibold uppercase mb-1">Reduction</div>
                        <div className="text-2xl font-extrabold text-blue-900">{results.epl.reduction_pct?.toFixed(1)}%</div>
                      </div>
                    </div>
                    <div className="p-4 bg-white rounded-lg border border-blue-200">
                      <div className="text-xs text-slate-500 font-semibold uppercase mb-1">Estimated Speed at Limited Power</div>
                      <div className="text-xl font-extrabold text-blue-900">{results.epl.new_v_ref?.toFixed(2)} knots</div>
                    </div>
                    <p className="text-sm text-blue-900 leading-relaxed">{results.epl.note}</p>
                  </div>
                ) : (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-center">
                    <div className="text-red-900 font-semibold mb-2">EPL Not Sufficient</div>
                    <p className="text-sm text-red-800 leading-relaxed">{results.epl.note}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
