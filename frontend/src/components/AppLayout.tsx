'use client';

import { useState } from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

interface AppLayoutProps {
  children: React.ReactNode;
  title: string;
}

export default function AppLayout({ children, title }: AppLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

  return (
    <>
      <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />
      <main className="flex-1 ml-0 lg:ml-64 main-content-transition min-h-screen flex flex-col">
        <TopBar onMenuClick={toggleSidebar} title={title} />
        <div className="p-6 flex-1">
          {children}
        </div>
      </main>
    </>
  );
}
