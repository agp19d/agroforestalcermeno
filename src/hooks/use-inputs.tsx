import { createContext, useContext, useReducer, type ReactNode } from 'react';
import { DEFAULT_INPUTS, sanitizeInputs, type InputValues } from '@/lib/config';

type Action =
  | { type: 'SET_FIELD'; key: keyof InputValues; value: number }
  | { type: 'LOAD_SCENARIO'; inputs: InputValues }
  | { type: 'RESET_DEFAULTS' };

function reducer(state: InputValues, action: Action): InputValues {
  switch (action.type) {
    case 'SET_FIELD': {
      // Security: reject non-finite values to prevent NaN propagation
      const val = action.value;
      if (typeof val !== 'number' || !Number.isFinite(val)) return state;
      return { ...state, [action.key]: val };
    }
    case 'LOAD_SCENARIO':
      // Security: sanitize loaded scenario data to prevent prototype pollution
      // and NaN propagation from tampered localStorage
      return sanitizeInputs(action.inputs) ?? { ...DEFAULT_INPUTS };
    case 'RESET_DEFAULTS':
      return { ...DEFAULT_INPUTS };
    default:
      return state;
  }
}

interface InputsContextValue {
  inputs: InputValues;
  setField: (key: keyof InputValues, value: number) => void;
  loadScenario: (inputs: InputValues) => void;
  resetDefaults: () => void;
}

const InputsContext = createContext<InputsContextValue | null>(null);

export function InputsProvider({ children }: { children: ReactNode }) {
  const [inputs, dispatch] = useReducer(reducer, DEFAULT_INPUTS);
  const value: InputsContextValue = {
    inputs,
    setField: (key, value) => dispatch({ type: 'SET_FIELD', key, value }),
    loadScenario: (inputs) => dispatch({ type: 'LOAD_SCENARIO', inputs }),
    resetDefaults: () => dispatch({ type: 'RESET_DEFAULTS' }),
  };
  return <InputsContext.Provider value={value}>{children}</InputsContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useInputs() {
  const ctx = useContext(InputsContext);
  if (!ctx) throw new Error('useInputs must be used within InputsProvider');
  return ctx;
}
