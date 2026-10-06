import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { MobileNavigation } from './MobileNavigation';

export const AppLayout = () => {
  return (
    <div className="app-shell min-h-screen bg-[#0b0e17] text-slate-100 flex overflow-x-hidden">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Shell */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0 w-full">
        <Header />

        <main className="flex-1 px-3 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 pb-24 lg:pb-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>

        <MobileNavigation />
      </div>
    </div>
  );
};
