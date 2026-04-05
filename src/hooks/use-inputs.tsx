import { createContext, useContext, useReducer, type ReactNode } from 'react';
import { DEFAULT_INPUTS, type InputValues } from '@/lib/config';

type Action =
  | { type: 'SET_FIELD'; key: keyof InputValues; value: number }
  | { type: 'LOAD_SCENARIO'; inputs: InputValues }
  | { type: 'RESET_DEFAULTS' };

function reducer(state: InputValues, action: Action): InputValues {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, [action.key]: action.value };
    case 'LOAD_SCENARIO':
      return { ...action.inputs };
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

export function useInputs() {
  const ctx = useContext(InputsContext);
  if (!ctx) throw new Error('useInputs must be used within InputsProvider');
  return ctx;
}
