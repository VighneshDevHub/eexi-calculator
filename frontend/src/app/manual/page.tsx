'use client';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faShip,
  faChartLine,
  faWind,
  faMicroscope,
  faShield,
  faCheckCircle,
  faTachometerAlt,
  faLightbulb,
  faBolt,
  faLeaf,
} from '@fortawesome/free-solid-svg-icons';
import AppLayout from '@/components/AppLayout';

export default function ManualPage() {
  return (
    <AppLayout title="User Manual">
      <div className="space-y-12">
        {/* Hero Section */}
        <div className="relative rounded-2xl overflow-hidden shadow-lg" style={{
          background: 'url("https://images.unsplash.com/photo-1516216628859-9bccecad13ef?auto=format&fit=crop&q=80&w=2000") center/cover',
          height: '350px',
        }}>
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900/90 to-blue-600/50"></div>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center text-white p-8">
            <span className="bg-blue-600 text-white px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider mb-6">
              Technical Documentation
            </span>
            <h1 className="text-5xl font-extrabold mb-2 drop-shadow-lg">
              Maritime Suite User Manual
            </h1>
            <p className="text-xl opacity-90">
              Mastering EEXI, CII, and EGBP Compliance Tools
            </p>
          </div>
        </div>

        {/* EEXI Section */}
        <section className="bg-white rounded-2xl shadow-lg border border-slate-200 p-10">
          <div className="flex items-start gap-8">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center shrink-0 shadow-lg">
              <FontAwesomeIcon icon={faShip} className="text-4xl text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">1. Energy Efficiency Existing Ship Index (EEXI)</h2>
              <div className="p-6 bg-slate-50 border-l-4 border-blue-600 rounded-xl mb-8">
                <p className="text-slate-700 leading-relaxed">
                  The EEXI is a technical measure applicable to existing ships above 400 GT. It evaluates a vessel's design efficiency based on its technical specifications rather than operational performance.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h3 className="flex items-center gap-2 text-xl font-semibold text-blue-700 mb-3">
                    <FontAwesomeIcon icon={faCheckCircle} />
                    Applicability
                  </h3>
                  <p className="text-slate-600">
                    Mandatory for all ships subject to MARPOL Annex VI regulations. Includes tankers, bulk carriers, gas carriers, and container ships.
                  </p>
                </div>
                <div>
                  <h3 className="flex items-center gap-2 text-xl font-semibold text-blue-700 mb-3">
                    <FontAwesomeIcon icon={faTachometerAlt} />
                    Key Metric
                  </h3>
                  <p className="text-slate-600">
                    Measures gCO2 emissions per tonne-mile based on design parameters (MCR, SFC, Speed, Capacity).
                  </p>
                </div>
              </div>

              <div className="p-5 bg-yellow-50 border border-yellow-200 rounded-xl flex items-start gap-4">
                <FontAwesomeIcon icon={faLightbulb} className="text-2xl text-yellow-600 mt-0.5" />
                <div>
                  <h4 className="font-bold text-slate-800 mb-1">Pro Tip</h4>
                  <p className="text-slate-700">
                    Ensure you use certified SFOC values from the engine's Technical File for accurate EEXI results.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CII Section */}
        <section className="bg-white rounded-2xl shadow-lg border border-slate-200 p-10">
          <div className="flex items-start gap-8">
            <div className="w-20 h-20 bg-gradient-to-br from-green-600 to-green-700 rounded-2xl flex items-center justify-center shrink-0 shadow-lg">
              <FontAwesomeIcon icon={faChartLine} className="text-4xl text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">2. Carbon Intensity Indicator (CII)</h2>
              <div className="p-6 bg-slate-50 border-l-4 border-green-600 rounded-xl mb-8">
                <p className="text-slate-700 leading-relaxed">
                  Unlike EEXI, CII is an <strong>operational measure</strong>. It rates ships from A to E based on how they are actually operated throughout the year, focusing on fuel consumption and distance sailed.
                </p>
              </div>

              <div className="flex gap-3 mb-8">
                <div className="flex-1 bg-green-700 text-white py-3 rounded-lg text-center font-extrabold text-lg">A</div>
                <div className="flex-1 bg-green-600 text-white py-3 rounded-lg text-center font-extrabold text-lg">B</div>
                <div className="flex-1 bg-yellow-500 text-white py-3 rounded-lg text-center font-extrabold text-lg">C</div>
                <div className="flex-1 bg-red-600 text-white py-3 rounded-lg text-center font-extrabold text-lg">D</div>
                <div className="flex-1 bg-red-800 text-white py-3 rounded-lg text-center font-extrabold text-lg">E</div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xl font-semibold text-slate-800 mb-3">Annual Assessment</h3>
                  <p className="text-slate-600">
                    CII targets become 2% stricter every year from 2023 to 2027 to encourage continuous improvement.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-slate-800 mb-3">SEEMP Part III</h3>
                  <p className="text-slate-600">
                    Vessels rated D for three consecutive years or E for one year must submit an implementation plan for improvement.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* EGBP Section */}
        <section className="bg-white rounded-2xl shadow-lg border border-slate-200 p-10">
          <div className="flex items-start gap-8">
            <div className="w-20 h-20 bg-gradient-to-br from-amber-600 to-amber-700 rounded-2xl flex items-center justify-center shrink-0 shadow-lg">
              <FontAwesomeIcon icon={faWind} className="text-4xl text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">3. Exhaust Gas Back Pressure (EGBP)</h2>
              <div className="p-6 bg-slate-50 border-l-4 border-amber-600 rounded-xl mb-8">
                <p className="text-slate-700 leading-relaxed">
                  Essential for scrubber retrofits and engine health. Our calculator uses the Darcy-Weisbach methodology to ensure your exhaust system remains within manufacturer limits.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-5xl font-extrabold text-slate-200 absolute top-4 right-4">01</span>
                  <h4 className="text-lg font-semibold text-slate-800 mb-2">Define Elements</h4>
                  <p className="text-sm text-slate-600">
                    Add pipes, bends, valves, and silencers to your system model.
                  </p>
                </div>
                <div className="p-6 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-5xl font-extrabold text-slate-200 absolute top-4 right-4">02</span>
                  <h4 className="text-lg font-semibold text-slate-800 mb-2">Set Flow Data</h4>
                  <p className="text-sm text-slate-600">
                    Enter mass flow and temperature after the turbocharger.
                  </p>
                </div>
                <div className="p-6 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-5xl font-extrabold text-slate-200 absolute top-4 right-4">03</span>
                  <h4 className="text-lg font-semibold text-slate-800 mb-2">Analyze Loss</h4>
                  <p className="text-sm text-slate-600">
                    Identify which components cause the most pressure drop (ΔP).
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Methodology Section */}
        <section className="bg-white rounded-2xl shadow-lg border border-slate-200 p-10">
          <div className="flex items-start gap-8">
            <div className="w-20 h-20 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl flex items-center justify-center shrink-0 shadow-lg">
              <FontAwesomeIcon icon={faMicroscope} className="text-4xl text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">4. Technical Methodology</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="p-8 bg-slate-800 text-white rounded-xl text-center">
                  <div className="text-xs uppercase tracking-widest text-slate-300 mb-4">EEXI Attained</div>
                  <code className="text-lg font-mono">
                    (P<sub>ME</sub> × C<sub>F</sub> × SFC) / (Capacity × V<sub>ref</sub>)
                  </code>
                </div>
                <div className="p-8 bg-slate-800 text-white rounded-xl text-center">
                  <div className="text-xs uppercase tracking-widest text-slate-300 mb-4">Pressure Loss (ΔP)</div>
                  <code className="text-lg font-mono">
                    ξ × (ρ/2) × v²
                  </code>
                </div>
              </div>
              <p className="text-slate-600">
                Our calculators are built upon IMO Resolution MEPC.350(78) and Wärtsilä engineering standards to ensure regulatory compliance and engineering accuracy.
              </p>
            </div>
          </div>
        </section>

        {/* Solutions Section */}
        <section className="bg-white rounded-2xl shadow-lg border border-slate-200 p-10">
          <div className="flex items-start gap-8">
            <div className="w-20 h-20 bg-gradient-to-br from-red-600 to-red-700 rounded-2xl flex items-center justify-center shrink-0 shadow-lg">
              <FontAwesomeIcon icon={faShield} className="text-4xl text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">5. Compliance Solutions</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <FontAwesomeIcon icon={faBolt} className="text-2xl text-blue-600" />
                    <h4 className="text-xl font-semibold text-slate-800">Engine Power Limitation (EPL)</h4>
                  </div>
                  <p className="text-slate-600 ml-10">
                    The most common technical solution for EEXI compliance. Our tool recommends the exact MCR<sub>lim</sub> needed to pass.
                  </p>
                </div>
                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <FontAwesomeIcon icon={faLeaf} className="text-2xl text-green-600" />
                    <h4 className="text-xl font-semibold text-slate-800">Operational Efficiency</h4>
                  </div>
                  <p className="text-slate-600 ml-10">
                    Improve CII ratings through slow steaming, route optimization, and frequent hull cleaning.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  );
}
