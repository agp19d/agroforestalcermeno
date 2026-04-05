import { runSimulation } from './simulation';
import type { InputValues } from './config';
import type { VariableRange } from './simulation';

export interface WorkerInput {
  inputs: InputValues;
  ranges: VariableRange[];
  nIterations: number;
}

self.onmessage = (e: MessageEvent<WorkerInput>) => {
  const { inputs, ranges, nIterations } = e.data;
  const results = runSimulation(inputs, ranges, nIterations);
  self.postMessage(results);
};
