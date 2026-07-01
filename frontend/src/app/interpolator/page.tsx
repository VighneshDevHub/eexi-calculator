'use client';

import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRulerCombined, faFileImport, faEraser, faCalculator } from '@fortawesome/free-solid-svg-icons';
import AppLayout from '@/components/AppLayout';
import { apiRequest } from '@/lib/api';

interface InterpolationData {
  x1: string;
  y1: string;
  x2: string;
  y2: string;
  x3: string;
  y3: string;
}

interface InterpolationResult {
  blank_field: string;
  result: number;
  result_str: string;
  all_values: Record<string, string>;
  formula_used: string;
  steps: string[];
}

export default function InterpolatorPage() {
  const [data, setData] = useState<InterpolationData>({
    x1: '',
    y1: '',
    x2: '',
    y2: '',
    x3: '',
    y3: '',
  });

  const [results, setResults] = useState<InterpolationResult | null>(null);

  const handleChange = (key: keyof InterpolationData, value: string) => {
    setData(prev => ({ ...prev, [key]: value }));
  };

  const loadExample = () => {
    setData({
      x1: '100',
      y1: '0.25',
      x2: '200',
      y2: '0.18',
      x3: '150',
      y3: '',
    });
  };

  const resetAll = () => {
    setData({
      x1: '',
      y1: '',
      x2: '',
      y2: '',
      x3: '',
      y3: '',
    });
    setResults(null);
  };

  const calculate = async () => {
    try {
      const result = await apiRequest<InterpolationResult>('/api/calculate-interpolator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      setResults(result);
      setData(prev => ({
        ...prev,
        [result.blank_field]: result.result_str,
      }));
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Calculation error! Please check your inputs.');
    }
  };

  return (
    <AppLayout title="Linear Interpolator">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <FontAwesomeIcon
                icon={faRulerCombined}
                className="text-3xl text-blue-600"
              />
              <div>
                <h2 className="text-2xl font-bold text-slate-800">
                  Interpolation Calculator
                </h2>
                <p className="text-slate-500 text-sm">
                  Fill in five values and leave one blank. Click Calculate to
                  solve.
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={loadExample}
                className="flex items-center gap-2 px-4 py-2 border-2 border-slate-200 hover:border-blue-500 hover:text-blue-600 rounded-lg text-sm font-semibold transition-all"
              >
                <FontAwesomeIcon icon={faFileImport} /> Load Example
              </button>
              <button
                onClick={resetAll}
                className="flex items-center gap-2 px-4 py-2 border-2 border-slate-200 hover:border-slate-400 rounded-lg text-sm font-semibold transition-all"
              >
                <FontAwesomeIcon icon={faEraser} /> Clear
              </button>
            </div>
          </div>

          <div className="mb-8">
            <svg
              width="100%"
              viewBox="0 0 320 115"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <marker
                  id="arrowhead"
                  viewBox="0 0 8 8"
                  refX="6"
                  refY="4"
                  markerWidth="5"
                  markerHeight="5"
                  orient="auto"
                >
                  <path
                    d="M1 1L7 4L1 7"
                    fill="none"
                    stroke="#888780"
                    strokeWidth="1.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </marker>
              </defs>
              <line
                x1="30"
                y1="90"
                x2="300"
                y2="90"
                stroke="#B4B2A9"
                strokeWidth="1"
                markerEnd="url(#arrowhead)"
              />
              <line
                x1="30"
                y1="90"
                x2="30"
                y2="10"
                stroke="#B4B2A9"
                strokeWidth="1"
                markerEnd="url(#arrowhead)"
              />
              <polyline
                points="34,85 60,70 90,48 120,32 150,23 185,19 225,18 270,20"
                fill="none"
                stroke="#D3D1C7"
                strokeWidth="1"
                strokeDasharray="3,2"
              />
              <line
                x1="80"
                y1="50"
                x2="220"
                y2="20"
                stroke="#5F5E5A"
                strokeWidth="1.5"
              />
              <circle cx="80" cy="50" r="4.5" fill="white" stroke="#5F5E5A" strokeWidth="1.5" />
              <line x1="80" y1="91" x2="80" y2="50" stroke="#B4B2A9" strokeWidth="0.8" strokeDasharray="3,2" />
              <text x="80" y="104" fontSize="12" fill="#5F5E5A" textAnchor="middle" fontFamily="system-ui,sans-serif">
                x₁
              </text>
              <circle cx="148" cy="35" r="5" fill="#E6F1FB" stroke="#185FA5" strokeWidth="1.5" />
              <line x1="148" y1="91" x2="148" y2="35" stroke="#185FA5" strokeWidth="0.8" strokeDasharray="3,2" />
              <text x="148" y="104" fontSize="12" fill="#185FA5" textAnchor="middle" fontFamily="system-ui,sans-serif">
                x₃
              </text>
              <circle cx="220" cy="20" r="4.5" fill="white" stroke="#5F5E5A" strokeWidth="1.5" />
              <line x1="220" y1="91" x2="220" y2="20" stroke="#B4B2A9" strokeWidth="0.8" strokeDasharray="3,2" />
              <text x="220" y="104" fontSize="12" fill="#5F5E5A" textAnchor="middle" fontFamily="system-ui,sans-serif">
                x₂
              </text>
              <text x="305" y="94" fontSize="11" fill="#888780" fontFamily="system-ui,sans-serif">
                x
              </text>
              <text x="22" y="10" fontSize="11" fill="#888780" fontFamily="system-ui,sans-serif">
                y
              </text>
            </svg>
          </div>

          <div className="mb-8">
            <div className="grid grid-cols-2 gap-2 mb-2">
              <div className="text-sm font-semibold text-slate-600 uppercase">x</div>
              <div className="text-sm font-semibold text-slate-600 uppercase">y</div>
            </div>
            {[
              { xKey: 'x1', xLabel: 'x₁', yKey: 'y1', yLabel: 'y₁' },
              { xKey: 'x2', xLabel: 'x₂', yKey: 'y2', yLabel: 'y₂' },
              { xKey: 'x3', xLabel: 'x₃', yKey: 'y3', yLabel: 'y₃' },
            ].map((row, idx) => (
              <div key={idx} className="grid grid-cols-2 gap-4 mb-4">
                <input
                  type="number"
                  step="any"
                  placeholder={row.xLabel}
                  value={data[row.xKey as keyof InterpolationData]}
                  onChange={(e) => handleChange(row.xKey as keyof InterpolationData, e.target.value)}
                  className={`px-4 py-3 border-2 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all ${
                    results?.blank_field === row.xKey
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-slate-200'
                  }`}
                />
                <input
                  type="number"
                  step="any"
                  placeholder={row.yLabel}
                  value={data[row.yKey as keyof InterpolationData]}
                  onChange={(e) => handleChange(row.yKey as keyof InterpolationData, e.target.value)}
                  className={`px-4 py-3 border-2 rounded-xl text-slate-800 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all ${
                    results?.blank_field === row.yKey
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-slate-200'
                  }`}
                />
              </div>
            ))}
          </div>

          <button
            onClick={calculate}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/30 transition-all"
          >
            <FontAwesomeIcon icon={faCalculator} /> Calculate
          </button>
        </div>

        {results && (
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
            <h2 className="text-2xl font-bold text-slate-800 mb-6">Result</h2>
            
            {/* Answer */}
            <div className="mb-6 p-6 bg-blue-50 border border-blue-200 rounded-xl text-center">
              <div className="text-sm text-blue-600 font-semibold uppercase mb-2">
                Answer
              </div>
              <div className="text-4xl font-extrabold text-blue-900">
                {results.result_str}
              </div>
              <div className="text-lg text-blue-700 mt-2">
                {results.blank_field.replace('x', 'x₍').replace('y', 'y₍').replace(/([0-9])/g, '$1₎')}
              </div>
            </div>

            {/* Formula Used */}
            <div className="mb-6">
              <div className="text-sm text-slate-500 font-semibold uppercase mb-2">
                Formula Used
              </div>
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg font-mono text-sm text-slate-800">
                {results.formula_used}
              </div>
            </div>

            {/* Step-by-Step */}
            <details className="mb-6" open>
              <summary className="text-sm text-slate-500 font-semibold uppercase mb-3 cursor-pointer">
                Step-by-Step Derivation
              </summary>
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                <ol className="list-decimal list-inside space-y-2 text-slate-800 font-mono text-sm">
                  {results.steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            </details>

            {/* All Six Values */}
            <div>
              <div className="text-sm text-slate-500 font-semibold uppercase mb-3">
                All Six Values
              </div>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(results.all_values).map(([key, value]) => (
                  <div
                    key={key}
                    className={`p-3 border rounded-lg text-center ${
                      results.blank_field === key
                        ? 'bg-blue-50 border-blue-200'
                        : 'bg-slate-50 border-slate-200'
                    }`}
                  >
                    <div className="text-xs font-semibold text-slate-500 uppercase">
                      {key.replace('x', 'x₍').replace('y', 'y₍').replace(/([0-9])/g, '$1₎')}
                    </div>
                    <div className="text-lg font-bold text-slate-800">
                      {value}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
