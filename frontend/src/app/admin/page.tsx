'use client';

import { useEffect, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserShield } from '@fortawesome/free-solid-svg-icons';
import AppLayout from '@/components/AppLayout';
import { apiRequest } from '@/lib/api';

interface AdminStats {
  total_calculations: number;
  compliant_count: number;
  non_compliant_count: number;
  recent_vessels: any[];
}

export default function AdminPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, []);

  async function loadStats() {
    try {
      const data = await apiRequest<AdminStats>('/api/admin/stats');
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout title="Admin Dashboard">
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 text-center">
            <div className="text-sm text-slate-500 font-semibold uppercase mb-3">
              Total Calculations
            </div>
            <div className="text-5xl font-extrabold text-slate-800">
              {stats?.total_calculations || 0}
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 text-center">
            <div className="text-sm text-green-600 font-semibold uppercase mb-3">
              Compliant
            </div>
            <div className="text-5xl font-extrabold text-green-600">
              {stats?.compliant_count || 0}
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 text-center">
            <div className="text-sm text-red-600 font-semibold uppercase mb-3">
              Non-Compliant
            </div>
            <div className="text-5xl font-extrabold text-red-600">
              {stats?.non_compliant_count || 0}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
          <div className="flex items-center gap-3 mb-8">
            <FontAwesomeIcon
              icon={faUserShield}
              className="text-3xl text-blue-600"
            />
            <h2 className="text-2xl font-bold text-slate-800">
              Recent Calculations
            </h2>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="text-2xl text-slate-400">Loading...</div>
            </div>
          ) : error ? (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
              {error}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Vessel Name</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Ship Type</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Attained</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Required</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {stats?.recent_vessels.map((vessel) => (
                    <tr key={vessel.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm text-slate-800 font-medium">
                        {vessel.name || 'Unnamed'}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">
                        {vessel.ship_type}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">
                        {vessel.attained_eexi}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">
                        {vessel.required_eexi}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            vessel.status === 'COMPLIANT'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          {vessel.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
