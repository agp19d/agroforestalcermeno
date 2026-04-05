import { InputsProvider } from '@/hooks/use-inputs';
import { AppShell } from '@/components/layout/app-shell';
import { Dashboard } from '@/components/dashboard/dashboard';

export default function App() {
  return (
    <InputsProvider>
      <AppShell>
        <Dashboard />
      </AppShell>
    </InputsProvider>
  );
}
