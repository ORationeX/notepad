import React from 'react';
import { useSimulation } from '../context/SimulationContext';
import type { MetricSnapshot } from '../types';
import { ShieldAlert, Activity, ShieldCheck, Thermometer, Radio, Wrench, Zap } from 'lucide-react';

interface TelemetrySidebarProps {
  selectedMachineId: string | null;
  onClearSelection: () => void;
}

export const TelemetrySidebar: React.FC<TelemetrySidebarProps> = ({
  selectedMachineId,
  onClearSelection,
}) => {
  const {
    machines,
    alerts,
    history,
    performMaintenance,
    triggerBreakdown,
  } = useSimulation();

  const selectedMachine = machines.find((m) => m.id === selectedMachineId);

  // SVG Chart Generator Helper
  const renderLineChart = (
    data: MetricSnapshot[],
    dataKey: 'throughput' | 'defectRate' | 'energyConsumption',
    color: string,
    label: string,
    unit: string
  ) => {
    const width = 280;
    const height = 90;
    const padding = { top: 15, right: 10, bottom: 20, left: 35 };

    if (data.length < 2) {
      return (
        <div className="h-[90px] flex items-center justify-center border border-[var(--border-soft)] rounded bg-slate-950/20 text-xs text-slate-500 font-mono">
          AGGREGATING SENSOR TELEMETRY...
        </div>
      );
    }

    const values = data.map((d) => d[dataKey]);
    const maxVal = Math.max(...values, 0.1) * 1.1; // padding at top
    const minVal = 0;

    // Map points to SVG coordinates
    const points = data.map((d, i) => {
      const x = padding.left + (i / (data.length - 1)) * (width - padding.left - padding.right);
      // invert Y for SVG
      const y = padding.top + ((maxVal - d[dataKey]) / (maxVal - minVal)) * (height - padding.top - padding.bottom);
      return { x, y };
    });

    const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');
    
    // Closed path for filled gradient
    const fillPath = `${linePath} L ${points[points.length - 1].x.toFixed(1)} ${(height - padding.bottom).toFixed(1)} L ${points[0].x.toFixed(1)} ${(height - padding.bottom).toFixed(1)} Z`;

    return (
      <div className="flex flex-col gap-1">
        <div className="flex justify-between items-baseline font-mono">
          <span className="text-xs text-slate-400 font-bold uppercase">{label}</span>
          <span className="text-sm font-black" style={{ color }}>
            {values[values.length - 1]} <span className="text-[10px] text-slate-500">{unit}</span>
          </span>
        </div>
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} className="overflow-visible select-none">
          <defs>
            <linearGradient id={`grad-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.4" />
              <stop offset="100%" stopColor={color} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          <line x1={padding.left} y1={padding.top} x2={width - padding.right} y2={padding.top} stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1={padding.left} y1={(height - padding.bottom + padding.top) / 2} x2={width - padding.right} y2={(height - padding.bottom + padding.top) / 2} stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line
            x1={padding.left}
            y1={height - padding.bottom}
            x2={width - padding.right}
            y2={height - padding.bottom}
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="1.5"
          />

          {/* Left Axis label */}
          <text x={padding.left - 5} y={padding.top + 3} fill="rgba(255,255,255,0.3)" fontSize="8" fontFamily="var(--font-mono)" textAnchor="end">
            {maxVal.toFixed(1)}
          </text>
          <text x={padding.left - 5} y={height - padding.bottom + 2} fill="rgba(255,255,255,0.3)" fontSize="8" fontFamily="var(--font-mono)" textAnchor="end">
            0
          </text>

          {/* Filled gradient area */}
          <path d={fillPath} fill={`url(#grad-${dataKey})`} />

          {/* Sparkline curve */}
          <path d={linePath} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />

          {/* Highlight latest point */}
          <circle cx={points[points.length - 1].x} cy={points[points.length - 1].y} r="4" fill={color} stroke="#0f172a" strokeWidth="1.5" />
        </svg>
      </div>
    );
  };

  return (
    <div className="glass-panel panel-container flex flex-col h-full">
      {/* Header */}
      <div className="px-6 py-4 border-b border-[var(--border-soft)] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Radio className="text-[var(--color-blue)] w-5 h-5 animate-pulse" />
          <h2 className="text-xl font-bold uppercase tracking-wider font-mono m-0 text-slate-100">
            System Diagnostics
          </h2>
        </div>
        {selectedMachineId && (
          <button
            onClick={onClearSelection}
            className="text-[10px] font-mono bg-slate-800 hover:bg-slate-700 text-slate-300 py-0.5 px-1.5 rounded"
          >
            DESELECT
          </button>
        )}
      </div>

      <div className="panel-body flex flex-col gap-5">
        {/* Machine Telemetry Inspector */}
        <div className="flex-1 min-h-[220px] flex flex-col bg-slate-900/20 p-4 rounded-lg border border-[var(--border-soft)] overflow-hidden">
          {selectedMachine ? (
            <div className="flex flex-col h-full justify-between">
              {/* Header Title */}
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-base font-bold font-mono text-slate-100 uppercase m-0 leading-tight">
                    {selectedMachine.name}
                  </h3>
                  <span className="text-[10px] text-slate-500 font-mono tracking-wider">
                    MODULE ID: {selectedMachine.id.toUpperCase()}
                  </span>
                </div>
                <span className={`status-indicator ${
                  selectedMachine.status === 'RUNNING' ? 'status-running' :
                  selectedMachine.status === 'IDLE' ? 'status-idle' :
                  selectedMachine.status === 'MAINTENANCE' ? 'status-maintenance' :
                  'status-error'
                }`}>
                  {selectedMachine.status}
                </span>
              </div>

              {/* Core Telemetry Gauges Grid */}
              <div className="grid grid-cols-2 gap-4 my-3">
                {/* Temperature Card */}
                <div className="bg-slate-900/40 p-2.5 rounded border border-[var(--border-soft)] flex items-center gap-2.5">
                  <Thermometer className={selectedMachine.temperature > 60 ? 'text-[var(--color-red)]' : 'text-[var(--color-blue)]'} size={20} />
                  <div className="flex flex-col">
                    <span className="text-[9px] text-slate-500 font-mono uppercase">Core Temp</span>
                    <span className="text-sm font-bold font-mono text-slate-200">
                      {selectedMachine.temperature.toFixed(1)}°C
                    </span>
                  </div>
                </div>

                {/* Vibration Card */}
                <div className="bg-slate-900/40 p-2.5 rounded border border-[var(--border-soft)] flex items-center gap-2.5">
                  <Activity className={selectedMachine.vibration > 4.0 ? 'text-[var(--color-orange)] animate-bounce' : 'text-[var(--color-blue)]'} size={20} />
                  <div className="flex flex-col">
                    <span className="text-[9px] text-slate-500 font-mono uppercase">Vibration</span>
                    <span className="text-sm font-bold font-mono text-slate-200">
                      {selectedMachine.vibration.toFixed(2)} <span className="text-[8px] text-slate-400">mm/s</span>
                    </span>
                  </div>
                </div>

                {/* Energy Consumption Card */}
                <div className="bg-slate-900/40 p-2.5 rounded border border-[var(--border-soft)] flex items-center gap-2.5">
                  <Zap className="text-[var(--color-blue)]" size={20} />
                  <div className="flex flex-col">
                    <span className="text-[9px] text-slate-500 font-mono uppercase">Load Rate</span>
                    <span className="text-sm font-bold font-mono text-slate-200">
                      {selectedMachine.energyConsumption.toFixed(1)} <span className="text-[8px] text-slate-400">kW</span>
                    </span>
                  </div>
                </div>

                {/* Wear level card */}
                <div className="bg-slate-900/40 p-2.5 rounded border border-[var(--border-soft)] flex items-center gap-2.5">
                  <Wrench className={selectedMachine.wearLevel > 75 ? 'text-[var(--color-red)]' : 'text-[var(--color-blue)]'} size={20} />
                  <div className="flex flex-col">
                    <span className="text-[9px] text-slate-500 font-mono uppercase">Wear index</span>
                    <span className="text-sm font-bold font-mono text-slate-200">
                      {Math.round(selectedMachine.wearLevel)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Maintenance Scheduler Overlay Control */}
              <div className="flex gap-2">
                <button
                  onClick={() => performMaintenance(selectedMachine.id)}
                  disabled={selectedMachine.status === 'MAINTENANCE'}
                  className="flex-1 py-1.5 text-xs font-bold font-mono border border-[var(--color-orange)] text-[var(--color-orange)] hover:bg-[var(--color-orange)] hover:text-black rounded transition-all disabled:opacity-30 disabled:pointer-events-none"
                >
                  ⚙️ RUN REPAIR CALIBRATION
                </button>
                <button
                  onClick={() => triggerBreakdown(selectedMachine.id)}
                  disabled={selectedMachine.status === 'ERROR' || selectedMachine.status === 'MAINTENANCE'}
                  className="py-1.5 px-3 text-xs font-bold font-mono border border-[var(--color-red)] text-[var(--color-red)] hover:bg-[var(--color-red)] hover:text-white rounded transition-all disabled:opacity-30 disabled:pointer-events-none"
                  title="Force Breakdown to test failsafes"
                >
                  🚨 TRIGGER FAIL
                </button>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col justify-center items-center text-center p-4 border border-dashed border-slate-700/60 rounded">
              <ShieldCheck className="text-slate-600 w-10 h-10 mb-2 animate-pulse" />
              <p className="text-sm font-bold text-slate-400 font-mono uppercase tracking-wider">
                Twin Inactive Inspector
              </p>
              <p className="text-[11px] text-slate-500 max-w-[200px] leading-relaxed mt-1">
                Click a machine node card on the 2D visualizer to mount live sensor data and diagnostic override tools.
              </p>
            </div>
          )}
        </div>

        {/* Real-time Custom SVG charts */}
        <div className="flex flex-col gap-4 bg-slate-900/10 p-3 rounded-lg border border-[var(--border-soft)]">
          {renderLineChart(
            history,
            'throughput',
            'var(--color-green)',
            'Completed Throughput Trend',
            'ppm'
          )}
          {renderLineChart(
            history,
            'energyConsumption',
            'var(--color-blue)',
            'Cumulative Power Log',
            'kWh'
          )}
        </div>

        {/* Terminal Alerts Console */}
        <div className="h-[140px] flex flex-col bg-black/40 rounded-lg border border-[var(--border-soft)] overflow-hidden">
          <div className="bg-slate-900/80 px-4 py-2 border-b border-[var(--border-soft)] flex items-center gap-2">
            <ShieldAlert size={14} className="text-slate-400" />
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
              System Alerts & Audit Log
            </span>
          </div>
          <div className="flex-1 p-3 overflow-y-auto font-mono text-[10px] leading-relaxed flex flex-col gap-2 scrollbar-thin">
            {alerts.map((alert) => {
              const color =
                alert.severity === 'DANGER'
                  ? 'text-[#ef4444]'
                  : alert.severity === 'WARNING'
                  ? 'text-[#f59e0b]'
                  : 'text-[#10b981]';
              return (
                <div key={alert.id} className="flex gap-2 items-start border-b border-white/5 pb-1">
                  <span className="text-slate-600 flex-shrink-0">[{alert.timestamp}]</span>
                  <span className={`${color} flex-1`}>{alert.message}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
