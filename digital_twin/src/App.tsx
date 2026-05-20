import { useState } from 'react';
import { SimulationProvider, useSimulation } from './context/SimulationContext';
import { ControlPanel } from './components/ControlPanel';
import { FactoryVisualizer } from './components/FactoryVisualizer';
import { TelemetrySidebar } from './components/TelemetrySidebar';
import { Activity, ShieldCheck, ShieldAlert, Wrench } from 'lucide-react';

function DashboardShell() {
  const [selectedMachineId, setSelectedMachineId] = useState<string | null>(null);
  const { machines, metrics } = useSimulation();

  // Find system status based on machines
  const hasError = machines.some((m) => m.status === 'ERROR');
  const hasMaintenance = machines.some((m) => m.status === 'MAINTENANCE');

  const getSystemStatusHeader = () => {
    if (hasError) {
      return (
        <div className="flex items-center gap-2 text-[var(--color-red)] font-bold text-sm bg-[var(--color-red-glow)] py-1 px-3 rounded-full border border-red-500/25 animate-pulse">
          <ShieldAlert size={16} />
          SYSTEM CRITICAL: MACHINE FAULT DETECTED
        </div>
      );
    }
    if (hasMaintenance) {
      return (
        <div className="flex items-center gap-2 text-[var(--color-orange)] font-bold text-sm bg-[var(--color-orange-glow)] py-1 px-3 rounded-full border border-amber-500/25">
          <Wrench size={16} />
          SYSTEM ALIGNED: CALIBRATION IN PROGRESS
        </div>
      );
    }
    return (
      <div className="flex items-center gap-2 text-[var(--color-green)] font-bold text-sm bg-[var(--color-green-glow)] py-1 px-3 rounded-full border border-emerald-500/25">
        <ShieldCheck size={16} />
        ALL SYSTEMS OPERATIONAL
      </div>
    );
  };

  // Convert uptime seconds into mm:ss or hh:mm:ss format
  const formatUptime = (totalSeconds: number) => {
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = Math.floor(totalSeconds % 60);
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen flex flex-col bg-[var(--bg-darker)] overflow-hidden">
      {/* Header bar */}
      <header className="px-6 py-4 border-b border-[var(--border-soft)] bg-slate-950/60 backdrop-blur-md flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="bg-[var(--color-blue-glow)] p-2 rounded-lg border border-[#0ea5e9]/30">
            <Activity className="text-[var(--color-blue)] w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-black uppercase tracking-wider font-mono m-0 text-slate-100 flex items-center gap-2">
              Cyber Factory <span className="text-[var(--color-blue)]">Digital Twin</span>
            </h1>
            <p className="text-[10px] text-slate-500 font-mono tracking-widest uppercase m-0 mt-0.5">
              Live IoT Physical System Mockup • In-Memory Simulation Engine
            </p>
          </div>
        </div>

        {/* Global status & active ticks */}
        <div className="hidden md:flex items-center gap-6">
          {getSystemStatusHeader()}

          <div className="flex flex-col text-right font-mono">
            <span className="text-[9px] text-slate-500 uppercase tracking-wider">Sim Running Time</span>
            <span className="text-sm font-bold text-slate-200">{formatUptime(metrics.uptime)}</span>
          </div>
        </div>
      </header>

      {/* Main Grid Wrapper */}
      <main className="dashboard-grid flex-1">
        {/* Left Side: Control Panel */}
        <ControlPanel />

        {/* Center: Live Floor Visualizer */}
        <FactoryVisualizer
          selectedMachineId={selectedMachineId}
          onSelectMachine={setSelectedMachineId}
        />

        {/* Right Side: Telemetry Sidebar */}
        <TelemetrySidebar
          selectedMachineId={selectedMachineId}
          onClearSelection={() => setSelectedMachineId(null)}
        />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <SimulationProvider>
      <DashboardShell />
    </SimulationProvider>
  );
}
