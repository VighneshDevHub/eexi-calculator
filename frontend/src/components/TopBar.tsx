'use client';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBars, faBell, faUser } from '@fortawesome/free-solid-svg-icons';

interface TopBarProps {
  onMenuClick: () => void;
  title: string;
}

export default function TopBar({ onMenuClick, title }: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between px-6 py-3 bg-white/80 backdrop-blur-xl border-b border-slate-200 shadow-sm">
      <div className="flex items-center gap-6">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-700"
        >
          <FontAwesomeIcon icon={faBars} className="text-xl" />
        </button>
        <h1 className="text-xl font-bold text-slate-800">{title}</h1>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="w-10 h-10 flex items-center justify-center text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition-all">
          <FontAwesomeIcon icon={faBell} />
        </button>
        
        <div className="flex items-center gap-3 px-3 py-2 bg-slate-50 rounded-full border border-slate-200 hover:border-blue-300 hover:bg-white hover:shadow-sm transition-all cursor-pointer">
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-bold text-slate-800 hidden sm:block">Engineering Team</span>
            <span className="text-xs text-slate-500">
              {new Date().toLocaleDateString('en-GB', {
                day: 'numeric',
                month: 'short',
                year: 'numeric',
              })}
            </span>
          </div>
          <div className="w-8 h-8 flex items-center justify-center bg-blue-500 text-white rounded-full">
            <FontAwesomeIcon icon={faUser} size="sm" />
          </div>
        </div>
      </div>
    </header>
  );
}
