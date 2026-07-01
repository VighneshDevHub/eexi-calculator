'use client';

import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faChartLine,
  faEdit,
  faMagic,
  faGasPump,
  faPlusCircle,
  faCalculator,
  faPoll,
  faRedo,
  faDownload,
} from '@fortawesome/free-solid-svg-icons';
import AppLayout from '@/components/AppLayout';
import { SHIP_LABELS, CII_YEARS } from '@/lib/constants';
import type { CIIFormData, CIIResult } from '@/lib/types';
import { apiRequest, downloadReport } from '@/lib/api';

export default function CIIPage() {
  const [formData, setFormData] = useState<CIIFormData>({
    ship_type: 'bulk_carrier',
    year: '2024',
    dwt: '',
    gt: '',
    distance_nm: '',
    fc_hfo: '0',
    fc_mdo: '0',
    fc_lng: '0',
    fc_methanol: '0',
    fc_lpg_propane: '0',
    fc_lpg_butane: '0',
    fc_ethane: '0',
    tanker_op: 'none',
    reefer_kwh: '0',
    sfoc_electrical: '175',
    voyage_hfo: '0',
    voyage_distance: '0',
  });

  const [results, setResults] = useState<CIIResult | null>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData((prev) => ({ ...prev, [e.target.id]: e.target.value }));
  };

  const loadExample = () => {
    setFormData({
      ship_type: 'bulk_carrier',
      year: '2024',
      dwt: '75000',
      gt: '',
      distance_nm: '120000',
      fc_hfo: '10000',
      fc_mdo: '500',
      fc_lng: '0',
      fc_methanol: '0',
      fc_lpg_propane: '0',
      fc_lpg_butane: '0',
      fc_ethane: '0',
      tanker_op: 'none',
      reefer_kwh: '0',
      sfoc_electrical: '175',
      voyage_hfo: '0',
      voyage_distance: '0',
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await apiRequest<CIIResult>('/api/calculate-cii', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      setResults(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      ship_type: 'bulk_carrier',
      year: '2024',
      dwt: '',
      gt: '',
      distance_nm: '',
      fc_hfo: '0',
      fc_mdo: '0',
      fc_lng: '0',
      fc_methanol: '0',
      fc_lpg_propane: '0',
      fc_lpg_butane: '0',
      fc_ethane: '0',
      tanker_op: 'none',
      reefer_kwh: '0',
      sfoc_electrical: '175',
      voyage_hfo: '0',
      voyage_distance: '0',
    });
    setResults(null);
  };

  const handleDownloadReport = async () => {
    if (!results) {
      alert('Please run a calculation first.');
      return;
    }

    setLoadingReport(true);
    try {
      await downloadReport(
        '/api/cii-report',
        results,
        `CII_Report_${new Date().toISOString().split('T')[0]}.pdf`
      );
    } catch (err) {
      console.error('Failed to generate report:', err);
      alert('Failed to generate report');
    } finally {
      setLoadingReport(false);
    }
  };

  const isGTBased = formData.ship_type === 'ro_ro_pass' || formData.ship_type === 'cruise';
  const isTanker = formData.ship_type === 'tanker';

  return (
    <AppLayout title="CII Calculator">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <FontAwesomeIcon
                icon={faChartLine}
                className="text-3xl text-blue-600"
              />
              <div>
                <h2 className="text-2xl font-bold text-slate-800">
                  CII Calculator
                </h2>
                <p className="text-slate-500 text-sm">
                  Annual Carbon Intensity Indicator - MEPC.352(78)
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={loadExample}
              className="flex items-center gap-2 px-4 py-2 border-2 border-slate-200 hover:border-blue-500 hover:text-blue-600 rounded-lg text-sm font-semibold transition-all"
            >
              <FontAwesomeIcon icon={faMagic} />
              Load Example
            </button>
          </div>

          {error && (
            <div className="mb-6 flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
              <FontAwesomeIcon icon={faEdit} className="text-lg" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Operating Data */}
            <section>
              <h3 className="flex items-center gap-2 text-lg font-bold text-slate-800 mb-5">
                <FontAwesomeIcon icon={faEdit} className="text-blue-500" />
                1. Basic Operating Data
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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

                <div className="space-y-2">
                  <label
                    htmlFor="year"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Assessment Year
                  </label>
                  <select
                    id="year"
                    required
                    value={formData.year}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  >
                    {CII_YEARS.map((y) => (
                      <option key={y} value={y}>
                        {y}
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
                    id="dwt"
                    min="100"
                    step="any"
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
                    id="gt"
                    min="100"
                    step="any"
                    placeholder="e.g., 45000"
                    value={formData.gt}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="distance_nm"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Distance Sailed
                    <span className="text-slate-400 ml-1">[nm]</span>
                  </label>
                  <input
                    type="number"
                    id="distance_nm"
                    required
                    placeholder="e.g., 120000"
                    value={formData.distance_nm}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>
              </div>
            </section>

            {/* Fuel Consumption */}
            <section className="pt-6 border-t border-slate-200">
              <h3 className="flex items-center gap-2 text-lg font-bold text-slate-800 mb-5">
                <FontAwesomeIcon
                  icon={faGasPump}
                  className="text-blue-500"
                />
                2. Fuel Consumption (tonnes)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label
                    htmlFor="fc_hfo"
                    className="text-sm font-semibold text-slate-700"
                  >
                    HFO / RMG
                  </label>
                  <input
                    type="number"
                    id="fc_hfo"
                    value={formData.fc_hfo}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="fc_mdo"
                    className="text-sm font-semibold text-slate-700"
                  >
                    MDO / MGO
                  </label>
                  <input
                    type="number"
                    id="fc_mdo"
                    value={formData.fc_mdo}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="fc_lng"
                    className="text-sm font-semibold text-slate-700"
                  >
                    LNG
                  </label>
                  <input
                    type="number"
                    id="fc_lng"
                    value={formData.fc_lng}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="fc_methanol"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Methanol
                  </label>
                  <input
                    type="number"
                    id="fc_methanol"
                    value={formData.fc_methanol}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="fc_lpg_propane"
                    className="text-sm font-semibold text-slate-700"
                  >
                    LPG Propane
                  </label>
                  <input
                    type="number"
                    id="fc_lpg_propane"
                    value={formData.fc_lpg_propane}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="fc_lpg_butane"
                    className="text-sm font-semibold text-slate-700"
                  >
                    LPG Butane
                  </label>
                  <input
                    type="number"
                    id="fc_lpg_butane"
                    value={formData.fc_lpg_butane}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="fc_ethane"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Ethane
                  </label>
                  <input
                    type="number"
                    id="fc_ethane"
                    value={formData.fc_ethane}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>
              </div>
            </section>

            {/* Correction Factors */}
            <section className="pt-6 border-t border-slate-200">
              <h3 className="flex items-center gap-2 text-lg font-bold text-slate-800 mb-5">
                <FontAwesomeIcon
                  icon={faPlusCircle}
                  className="text-blue-500"
                />
                3. Correction Factors (Optional)
              </h3>

              {isTanker && (
                <div className="space-y-2 mb-6">
                  <label className="text-sm font-semibold text-slate-700">
                    STS / Shuttle Tanker Operation
                  </label>
                  <select
                    id="tanker_op"
                    value={formData.tanker_op}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  >
                    <option value="none">Standard Operation</option>
                    <option value="sts">Ship-to-Ship (STS)</option>
                    <option value="shuttle">Shuttle Tanker</option>
                  </select>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label
                    htmlFor="reefer_kwh"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Reefer Energy [kWh]
                  </label>
                  <input
                    type="number"
                    id="reefer_kwh"
                    value={formData.reefer_kwh}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="sfoc_electrical"
                    className="text-sm font-semibold text-slate-700"
                  >
                    SFOC Aux Engines
                  </label>
                  <input
                    type="number"
                    id="sfoc_electrical"
                    value={formData.sfoc_electrical}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="voyage_hfo"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Voyage Deductions [t]
                  </label>
                  <input
                    type="number"
                    id="voyage_hfo"
                    value={formData.voyage_hfo}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label
                    htmlFor="voyage_distance"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Distance Deducted [nm]
                  </label>
                  <input
                    type="number"
                    id="voyage_distance"
                    value={formData.voyage_distance}
                    step="any"
                    onChange={handleChange}
                    className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
                  />
                </div>
              </div>
            </section>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/30 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              <FontAwesomeIcon icon={faCalculator} />
              {loading ? 'Calculating...' : 'Calculate CII'}
            </button>
          </form>
        </div>

        {/* Results Section */}
        <div
          className={`bg-white rounded-2xl shadow-lg border border-slate-200 p-8 ${!results ? 'opacity-50 pointer-events-none' : ''}`}
        >
          <div className="flex items-center gap-3 mb-8">
            <FontAwesomeIcon
              icon={faPoll}
              className="text-3xl text-blue-600"
            />
            <div>
              <h3 className="text-2xl font-bold text-slate-800">
                Performance Assessment
              </h3>
            </div>
          </div>

          {results && (
            <>
              {/* Rating Display */}
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white text-6xl font-extrabold shadow-lg shadow-blue-500/25 mb-3">
                  {results.rating?.rating || '—'}
                </div>
                <div className="text-slate-600">CII Rating</div>
              </div>

              {/* Rating Band */}
              <div className="relative mb-8 h-12 rounded-full overflow-hidden bg-slate-100">
                <div className="absolute inset-0 flex">
                  <div className="w-1/5 h-full bg-emerald-600 opacity-70 flex items-center justify-center text-white font-bold">
                    A
                  </div>
                  <div className="w-1/5 h-full bg-emerald-400 opacity-70 flex items-center justify-center text-white font-bold">
                    B
                  </div>
                  <div className="w-1/5 h-full bg-amber-500 opacity-70 flex items-center justify-center text-white font-bold">
                    C
                  </div>
                  <div className="w-1/5 h-full bg-red-500 opacity-70 flex items-center justify-center text-white font-bold">
                    D
                  </div>
                  <div className="w-1/5 h-full bg-red-700 opacity-70 flex items-center justify-center text-white font-bold">
                    E
                  </div>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-center">
                  <div className="text-sm text-slate-500 font-semibold uppercase mb-1">
                    Attained
                  </div>
                  <div className="text-3xl font-extrabold text-slate-800">
                    {results.attained_cii?.toFixed(2) || '—'}
                  </div>
                  <div className="text-xs text-slate-400">
                    gCO₂/(cap·nm)
                  </div>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 text-center">
                  <div className="text-sm text-blue-600 font-semibold uppercase mb-1">
                    Required
                  </div>
                  <div className="text-3xl font-extrabold text-blue-800">
                    {results.required_cii?.toFixed(2) || '—'}
                  </div>
                  <div className="text-xs text-blue-500">
                    gCO₂/(cap·nm)
                  </div>
                </div>
                <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-center">
                  <div className="text-sm text-emerald-600 font-semibold uppercase mb-1">
                    Compliance
                  </div>
                  <div className="text-3xl font-extrabold text-emerald-800">
                    {results.rating?.margin_pct?.toFixed(2) || '—'}%
                  </div>
                  <div className="text-xs text-emerald-500">
                    Margin
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={resetForm}
                  className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold rounded-xl transition-all"
                >
                  <FontAwesomeIcon icon={faRedo} />
                  Reset
                </button>
                <button
                  onClick={handleDownloadReport}
                  disabled={loadingReport}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/25 transition-all disabled:opacity-70"
                >
                  <FontAwesomeIcon icon={faDownload} />
                  {loadingReport ? 'Generating...' : 'Download Report'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
