export type MachineStatus = 'RUNNING' | 'MAINTENANCE' | 'ERROR' | 'IDLE';

export type MachineType = 'INTAKE' | 'CNC' | 'ASSEMBLY' | 'INSPECTION' | 'PACKAGING';

export interface Machine {
  id: string;
  name: string;
  type: MachineType;
  status: MachineStatus;
  temperature: number;      // in °C
  vibration: number;        // in mm/s
  energyConsumption: number;// in kW/h
  wearLevel: number;        // 0 to 100
  failureRate: number;      // 0 to 100 (probability offset)
  speed: number;            // cycles per minute
  lastMaintenance: Date;
  x: number;                // SVG X coordinate for layout
  y: number;                // SVG Y coordinate for layout
}

export type PartStage = 'RAW' | 'MACHINED' | 'ASSEMBLED' | 'INSPECTED' | 'PACKAGED' | 'DEFECTIVE';

export interface Part {
  id: string;
  stage: PartStage;
  // Conveyor tracking
  segmentIndex: number;     // index of the conveyor segment it is on (0 = Intake to CNC, 1 = CNC to Assembly, etc.)
  progress: number;         // 0 to 1 along the conveyor segment
  x: number;                // computed current SVG X
  y: number;                // computed current SVG Y
}

export type AlertSeverity = 'INFO' | 'WARNING' | 'DANGER';

export interface AlertLog {
  id: string;
  timestamp: string;
  machineId?: string;
  machineName?: string;
  severity: AlertSeverity;
  message: string;
}

export interface MetricSnapshot {
  timestamp: string;
  throughput: number;       // completed parts per minute
  defectRate: number;       // percentage of defectives
  energyConsumption: number;// cumulative/current power
  activeAlertsCount: number;
}
