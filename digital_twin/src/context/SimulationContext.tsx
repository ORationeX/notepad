import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import type { Machine, Part, AlertLog, MetricSnapshot, MachineStatus } from '../types';

interface SimulationContextProps {
  machines: Machine[];
  parts: Part[];
  alerts: AlertLog[];
  metrics: {
    totalProcessed: number;
    totalCompleted: number;
    totalDefects: number;
    currentEnergy: number;
    uptime: number; // in seconds
  };
  history: MetricSnapshot[];
  isPlaying: boolean;
  speedMultiplier: number;
  defectProbability: number;
  wearRateMultiplier: number;
  activeInspectorId: string | null;
  togglePlay: () => void;
  setSpeed: (speed: number) => void;
  setDefectProbability: (prob: number) => void;
  setWearRateMultiplier: (rate: number) => void;
  triggerBreakdown: (machineId: string) => void;
  performMaintenance: (machineId: string) => void;
  resetSimulation: () => void;
  setActiveInspectorId: (id: string | null) => void;
}

const SimulationContext = createContext<SimulationContextProps | undefined>(undefined);

const INITIAL_MACHINES = (): Machine[] => [
  {
    id: 'intake',
    name: 'Material Intake',
    type: 'INTAKE',
    status: 'RUNNING',
    temperature: 24.5,
    vibration: 0.2,
    energyConsumption: 1.2,
    wearLevel: 0,
    failureRate: 0.1,
    speed: 15,
    lastMaintenance: new Date(),
    x: 120,
    y: 180,
  },
  {
    id: 'cnc',
    name: 'CNC Machining Center',
    type: 'CNC',
    status: 'RUNNING',
    temperature: 42.0,
    vibration: 4.8,
    energyConsumption: 14.5,
    wearLevel: 0,
    failureRate: 1.5,
    speed: 12,
    lastMaintenance: new Date(),
    x: 360,
    y: 180,
  },
  {
    id: 'assembly',
    name: 'Robotic Assembly Arm',
    type: 'ASSEMBLY',
    status: 'RUNNING',
    temperature: 35.2,
    vibration: 2.5,
    energyConsumption: 8.0,
    wearLevel: 0,
    failureRate: 1.0,
    speed: 10,
    lastMaintenance: new Date(),
    x: 600,
    y: 180,
  },
  {
    id: 'inspection',
    name: 'Laser Quality Scanner',
    type: 'INSPECTION',
    status: 'RUNNING',
    temperature: 28.0,
    vibration: 0.5,
    energyConsumption: 3.5,
    wearLevel: 0,
    failureRate: 0.5,
    speed: 20,
    lastMaintenance: new Date(),
    x: 600,
    y: 360,
  },
  {
    id: 'packaging',
    name: 'Auto Packaging Unit',
    type: 'PACKAGING',
    status: 'RUNNING',
    temperature: 31.8,
    vibration: 1.8,
    energyConsumption: 5.2,
    wearLevel: 0,
    failureRate: 0.8,
    speed: 14,
    lastMaintenance: new Date(),
    x: 360,
    y: 360,
  },
];

// Conveyor layouts
// 0: Intake -> CNC (120, 180 to 360, 180)
// 1: CNC -> Assembly (360, 180 to 600, 180)
// 2: Assembly -> Inspection (600, 180 to 600, 360)
// 3: Inspection -> Packaging (600, 360 to 360, 360) (for normal parts)
// 4: Inspection -> Reject Bin (600, 360 to 760, 360) (for defective parts)
// 5: Packaging -> Exit (360, 360 to 120, 360)

export const SimulationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [speedMultiplier, setSpeedMultiplier] = useState<number>(1);
  const [defectProbability, setDefectProbability] = useState<number>(0.05); // 5% defect rate default
  const [wearRateMultiplier, setWearRateMultiplier] = useState<number>(1.0);
  const [activeInspectorId, setActiveInspectorId] = useState<string | null>(null);

  const [machines, setMachines] = useState<Machine[]>(INITIAL_MACHINES());
  const [parts, setParts] = useState<Part[]>([]);
  const [alerts, setAlerts] = useState<AlertLog[]>([
    {
      id: 'init',
      timestamp: new Date().toLocaleTimeString(),
      severity: 'INFO',
      message: 'Digital Twin Simulation initialized. All systems normal.',
    },
  ]);

  const [metrics, setMetrics] = useState({
    totalProcessed: 0,
    totalCompleted: 0,
    totalDefects: 0,
    currentEnergy: 0,
    uptime: 0,
  });

  const [history, setHistory] = useState<MetricSnapshot[]>([]);

  // We keep tracking of machine processing countdowns
  // MachineId -> { partId: string, durationRemaining: number }
  const processingQueue = useRef<Record<string, { partId: string; totalDuration: number; remaining: number }>>({});
  const maintenanceQueue = useRef<Record<string, { remaining: number }>>({});

  // Helper to add alert logs
  const addAlert = (severity: 'INFO' | 'WARNING' | 'DANGER', message: string, machineId?: string, machineName?: string) => {
    const newAlert: AlertLog = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toLocaleTimeString(),
      severity,
      message,
      machineId,
      machineName,
    };
    setAlerts((prev) => [newAlert, ...prev].slice(0, 100)); // Limit to last 100 alerts
  };

  const togglePlay = () => setIsPlaying(!isPlaying);
  const setSpeed = (speed: number) => setSpeedMultiplier(speed);

  const triggerBreakdown = (machineId: string) => {
    setMachines((prev) =>
      prev.map((m) => {
        if (m.id === machineId) {
          addAlert('DANGER', `CRITICAL FAILURE: ${m.name} broke down! Manual repair required immediately.`, m.id, m.name);
          // If machine was processing a part, let's keep it stuck
          return {
            ...m,
            status: 'ERROR' as MachineStatus,
            wearLevel: 100,
            temperature: Math.min(m.temperature + 25, 95), // spikes temperature on error
            vibration: m.vibration * 2.5,
          };
        }
        return m;
      })
    );
  };

  const performMaintenance = (machineId: string) => {
    setMachines((prev) =>
      prev.map((m) => {
        if (m.id === machineId) {
          addAlert('INFO', `Scheduled maintenance started for ${m.name}.`, m.id, m.name);
          maintenanceQueue.current[m.id] = { remaining: 4.0 }; // Maintenance takes 4.0 simulated seconds
          return {
            ...m,
            status: 'MAINTENANCE' as MachineStatus,
            vibration: 0,
            energyConsumption: 0.5, // low power during maintenance
          };
        }
        return m;
      })
    );
  };

  const resetSimulation = () => {
    setMachines(INITIAL_MACHINES());
    setParts([]);
    processingQueue.current = {};
    maintenanceQueue.current = {};
    setMetrics({
      totalProcessed: 0,
      totalCompleted: 0,
      totalDefects: 0,
      currentEnergy: 0,
      uptime: 0,
    });
    setHistory([]);
    setAlerts([
      {
        id: 'reset',
        timestamp: new Date().toLocaleTimeString(),
        severity: 'INFO',
        message: 'Simulation reset. Digital Twin restarted.',
      },
    ]);
  };

  // Main simulation loop ticker (runs every 100ms of real-time)
  useEffect(() => {
    if (!isPlaying) return;

    const timer = setInterval(() => {
      const dt = 0.1 * speedMultiplier; // simulated seconds elapsed in this 100ms tick

      // 1. Update Uptime
      setMetrics((prev) => ({
        ...prev,
        uptime: prev.uptime + dt,
      }));

      // 2. Handle Machine Maintenance Progress
      setMachines((prevMachines) => {
        return prevMachines.map((machine) => {
          if (machine.status === 'MAINTENANCE') {
            const maint = maintenanceQueue.current[machine.id];
            if (maint) {
              const remaining = maint.remaining - dt;
              if (remaining <= 0) {
                delete maintenanceQueue.current[machine.id];
                addAlert('INFO', `Maintenance completed for ${machine.name}. System calibrated.`, machine.id, machine.name);
                return {
                  ...machine,
                  status: 'RUNNING' as MachineStatus,
                  wearLevel: 0,
                  temperature: 25.0, // reset temperature
                  vibration: machine.id === 'cnc' ? 4.8 : machine.id === 'assembly' ? 2.5 : machine.id === 'inspection' ? 0.5 : machine.id === 'packaging' ? 1.8 : 0.2,
                  energyConsumption: machine.id === 'cnc' ? 14.5 : machine.id === 'assembly' ? 8.0 : machine.id === 'inspection' ? 3.5 : machine.id === 'packaging' ? 5.2 : 1.2,
                  lastMaintenance: new Date(),
                };
              } else {
                maintenanceQueue.current[machine.id] = { remaining };
              }
            }
          }
          return machine;
        });
      });

      // 3. Handle Machine Processing timers
      setMachines((prevMachines) => {
        let spawnedPart = false;

        const updated = prevMachines.map((machine) => {
          // If machine is not running, telemetry should adjust
          if (machine.status === 'ERROR') {
            // Keep temperature high and vibration erratic
            return {
              ...machine,
              temperature: Math.max(25.0, machine.temperature - dt * 0.5), // cools down very slowly
              energyConsumption: 2.0, // static error mode consumption
            };
          } else if (machine.status === 'IDLE' || machine.status === 'RUNNING') {
            // Check if machine is currently processing a part
            const proc = processingQueue.current[machine.id];
            if (proc) {
              const remaining = proc.remaining - dt;
              
              // Telemetry adjustments during active operation
              const wearIncrease = (machine.type === 'CNC' ? 0.8 : machine.type === 'ASSEMBLY' ? 0.6 : machine.type === 'INSPECTION' ? 0.2 : machine.type === 'PACKAGING' ? 0.4 : 0.05) * dt * wearRateMultiplier;
              const newWear = Math.min(100, machine.wearLevel + wearIncrease);
              
              // Vibration fluctuates slightly
              const baseVib = machine.type === 'CNC' ? 4.8 : machine.type === 'ASSEMBLY' ? 2.5 : machine.type === 'INSPECTION' ? 0.5 : machine.type === 'PACKAGING' ? 1.8 : 0.2;
              const currentVib = baseVib + (Math.random() - 0.5) * 0.4;

              // Temperature rises during work
              const maxTemp = machine.type === 'CNC' ? 72 : machine.type === 'ASSEMBLY' ? 48 : machine.type === 'INSPECTION' ? 32 : machine.type === 'PACKAGING' ? 38 : 28;
              const targetTemp = maxTemp + (newWear > 70 ? (newWear - 70) * 0.5 : 0); // wear increases heat
              const currentTemp = machine.temperature + (targetTemp - machine.temperature) * 0.1 * dt;

              // Check if processing completed
              if (remaining <= 0) {
                // Completed!
                const partId = proc.partId;
                delete processingQueue.current[machine.id];

                // Route part to its next segment
                setParts((prevParts) => {
                  return prevParts.map((p) => {
                    if (p.id === partId) {
                      // Process transitions
                      let nextStage = p.stage;
                      let nextSegment = p.segmentIndex;

                      if (machine.type === 'CNC') {
                        nextStage = 'MACHINED';
                        nextSegment = 1; // CNC -> Assembly conveyor
                      } else if (machine.type === 'ASSEMBLY') {
                        nextStage = 'ASSEMBLED';
                        nextSegment = 2; // Assembly -> Inspection conveyor
                      } else if (machine.type === 'INSPECTION') {
                        // Inspect for defectives
                        const isDefective = Math.random() < defectProbability;
                        if (isDefective) {
                          nextStage = 'DEFECTIVE';
                          nextSegment = 4; // Inspection -> Reject Bin conveyor
                          setMetrics((prev) => ({
                            ...prev,
                            totalDefects: prev.totalDefects + 1,
                          }));
                          addAlert('WARNING', `Quality Warning: Defect detected. Part ${p.id.slice(-4)} routed to reject bin.`, machine.id, machine.name);
                        } else {
                          nextStage = 'INSPECTED';
                          nextSegment = 3; // Inspection -> Packaging conveyor
                        }
                      } else if (machine.type === 'PACKAGING') {
                        nextStage = 'PACKAGED';
                        nextSegment = 5; // Packaging -> Exit conveyor
                      }

                      return {
                        ...p,
                        stage: nextStage,
                        segmentIndex: nextSegment,
                        progress: 0,
                      };
                    }
                    return p;
                  });
                });

                // Random wear breakdown check if wear is high
                if (newWear >= 100) {
                  // Instant failure!
                  setTimeout(() => triggerBreakdown(machine.id), 0);
                  return {
                    ...machine,
                    status: 'ERROR' as MachineStatus,
                    wearLevel: 100,
                    temperature: currentTemp,
                    vibration: currentVib,
                  };
                } else if (newWear > 70 && Math.random() < (newWear - 70) * 0.002 * dt) {
                  // Wear based failure
                  setTimeout(() => triggerBreakdown(machine.id), 0);
                  return {
                    ...machine,
                    status: 'ERROR' as MachineStatus,
                    wearLevel: newWear,
                    temperature: currentTemp,
                    vibration: currentVib,
                  };
                }

                return {
                  ...machine,
                  status: 'RUNNING' as MachineStatus,
                  wearLevel: newWear,
                  temperature: currentTemp,
                  vibration: currentVib,
                };
              } else {
                // Still processing
                processingQueue.current[machine.id] = {
                  ...proc,
                  remaining,
                };
                return {
                  ...machine,
                  status: 'RUNNING' as MachineStatus,
                  wearLevel: newWear,
                  temperature: currentTemp,
                  vibration: currentVib,
                };
              }
            } else {
              // Idle state telemetry (cools down)
              const ambientTemp = 24.5;
              const currentTemp = machine.temperature + (ambientTemp - machine.temperature) * 0.05 * dt;
              const baseVib = machine.type === 'CNC' ? 0.8 : machine.type === 'ASSEMBLY' ? 0.3 : machine.type === 'INSPECTION' ? 0.1 : machine.type === 'PACKAGING' ? 0.2 : 0.1;
              const currentVib = baseVib + (Math.random() - 0.5) * 0.05;

              return {
                ...machine,
                status: 'IDLE' as MachineStatus,
                temperature: currentTemp,
                vibration: currentVib,
                energyConsumption: machine.type === 'INTAKE' ? 0.5 : 1.0, // lower idle power
              };
            }
          }
          return machine;
        });

        // 4. Handle Material Intake spawning logic
        // Intake spawn timer: every machine.speed seconds
        const intakeMachine = updated.find((m) => m.type === 'INTAKE');
        if (intakeMachine && intakeMachine.status === 'RUNNING') {
          // Check if there is space on Conveyor 0
          // Spawn interval: e.g. every 4 seconds
          const spawnInterval = 4.0;
          const isTime = Math.floor(metrics.uptime / spawnInterval) !== Math.floor((metrics.uptime - dt) / spawnInterval);
          if (isTime) {
            spawnedPart = true;
          }
        }

        if (spawnedPart) {
          const newPartId = `PART-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
          setParts((prevParts) => {
            // Check if there's a part blocked at the start of conveyor 0 (progress <= 0.1)
            const isBlocked = prevParts.some((p) => p.segmentIndex === 0 && p.progress <= 0.15);
            if (isBlocked) {
              return prevParts; // Skip spawning if blocked to prevent overlapping
            }
            setMetrics((prev) => ({
              ...prev,
              totalProcessed: prev.totalProcessed + 1,
            }));
            return [
              ...prevParts,
              {
                id: newPartId,
                stage: 'RAW',
                segmentIndex: 0,
                progress: 0,
                x: 120,
                y: 180,
              },
            ];
          });
        }

        return updated;
      });

      // 5. Update Part Conveyor positions & check arrivals at machines
      setParts((prevParts) => {
        // We determine which conveyor segments are "blocked" (have a part stuck at progress >= 1.0 waiting to enter a machine)
        // Conveyors: 
        // 0: CNC, 1: Assembly, 2: Inspection, 3: Packaging, 4: Reject Bin, 5: Exit
        const conveyorBlocked: Record<number, boolean> = {};

        // Compute blocks first
        prevParts.forEach((part) => {
          if (part.progress >= 1.0) {
            conveyorBlocked[part.segmentIndex] = true;
          }
        });

        // Advance unblocked parts
        let updatedParts = prevParts.map((part) => {
          if (part.progress >= 1.0) {
            // Part is waiting to dock into next machine
            return part;
          }

          // Check if segment is blocked
          // But wait, parts can advance if they are behind a moving part.
          // To make it simple: if the lead part of this segment is blocked (meaning conveyorBlocked[segmentIndex] is true),
          // then the entire conveyor segment stops.
          if (conveyorBlocked[part.segmentIndex]) {
            return part; // conveyor stopped
          }

          // Advance progress
          // Speed: it takes 3 seconds to traverse standard horizontal conveyors (segments 0, 1, 3, 5)
          // Segment 2 (vertical) takes 2 seconds.
          // Segment 4 (reject) takes 2 seconds.
          const traverseTime = part.segmentIndex === 2 || part.segmentIndex === 4 ? 2.0 : 3.0;
          const deltaProgress = dt / traverseTime;
          const nextProgress = Math.min(1.0, part.progress + deltaProgress);

          // Check if there is another part ahead on the same conveyor segment
          // We can prevent overlapping by checking if another part is within `deltaProgress * 1.5` distance
          const partAhead = prevParts.find(
            (other) =>
              other.id !== part.id &&
              other.segmentIndex === part.segmentIndex &&
              other.progress > part.progress &&
              other.progress - part.progress < 0.2
          );

          if (partAhead) {
            // Slow down or stop to maintain spacing
            return part;
          }

          return {
            ...part,
            progress: nextProgress,
          };
        });

        // 6. Dock parts that arrived at their destination machines
        // We need to mutate processingQueue inside this setParts call, or schedule it.
        // Since we are in the React loop, let's look at parts that reached progress = 1.0
        // and try to dock them.
        const partsToKeep: Part[] = [];

        updatedParts.forEach((part) => {
          if (part.progress >= 1.0) {
            // Find target machine
            let targetMachineId = '';
            let processDuration = 2.0;

            if (part.segmentIndex === 0) {
              targetMachineId = 'cnc';
              processDuration = 3.0;
            } else if (part.segmentIndex === 1) {
              targetMachineId = 'assembly';
              processDuration = 4.0;
            } else if (part.segmentIndex === 2) {
              targetMachineId = 'inspection';
              processDuration = 2.0;
            } else if (part.segmentIndex === 3) {
              targetMachineId = 'packaging';
              processDuration = 2.5;
            } else if (part.segmentIndex === 4) {
              // Reject Bin: consumes instantly
              setMetrics((prev) => ({
                ...prev,
                // Already counted defectives in step 3
              }));
              // Do NOT keep this part (archived!)
              return;
            } else if (part.segmentIndex === 5) {
              // Packaging to Exit: completes instantly
              setMetrics((prev) => ({
                ...prev,
                totalCompleted: prev.totalCompleted + 1,
              }));
              // Do NOT keep this part (archived!)
              return;
            }

            // Check if target machine is running and not processing
            let machineAvailable = false;
            setMachines((prevMachines) => {
              const machine = prevMachines.find((m) => m.id === targetMachineId);
              if (machine && machine.status === 'RUNNING' && !processingQueue.current[targetMachineId]) {
                machineAvailable = true;
              }
              return prevMachines;
            });

            if (machineAvailable) {
              // Start processing in the machine
              processingQueue.current[targetMachineId] = {
                partId: part.id,
                totalDuration: processDuration,
                remaining: processDuration,
              };
              // Keep the part in active state, but set its X and Y to the machine coordinates
              // (we make it invisible or dock it visually on the factory floor)
              partsToKeep.push({
                ...part,
                // Docked inside machine: set progress to slightly over 1 to designate docked
                progress: 1.1,
              });
            } else {
              // Kept waiting at the end of conveyor
              partsToKeep.push(part);
            }
          } else {
            // Still travelling on conveyor
            partsToKeep.push(part);
          }
        });

        // Compute SVG positions for all active parts
        return partsToKeep.map((part) => {
          let x = 120;
          let y = 180;
          const p = Math.min(1.0, part.progress);

          if (part.segmentIndex === 0) {
            // Intake (120,180) -> CNC (360,180)
            x = 120 + p * 240;
            y = 180;
          } else if (part.segmentIndex === 1) {
            // CNC (360,180) -> Assembly (600,180)
            x = 360 + p * 240;
            y = 180;
          } else if (part.segmentIndex === 2) {
            // Assembly (600,180) -> Inspection (600,360)
            x = 600;
            y = 180 + p * 180;
          } else if (part.segmentIndex === 3) {
            // Inspection (600,360) -> Packaging (360,360)
            x = 600 - p * 240;
            y = 360;
          } else if (part.segmentIndex === 4) {
            // Inspection (600,360) -> Reject Bin (760,360)
            x = 600 + p * 160;
            y = 360;
          } else if (part.segmentIndex === 5) {
            // Packaging (360,360) -> Exit (120,360)
            x = 360 - p * 240;
            y = 360;
          }

          // If docked inside a machine, lock position to machine center
          if (part.progress > 1.0) {
            if (part.segmentIndex === 0) { x = 360; y = 180; } // inside CNC
            else if (part.segmentIndex === 1) { x = 600; y = 180; } // inside Assembly
            else if (part.segmentIndex === 2) { x = 600; y = 360; } // inside Inspection
            else if (part.segmentIndex === 3) { x = 360; y = 360; } // inside Packaging
          }

          return {
            ...part,
            x,
            y,
          };
        });
      });

      // 7. Update Energy and Analytics Metric History
      setMetrics((prev) => {
        let activePower = 0;
        setMachines((prevMachines) => {
          prevMachines.forEach((m) => {
            activePower += m.energyConsumption;
          });
          return prevMachines;
        });

        const newEnergy = prev.currentEnergy + (activePower * dt) / 3600; // in kWh

        return {
          ...prev,
          currentEnergy: newEnergy,
        };
      });

    }, 100);

    return () => clearInterval(timer);
  }, [isPlaying, speedMultiplier, defectProbability, wearRateMultiplier]);

  // Aggregate stats every 3 seconds for historical charts
  useEffect(() => {
    if (!isPlaying) return;

    const timer = setInterval(() => {
      setMetrics((prev) => {
        setHistory((prevHistory) => {
          // Calculate defect rate
          const totalItems = prev.totalCompleted + prev.totalDefects;
          const rate = totalItems > 0 ? Math.round((prev.totalDefects / totalItems) * 100) : 0;
          // Calculate throughput: average output per minute
          // We can approximate active throughput based on completed items in the last interval or cumulative
          const activeUptimeMin = prev.uptime / 60;
          const throughput = activeUptimeMin > 0 ? parseFloat((prev.totalCompleted / activeUptimeMin).toFixed(1)) : 0;

          const snapshot: MetricSnapshot = {
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            throughput,
            defectRate: rate,
            energyConsumption: parseFloat(prev.currentEnergy.toFixed(3)),
            activeAlertsCount: alerts.filter(a => a.severity === 'DANGER' || a.severity === 'WARNING').length,
          };

          return [...prevHistory, snapshot].slice(-15); // keep last 15 ticks (45 seconds of stats)
        });

        return prev;
      });
    }, 3000);

    return () => clearInterval(timer);
  }, [isPlaying, alerts]);

  return (
    <SimulationContext.Provider
      value={{
        machines,
        parts,
        alerts,
        metrics,
        history,
        isPlaying,
        speedMultiplier,
        defectProbability,
        wearRateMultiplier,
        activeInspectorId,
        togglePlay,
        setSpeed,
        setDefectProbability,
        setWearRateMultiplier,
        triggerBreakdown,
        performMaintenance,
        resetSimulation,
        setActiveInspectorId,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
};

export const useSimulation = () => {
  const context = useContext(SimulationContext);
  if (context === undefined) {
    throw new Error('useSimulation must be used within a SimulationProvider');
  }
  return context;
};
