import { AppProviders } from './app/providers/AppProviders';
import { HoloShell } from './BackofficeScene/HoloShell';

export function App() {
  return (
    <AppProviders>
      <HoloShell />
    </AppProviders>
  );
}
