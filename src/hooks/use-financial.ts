import { useMemo } from 'react';
import { calculate } from '@/lib/models';
import type { InputValues } from '@/lib/config';

export function useFinancial(inputs: InputValues) {
  return useMemo(() => calculate(inputs), [inputs]);
}
