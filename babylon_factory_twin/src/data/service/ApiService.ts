import type { IFloor, IMachine } from '../model/Types';
import { floors, machines } from '../repository/MockDB';

export class ApiService {
  /**
   * Fetch all floor data
   */
  public async getFloors(): Promise<IFloor[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([...floors]);
      }, 500); // 500ms network delay simulation
    });
  }

  /**
   * Fetch machines by floor ID
   */
  public async getMachinesByFloor(floorId: number): Promise<IMachine[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(machines.filter(m => m.floorId === floorId));
      }, 600);
    });
  }

  /**
   * Fetch all machines
   */
  public async getAllMachines(): Promise<IMachine[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([...machines]);
      }, 800);
    });
  }
}
