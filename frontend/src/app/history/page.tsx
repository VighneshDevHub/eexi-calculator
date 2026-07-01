'use client';

import { useEffect, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileInvoice } from '@fortawesome/free-solid-svg-icons';
import AppLayout from '@/components/AppLayout';
import { apiRequest } from '@/lib/api';

interface HistoryItem {
  id: number;
  calc_type: string;
  created_at: string;
  name?: string;
  ship_type?: string;
  status?: string;
  attained?: string;
  required?: string;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    try {
      const data = await apiRequest<HistoryItem[]>('/api/history');
      setHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout title="Assessment History">
      <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
        <div className="flex items-center gap-3 mb-8">
          <FontAwesomeIcon
            icon={faFileInvoice}
            className="text-3xl text-blue-600"
          />
          <div>
            <h2 className="text-2xl font-bold text-slate-800">
              Assessment History
            </h2>
            <p className="text-slate-500 text-sm">
              Review previous calculations from the local database.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
            <FontAwesomeIcon icon={faFileInvoice} />
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="text-2xl text-slate-400">Loading...</div>
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            No records found. Start a new calculation to see history.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Date</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Type</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Vessel / Parameters</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Attained</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Required / Limit</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={`${item.calc_type}-${item.id}`} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-3 px-4 text-sm text-slate-600">{item.created_at}</td>
                    <td className="py-3 px-4">
                      <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                        {item.calc_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-800 font-medium">
                      {item.name || item.ship_type || 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-sm text-slate-600">{item.attained}</td>
                    <td className="py-3 px-4 text-sm text-slate-600">{item.required}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          item.status?.includes('COMPLIANT') ||
                          item.status?.includes('PASS') ||
                          item.status?.includes('RATING A') ||
                          item.status?.includes('RATING B') ||
                          item.status?.includes('RATING C')
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
