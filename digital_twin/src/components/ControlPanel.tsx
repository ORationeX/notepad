import React from 'react';
import { useSimulation } from '../context/SimulationContext';
import { Play, Pause, RotateCcw, Sliders } from 'lucide-react';

export const ControlPanel: React.FC = () => {
  const {
    isPlaying,
    speedMultiplier,
    defectProbability,
    wearRateMultiplier,
    metrics,
    machines,
    togglePlay,
    setSpeed,
    setDefectProbability,
    setWearRateMultiplier,
    resetSimulation,
    performMaintenance,
    triggerBreakdown,
  } = useSimulation();

  return (
    <div className="glass-panel panel-container flex flex-col h-full">
      {/* Header */}
      <div className="px-6 py-4 border-b border-[var(--border-soft)] flex items-center gap-3">
        <Sliders className="text-[var(--color-blue)] w-5 h-5" />
        <h2 className="text-xl font-bold uppercase tracking-wider font-mono m-0 text-slate-100">
          Control Center
        </h2>
      </div>

      <div className="panel-body flex flex-col gap-6">
        {/* Play/Pause & Speed */}
        <div className="flex flex-col gap-3">
          <label className="text-xs uppercase tracking-widest text-slate-400 font-mono">Simulation Control</label>
          <div className="flex gap-2">
            <button
              onClick={togglePlay}
              className={`flex-1 neon-btn ${isPlaying ? 'neon-btn-warning' : 'neon-btn-success'}`}
            >
              {isPlaying ? <Pause size={16} /> : <Play size={16} />}
              {isPlaying ? 'PAUSE' : 'RESUME'}
            </button>
            <button
              onClick={resetSimulation}
              className="neon-btn neon-btn-danger px-4"
              title="Reset Simulation"
            >
              <RotateCcw size={16} />
              RESET
            </button>
          </div>

          {/* Speed Selection */}
          <div className="grid grid-cols-4 gap-1 bg-slate-900/60 p-1 rounded-md border border-[var(--border-soft)]">
            {([0.5, 1, 2, 5] as const).map((spd) => (
              <button
                key={spd}
                onClick={() => setSpeed(spd)}
                className={`py-1 text-xs font-mono rounded transition-all ${
                  speedMultiplier === spd
                    ? 'bg-[var(--color-blue)] text-slate-950 font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {spd}x
              </button>
            ))}
          </div>
        </div>

        {/* Adjusters (Sliders) */}
        <div className="flex flex-col gap-4 bg-slate-900/30 p-4 rounded-lg border border-[var(--border-soft)]">
          <label className="text-xs uppercase tracking-widest text-slate-300 font-bold font-mono">Parameters</label>
          
          {/* Defect Slider */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">DEFECT RATE LIMIT</span>
              <span className="text-[var(--color-orange)] font-bold">{(defectProbability * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.5"
              step="0.01"
              value={defectProbability}
              onChange={(e) => setDefectProbability(parseFloat(e.target.value))}
            />
          </div>

          {/* Wear Rate Multiplier Slider */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">WEAR-AND-TEAR COEFFICIENT</span>
              <span className="text-[var(--color-blue)] font-bold">{wearRateMultiplier.toFixed(1)}x</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="5.0"
              step="0.1"
              value={wearRateMultiplier}
              onChange={(e) => setWearRateMultiplier(parseFloat(e.target.value))}
            />
          </div>
        </div>

        {/* Global Factory Metrics counters */}
        <div className="flex flex-col gap-3">
          <label className="text-xs uppercase tracking-widest text-slate-400 font-mono">Operational Metrics</label>
          <div className="grid grid-cols-2 gap-3">
            {/* Total Processed */}
            <div className="bg-slate-900/40 p-3 rounded-lg border border-[var(--border-soft)] flex flex-col">
              <span className="text-[10px] text-slate-400 font-mono">TOTAL INGESTED</span>
              <span className="text-2xl font-bold font-mono text-slate-200 mt-1">{metrics.totalProcessed}</span>
            </div>
            {/* Total Completed */}
            <div className="bg-slate-900/40 p-3 rounded-lg border border-[var(--border-soft)] flex flex-col">
              <span className="text-[10px] text-slate-400 font-mono">TOTAL YIELD (OK)</span>
              <span className="text-2xl font-bold font-mono text-[var(--color-green)] mt-1">{metrics.totalCompleted}</span>
            </div>
            {/* Total Defects */}
            <div className="bg-slate-900/40 p-3 rounded-lg border border-[var(--border-soft)] flex flex-col">
              <span className="text-[10px] text-slate-400 font-mono">TOTAL REJECTS (NG)</span>
              <span className="text-2xl font-bold font-mono text-[var(--color-red)] mt-1">{metrics.totalDefects}</span>
            </div>
            {/* Power Consumption */}
            <div className="bg-slate-900/40 p-3 rounded-lg border border-[var(--border-soft)] flex flex-col">
              <span className="text-[10px] text-slate-400 font-mono">ENERGY CONSU.</span>
              <span className="text-2xl font-bold font-mono text-[var(--color-blue)] mt-1 flex items-baseline gap-1">
                {metrics.currentEnergy.toFixed(2)}
                <span className="text-[10px] text-slate-500">kWh</span>
              </span>
            </div>
          </div>
        </div>

        {/* Machine Fast Controls List */}
        <div className="flex flex-col gap-3 flex-1 overflow-hidden">
          <label className="text-xs uppercase tracking-widest text-slate-400 font-mono">
            Machine Quick Override
          </label>
          <div className="flex-1 overflow-y-auto flex flex-col gap-2.5 pr-1">
            {machines.map((machine) => {
              const wearColor =
                machine.wearLevel > 80
                  ? 'bg-[#ef4444]'
                  : machine.wearLevel > 50
                  ? 'bg-[#f59e0b]'
                  : 'bg-[#10b981]';

              return (
                <div
                  key={machine.id}
                  className="bg-slate-900/30 p-3 rounded-lg border border-[var(--border-soft)] flex flex-col gap-2"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-slate-200">{machine.name}</span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                      machine.status === 'RUNNING' ? 'text-[#10b981] bg-[#10b981]/10' :
                      machine.status === 'IDLE' ? 'text-[#0ea5e9] bg-[#0ea5e9]/10' :
                      machine.status === 'MAINTENANCE' ? 'text-[#f59e0b] bg-[#f59e0b]/10' :
                      'text-[#ef4444] bg-[#ef4444]/10 animate-pulse'
                    }`}>
                      {machine.status}
                    </span>
                  </div>

                  {/* Wear level mini bar */}
                  <div className="w-full bg-slate-850 h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${wearColor}`}
                      style={{ width: `${machine.wearLevel}%` }}
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 mt-1">
                    <button
                      onClick={() => performMaintenance(machine.id)}
                      disabled={machine.status === 'MAINTENANCE'}
                      className="flex-1 py-1 px-2 text-[10px] font-mono border border-slate-700 hover:border-[var(--color-orange)] text-slate-300 hover:text-[var(--color-orange)] rounded transition-all disabled:opacity-30 disabled:pointer-events-none"
                    >
                      🛠️ MAINTAIN
                    </button>
                    <button
                      onClick={() => triggerBreakdown(machine.id)}
                      disabled={machine.status === 'ERROR' || machine.status === 'MAINTENANCE'}
                      className="py-1 px-2 text-[10px] font-mono border border-slate-700 hover:border-[var(--color-red)] text-slate-300 hover:text-[var(--color-red)] rounded transition-all disabled:opacity-30 disabled:pointer-events-none"
                    >
                      💥 BREAK
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
