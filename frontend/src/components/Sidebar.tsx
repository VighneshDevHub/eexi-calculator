'use client';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faShip,
  faTimes,
  faCalculator,
  faChartLine,
  faWind,
  faCube,
  faRulerCombined,
  faFileInvoice,
  faUserShield,
  faBook,
} from '@fortawesome/free-solid-svg-icons';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const navItems = [
  { href: '/', label: 'EEXI Calculator', icon: faCalculator },
  { href: '/cii', label: 'CII Calculator', icon: faChartLine },
  { href: '/egbp', label: 'EGBP Calculator', icon: faWind },
  { href: '/pipe', label: 'Pipe Wall Calc', icon: faCube },
  { href: '/interpolator', label: 'Linear Interpolator', icon: faRulerCombined },
  { href: '/history', label: 'Assessment History', icon: faFileInvoice },
  { href: '/admin', label: 'Admin Dashboard', icon: faUserShield },
  { href: '/manual', label: 'User Manual', icon: faBook },
];

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      <div
        className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onToggle}
      />
      
      <aside
        className={`fixed top-0 left-0 z-50 w-64 h-full bg-slate-900 text-slate-100 sidebar-transition shadow-2xl ${isOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0`}
      >
        <div className="flex items-center justify-between p-6 border-b border-slate-700/50">
          <Link href="/" className="flex items-center gap-3">
            <FontAwesomeIcon
              icon={faShip}
              className="text-2xl text-blue-500 animate-pulse-glow"
            />
            <div className="flex flex-col">
              <span className="text-base font-extrabold tracking-wider bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent uppercase">
                Maritime Suite
              </span>
              <span className="text-xs font-medium text-slate-400 uppercase">
                Compliance & Analysis
              </span>
            </div>
          </Link>
          <button
            onClick={onToggle}
            className="lg:hidden p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <FontAwesomeIcon icon={faTimes} />
          </button>
        </div>
        
        <nav className="flex-1 p-3 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onToggle}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 transition-all duration-200 font-medium text-sm relative group
                  ${isActive
                    ? 'text-white bg-blue-500/10 font-semibold'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50 hover:translate-x-1'}
                `}
              >
                {isActive && (
                  <div className="absolute left-0 top-2 bottom-2 w-1 bg-blue-500 rounded-r-full shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
                )}
                <FontAwesomeIcon
                  icon={item.icon}
                  className={`w-5 text-center transition-transform duration-200 ${isActive ? 'text-blue-500' : 'group-hover:scale-110 group-hover:text-blue-500'}`}
                />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        
        <div className="p-6 border-t border-slate-700/50 bg-black/10">
          <div className="flex items-center gap-3">
            <div className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-xs font-bold">
              v2.0.0
            </div>
            <div className="text-xs text-slate-500">
              <p>© {new Date().getFullYear()} Goltens</p>
              <p>Maritime Compliance</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
